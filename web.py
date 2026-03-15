#!/usr/bin/env python3
"""
MastoCloud Web Interface
Run: python web.py
Then open http://localhost:5000 in your browser.
"""

import sys
import os
import io
import json
import base64
import subprocess
import tempfile
from pathlib import Path
from threading import Timer

from flask import Flask, request, Response, stream_with_context, render_template_string, jsonify
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / '.env'

COLOUR_SCHEMES = [
    'default', 'ocean', 'fire', 'forest', 'sunset',
    'purple', 'grayscale', 'rainbow', 'plasma', 'viridis',
]

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MastoCloud</title>
<style>
:root {
    --bg:           #191b22;
    --surface:      #282c37;
    --card:         #313543;
    --border:       #404457;
    --accent:       #6364ff;
    --accent-hover: #7775ff;
    --accent-dim:   #6364ff33;
    --text:         #d9e1e8;
    --muted:        #9baec8;
    --success:      #79bd9a;
    --error:        #df405a;
    --input-bg:     #1f232b;
    --terminal-bg:  #0d1117;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.logo-icon { font-size: 2rem; }

header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent);
}

header p {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.1rem;
}

.header-spacer { flex: 1; }

.btn-settings {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--muted);
    padding: 0.45rem 0.9rem;
    font-size: 0.85rem;
    cursor: pointer;
    transition: border-color 0.2s, color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.btn-settings:hover {
    border-color: var(--accent);
    color: var(--text);
}

main {
    display: grid;
    grid-template-columns: 380px 1fr 300px;
    gap: 1.5rem;
    padding: 1.5rem 2rem;
    flex: 1;
    max-width: 1600px;
    width: 100%;
    margin: 0 auto;
}

@media (max-width: 1100px) {
    main { grid-template-columns: 380px 1fr; }
    .action-panel { display: none; }
}

@media (max-width: 900px) {
    main { grid-template-columns: 1fr; }
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
}

.section-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 0.75rem;
}

.field { margin-bottom: 1rem; }

.field label {
    display: block;
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 0.35rem;
}

input[type=text],
select,
textarea {
    width: 100%;
    background: var(--input-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    padding: 0.55rem 0.75rem;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
}

input:focus, select:focus, textarea:focus {
    border-color: var(--accent);
}

.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.1rem 0;
}

