import requests
import json
import re
import time, argparse
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import matplotlib.pyplot as py
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import numpy as np
from dotenv import load_dotenv, set_key
from tqdm import tqdm

ENV_FILE = Path(__file__).parent.parent / '.env'

def _load_env():
    load_dotenv(ENV_FILE)

def _prompt_and_save(env_var, prompt_text):
    value = input(prompt_text).strip()
    if not value:
        print(f"Error: {env_var} cannot be empty.")
        raise SystemExit(1)
    ENV_FILE.touch(mode=0o600)
    set_key(str(ENV_FILE), env_var, value)
    print(f"{env_var} saved to {ENV_FILE}")
    return value

def get_api_key():
    _load_env()
    key = os.getenv('MASTODON_API_KEY')
    if not key:
        print("No API key found.")
        key = _prompt_and_save('MASTODON_API_KEY', "Enter your Mastodon API access token: ")
    return key

def get_server_url():
    _load_env()
    url = os.getenv('MASTODON_SERVER_URL')
    if not url:
        print("No Mastodon server URL found.")
        url = _prompt_and_save('MASTODON_SERVER_URL', "Enter your Mastodon server URL (e.g. https://hachyderm.io/): ")
    if not url.endswith('/'):
        url += '/'
    return url

COLOUR_SCHEMES = {
    'default':    {'colormap': None,             'contour_color': 'steelblue'},
    'ocean':      {'colormap': 'ocean',          'contour_color': 'navy'},
    'fire':       {'colormap': 'hot',            'contour_color': 'darkred'},
    'forest':     {'colormap': 'Greens',         'contour_color': 'darkgreen'},
    'sunset':     {'colormap': 'RdYlBu_r',       'contour_color': 'orangered'},
    'purple':     {'colormap': 'Purples',        'contour_color': 'indigo'},
    'grayscale':  {'colormap': 'gray',           'contour_color': 'dimgray'},
    'rainbow':    {'colormap': 'hsv',            'contour_color': 'black'},
    'plasma':     {'colormap': 'plasma',         'contour_color': 'purple'},
    'viridis':    {'colormap': 'viridis',        'contour_color': 'teal'},
}

