import requests
import json
import time, argparse
import os
from pathlib import Path
import matplotlib.pyplot as py
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import numpy as np
from dotenv import load_dotenv, set_key

ENV_FILE = Path(__file__).parent.parent / '.env'

def get_api_key():
    load_dotenv(ENV_FILE)
    key = os.getenv('MASTODON_API_KEY')
    if not key:
        print("No API key found.")
        key = input("Enter your Mastodon API access token: ").strip()
        if not key:
            print("Error: API key cannot be empty.")
            raise SystemExit(1)
        ENV_FILE.touch(mode=0o600)
        set_key(str(ENV_FILE), 'MASTODON_API_KEY', key)
        print(f"API key saved to {ENV_FILE}")
    return key

COLOUR_SCHEMES = {
    'default':    {'colormap': None,   'contour_color': 'steelblue'},
    'ocean':      {'colormap': 'ocean',          'contour_color': 'navy'},
    'fire':       {'colormap': 'hot',            'contour_color': 'darkred'},
    'forest':     {'colormap': 'Greens',         'contour_color': 'darkgreen'},
    'sunset':     {'colormap': 'RdYlBu_r',       'contour_color': 'orangered'},
    'purple':     {'colormap': 'Purples',         'contour_color': 'indigo'},
    'grayscale':  {'colormap': 'gray',           'contour_color': 'dimgray'},
    'rainbow':    {'colormap': 'hsv',            'contour_color': 'black'},
    'plasma':     {'colormap': 'plasma',         'contour_color': 'purple'},
    'viridis':    {'colormap': 'viridis',        'contour_color': 'teal'},
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--account", help="Handle to use", required=True)
    parser.add_argument("-m", "--mask", help="Masking Image to use", required=True)
    parser.add_argument("-o", "--output", help="Output File Name", required=True)
    parser.add_argument("-t", "--transparent", help="Transparent Image", required=True)
    parser.add_argument("-p", "--post", help="Auto post?", required=True)
    parser.add_argument(
        "-c", "--colour",
        help=f"Colour scheme. Choices: {', '.join(COLOUR_SCHEMES)}",
        choices=COLOUR_SCHEMES.keys(),
        default='default',
    )
    args = parser.parse_args()
    config = vars(args)

    accountname = args.account
    accessToken = get_api_key()
    transparent = args.transparent
    auto_post = args.post
    scheme = COLOUR_SCHEMES[args.colour]

    api_url = 'https://hachyderm.io/'
    headers = {'Authorization': f'Bearer {accessToken}'}
    url_account = f'{api_url}api/v1/accounts/verify_credentials'

    response_account = requests.get(url_account, headers=headers)

    if response_account.status_code != 200:
        print(f"Error authenticating: HTTP {response_account.status_code}")
        print(f"Response: {response_account.json()}")
        return

    account_info = response_account.json()
    if 'id' not in account_info:
        print(f"Unexpected response: {account_info}")
        return
    account_id = account_info['id']

    def limit_string_length(input_string, limit=1500):
        return input_string[:limit]

    def get_statuses():
        url_statuses = f'{api_url}api/v1/accounts/{account_id}/statuses'
        params = {
            'limit': 1000
        }

        statuses = []

        while True:
            response = requests.get(url_statuses, headers=headers, params=params)
            response_data = response.json()
            if not response_data:
                break
            statuses.extend(response_data)
            params['max_id'] = int(response_data[-1]['id']) - 1
        return statuses

    statuses = get_statuses()

    texts = [status['content'] for status in statuses]

    maskingfilename = args.mask
    wordcloudfile = args.output

    stopwords = set(STOPWORDS)
    stopwords.add('https')
    stopwords.add('t')
    stopwords.add('co')
    stopwords.add('https://t.co')
    stopwords.add('span')
    stopwords.add('href')
    stopwords.add('class')
    stopwords.add('mention')
    stopwords.add('hashtag')
    stopwords.add('url')
    stopwords.add('rel')
    stopwords.add('tag')
    stopwords.add('tags')
    stopwords.add('fosstodon.org')
    stopwords.add('fosstodon')
    stopwords.add('org')
    stopwords.add('mstdn')
    stopwords.add('p')
    stopwords.add('u')
    stopwords.add('h')
    stopwords.add('card')
    stopwords.add('ca')
    stopwords.add('br')
    stopwords.add('sbb')
    stopwords.add('joinin')
    stopwords.add('_blank')
    stopwords.add('noopener')
    stopwords.add('ac2c7')
    stopwords.add('ac2c7b8aad917bd297f1bdcaddc066f2')
    stopwords.add('n8aad917bd297f1bdcaddc066f2')
    stopwords.add('b8aad917bd297f1bdcaddc066f2')
    stopwords.add('nofollow')
    stopwords.add('noreferrer')
    stopwords.add('target')
    stopwords.add('translate')
    stopwords.add('hachyderm')
    stopwords.add('io')
    text = ' '.join(texts)

    twitter_mask = np.array(Image.open(maskingfilename))

    if transparent == "yes":
        wCloud = WordCloud(
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
        wCloud = WordCloud(
            margin=1,
            mask=twitter_mask,
            contour_color=scheme['contour_color'],
            contour_width=1,
            stopwords=stopwords,
            colormap=scheme['colormap'],
        ).generate(text)

    wCloud.to_file(wordcloudfile)

    alt_pretext = 'This image Contains words i''ve used most offten in my toots. Including: '
    wCloud_strings = ' '.join(wCloud.words_)
    output_string = alt_pretext + wCloud_strings
    output_string = limit_string_length(output_string)
    # print(wCloud_strings)
    filename = "alttext_for_mastocloud.txt"
    with open(filename, "w") as file:
        file.write(output_string)

    if auto_post == 'Yes':
        status_message = 'This is my latest #WordCloud from my Python Code over on #GitHub https://github.com/vwillcox/MastoCloud #MastoCloud #AutoPost'

        # Upload the image

        media_url = f'{api_url}/api/v2/media'
        headers = {'Authorization': f'Bearer {accessToken}'}
        files = {
            'file': open(wordcloudfile, 'rb')
        }
        data = {
            'description': output_string
        }
        print(wordcloudfile)
        response = requests.post(media_url, headers=headers, files=files, data=data)

        print(f'Upload response status code: {response.status_code}')
        print(f'Upload response content: {response.json()}')

        if response.status_code == 200:
            media_id = response.json()['id']
            print(f'Image uploaded successfully. Media ID: {media_id}')

            # Post the status with the uploaded image
            status_url = f'{api_url}/api/v1/statuses'
            print(status_url)
            data = {
                'status': status_message,
                'media_ids[]': [media_id]
            }
            response = requests.post(status_url, headers=headers, data=data)

            print(f'Status post response status code: {response.status_code}')
            print(f'Status post response content: {response.json()}')
            if response.status_code == 200:
                print('Status posted successfully!')
            else:
                print(f'Error posting status: {response.status_code}')
        else:
            print(f'Error uploading image: {response.status_code}')

if __name__ == "__main__":
    main()