.mode-toggle {
    display: grid;
    grid-template-columns: 1fr 1fr;
    background: var(--input-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.mode-btn {
    padding: 0.55rem;
    border: none;
    background: transparent;
    color: var(--muted);
    font-size: 0.9rem;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
}

.mode-btn.active {
    background: var(--accent);
    color: #fff;
    font-weight: 600;
}

.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.drop-zone {
    border: 2px dashed var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    text-align: center;
    cursor: pointer;
    color: var(--muted);
    font-size: 0.85rem;
    transition: border-color 0.2s, background 0.2s;
}

.drop-zone:hover, .drop-zone.dragover {
    border-color: var(--accent);
    background: var(--accent-dim);
    color: var(--text);
}

.drop-zone .drop-icon { font-size: 1.5rem; display: block; margin-bottom: 0.3rem; }
.drop-filename { font-size: 0.8rem; color: var(--accent); margin-top: 0.4rem; }

#maskInput { display: none; }

.btn-generate {
    width: 100%;
    padding: 0.75rem;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s, opacity 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.btn-generate:hover:not(:disabled) { background: var(--accent-hover); }
.btn-generate:disabled { opacity: 0.55; cursor: not-allowed; }

.spinner {
    width: 18px; height: 18px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: none;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Output panel */
.output-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.status-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: var(--muted);
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--border);
    transition: background 0.3s;
}

.status-dot.running { background: var(--accent); animation: pulse 1s infinite; }
.status-dot.done    { background: var(--success); animation: none; }
.status-dot.error   { background: var(--error);   animation: none; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

.terminal {
    background: var(--terminal-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.8rem;
    color: #8b949e;
    height: 240px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
    line-height: 1.5;
}

.terminal .line-success { color: var(--success); }
.terminal .line-error   { color: var(--error); }

.image-panel {
    display: none;
    flex-direction: column;
    gap: 0.75rem;
}

.image-panel img {
    width: 100%;
    border-radius: 10px;
    border: 1px solid var(--border);
}

.btn-download {
    align-self: flex-start;
    padding: 0.5rem 1.2rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 0.85rem;
    text-decoration: none;
    transition: border-color 0.2s, background 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

.btn-download:hover {
    border-color: var(--accent);
    background: var(--accent-dim);
}

input[type=range] {
    width: 100%;
    accent-color: var(--accent);
    cursor: pointer;
}

.btn-sm {
    padding: 0.4rem 0.9rem;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: background 0.2s, border-color 0.2s;
}

.btn-sm-primary {
    background: var(--accent);
    color: #fff;
}

.btn-sm-primary:hover { background: var(--accent-hover); }

.btn-sm-secondary {
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--text);
}

.btn-sm-secondary:hover { border-color: var(--accent); }

.creator-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.75rem;
}

.mask-compare {
    display: none;
    gap: 0.75rem;
    margin-top: 0.75rem;
}

.mask-compare > div {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}

.mask-compare img {
    width: 100%;
    border-radius: 8px;
    border: 1px solid var(--border);
    max-height: 150px;
    object-fit: contain;
    background: #000;
}

.mask-compare span {
    font-size: 0.72rem;
    color: var(--muted);
    text-align: center;
}

/* Modal */
.modal-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.65);
    z-index: 100;
    align-items: center;
    justify-content: center;
}

.modal-backdrop.open { display: flex; }

.modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    width: min(560px, 95vw);
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-header h2 {
    font-size: 1rem;
    font-weight: 600;
}

.modal-close {
    background: none;
    border: none;
    color: var(--muted);
    font-size: 1.3rem;
    cursor: pointer;
    line-height: 1;
}

.modal-close:hover { color: var(--text); }

.modal textarea {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.85rem;
    resize: vertical;
    min-height: 220px;
}

.modal-note {
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.5;
}

.modal-footer {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
}

.btn-secondary {
    padding: 0.5rem 1.1rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 0.9rem;
    cursor: pointer;
    transition: border-color 0.2s;
}

.btn-secondary:hover { border-color: var(--accent); }

.btn-primary {
    padding: 0.5rem 1.1rem;
    background: var(--accent);
    border: none;
    border-radius: 8px;
    color: #fff;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-primary:hover { background: var(--accent-hover); }

.modal-save-status {
    font-size: 0.8rem;
    color: var(--success);
    align-self: center;
    display: none;
}

.post-panel {
    display: none;
    flex-direction: column;
    gap: 0.6rem;
}

.post-panel textarea {
    resize: vertical;
    min-height: 120px;
    font-size: 0.85rem;
    line-height: 1.5;
}

.char-counter {
    font-size: 0.75rem;
    color: var(--muted);
    text-align: right;
}

.char-counter.near-limit { color: #f0a500; }
.char-counter.over-limit { color: var(--error); }

.post-status {
    font-size: 0.8rem;
    padding: 0.45rem 0.65rem;
    border-radius: 6px;
    display: none;
    line-height: 1.4;
}

.post-status.success {
    background: rgba(121,189,154,0.15);
    color: var(--success);
}

.post-status.error {
    background: rgba(223,64,90,0.15);
    color: var(--error);
}
</style>
</head>
<body>

<header>
    <span class="logo-icon">☁</span>
    <div>
        <h1>MastoCloud</h1>
        <p>Mastodon Word Cloud Generator</p>
    </div>
    <div class="header-spacer"></div>
    <button class="btn-settings" onclick="openSettings()">⚙ Edit Config</button>
</header>

<main>

<!-- ── Left: Form ─────────────────────────────────────────── -->
<div>
<form id="cloudForm" enctype="multipart/form-data">

    <div class="card">
        <p class="section-title">Source</p>

        <div class="mode-toggle">
            <button type="button" class="mode-btn active" id="btnAccount"
                    onclick="setMode('account')">👤 Account</button>
            <button type="button" class="mode-btn" id="btnHashtag"
                    onclick="setMode('hashtag')">＃ Hashtags</button>
        </div>
        <input type="hidden" name="mode" id="modeInput" value="account">

        <div id="accountField" class="field" style="margin-bottom:0">
            <label>Account Handle</label>
            <input type="text" name="account" placeholder="@you@instance.social">
        </div>

        <div id="hashtagField" class="field" style="margin-bottom:0; display:none">
            <label>Hashtags (space-separated)</label>
            <input type="text" name="hashtags" placeholder="python linux infosec">
        </div>
    </div>

    <div class="card" style="margin-top:1rem">
        <p class="section-title">Mask Creator</p>
        <p style="font-size:0.8rem; color:var(--muted); margin-bottom:0.75rem">
            Convert any image into a word cloud mask shape.
        </p>

        <div class="drop-zone" id="creatorDropZone"
             onclick="document.getElementById('creatorInput').click()"
             ondragover="onCreatorDragOver(event)"
             ondragleave="onCreatorDragLeave()"
             ondrop="onCreatorDrop(event)">
            <span class="drop-icon">📸</span>
            Drop source image or click to browse
            <div class="drop-filename" id="creatorFilename"></div>
        </div>
        <input type="file" id="creatorInput" accept="image/*" style="display:none"
               onchange="onCreatorFile(this.files[0])">

        <div class="field" style="margin-top:0.75rem">
            <label>Conversion Method</label>
            <select id="creatorMethod">
                <option value="auto">Auto-detect</option>
                <option value="dark">Dark shape on light background</option>
                <option value="light">Light shape on dark background</option>
                <option value="alpha">Use transparency (PNG with alpha)</option>
            </select>
        </div>

        <div class="field" style="margin-bottom:0.5rem">
            <label>Threshold: <span id="thresholdVal">128</span></label>
            <input type="range" min="0" max="255" value="128" id="thresholdSlider"
                   oninput="document.getElementById('thresholdVal').textContent=this.value">
        </div>

        <div class="creator-actions">
            <button type="button" class="btn-sm btn-sm-primary" onclick="createMask()">
                Create Mask
            </button>
            <button type="button" class="btn-sm btn-sm-secondary" id="useMaskBtn"
                    style="display:none" onclick="useMask()">
                ✓ Use as Mask
            </button>
            <a class="btn-sm btn-sm-secondary" id="downloadMaskBtn"
               style="display:none; text-decoration:none" download="mask.png">
                ⬇ Download
            </a>
        </div>

        <div class="mask-compare" id="maskCompare">
            <div>
                <img id="creatorSourcePreview" src="" alt="Source">
                <span>Source</span>
            </div>
            <div>
                <img id="creatorMaskPreview" src="" alt="Mask">
                <span>Generated Mask</span>
            </div>
        </div>
    </div>

    <div class="card" style="margin-top:1rem">
        <p class="section-title">Options</p>

        <div class="grid-2">
            <div class="field">
                <label>Colour Scheme</label>
                <select name="colour">
                    {% for scheme in colour_schemes %}
                    <option value="{{ scheme }}">{{ scheme.capitalize() }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="field">
                <label>Transparent BG</label>
                <select name="transparent">
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                </select>
            </div>
        </div>

        <div class="field" style="margin-bottom:0">
            <label>Auto-post to Mastodon</label>
            <select name="auto_post">
                <option value="No">No</option>
                <option value="Yes">Yes</option>
            </select>
        </div>

        <hr class="divider">

        <p class="section-title">Mask Image (optional)</p>
        <div class="drop-zone" id="dropZone"
             onclick="document.getElementById('maskInput').click()"
             ondragover="onDragOver(event)"
             ondragleave="onDragLeave()"
             ondrop="onDrop(event)">
            <span class="drop-icon">🖼</span>
            Drop an image here or click to browse
            <div class="drop-filename" id="dropFilename"></div>
        </div>
        <input type="file" name="mask" id="maskInput" accept="image/*"
               onchange="showFilename(this.files[0])">
        <img id="maskPreview" src="" alt="Mask preview"
             style="display:none; width:100%; margin-top:0.75rem; border-radius:8px;
                    border:1px solid var(--border); max-height:200px; object-fit:contain;">
    </div>

</form>
</div>

<!-- ── Middle: Output ─────────────────────────────────────── -->
<div class="output-panel">

    <div class="card" style="padding: 0.75rem 1.25rem;">
        <div class="status-bar">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">Ready</span>
        </div>
    </div>

    <div class="card" style="padding: 0; overflow: hidden; flex: 0 0 auto;">
        <div class="terminal" id="terminal">Waiting to generate…</div>
    </div>

    <div class="image-panel card" id="imagePanel">
        <p class="section-title">Generated Word Cloud</p>
        <img id="resultImg" src="" alt="Generated word cloud">
        <a class="btn-download" id="downloadBtn" href="#" download="wordcloud.png">
            ⬇ Download Image
        </a>
    </div>

</div>

<!-- ── Right: Actions ─────────────────────────────────────── -->
<div class="action-panel">
    <div class="card" style="display:flex; flex-direction:column; gap:1rem; position:sticky; top:1.5rem;">
        <p class="section-title">Actions</p>
        <button type="submit" form="cloudForm" class="btn-generate" id="generateBtn">
            <div class="spinner" id="spinner"></div>
            <span id="btnLabel">⚡ Generate</span>
        </button>

        <div class="post-panel" id="postPanel">
            <hr class="divider" style="margin:0">
            <p class="section-title">Post to Mastodon</p>
            <textarea id="postText" name="postText" rows="6"
                      placeholder="Write your post…"
                      oninput="updateCharCount()"></textarea>
            <div class="char-counter" id="charCounter">0 / 500</div>
            <button type="button" class="btn-sm btn-sm-primary" id="postBtn"
                    onclick="postToMastodon()"
                    style="width:100%; padding:0.6rem; font-size:0.9rem">
                📤 Post to Mastodon
            </button>
            <div class="post-status" id="postStatus"></div>
        </div>
    </div>
</div>
</main>

<footer style="text-align:center; padding:1rem 2rem; font-size:0.85rem; color:var(--muted);
               border-top:1px solid var(--border); background:var(--surface);
               display:flex; align-items:center; justify-content:center; gap:1.5rem;">
    <a href="https://github.com/vwillcox/MastoCloud" target="_blank" rel="noopener"
       style="color:var(--muted); text-decoration:none; display:flex; align-items:center; gap:0.4rem;
              transition:color 0.2s;" onmouseover="this.style.color='var(--text)'"
       onmouseout="this.style.color='var(--muted)'">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57
                     0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41
                     -1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815
                     2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925
                     0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23
                     .96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65
                     .24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925
                     .435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57
                     A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
        </svg>
        vwillcox/MastoCloud
    </a>
    <span style="color:var(--border)">|</span>
    <a href="https://hachyderm.io/@talktech" target="_blank" rel="noopener"
       style="color:var(--muted); text-decoration:none; display:flex; align-items:center; gap:0.4rem;
              transition:color 0.2s;" onmouseover="this.style.color='var(--text)'"
       onmouseout="this.style.color='var(--muted)'">
        <svg width="18" height="18" viewBox="0 0 216.4 232" fill="currentColor">
            <path d="M211.8 139.7c-3.2 16.6-28.9 34.8-58.4 38.3-15.4 1.8-30.5 3.5-46.6 2.7
                     -26.4-1.2-47.2-6.3-47.2-6.3 0 2.6.2 5 .5 7.4 3.5 26.8 26.5 28.4 48.3 29.1
                     21.9.7 41.4-5.4 41.4-5.4l.9 19.9s-15.3 8.2-42.6 9.7c-15.1.8-33.8-.4-55.6-5.8
                     C9.8 220.5 1.6 182.2.3 143.3c-.4-10.9-.2-21.2-.2-29.8 0-37.5 24.6-48.5 24.6-48.5
                     12.4-5.7 33.7-8.1 55.8-8.3h.5c22.2.2 43.5 2.6 55.9 8.3 0 0 24.6 11 24.6 48.5
                     0 0 .3 27.7-4.7 45.7M178 80.1c0-11-2.8-19.7-8.4-26.2-5.8-6.5-13.4-9.8-22.9-9.8
                     -10.9 0-19.2 4.2-24.6 12.6l-5.3 8.9-5.3-8.9c-5.4-8.4-13.7-12.6-24.6-12.6
                     -9.5 0-17.1 3.3-22.9 9.8C58.4 60.4 55.6 69.1 55.6 80.1v50.7h20.1V81.4
                     c0-11 4.6-16.6 13.8-16.6 10.2 0 15.3 6.6 15.3 19.6v28.4h20V84.4c0-13 5.1-19.6
                     15.3-19.6 9.2 0 13.8 5.6 13.8 16.6v49.4H178V80.1z"/>
        </svg>
        @talktech@hachyderm.io
    </a>
</footer>

<!-- ── Settings Modal ─────────────────────────────────────── -->
<div class="modal-backdrop" id="modalBackdrop" onclick="closeOnBackdrop(event)">
    <div class="modal">
        <div class="modal-header">
            <h2>⚙ Edit Config (.env)</h2>
            <button class="modal-close" onclick="closeSettings()">✕</button>
        </div>
        <textarea id="envEditor" spellcheck="false" placeholder="Loading…"></textarea>
        <p class="modal-note">
            Set <code>MASTODON_API_KEY</code> and <code>MASTODON_SERVER_URL</code> here.
            Changes are saved directly to the <code>.env</code> file.
        </p>
        <div class="modal-footer">
            <span class="modal-save-status" id="saveStatus">✓ Saved</span>
            <button class="btn-secondary" onclick="closeSettings()">Cancel</button>
            <button class="btn-primary" onclick="saveSettings()">Save</button>
        </div>
    </div>
</div>

<script>
function setMode(mode) {
    document.getElementById('modeInput').value = mode;
    document.getElementById('accountField').style.display = mode === 'account' ? '' : 'none';
    document.getElementById('hashtagField').style.display = mode === 'hashtag' ? '' : 'none';
    document.getElementById('btnAccount').classList.toggle('active', mode === 'account');
    document.getElementById('btnHashtag').classList.toggle('active', mode === 'hashtag');
}

function showFilename(file) {
    document.getElementById('dropFilename').textContent = file ? file.name : '';
    const preview = document.getElementById('maskPreview');
    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
        preview.src = '';
    }
}

function onDragOver(e) {
    e.preventDefault();
    document.getElementById('dropZone').classList.add('dragover');
}

function onDragLeave() {
    document.getElementById('dropZone').classList.remove('dragover');
}

function onDrop(e) {
    e.preventDefault();
    document.getElementById('dropZone').classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) {
        const input = document.getElementById('maskInput');
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        showFilename(file);
    }
}

function setStatus(state, text) {
    const dot = document.getElementById('statusDot');
    dot.className = 'status-dot' + (state ? ' ' + state : '');
    document.getElementById('statusText').textContent = text;
}

function appendLog(text) {
    const el = document.getElementById('terminal');
    if (text.includes('\r')) {
        const parts = text.split('\r');
        const lines = el.innerHTML.split('\n');
        lines[lines.length - 1] = parts[parts.length - 1];
        el.innerHTML = lines.join('\n');
    } else {
        const div = document.createElement('div');
        div.textContent = text;
        if (text.toLowerCase().includes('error') || text.toLowerCase().includes('failed')) {
            div.className = 'line-error';
        } else if (text.toLowerCase().includes('saved') || text.toLowerCase().includes('success')) {
            div.className = 'line-success';
        }
        el.appendChild(div);
    }
    el.scrollTop = el.scrollHeight;
}

// Settings modal
async function openSettings() {
    const res = await fetch('/env');
    document.getElementById('envEditor').value = await res.text();
    document.getElementById('saveStatus').style.display = 'none';
    document.getElementById('modalBackdrop').classList.add('open');
}

function closeSettings() {
    document.getElementById('modalBackdrop').classList.remove('open');
}

function closeOnBackdrop(e) {
    if (e.target === document.getElementById('modalBackdrop')) closeSettings();
}

async function saveSettings() {
    const content = document.getElementById('envEditor').value;
    const res = await fetch('/env', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: content,
    });
    if (res.ok) {
        const status = document.getElementById('saveStatus');
        status.style.display = 'inline';
        setTimeout(() => { status.style.display = 'none'; }, 2000);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeSettings();
});

// Mask Creator
let creatorFile = null;

function onCreatorFile(file) {
    if (!file) return;
    creatorFile = file;
    document.getElementById('creatorFilename').textContent = file.name;
    document.getElementById('creatorSourcePreview').src = URL.createObjectURL(file);
    document.getElementById('maskCompare').style.display = 'none';
    document.getElementById('useMaskBtn').style.display = 'none';
    document.getElementById('downloadMaskBtn').style.display = 'none';
}

function onCreatorDragOver(e) {
    e.preventDefault();
    document.getElementById('creatorDropZone').classList.add('dragover');
}

function onCreatorDragLeave() {
    document.getElementById('creatorDropZone').classList.remove('dragover');
}

function onCreatorDrop(e) {
    e.preventDefault();
    document.getElementById('creatorDropZone').classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) {
        document.getElementById('creatorInput').files = (() => {
            const dt = new DataTransfer(); dt.items.add(file); return dt.files;
        })();
        onCreatorFile(file);
    }
}

