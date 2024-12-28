import requests
import json
import time, argparse
import matplotlib.pyplot as py
from wordcloud import WordCloud,STOPWORDS
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--account", help="Handle to use", required=True)
parser.add_argument("-m", "--mask", help="Masking Image to use", required=True)
parser.add_argument("-o", "--output", help="Output File Name", required=True)
parser.add_argument("-k", "--key", help="API Access Token", required=True)
parser.add_argument("-t", "--transparent", help="Tansparent Image", required=True)
parser.add_argument("-p", "--post", help="Auto post?", required=True)
args = parser.parse_args()
config = vars(args)

accountname = args.account
accessToken = args.key
transparent = args.transparent
auto_post = args.post

api_url = 'https://fosstodon.org/'
headers = {'Authorization': f'Bearer {accessToken}'}
url_account = f'{api_url}api/v1/accounts/verify_credentials'

response_account = requests.get(url_account, headers=headers)

account_info = response_account.json()
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

statuses=get_statuses()

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
text = ' '.join(texts)

if transparent == "yes":
   twitter_mask= np.array(Image.open(maskingfilename)) #sitr.jpg image name
   wCloud= WordCloud(
   margin=2,
   background_color=None,
   mask=twitter_mask,
   mode="RGBA",
   stopwords=stopwords,
   min_font_size=1,
   max_font_size=20,
   relative_scaling=1,
   contour_width=1
   ).generate(text)
   wCloud.to_file(wordcloudfile)
else:
   twitter_mask= np.array(Image.open(maskingfilename)) #sitr.jpg image name
   wCloud= WordCloud(
   margin=1,
   mask=twitter_mask,
   contour_color='steelblue',
   stopwords=stopwords,
   contour_width=1
   ).generate(text)
   wCloud.to_file(wordcloudfile)

alt_pretext = 'This image Contains words i''ve used most offten in my toots. Including: ' 
wCloud_strings = ' '.join(wCloud.words_)
output_string = alt_pretext + wCloud_strings
output_string = limit_string_length(output_string)
#print(wCloud_strings)
filename = "alttext_for_mastocloud.txt"
with open(filename, "w") as file:
   file.write(output_string)


if auto_post == 'Yes':
   status_message = 'This is my latest #WordCloud from my Python Code over on #GitHub https://github.com/vwillcox/MastoCloud #MastoCloud #AutoPost'

   #Upload the image

   media_url = f'{api_url}/api/v2/media'
   headers = {'Authorization': f'Bearer {accessToken}'}
   files = {
       'file': open(wordcloudfile, 'rb')
   }
   data = {
       'description': output_string
   }
   print (wordcloudfile)
   response = requests.post(media_url, headers=headers, files=files, data=data)
   
   print(f'Upload response status code: {response.status_code}')
   print(f'Upload response content: {response.json()}')


   if response.status_code == 200:
       media_id = response.json()['id']
       print(f'Image uploaded successfully. Media ID: {media_id}')

    # Post the status with the uploaded image
       status_url = f'{api_url}/api/v1/statuses'
       print (status_url)
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
   
