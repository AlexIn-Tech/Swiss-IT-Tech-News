import logging
import os
import time
from time import gmtime, strftime
from datetime import datetime, timezone
from calendar import timegm

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import feedparser
import schedule
from dateutil.parser import parse
from dotenv import load_dotenv
import tomllib

# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,  # set to DEBUG for detailed output
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ---------------------------------------------------------------------
# HTTP session with retries, timeouts, and user-agent
# ---------------------------------------------------------------------
def build_session() -> requests.Session:
    """Create a requests session with retry and backoff strategy."""
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.headers.update({
        "User-Agent": "TelegramRSSBot/1.0"
    })
    return s

session = build_session()

# ---------------------------------------------------------------------
# Configuration loader (TOML or ENV)
# ---------------------------------------------------------------------
def load_configuration(configfile: str = "configuration.toml") -> dict:
    """
    Read a configuration file, TOML formatted.
    If Config file fails, defaults to ENV VARs
    Outputs a dict with the configuration.

    Example of a configuration.toml:
    # Configuration file for Telegram Bot

    # General settings
    TIME_INTERVAL_MIN = 20  # Run the feedparser every n minutes
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

    config = {}
    try:
        with open(configfile, "rb") as f:
            config = tomllib.load(f)
            logging.info("Configuration file found and loaded.")
    except Exception as e:
        logging.error(f"Configuration file error: {e}")
        logging.info("Falling back to environment variables.")
        load_dotenv()
        try:
            config = {
                "TIME_INTERVAL_MIN": int(os.getenv("TIME_INTERVAL_MIN", "20")),
                "ENTRY_MAX_TIME_OLD": int(os.getenv("ENTRY_MAX_TIME_OLD", "1200")),
                "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
                "CHANNEL_ID": os.getenv("CHANNEL_ID", ""),
                "RSS_URLS": [u.strip() for u in os.getenv("RSS_URLS", "").split(",") if u.strip()],
            }
        except Exception as env_e:
            logging.exception(f"Environment variable parsing error: {env_e}")
            config = {}

    if not config:
        logging.error("No configuration found. Provide a TOML file or ENV variables.")
        raise SystemExit(1)

    # Validate critical fields
    if not config.get("BOT_TOKEN") or not config.get("CHANNEL_ID"):
        logging.error("BOT_TOKEN or CHANNEL_ID missing.")
        raise SystemExit(1)
    if not config.get("RSS_URLS"):
        logging.error("RSS_URLS list is empty.")
        raise SystemExit(1)

    logging.debug(config)
    return config

# ---------------------------------------------------------------------
# Cache logic to avoid duplicate messages
# ---------------------------------------------------------------------
cache = {}
cache_flush_interval_days = 7  # reset every 7 days

def clear_cache():
    """Clear the cache that prevents duplicate posts."""
    global cache
    cache = {}
    logging.info("Cache cleared.")

# ---------------------------------------------------------------------
# Telegram message sender
# ---------------------------------------------------------------------
def send_message(bot_token: str, channel_id: str, message: str):
    """Send a message to a Telegram channel."""
    try:
        r = session.get(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            params={"chat_id": channel_id, "text": message},
            timeout=10,
        )
        if r.status_code != 200:
            logging.warning(f"Telegram returned {r.status_code}: {r.text[:200]}")
        else:
            logging.info("Message sent to Telegram successfully.")
    except requests.RequestException as e:
        logging.exception(f"Telegram send error: {e}")

# ---------------------------------------------------------------------
# Utility to parse RSS entry publish time
# ---------------------------------------------------------------------
def entry_datetime_utc(entry) -> datetime | None:
    """Extract and return the UTC datetime of a feed entry."""
    st = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not st:
        return None
    return datetime.fromtimestamp(timegm(st), tz=timezone.utc)

# ---------------------------------------------------------------------
# RSS parsing and posting logic
# ---------------------------------------------------------------------
def parse_rss(rss_feeds: list, entry_max_time_old: int, bot_token: str, channel_id: str):
    """Fetch and parse multiple RSS feeds safely, posting only new entries."""
    current_utc = datetime.now(timezone.utc)

    for url in rss_feeds:
        try:
            logging.debug(f"Fetching feed: {url}")
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except requests.RequestException as e:
            logging.warning(f"Feed fetch failed for {url}: {e}")
            continue
        except Exception as e:
            logging.exception(f"Unexpected error while fetching {url}: {e}")
            continue

        if not getattr(feed, "entries", []):
            logging.warning(f"No entries found for feed: {url}")
            continue

        for entry in feed.entries:
            try:
                published_dt = entry_datetime_utc(entry)
                if not published_dt:
                    logging.debug(f"Skipping entry with no publish date: {getattr(entry, 'title', 'no title')}")
                    continue

                delta_sec = (current_utc - published_dt).total_seconds()
                if delta_sec >= entry_max_time_old:
                    # Too old, skip
                    continue

                link = getattr(entry, "link", None)
                title = getattr(entry, "title", "(no title)")
                if not link:
                    logging.debug(f"Skipping entry with no link: {title}")
                    continue

                if link in cache:
                    logging.debug(f"Duplicate entry skipped: {title} -> {link}")
                    continue

                # Send message to Telegram
                message = f"{title}   {link}"
                send_message(bot_token, channel_id, message)
                cache[link] = current_utc

            except Exception as e:
                logging.exception(f"Error while processing entry from {url}: {e}")
                continue

    logging.debug("All feeds checked.")

# ---------------------------------------------------------------------
# Main scheduler
# ---------------------------------------------------------------------
def main():
    config = load_configuration()
    bot_token = config["BOT_TOKEN"]
    channel_id = config["CHANNEL_ID"]
    rss_urls = config["RSS_URLS"]
    entry_max_time_old = config["ENTRY_MAX_TIME_OLD"]
    time_interval_min = config["TIME_INTERVAL_MIN"]

    # Schedule main RSS task
    schedule.every(time_interval_min).minutes.do(
        parse_rss,
        rss_feeds=rss_urls,
        entry_max_time_old=entry_max_time_old,
        bot_token=bot_token,
        channel_id=channel_id,
    )
    logging.info(f"Scheduler set to run every {time_interval_min} minutes.")

    # Schedule cache cleanup
    schedule.every(cache_flush_interval_days).days.do(clear_cache)
    logging.info("Cache cleanup scheduled once per week.")

    # Infinite loop that never breaks
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.exception(f"Unexpected error in scheduler loop: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()