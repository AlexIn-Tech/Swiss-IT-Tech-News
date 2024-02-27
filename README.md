# Swiss IT Tech News
Bot for telegram channel that 'll publish news based on RSS feed : 
https://t.me/SwissITNews

# How to use this bot :

1) Download or fork the content of this repository

2) Get a Raspberry Pi and install the needed libraries : 

```bash
virtualenv .venv -p python3
source .venv/bin/activate
pip install -r requirements.txt
```

3) Create your telegram channel , for example here is mine : 
https://t.me/SwissITNews

4) Create a bot by sending a message to "@BotFather" on Telegram : https://telegram.me/BotFather

![Bot Father](https://cdn1.telesco.pe/file/NZabVMBzG_0Rntl0ZsfxwQHwpbwdyznyiF-TLzQu7vdYlr8FcuQPbAxuhZRGYjkQUL-WkfdrmqDWiRsVaiM_CVC_Ugb6_2EYdPITtANtCTqXusUUTyXQzzGA9hYaZuahAwYm27-aaBgoh-zs3lXO3UfluRrQNeO0CiijcpNtEJI3ug1aVjyOICWdLsz4awsD92acA8VctWGyF7ZWRgQnpGdbfDkChucbh9BnPfTlxB8LeAVZmAV7YqF6eG910usqlImOPdRZGIJq2Ky42hc55ZbELry3t_bx4Rxbev8DQLM9iQhoKzmAjZ2m02DEgaCPKMIZ4X-hbOj2X87zgyTWmA.jpg)

5) Add your bot to your channel and setup permissions to send messages

6) Replace your bot token , channel ID and RSS feeds in the script 

```python
BOT_TOKEN = 'YOUR BOT TOKEN'
CHANNEL_ID = '@YourChannel'
RSS_URLS = [
    'https://korben.info/feed',
    'https://www.ictjournal.ch/taxonomy/term/404/feed',
    'https://www.ictjournal.ch/taxonomy/term/31/feed',
    'https://www.ictjournal.ch/taxonomy/term/406/feed',
    'https://www.newsd.admin.ch/newsd/feeds/rss?lang=fr&org-nr=1&offer-nr=308',
    'https://feeds.feedburner.com/TheHackersNews',
    'https://mspoweruser.com/feed/',
    'https://www.numerama.com/feed/',
    ]
```

7) The script will continuously run and execute an update at the time interval specified by `TIME_INTERVAL_MIN`.

# Configuration
This code supports a TOML formatted configuration file:
```toml
$ cat configuration.toml

# Configuration file for Telegram Bot

# General settings
TIME_INTERVAL_MIN = 1  # Run the feedparser every n minutes
ENTRY_MAX_TIME_OLD = 1200  # 1200 seconds = 20 min

# Bot Configuration
BOT_TOKEN = "YOUR BOT TOKEN"
CHANNEL_ID = "@YourChannel"

# News, RSS feeds
RSS_URLS = [
    "https://korben.info/feed",
    "https://www.ictjournal.ch/taxonomy/term/404/feed",
    "https://www.ictjournal.ch/taxonomy/term/31/feed",
    "https://www.ictjournal.ch/taxonomy/term/406/feed",
    "https://www.newsd.admin.ch/newsd/feeds/rss?lang=fr&org-nr=1&offer-nr=308",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://mspoweruser.com/feed/",
    "https://www.numerama.com/feed/",
    ]
```

If the configuration file fails (doesn't exist or incorrect synthax), it will default to `ENV VARs`. This last approach is highly recommended, to follow the [Twelve Factor App](https://12factor.net).

To ease the development work, you can rely on a .env file with:

```
# Development settings
TIME_INTERVAL_MIN=1
ENTRY_MAX_TIME_OLD=1200
BOT_TOKEN="YOUR BOT TOKEN"
CHANNEL_ID="@YourChannel"
RSS_URLS="https://korben.info/feed
https://www.ictjournal.ch/taxonomy/term/404/feed
https://www.ictjournal.ch/taxonomy/term/31/feed
https://www.ictjournal.ch/taxonomy/term/406/feed
https://www.newsd.admin.ch/newsd/feeds/rss?lang=fr&org-nr=1&offer-nr=308
https://feeds.feedburner.com/TheHackersNews
https://mspoweruser.com/feed/
https://www.numerama.com/feed/"
```

Env Variables can be set/intjected via Dockerfile or a Kubernetes manifest.
