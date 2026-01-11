"""Main entry point for the Twitter Digest application."""

import logging
import sys
from datetime import datetime
from pathlib import Path

from .config_loader import load_config
from .twitter_client import fetch_all_tweets
from .gemini_client import generate_digest, create_daily_digest, create_fallback_digest
from .html_builder import build_digest_html, build_index_html

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = "docs"


def main(config_path: str = "config/config.yaml") -> int:
    """Run the Twitter Digest pipeline."""
    logger.info("=" * 50)
    logger.info("Twitter Digest - Starting")
    logger.info("=" * 50)

    try:
        config = load_config(config_path)
        config.validate()
        logger.info(f"Configuration loaded: {len(config.handles)} handles to track")
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1

    logger.info("Fetching tweets from Twitter API...")
    tweets_by_handle = fetch_all_tweets(
        handles=config.handles,
        bearer_token=config.twitter_bearer_token,
        lookback_hours=config.digest.lookback_hours,
        max_tweets_per_handle=config.digest.max_tweets_per_handle,
    )

    total_tweets = sum(len(tweets) for tweets in tweets_by_handle.values())
    handles_with_tweets = sum(1 for tweets in tweets_by_handle.values() if tweets)
    logger.info(f"Fetched {total_tweets} tweets from {handles_with_tweets}/{len(config.handles)} handles")

    if total_tweets == 0:
        logger.warning("No tweets found in the lookback period")
        markdown_content = "# Twitter Digest\n\nNo new tweets found in the last 24 hours."
    else:
        try:
            logger.info("Generating AI summary with Gemini...")
            markdown_content = generate_digest(
                api_key=config.gemini_api_key,
                tweets_by_handle=tweets_by_handle,
                custom_prompt=config.gemini_prompt,
            )
            logger.info("AI summary generated successfully")
        except Exception as e:
            logger.warning(f"Gemini API failed, using fallback: {e}")
            markdown_content = create_fallback_digest(tweets_by_handle)

    digest = create_daily_digest(tweets_by_handle, markdown_content)

    logger.info("Building HTML pages...")
    try:
        filename = build_digest_html(
            digest=digest,
            output_dir=OUTPUT_DIR,
            title=config.digest.title,
        )
        logger.info(f"Digest HTML generated: {OUTPUT_DIR}/{filename}")

        build_index_html(output_dir=OUTPUT_DIR, title=config.digest.title)
        logger.info(f"Index HTML updated: {OUTPUT_DIR}/index.html")

    except Exception as e:
        logger.error(f"Failed to generate HTML: {e}")
        return 1

    logger.info("=" * 50)
    logger.info("Twitter Digest - Complete")
    logger.info(f"  Handles: {len(config.handles)}")
    logger.info(f"  Tweets: {total_tweets}")
    logger.info(f"  Output: {OUTPUT_DIR}/{filename}")
    logger.info("=" * 50)

    return 0


if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config/config.yaml"
    sys.exit(main(config_file))
