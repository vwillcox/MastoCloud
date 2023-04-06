# Wordcloud for Mastodon Accounts

This script will create an image Wordcloud based on your posts on any Mastodon Server that you have an account on.
You will require an API account for your Mastodon account.

## Setting up your Mastodon account

To get your API Key you can go to https://<yourmastohost.com>/settings/applications

For example if your account is on the Fosstodon Servers you would go to https://fosstodon.org/settings/applications

NEVER give this key away as people can use it to impersonate you and post to your Mastodon account.

## Ammending the code

You will need to change lines 22 and 28 to your servers API URL

```
accounts = requests.get('https://fosstodon.org/
```

Would change to 

```
accounts = requests.get('https://mastodon.org/
```

For example

## Running the code

This is designed to be run from the BASH / Command shell with a simple command

```
python3 main.py -m masto.svg.png -o talktech040223-v5.png -a talktech -k <YOURAPIKEY> -t yes
```

### What are the options

| Command | Meaning                      |
|---------|----------------------------- |
| -m      | Masking image                |
| -o      | Output image                 |
| -a      | Mastodon Account             |
| -k      | API Key                      |
| -t      | Generate a transparent image |