async function createMask() {
    if (!creatorFile) { alert('Please select a source image first.'); return; }
    const fd = new FormData();
    fd.append('image', creatorFile);
    fd.append('method', document.getElementById('creatorMethod').value);
    fd.append('threshold', document.getElementById('thresholdSlider').value);

    const res = await fetch('/create-mask', { method: 'POST', body: fd });
    const data = await res.json();
    if (data.error) { alert('Error: ' + data.error); return; }

    const src = 'data:image/png;base64,' + data.mask;
    document.getElementById('creatorMaskPreview').src = src;
    document.getElementById('maskCompare').style.display = 'flex';

    const dlBtn = document.getElementById('downloadMaskBtn');
    dlBtn.href = src;
    dlBtn.style.display = 'inline-flex';

    document.getElementById('useMaskBtn').style.display = 'inline-flex';
}

async function useMask() {
    const src = document.getElementById('creatorMaskPreview').src;
    const blob = await fetch(src).then(r => r.blob());
    const file = new File([blob], 'mask.png', { type: 'image/png' });
    const dt = new DataTransfer();
    dt.items.add(file);
    document.getElementById('maskInput').files = dt.files;
    showFilename(file);
}

// Post to Mastodon
function updateCharCount() {
    const len     = document.getElementById('postText').value.length;
    const counter = document.getElementById('charCounter');
    counter.textContent = `${len} / 500`;
    counter.className   = 'char-counter' + (len > 500 ? ' over-limit' : len > 450 ? ' near-limit' : '');
}