def main():
    parser = argparse.ArgumentParser(description="Generate a wordcloud from Mastodon posts")

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-a", "--account", help="Generate from a user account handle")
    mode_group.add_argument("-H", "--hashtags", nargs='+', metavar="TAG",
                            help="Generate from one or more hashtags (e.g. -H infosec security python)")

    parser.add_argument("-m", "--mask", help="Masking image to use (omit for rectangular cloud)", default=None)
    parser.add_argument("-o", "--output", help="Output file name", required=True)
    parser.add_argument("-t", "--transparent", help="Transparent background (yes/no)", required=True)
    parser.add_argument("-p", "--post", help="Auto-post to Mastodon (Yes/No)", required=True)
    parser.add_argument(
        "-c", "--colour",
        help=f"Colour scheme. Choices: {', '.join(COLOUR_SCHEMES)}",
        choices=COLOUR_SCHEMES.keys(),
        default='default',
    )
    args = parser.parse_args()

    accessToken = get_api_key()
    transparent = args.transparent
    auto_post = args.post
    scheme = COLOUR_SCHEMES[args.colour]

    api_url = get_server_url()
    headers = {'Authorization': f'Bearer {accessToken}'}

    def limit_string_length(input_string, limit=1500):
        return input_string[:limit]

    def get_account_statuses():
        url_account = f'{api_url}api/v1/accounts/verify_credentials'
        response_account = requests.get(url_account, headers=headers)

        if response_account.status_code != 200:
            print(f"Error authenticating: HTTP {response_account.status_code}")
            print(f"Response: {response_account.json()}")
            raise SystemExit(1)

        account_info = response_account.json()
        if 'id' not in account_info:
            print(f"Unexpected response: {account_info}")
            raise SystemExit(1)

        account_id = account_info['id']
        url_statuses = f'{api_url}api/v1/accounts/{account_id}/statuses'
        params = {'limit': 40}
        statuses = []

        with tqdm(desc=f"Fetching posts for @{args.account}", unit=" posts", dynamic_ncols=True) as pbar:
            while True:
                response = requests.get(url_statuses, headers=headers, params=params)
                response_data = response.json()
                if not response_data:
                    break
                statuses.extend(response_data)
                pbar.update(len(response_data))
                params['max_id'] = int(response_data[-1]['id']) - 1

        return statuses

    def get_hashtag_statuses(hashtags):
        statuses = []
        one_week_ago = datetime.now(timezone.utc) - timedelta(weeks=1)
        for tag in hashtags:
            tag = tag.lstrip('#')
            url = f'{api_url}api/v1/timelines/tag/{tag}'
            params = {'limit': 40}

            with tqdm(desc=f"Fetching #{tag}", unit=" posts", dynamic_ncols=True) as pbar:
                while True:
                    response = requests.get(url, headers=headers, params=params)
                    if response.status_code != 200:
                        print(f"Error fetching #{tag}: HTTP {response.status_code}")
                        break
                    response_data = response.json()
                    if not response_data:
                        break
                    excluded_tags = {'mastocloud', 'wordcloud'}
                    fresh = [s for s in response_data
                             if datetime.fromisoformat(s['created_at']) >= one_week_ago
                             and not excluded_tags.intersection(
                                 t['name'].lower() for t in s.get('tags', [])
                             )]
                    statuses.extend(fresh)
                    pbar.update(len(fresh))
                    if len(fresh) < len(response_data):
                        break
                    params['max_id'] = int(response_data[-1]['id']) - 1

        return statuses

    if args.hashtags:
        statuses = get_hashtag_statuses(args.hashtags)
        alt_pretext = f"Wordcloud of posts tagged {', '.join('#' + t.lstrip('#') for t in args.hashtags)}. Top words: "
    else:
        statuses = get_account_statuses()
        alt_pretext = "This image contains words used most often in my toots. Including: "

    if not statuses:
        print("No posts found. Exiting.")
        raise SystemExit(1)

    print(f"Total posts fetched: {len(statuses)}")

    def looks_random(word):
        """Return True if a word looks like a random/gibberish string."""
        if len(word) < 6:
            return False
        # Contains digits mixed with letters
        if re.search(r'[a-zA-Z]', word) and re.search(r'\d', word):
            return True
        # Three or more uppercase letters not at the start (e.g. IICedCFTbG)
        if sum(1 for c in word[1:] if c.isupper()) >= 3:
            return True
        # Very low vowel ratio for longer words (< 20% vowels)
        vowels = sum(1 for c in word.lower() if c in 'aeiou')
        if len(word) >= 8 and vowels / len(word) < 0.2:
            return True
        return False

    texts = [status['content'] for status in statuses]
    text = ' '.join(texts)
    text = ' '.join(w for w in text.split() if not looks_random(w))

    wordcloudfile = args.output

    stopwords = set(STOPWORDS)
    stopwords_file = Path(__file__).parent / 'stopwords.txt'
    with open(stopwords_file) as f:
        for line in f:
            word = line.split('#')[0].strip()
            if word:
                stopwords.add(word)

    if args.hashtags:
        for tag in args.hashtags:
            stopwords.add(tag.lstrip('#').lower())

    twitter_mask = np.array(Image.open(args.mask)) if args.mask else None

    if transparent == "yes":
        wCloud = WordCloud(
            width=3840,
            height=2160,
            margin=2,
            background_color=None,
            mask=twitter_mask,
            mode="RGBA",
            stopwords=stopwords,
            min_font_size=1,
            max_font_size=20,
            relative_scaling=1,
            colormap=scheme['colormap'],
        ).generate(text)
    else:
        if twitter_mask is not None:
            wCloud = WordCloud(
                width=3840,
                height=2160,
                margin=1,
                mask=twitter_mask,
                contour_color=scheme['contour_color'],
                contour_width=1,
                stopwords=stopwords,
                colormap=scheme['colormap'],
            ).generate(text)
        else:
            wCloud = WordCloud(
                width=3840,
                height=2160,
                margin=10,
                stopwords=stopwords,
                colormap=scheme['colormap'],
            ).generate(text)

    wCloud.to_file(wordcloudfile)
    print(f"Wordcloud saved to {wordcloudfile}")

    wCloud_strings = ' '.join(wCloud.words_)
    output_string = limit_string_length(alt_pretext + wCloud_strings)
    filename = "alttext_for_mastocloud.txt"
    with open(filename, "w") as file:
        file.write(output_string)

    def top_contributors(statuses, top_words, max_users=5):
        """Return handles of users whose posts contained the most top words."""
        strip_tags = re.compile(r'<[^>]+>')
        scores = {}
        word_set = set(w.lower() for w in top_words)
        for status in statuses:
            acct = status['account']['acct']
            plain = strip_tags.sub(' ', status['content']).lower()
            words_in_post = set(plain.split())
            score = len(word_set & words_in_post)
            if score:
                scores[acct] = scores.get(acct, 0) + score
        ranked = sorted(scores, key=scores.get, reverse=True)
        return ranked[:max_users]

    if auto_post == 'Yes':
        if args.hashtags:
            tags_str = ' '.join('#' + t.lstrip('#') for t in args.hashtags)
            top_users = top_contributors(statuses, list(wCloud.words_.keys())[:20])
            mentions = ' '.join(f'@{u}' for u in top_users)
            status_message = f"Wordcloud for {tags_str} — top contributors: {mentions}\n#MastoCloud #WordCloud https://github.com/vwillcox/MastoCloud #AutoPost\n{tags_str}"
        else:
            status_message = 'This is my latest #WordCloud from my Python Code over on #GitHub https://github.com/vwillcox/MastoCloud #MastoCloud #AutoPost'

        media_url = f'{api_url}api/v2/media'
        files = {'file': open(wordcloudfile, 'rb')}
        data = {'description': output_string}

        response = requests.post(media_url, headers=headers, files=files, data=data)
        print(f'Upload response status code: {response.status_code}')

        if response.status_code == 200:
            media_id = response.json()['id']
            print(f'Image uploaded successfully. Media ID: {media_id}')

            status_url = f'{api_url}api/v1/statuses'
            data = {
                'status': status_message,
                'media_ids[]': [media_id]
            }
            response = requests.post(status_url, headers=headers, data=data)
            print(f'Status post response status code: {response.status_code}')
            if response.status_code == 200:
                print('Status posted successfully!')
            else:
                print(f'Error posting status: {response.status_code}')
        else:
            print(f'Error uploading image: {response.status_code}')

if __name__ == "__main__":
    main()
