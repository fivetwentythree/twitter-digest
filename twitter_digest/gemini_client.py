"""Gemini API client for tweet summarization."""

import logging
from datetime import datetime

import google.generativeai as genai

from .models import DailyDigest, HandleDigest, Tweet

logger = logging.getLogger(__name__)

DEFAULT_PROMPT = """You are a sharp, insightful analyst creating a morning briefing from tweets by influential thinkers, founders, and investors.

Your goal: Help the reader start their day informed about what smart people are thinking and talking about.

## For Each Person (@handle)

1. **What They Said** — Summarize their tweets in 2-3 sentences. Capture the essence, not just the words.

2. **Why It Matters** — Only include this if there's important context:
   - What's the backstory? (e.g., ongoing debate, recent news, industry trend)
   - Why should the reader care?
   - Any non-obvious implications?
   
   Skip this section entirely if the tweets are self-explanatory or casual.

3. **Key Quote** — If there's a particularly sharp or memorable line, include it.

## Overall Takeaways

End with 3-5 bullet points capturing:
- The big themes across all accounts today
- Any contrarian or surprising takes
- Actionable insights or things to watch

## Style Guidelines
- Be direct and opinionated, not neutral and bland
- Write like a smart friend catching you up over coffee
- No fluff, no filler, no "it's interesting to note that..."
- Use plain language; explain jargon briefly if needed
- Format with Markdown: use **bold** for emphasis, `code` for terms/tickers
"""


def create_gemini_client(api_key: str) -> genai.GenerativeModel:
    """Initialize and return a Gemini client."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def build_prompt(
    tweets_by_handle: dict[str, list[Tweet]],
    custom_prompt: str | None = None,
) -> str:
    """Build the prompt for Gemini with all tweets."""
    base_prompt = custom_prompt or DEFAULT_PROMPT

    tweet_sections = []
    for handle, tweets in tweets_by_handle.items():
        if not tweets:
            continue

        tweet_list = []
        for tweet in tweets:
            time_str = tweet.published_at.strftime("%H:%M UTC")
            text = tweet.text[:500]
            tweet_list.append(f"- [{time_str}] {text}")

        tweet_section = f"\n### @{handle} ({len(tweets)} tweets)\n" + "\n".join(tweet_list)
        tweet_sections.append(tweet_section)

    if not tweet_sections:
        return ""

    full_prompt = f"""{base_prompt}

---

## Today's Tweets

{chr(10).join(tweet_sections)}

---

Please analyze the above tweets and provide the digest.
"""
    return full_prompt


def generate_digest(
    api_key: str,
    tweets_by_handle: dict[str, list[Tweet]],
    custom_prompt: str | None = None,
) -> str:
    """Generate a digest using Gemini."""
    prompt = build_prompt(tweets_by_handle, custom_prompt)

    if not prompt:
        return "No tweets available for analysis."

    try:
        model = create_gemini_client(api_key)
        response = model.generate_content(prompt)
        return response.text or "No response generated."
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


def create_daily_digest(
    tweets_by_handle: dict[str, list[Tweet]],
    gemini_response: str,
) -> DailyDigest:
    """Create a DailyDigest object from tweets and Gemini response."""
    handle_digests = []

    for handle, tweets in tweets_by_handle.items():
        handle_digests.append(
            HandleDigest(
                handle=handle,
                tweets=tweets,
                summary="",
            )
        )

    return DailyDigest(
        date=datetime.now(),
        handles=handle_digests,
        overall_summary="",
        raw_markdown=gemini_response,
    )


def create_fallback_digest(tweets_by_handle: dict[str, list[Tweet]]) -> str:
    """Create a simple digest without AI when Gemini is unavailable."""
    sections = ["# Twitter Digest\n", "*AI summarization unavailable - showing raw tweets*\n"]

    for handle, tweets in tweets_by_handle.items():
        if not tweets:
            continue

        sections.append(f"\n## @{handle}\n")
        for tweet in tweets:
            time_str = tweet.published_at.strftime("%Y-%m-%d %H:%M UTC")
            sections.append(f"- **{time_str}**: {tweet.text}\n")

    return "\n".join(sections)