async function postToMastodon() {
    const btn    = document.getElementById('postBtn');
    const status = document.getElementById('postStatus');
    const text   = document.getElementById('postText').value;

    btn.disabled    = true;
    btn.textContent = 'Posting…';
    status.style.display = 'none';

    try {
        const res = await fetch('/post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_b64: window._lastImageB64 || '',
                status:    text,
                alt_text:  window._lastAltText  || '',
            }),
        });
        const data = await res.json();
        if (data.ok) {
            status.textContent = '✓ Posted successfully!';
            status.className   = 'post-status success';
        } else {
            status.textContent = 'Error: ' + data.error;
            status.className   = 'post-status error';
        }
    } catch (err) {
        status.textContent = 'Error: ' + err.message;
        status.className   = 'post-status error';
    } finally {
        status.style.display = 'block';
        btn.disabled    = false;
        btn.textContent = '📤 Post to Mastodon';
    }
}

// Generate
document.getElementById('cloudForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn     = document.getElementById('generateBtn');
    const spinner = document.getElementById('spinner');
    const label   = document.getElementById('btnLabel');
    const terminal   = document.getElementById('terminal');
    const imagePanel = document.getElementById('imagePanel');

    btn.disabled = true;
    spinner.style.display = 'block';
    label.textContent = 'Generating…';
    terminal.innerHTML = '';
    imagePanel.style.display = 'none';
    document.getElementById('postPanel').style.display = 'none';
    document.getElementById('postStatus').style.display = 'none';
    setStatus('running', 'Generating…');

    try {
        const formData = new FormData(e.target);
        const response = await fetch('/generate', { method: 'POST', body: formData });

        if (!response.ok) {
            appendLog('HTTP error: ' + response.status);
            setStatus('error', 'Failed');
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;
                let msg;
                try { msg = JSON.parse(line); } catch { continue; }

                if (msg.type === 'log') {
                    appendLog(msg.text);
                } else if (msg.type === 'image') {
                    const src = 'data:image/png;base64,' + msg.data;
                    document.getElementById('resultImg').src = src;
                    document.getElementById('downloadBtn').href = src;
                    imagePanel.style.display = 'flex';
                    setStatus('done', 'Done!');
                    window._lastImageB64 = msg.data;
                    window._lastAltText  = msg.alt_text || '';
                    const autoPost = document.querySelector('select[name="auto_post"]').value;
                    if (autoPost === 'No') {
                        const mode     = document.getElementById('modeInput').value;
                        const hashtags = document.querySelector('input[name="hashtags"]').value.trim();
                        let defaultText;
                        if (mode === 'hashtag' && hashtags) {
                            const tags = hashtags.split(/\s+/).map(t => '#' + t.replace(/^#/, '')).join(' ');
                            defaultText = `Wordcloud for ${tags}\n#MastoCloud #WordCloud https://github.com/vwillcox/MastoCloud`;
                        } else {
                            defaultText = 'This is my latest #WordCloud from my Python Code over on #GitHub https://github.com/vwillcox/MastoCloud #MastoCloud';
                        }
                        document.getElementById('postText').value = defaultText;
                        updateCharCount();
                        document.getElementById('postPanel').style.display = 'flex';
                    }
                } else if (msg.type === 'error') {
                    appendLog('ERROR: ' + msg.text);
                    setStatus('error', 'Failed');
                }
            }
        }
    } catch (err) {
        appendLog('Error: ' + err.message);
        setStatus('error', 'Failed');
    } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
        label.textContent = '⚡ Generate Word Cloud';
    }
});
</script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML, colour_schemes=COLOUR_SCHEMES)


