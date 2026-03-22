"""Upload generated sites and landing page to Cloudflare R2."""

from __future__ import annotations

import logging
from pathlib import Path

import boto3
from botocore.config import Config as BotoConfig

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead

log = logging.getLogger(__name__)


def _get_r2_client(cfg: Config):
    """Create boto3 S3 client for R2."""
    endpoint = cfg.cloudflare_r2_endpoint or f"https://{cfg.cloudflare_account_id}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=cfg.cloudflare_r2_access_key,
        aws_secret_access_key=cfg.cloudflare_r2_secret_key,
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    )


def upload_site(slug: str, site_dir: Path, cfg: Config) -> int:
    """Upload a generated site to R2 at sites/{slug}/. Returns count of objects uploaded."""
    if not cfg.cloudflare_r2_access_key:
        raise RuntimeError("CLOUDFLARE_R2_ACCESS_KEY and CLOUDFLARE_R2_SECRET_KEY required.")

    client = _get_r2_client(cfg)
    bucket = cfg.cloudflare_r2_bucket
    prefix = f"sites/{slug}"
    count = 0

    for path in site_dir.rglob("*"):
        if path.is_file():
            key = f"{prefix}/{path.relative_to(site_dir)}".replace("\\", "/")
            content_type = "text/html" if path.suffix == ".html" else "application/octet-stream"
            if path.suffix in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                content_type = f"image/{path.suffix[1:]}"
            client.upload_file(str(path), bucket, key, ExtraArgs={"ContentType": content_type})
            count += 1
            log.debug("Uploaded %s", key)

    return count


def upload_landing_page(landing_dist: Path, cfg: Config) -> int:
    """Upload Astro landing page to R2 at _marketing/."""
    if not cfg.cloudflare_r2_access_key:
        raise RuntimeError("CLOUDFLARE_R2_ACCESS_KEY required.")

    client = _get_r2_client(cfg)
    bucket = cfg.cloudflare_r2_bucket
    prefix = "_marketing"
    count = 0

    for path in landing_dist.rglob("*"):
        if path.is_file():
            key = f"{prefix}/{path.relative_to(landing_dist)}".replace("\\", "/")
            content_type = "text/html" if path.suffix == ".html" else "application/octet-stream"
            if path.suffix in (".css",):
                content_type = "text/css"
            elif path.suffix in (".js",):
                content_type = "application/javascript"
            elif path.suffix in (".jpg", ".jpeg", ".png", ".webp", ".svg", ".ico"):
                content_type = f"image/{path.suffix[1:]}"
            client.upload_file(str(path), bucket, key, ExtraArgs={"ContentType": content_type})
            count += 1

    return count
