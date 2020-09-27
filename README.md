# Swiss-IT-Tech-News
Bot for telegram channel that 'll publish news based on RSS feed
https://t.me/SwissITNews

# How to use this bot :

1) Download or fork the content of this repository

2) Get a Raspberry Pi and install the needed libraries : 

```python
pip3 install requests
```

```python
pip3 install feedparser
```

```
pip3 install python-dateutil
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
feeds = []
```

7) Setup a cronjob on your Raspberry Pi to run this script each 20'' minutes 