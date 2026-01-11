"""Nitter RSS client for fetching tweets."""

import html
import logging
import re
from datetime import datetime, timedelta, timezone

import feedparser
import httpx

from .models import Tweet

logger = logging.getLogger(__name__)


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_rss_date(date_str: str) -> datetime:
    """Parse RSS date string to datetime."""
    from dateutil import parser
    try:
        dt = parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)


def fetch_tweets_for_handle(
    handle: str,
    instances: list[str],
    lookback_hours: int = 24,
    max_tweets: int = 20,
    timeout: float = 15.0,
) -> list[Tweet]:
    """
    Fetch tweets for a handle from Nitter RSS feed.

    Tries multiple Nitter instances with fallback on failure.
    """
    handle = handle.lstrip("@")
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    tweets: list[Tweet] = []

    for instance in instances:
        instance = instance.rstrip("/")
        rss_url = f"{instance}/{handle}/rss"

        try:
            logger.info(f"Fetching RSS for @{handle} from {instance}")

            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                response = client.get(
                    rss_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; TwitterDigest/1.0)"
                    },
                )
                response.raise_for_status()

            feed = feedparser.parse(response.text)

            if not feed.entries:
                logger.warning(f"No entries found in RSS feed for @{handle}")
                continue

            for entry in feed.entries:
                published_str = entry.get("published") or entry.get("updated", "")
                published_at = parse_rss_date(published_str)

                if published_at < cutoff_time:
                    continue

                text = strip_html(entry.get("title") or entry.get("summary", ""))
                url = entry.get("link", "")

                if text:
                    tweets.append(
                        Tweet(
                            handle=handle,
                            text=text,
                            url=url,
                            published_at=published_at,
                        )
                    )

            tweets.sort(key=lambda t: t.published_at, reverse=True)
            tweets = tweets[:max_tweets]

            logger.info(f"Found {len(tweets)} tweets for @{handle}")
            return tweets

        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error fetching @{handle} from {instance}: {e.response.status_code}")
            continue
        except httpx.RequestError as e:
            logger.warning(f"Request error fetching @{handle} from {instance}: {e}")
            continue
        except Exception as e:
            logger.warning(f"Unexpected error fetching @{handle} from {instance}: {e}")
            continue

    logger.error(f"Failed to fetch tweets for @{handle} from all instances")
    return []


def fetch_all_tweets(
    handles: list[str],
    instances: list[str],
    lookback_hours: int = 24,
    max_tweets_per_handle: int = 20,
) -> dict[str, list[Tweet]]:
    """Fetch tweets for all handles."""
    results: dict[str, list[Tweet]] = {}

    for handle in handles:
        tweets = fetch_tweets_for_handle(
            handle=handle,
            instances=instances,
            lookback_hours=lookback_hours,
            max_tweets=max_tweets_per_handle,
        )
        results[handle] = tweets

    return results
