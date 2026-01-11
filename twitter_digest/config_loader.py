"""Configuration loader for Twitter Digest."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class DigestConfig:
    """Digest settings."""

    title: str = "Twitter Morning Digest"
    timezone: str = "UTC"
    max_tweets_per_handle: int = 20
    lookback_hours: int = 24


@dataclass
class EmailConfig:
    """Email settings loaded from environment variables."""

    from_address: str = ""
    to: list[str] = field(default_factory=list)
    subject_template: str = "Twitter Digest - {date}"

    @classmethod
    def from_env(cls, yaml_config: dict) -> "EmailConfig":
        """Load email config from environment with YAML fallback."""
        from_addr = os.getenv("EMAIL_FROM", yaml_config.get("from", ""))
        to_raw = os.getenv("EMAIL_TO", "")
        
        if to_raw:
            to_list = [e.strip() for e in to_raw.split(",") if e.strip()]
        else:
            to_list = yaml_config.get("to", [])
        
        return cls(
            from_address=from_addr,
            to=to_list,
            subject_template=yaml_config.get("subject_template", cls.subject_template),
        )


@dataclass
class NitterConfig:
    """Nitter instance settings."""

    instances: list[str] = field(default_factory=lambda: [
        "https://nitter.privacydev.net",
        "https://nitter.poast.org",
    ])


@dataclass
class SmtpConfig:
    """SMTP settings loaded from environment variables."""

    host: str = ""
    port: int = 587
    username: str = ""
    password: str = ""
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> "SmtpConfig":
        """Load SMTP config from environment variables."""
        return cls(
            host=os.getenv("SMTP_HOST", ""),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        )


@dataclass
class Config:
    """Main configuration container."""

    digest: DigestConfig = field(default_factory=DigestConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    nitter: NitterConfig = field(default_factory=NitterConfig)
    smtp: SmtpConfig = field(default_factory=SmtpConfig)
    handles: list[str] = field(default_factory=list)
    gemini_api_key: str = ""
    gemini_prompt: Optional[str] = None

    def validate(self) -> None:
        """Validate the configuration."""
        errors = []

        if not self.handles:
            errors.append("No Twitter handles configured")



        if not self.gemini_api_key:
            errors.append("GEMINI_API_KEY not set")



        if not self.nitter.instances:
            errors.append("No Nitter instances configured")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


def load_config(config_path: str = "config/config.yaml") -> Config:
    """Load configuration from YAML file and environment variables."""
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    digest_data = data.get("digest", {})
    digest = DigestConfig(
        title=digest_data.get("title", DigestConfig.title),
        timezone=digest_data.get("timezone", DigestConfig.timezone),
        max_tweets_per_handle=digest_data.get("max_tweets_per_handle", DigestConfig.max_tweets_per_handle),
        lookback_hours=digest_data.get("lookback_hours", DigestConfig.lookback_hours),
    )

    email_data = data.get("email", {})
    email = EmailConfig.from_env(email_data)

    nitter_data = data.get("nitter", {})
    nitter = NitterConfig(
        instances=nitter_data.get("instances", NitterConfig().instances),
    )

    config = Config(
        digest=digest,
        email=email,
        nitter=nitter,
        smtp=SmtpConfig.from_env(),
        handles=data.get("handles", []),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_prompt=data.get("gemini_prompt"),
    )

    return config
