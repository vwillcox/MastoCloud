#!/usr/bin/env python3
"""
MastoCloud Web Interface
Run: python web.py
Then open http://localhost:5000 in your browser.
"""

import sys
import os
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
    grid-template-columns: 380px 1fr;
    gap: 1.5rem;
    padding: 1.5rem 2rem;
    flex: 1;
    max-width: 1400px;
    width: 100%;
    margin: 0 auto;
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
    margin-top: 1.25rem;
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

    <button type="submit" class="btn-generate" id="generateBtn">
        <div class="spinner" id="spinner"></div>
        <span id="btnLabel">⚡ Generate Word Cloud</span>
    </button>

</form>
</div>

<!-- ── Right: Output ──────────────────────────────────────── -->
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
</main>

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
                yield json.dumps({'type': 'image', 'data': img_data}) + '\n'
            else:
                yield json.dumps({'type': 'error', 'text': 'Generation failed — check the log above.'}) + '\n'
        finally:
            if Path(output_path).exists():
                Path(output_path).unlink()
            if mask_path and Path(mask_path).exists():
                Path(mask_path).unlink()

    return Response(stream_with_context(run()), mimetype='application/x-ndjson')


if __name__ == '__main__':
    print('Starting MastoCloud Web Interface…')
    print('Opening http://localhost:5000')
    Timer(1.0, lambda: __import__('webbrowser').open('http://localhost:5000')).start()
    app.run(debug=False, port=5000, threaded=True)
