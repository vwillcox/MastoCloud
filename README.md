# Wordcloud for Mastodon Accounts

This script will create an image Wordcloud based on your posts on any Mastodon Server that you have an account on.
You will require an API account for your Mastodon account.

## Setting up your Mastodon account

To get your API Key go to `https://<yourmastohost.com>/settings/applications`

For example if your account is on Hachyderm: `https://hachyderm.io/settings/applications`

NEVER give this key away as people can use it to impersonate you and post to your Mastodon account.

## Amending the code for your server

Open `mastocloud/main.py` and change the `api_url` on line 25 to match your Mastodon server:

```python
api_url = 'https://hachyderm.io/'
```

## Requirements and Setup

Clone the repo — that's it. The `run.sh` script handles creating the virtual environment and installing all dependencies automatically.

```bash
git clone https://github.com/vwillcox/MastoCloud.git
cd MastoCloud
```

## Running the code

Use the `run.sh` script with your options:

```bash
./run.sh -a talktech -m masto.svg.png -o cloud.png -k <YOURAPIKEY> -t yes -p No
```

On first run it will create a `.venv` folder and install dependencies. Subsequent runs skip straight to generating the wordcloud.

## Options

| Flag | Long form     | Meaning                       | Example           |
|------|---------------|-------------------------------|-------------------|
| `-a` | `--account`   | Mastodon account handle       | `talktech`        |
| `-m` | `--mask`      | Masking image                 | `masto.svg.png`   |
| `-o` | `--output`    | Output image filename         | `cloud.png`       |
| `-k` | `--key`       | API access token              | `your_token_here` |
| `-t` | `--transparent` | Transparent background      | `yes` / `no`      |
| `-p` | `--post`      | Auto-post image to Mastodon   | `Yes` / `No`      |
| `-c` | `--colour`    | Colour scheme (see below)     | `fire`            |

## Colour Schemes

Pass `-c <name>` to choose a colour scheme. Omitting `-c` uses `default`.

| Name        | Description                  |
|-------------|------------------------------|
| `default`   | wordcloud default colours    |
| `ocean`     | Blues and greens             |
| `fire`      | Reds, yellows and oranges    |
| `forest`    | Greens                       |
| `sunset`    | Red, yellow and blue         |
| `purple`    | Purples                      |
| `grayscale` | Grays                        |
| `rainbow`   | Full spectrum                |
| `plasma`    | Pink, purple and yellow      |
| `viridis`   | Blue, green and yellow       |

### Example with a colour scheme

```bash
./run.sh -a talktech -m masto.svg.png -o cloud.png -k <YOURAPIKEY> -t no -p No -c fire
```

### Auto-posting

Using `-p Yes` will upload the image to your Mastodon account and post it with a caption including alt text.

Using `-p No` will save the wordcloud image and alt text to disk and exit.

### Example

![Current Word Cloud](https://talktech.info/wp-content/uploads/2023/04/talktech.png)
