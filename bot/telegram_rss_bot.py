import requests
import feedparser
import schedule
import time
from time import gmtime, strftime
from dateutil.parser import parse
import logging
import tomllib
from dotenv import dotenv_values


# Basic configuration for logging events
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Functions

def load_configuration(configfile: str = "configuration.toml") -> dict:
    """
    Read a configuration file, TOML formatted.
    If Config file fails, defaults to ENV VARs
    Outputs a dict with the configuration.

    Example of a configuration.toml:
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

    """
    try:
        with open(configfile, "rb") as f:
            config = tomllib.load(f)
            logging.info("Configuration file found and loaded.")

    except Exception as e:
        logging.error(f"Configuration file error:  {str(e)}")

        # Look for ENV VARs
        logging.info("Switching on config from ENV VARS.")
        env_vars = dotenv_values(".env")
        config = {
            "TIME_INTERVAL_MIN": int(env_vars['TIME_INTERVAL_MIN']),
            "ENTRY_MAX_TIME_OLD": int(env_vars['ENTRY_MAX_TIME_OLD']),
            "BOT_TOKEN": env_vars['BOT_TOKEN'],
            "CHANNEL_ID": env_vars['CHANNEL_ID'],
            "RSS_URLS": env_vars['RSS_URLS'].split(),
        }
    return config


def send_message(bot_token: str,
                 channel_id: str,
                 message: str):
    """
    Update the Telegram bot, using a security token,
    a channel id and a message to post.
    """
    try:
        requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={channel_id}&text={message}')
        logging.info(f"Bot content updated with {message}.")
    except requests.exceptions as e:
        logging.exception(f"An exception occurred:  {str(e)}")

    return


# Parsing rss
def parse_rss(rss_feeds: list,
              entry_max_time_old: int):
    """
    Parse a list of RSS feeds, defined in a configuration file.
    Only keep the latest news (ENTRY_MAX_TIME_OLD).
    Update the telegram bot.
    """
    feeds = []
    currenttime = strftime("%Y-%m-%d %H:%M:%S", gmtime())   # get current time and format it with "strftime" method.
                                                            # The strftime() method returns a string representing date and time using date, time or datetime object.
    parsecurrenttime = parse(currenttime)

    for url in rss_feeds:
        feeds.append(feedparser.parse(url))
        logging.debug(url)

    for feed in feeds:
        for entry in feed.entries:
            publishedtime = strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)   # get published time from feedparser and format it with "strftime" method.
                                                                                    # The strftime() method returns a string representing date and time using date, time or datetime object.
            parsepublishedtime = parse(publishedtime)
            deltatime = parsecurrenttime - parsepublishedtime

            if (deltatime.total_seconds() < entry_max_time_old):
                logging.info(f"Added new entry: {entry.title} -> {entry.link}")

                # Update telegram bot
                message = entry.title + "   " + entry.link
                send_message(bot_token, channel_id, message)
    return

# ######################################################################################


# Load configuration
config = load_configuration()

# Get values from configuration
bot_token = config['BOT_TOKEN']
channel_id = config['CHANNEL_ID']
rss_urls = config['RSS_URLS']
entry_max_time_old = config['ENTRY_MAX_TIME_OLD']
time_interval_min = config['TIME_INTERVAL_MIN']


def main():

    # Schedule the task to run every n minutes
    schedule.every(time_interval_min).minutes.do(parse_rss,
                                                 rss_feeds=rss_urls,
                                                 entry_max_time_old=entry_max_time_old)
    logging.info(f"Scheduler set for a run every {time_interval_min} minutes.")

    # Run the scheduled tasks indefinitely
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