@app.route('/env', methods=['GET'])
def env_get():
    content = ENV_FILE.read_text() if ENV_FILE.exists() else ''
    return content, 200, {'Content-Type': 'text/plain'}


@app.route('/env', methods=['POST'])
def env_save():
    content = request.get_data(as_text=True)
    ENV_FILE.write_text(content)
    return '', 204


@app.route('/generate', methods=['POST'])
def generate():
    # Always reload from .env at generation time
    load_dotenv(ENV_FILE, override=True)

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    colour      = request.form.get('colour',      'default')
    transparent = request.form.get('transparent', 'no')
    auto_post   = request.form.get('auto_post',   'No')
    mode        = request.form.get('mode',        'account')

    output_fd, output_path = tempfile.mkstemp(suffix='.png')
    os.close(output_fd)

    mask_path = None
    mask_file = request.files.get('mask')
    if mask_file and mask_file.filename:
        mask_fd, mask_path = tempfile.mkstemp(suffix='.png')
        os.close(mask_fd)
        mask_file.save(mask_path)

    cmd = [
        sys.executable, '-m', 'mastocloud.main',
        '-o', output_path,
        '-t', transparent,
        '-p', auto_post,
        '-c', colour,
    ]

    if mode == 'account':
        account = request.form.get('account', '').strip()
        if not account:
            def _err():
                yield json.dumps({'type': 'error', 'text': 'Account handle is required'}) + '\n'
            return Response(_err(), mimetype='application/x-ndjson')
        cmd += ['-a', account]
    else:
        hashtags = request.form.get('hashtags', '').split()
        if not hashtags:
            def _err():
                yield json.dumps({'type': 'error', 'text': 'At least one hashtag is required'}) + '\n'
            return Response(_err(), mimetype='application/x-ndjson')
        cmd += ['-H'] + hashtags

    if mask_path:
        cmd += ['-m', mask_path]

    def run():
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(PROJECT_ROOT),
                env=env,
            )
            for line in process.stdout:
                yield json.dumps({'type': 'log', 'text': line.rstrip('\n')}) + '\n'
            process.wait()

            if process.returncode == 0 and Path(output_path).exists():
                with open(output_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                alt_text = ''
                alt_file = PROJECT_ROOT / 'alttext_for_mastocloud.txt'
                if alt_file.exists():
                    alt_text = alt_file.read_text()
                yield json.dumps({'type': 'image', 'data': img_data, 'alt_text': alt_text}) + '\n'
            else:
                yield json.dumps({'type': 'error', 'text': 'Generation failed — check the log above.'}) + '\n'
        finally:
            if Path(output_path).exists():
                Path(output_path).unlink()
            if mask_path and Path(mask_path).exists():
                Path(mask_path).unlink()

    return Response(stream_with_context(run()), mimetype='application/x-ndjson')


@app.route('/create-mask', methods=['POST'])
def create_mask():
    from PIL import Image
    import numpy as np

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    img_file = request.files['image']
    method    = request.form.get('method', 'auto')
    threshold = int(request.form.get('threshold', 128))

    img = Image.open(img_file)

    if method == 'auto':
        method = 'alpha' if img.mode == 'RGBA' else 'dark'

    if method == 'alpha':
        img = img.convert('RGBA')
        alpha = np.array(img.split()[3])
        mask_arr = np.where(alpha > threshold, 0, 255).astype(np.uint8)
    elif method == 'light':
        gray = np.array(img.convert('L'))
        mask_arr = np.where(gray > threshold, 0, 255).astype(np.uint8)
    else:  # dark shape on light background
        gray = np.array(img.convert('L'))
        mask_arr = np.where(gray < threshold, 0, 255).astype(np.uint8)

    mask_img = Image.fromarray(mask_arr, 'L')
    buf = io.BytesIO()
    mask_img.save(buf, format='PNG')
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode()

    return jsonify({'mask': img_data})


@app.route('/post', methods=['POST'])
def post_to_mastodon():
    import requests as req
    load_dotenv(ENV_FILE, override=True)

    data       = request.get_json()
    image_b64  = data.get('image_b64', '')
    status_text = data.get('status', '')
    alt_text   = data.get('alt_text', '')

    api_key    = os.getenv('MASTODON_API_KEY', '')
    server_url = os.getenv('MASTODON_SERVER_URL', '')

    if not api_key or not server_url:
        return jsonify({'ok': False, 'error': 'API key or server URL not configured — use Edit Config'})

    if not server_url.endswith('/'):
        server_url += '/'

    headers = {'Authorization': f'Bearer {api_key}'}

    img_bytes = base64.b64decode(image_b64)
    resp = req.post(
        f'{server_url}api/v2/media',
        headers=headers,
        files={'file': ('wordcloud.png', img_bytes, 'image/png')},
        data={'description': alt_text[:1500]},
    )
    if resp.status_code not in (200, 202):
        return jsonify({'ok': False, 'error': f'Image upload failed: HTTP {resp.status_code}'})

    media_id = resp.json()['id']

    resp = req.post(
        f'{server_url}api/v1/statuses',
        headers=headers,
        data={'status': status_text, 'media_ids[]': [media_id]},
    )
    if resp.status_code == 200:
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': f'Post failed: HTTP {resp.status_code}'})


if __name__ == '__main__':
    print('Starting MastoCloud Web Interface…')
    print('Opening http://localhost:5000')
    Timer(1.0, lambda: __import__('webbrowser').open('http://localhost:5000')).start()
    app.run(debug=False, port=5000, threaded=True)
