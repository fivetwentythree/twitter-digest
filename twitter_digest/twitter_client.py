"""Twitter/X API client for fetching tweets."""

import logging
import os
from datetime import datetime, timedelta, timezone

import httpx

from .models import Tweet

logger = logging.getLogger(__name__)

TWITTER_API_BASE = "https://api.twitter.com/2"


def fetch_tweets_for_handle(
    handle: str,
    bearer_token: str,
    lookback_hours: int = 24,
    max_tweets: int = 20,
) -> list[Tweet]:
    """
    Fetch tweets for a handle using Twitter API v2.
    
    Requires a Twitter API Bearer Token (free tier available).
    """
    handle = handle.lstrip("@")
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "TwitterDigest/1.0",
    }
    
    try:
        with httpx.Client(timeout=15) as client:
            user_resp = client.get(
                f"{TWITTER_API_BASE}/users/by/username/{handle}",
                headers=headers,
            )
            user_resp.raise_for_status()
            user_data = user_resp.json()
            
            if "data" not in user_data:
                logger.warning(f"User @{handle} not found")
                return []
            
            user_id = user_data["data"]["id"]
            
            start_time = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()
            
            tweets_resp = client.get(
                f"{TWITTER_API_BASE}/users/{user_id}/tweets",
                headers=headers,
                params={
                    "max_results": min(max_tweets, 100),
                    "start_time": start_time,
                    "tweet.fields": "created_at,text",
                    "exclude": "retweets,replies",
                },
            )
            tweets_resp.raise_for_status()
            tweets_data = tweets_resp.json()
            
            tweets = []
            for tweet in tweets_data.get("data", []):
                published_at = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))
                tweets.append(
                    Tweet(
                        handle=handle,
                        text=tweet["text"],
                        url=f"https://x.com/{handle}/status/{tweet['id']}",
                        published_at=published_at,
                    )
                )
            
            logger.info(f"Found {len(tweets)} tweets for @{handle}")
            return tweets
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Twitter API error for @{handle}: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching tweets for @{handle}: {e}")
        return []


def fetch_all_tweets(
    handles: list[str],
    bearer_token: str,
    lookback_hours: int = 24,
    max_tweets_per_handle: int = 20,
) -> dict[str, list[Tweet]]:
    """Fetch tweets for all handles using Twitter API."""
    results: dict[str, list[Tweet]] = {}
    
    for handle in handles:
        tweets = fetch_tweets_for_handle(
            handle=handle,
            bearer_token=bearer_token,
            lookback_hours=lookback_hours,
            max_tweets=max_tweets_per_handle,
        )
        results[handle] = tweets
    
    return results
