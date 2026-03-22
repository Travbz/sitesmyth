"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


def _int_env(name: str, default: int) -> int:
    val = os.getenv(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


@dataclass
class Config:
    # Database
    database_url: str = "sqlite:///leads.db"

    # Google Places API (optional — use for discovery if set, else Apify)
    google_maps_key: str = ""

    # Apify (Google Maps fallback, Facebook, Instagram scraping)
    apify_api_token: str = ""

    # Google Gemini (content generation, vision)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Cloudflare (R2 + Worker hosting)
    cloudflare_account_id: str = ""
    cloudflare_api_token: str = ""
    cloudflare_r2_access_key: str = ""
    cloudflare_r2_secret_key: str = ""
    cloudflare_r2_bucket: str = "sitesmyth-sites"
    cloudflare_r2_endpoint: str = ""  # e.g. https://<account_id>.r2.cloudflarestorage.com

    # Outreach
    resend_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # SiteSmyth branding
    sitesmyth_domain: str = "sitesmyth.com"
    contact_email: str = "hello@sitesmyth.com"
    contact_phone: str = ""
    physical_address: str = ""

    # Paths
    data_dir: Path = field(default_factory=lambda: Path("data"))
    output_dir: Path = field(default_factory=lambda: Path("output"))

    # Pipeline defaults
    max_emails_per_hour: int = 50
    max_dm_per_day: int = 15

    @classmethod
    def load(cls, env_file: str | Path | None = None) -> Config:
        load_dotenv(env_file or ".env")
        db_url = os.getenv("DATABASE_URL") or "sqlite:///leads.db"
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        r2_endpoint = os.getenv("CLOUDFLARE_R2_ENDPOINT") or (
            f"https://{account_id}.r2.cloudflarestorage.com" if account_id else ""
        )
        return cls(
            database_url=db_url,
            google_maps_key=os.getenv("GOOGLE_MAPS_KEY", ""),
            apify_api_token=os.getenv("APIFY_API_TOKEN", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            cloudflare_account_id=account_id,
            cloudflare_api_token=os.getenv("CLOUDFLARE_API_TOKEN", ""),
            cloudflare_r2_access_key=os.getenv("CLOUDFLARE_R2_ACCESS_KEY", ""),
            cloudflare_r2_secret_key=os.getenv("CLOUDFLARE_R2_SECRET_KEY", ""),
            cloudflare_r2_bucket=os.getenv("CLOUDFLARE_R2_BUCKET", "sitesmyth-sites"),
            cloudflare_r2_endpoint=r2_endpoint,
            resend_api_key=os.getenv("RESEND_API_KEY", ""),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
            twilio_phone_number=os.getenv("TWILIO_PHONE_NUMBER", ""),
            sitesmyth_domain=os.getenv("SITESMYTH_DOMAIN", "sitesmyth.com"),
            contact_email=os.getenv("CONTACT_EMAIL", "hello@sitesmyth.com"),
            contact_phone=os.getenv("CONTACT_PHONE", ""),
            physical_address=os.getenv("PHYSICAL_ADDRESS", ""),
            data_dir=Path(os.getenv("SITESMYTH_DATA_DIR", "data")),
            output_dir=Path(os.getenv("SITESMYTH_OUTPUT_DIR", "output")),
            max_emails_per_hour=_int_env("SITESMYTH_MAX_EMAILS_PER_HOUR", 50),
            max_dm_per_day=_int_env("SITESMYTH_MAX_DM_PER_DAY", 15),
        )
