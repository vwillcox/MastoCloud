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
args = parser.parse_args()
config = vars(args)

accountname = args.account
accessToken = args.key
transparent = args.transparent
api_url = 'https://fosstodon.org/'

accounts = requests.get(api_url+'api/v2/search?q='+accountname+'&resolve=true&limit=1', headers={'Authorization': 'Bearer '+accessToken})
statuses = json.loads(accounts.text)

accountID = (statuses['accounts'][0]['id'])


response = requests.get(api_url+'api/v1/accounts/'+accountID+'/statuses', headers={'Authorization': 'Bearer '+accessToken})
statuses = json.loads(response.text)

maskingfilename = args.mask
wordcloudfile = args.output


tempwordfile="file.txt"
f=open (tempwordfile, "w+")
for status in statuses:
  f.write(str(status["content"]))
f.write("\n")
f.close

f = open(tempwordfile,"r")
words=f.read()
f.close()

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

if transparent == "yes":
   twitter_mask= np.array(Image.open(maskingfilename)) #sitr.jpg image name
   wCloud= WordCloud(
   margin=5,
   background_color=None,
   mask=twitter_mask,
   mode="RGBA",
   stopwords=stopwords
   ).generate(words)
   wCloud.to_file(wordcloudfile)
   


else:
   twitter_mask= np.array(Image.open(maskingfilename)) #sitr.jpg image name
   wCloud= WordCloud(
   margin=5,
   #background_color=None,
   #mode="RGBA",
   mask=twitter_mask,
   contour_width=2,
   contour_color='steelblue',
   stopwords=stopwords
   ).generate(words)
   wCloud.to_file(wordcloudfile)

alt_pretext = 'This image Contains words i''ve used most offten in my toots. Including: ' 
wCloud_strings = ' '.join(wCloud.words_)
output_string = alt_pretext + wCloud_strings
#print(wCloud_strings)
filename = "alttext_for_mastocloud.txt"
with open(filename, "w") as file:
   file.write(output_string)


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
