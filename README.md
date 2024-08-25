# Wordcloud for Mastodon Accounts

This script will create an image Wordcloud based on your posts on any Mastodon Server that you have an account on.
You will require an API account for your Mastodon account.

### Updated 25/08/2024 

To work with VENV on the latest Python3 I have added extra instructions below.
New Autopost switch - post the generated wordcloud straight to your Mastodon status!

## Setting up your Mastodon account

To get your API Key you can go to https://<yourmastohost.com>/settings/applications

For example if your account is on the Fosstodon Servers you would go to https://fosstodon.org/settings/applications

NEVER give this key away as people can use it to impersonate you and post to your Mastodon account.

## Ammending the code

You will need to change lines 21 to your servers API URL

```
api_url = 'https://fosstodon.org/'
```

Would change to 

```
api_url = 'https://mastodon.social/'
```

## Requirements and Setup

You need a couple of Python packages and if using a distro like Rasperry Pi Light you may also need to install the PIP tool

```
git clone https://github.com/vwillcox/MastoCloud.git
cd MastoCloud
python -m venv venv
source venv/bin/activate
sudo apt install python3-pip
pip3 install matplotlib
pip3 install wordcloud
pip3 install requests
```

## Running the code

This is designed to be run from the BASH / Command shell with a simple command

```
python3 main.py -m masto.svg.png -o talktech040223-v5.png -a talktech -k <YOURAPIKEY> -t yes -p yes
```

Using -p yes will post the image and add a caption to the post to help others view your post!

Using -p no will just save the Wordcloud and description to the drive and finish!

### What are the options

| Command | Meaning                      | Example             |
|---------|------------------------------|---------------------|
| -m      | Masking image                | masto.svg.png       |
| -o      | Output image                 | cloud.png           |
| -a      | Mastodon Account             | elonmusk            |
| -k      | API Key                      | Your access token   |
| -t      | Generate a transparent image | yes                 |
| -p      | Post the image to Mastadon   | yes                 |

### Example

![Current Word Cloud](https://talktech.info/wp-content/uploads/2023/04/talktech.png)
