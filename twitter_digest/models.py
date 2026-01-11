"""Data models for the Twitter Digest application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Tweet:
    """Represents a single tweet."""

    handle: str
    text: str
    url: str
    published_at: datetime


@dataclass
class HandleDigest:
    """Digest for a single Twitter handle."""

    handle: str
    tweets: list[Tweet] = field(default_factory=list)
    summary: str = ""
    background: Optional[str] = None


@dataclass
class DailyDigest:
    """Complete daily digest across all handles."""

    date: datetime
    handles: list[HandleDigest] = field(default_factory=list)
    overall_summary: str = ""
    raw_markdown: str = ""
