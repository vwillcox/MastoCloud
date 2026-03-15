# Wordcloud for Mastodon Accounts

This script creates a Wordcloud image based on your posts on any Mastodon server.

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/vwillcox/MastoCloud.git
cd MastoCloud
```

### 2. Get your API key

Go to `https://<your-mastodon-server>/settings/applications` and create an application to get your access token.

For example: `https://hachyderm.io/settings/applications`

> **Never share your API key** — it can be used to post to your account.

### 3. Run it

There are two ways to use MastoCloud — a **web interface** (recommended) or the **command line**.

---

## Web Interface

The web interface lets you generate word clouds from your browser with no command line needed.

### Starting the web server

```bash
./run.sh --web
```

This will:

- Create a Python virtual environment and install dependencies (first run only)
- Start the web server on `http://localhost:5000`
- Open your browser automatically

### Using the web interface

**Configure credentials (first time only)**

Click **⚙ Edit Config** in the top-right corner. This opens the `.env` file editor where you set:

```
MASTODON_API_KEY=your_access_token_here
MASTODON_SERVER_URL=https://hachyderm.io/
```

Click **Save** when done. Your credentials are stored locally and never sent anywhere other than your own Mastodon server.

**Generate a word cloud**

1. Choose **Account** or **Hashtags** as the source
2. Enter your account handle (e.g. `@you@instance.social`) or space-separated hashtags (e.g. `python linux infosec`)
3. Pick a colour scheme, transparent background option, and whether to auto-post
4. Optionally drag and drop a mask image to shape the word cloud
5. Click **⚡ Generate Word Cloud**

The log output streams in real time. When complete, the image appears on the right and can be downloaded with the **⬇ Download Image** button.

---

## Command Line

```bash
./run.sh -a yourhandle -m masto.svg.png -o cloud.png -t no -p No
```

The first time you run it:

- A Python virtual environment is created and dependencies are installed
- You will be prompted for your **Mastodon server URL** (e.g. `https://hachyderm.io/`)
- You will be prompted for your **API access token**
- Both are saved to a local `.env` file automatically

On every subsequent run both values are read from `.env` silently — no need to enter them again.

---

## All Options

`-a` and `-H` are mutually exclusive — use one or the other.

| Flag | Long form       | Meaning                                        | Example                    |
|------|-----------------|------------------------------------------------|----------------------------|
| `-a` | `--account`     | Generate from a user account handle            | `talktech`                 |
| `-H` | `--hashtags`    | Generate from one or more hashtags             | `infosec security python`  |
| `-m` | `--mask`        | Masking image for the shape (optional)         | `masto.svg.png`            |
| `-o` | `--output`      | Output image filename                          | `cloud.png`                |
| `-t` | `--transparent` | Transparent background                         | `yes` / `no`               |
| `-p` | `--post`        | Auto-post to Mastodon                          | `Yes` / `No`               |
| `-c` | `--colour`      | Colour scheme                                  | `fire`                     |

---

## Colour Schemes

Pass `-c <name>` to pick a colour scheme. Omitting `-c` uses `default`.

| Name        | Description               |
|-------------|---------------------------|
| `default`   | Wordcloud default colours |
| `ocean`     | Blues and greens          |
| `fire`      | Reds, yellows and oranges |
| `forest`    | Greens                    |
| `sunset`    | Red, yellow and blue      |
| `purple`    | Purples                   |
| `grayscale` | Grays                     |
| `rainbow`   | Full spectrum             |
| `plasma`    | Pink, purple and yellow   |
| `viridis`   | Blue, green and yellow    |

---

## Examples

Generate from your own account:

```bash
./run.sh -a talktech -m masto.svg.png -o cloud.png -t yes -p No -c fire
```

Generate from one or more hashtags:

```bash
./run.sh -H infosec security -m masto.svg.png -o cloud.png -t no -p No -c plasma
```

Generate from hashtags and auto-post the result:

```bash
./run.sh -H python linux -m masto.svg.png -o cloud.png -t no -p Yes -c ocean
```

---

## Auto-posting

When `-p Yes` is set, the script will:

1. Upload the generated image to your Mastodon account
2. Post a status with the image attached
3. Include auto-generated alt text describing the most common words

When `-p No` is set, the image and alt text are saved locally and the script exits.

---

## Output Files

| File                          | Contents                              |
|-------------------------------|---------------------------------------|
| `<output>.png`                | The generated wordcloud image         |
| `alttext_for_mastocloud.txt`  | Alt text description for the image    |

---

## Example Output

![Current Word Cloud](https://talktech.info/wp-content/uploads/2023/04/talktech.png)
