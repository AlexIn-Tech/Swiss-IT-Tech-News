# A cronjob run it each 20'' on a Raspberry Pi.

# needed library : 
# requests , to make requets for eg. to an API 
# pip3 install requests
# feedparser to get an rss feed and parse/format it 
# pip3 install feedparser
# pip3 install python-dateutil

import requests
import feedparser
import time
import sys
from time import gmtime, strftime
from dateutil.parser import parse


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
ENTRY_MAX_TIME_OLD = 1200 #1200 seconds = 20 min


def send_message(message):
 requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={message}')
#send_message('it works!')


#parsing rss
def main():
    #rss_feed = feedparser.parse(RSS_URLS)
    currenttime = strftime("%Y-%m-%d %H:%M:%S", gmtime())   # get current time and format it with "strftime" method. 
                                                            # # The strftime() method returns a string representing date and time using date, time or datetime object.
    parsecurrenttime = parse(currenttime)
    # print(parsecurrenttime)
    # print(type(parsecurrenttime))

    for url in RSS_URLS:
        feeds.append(feedparser.parse(url))

    for feed in feeds:
        for entry in feed.entries:
            publishedtime = strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)   # get published time from feedparser and format it with "strftime" method.
                                                                                    # The strftime() method returns a string representing date and time using date, time or datetime object.
            parsepublishedtime = parse(publishedtime)
            deltatime = parsecurrenttime - parsepublishedtime
            # delta_in_seconds = deltatime.total_seconds()
            # print("delta in seconds : ")
            # print(delta_in_seconds)
            
            if (deltatime.total_seconds() < ENTRY_MAX_TIME_OLD):
                # print(parsepublishedtime)
                # print(type(parsepublishedtime))
                # print("Deltatime.seconds : " + str(deltatime.seconds))
                # print("Deltatime.total_seconds() : " + str(deltatime.total_seconds()))
                print("entry title: " + entry.title)
                print("entry link: " + entry.link)
                send_message(entry.title + "   " + entry.link)

    sys.exit()

main()