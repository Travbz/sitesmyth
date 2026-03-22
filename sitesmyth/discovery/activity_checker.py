"""Check social media activity — only keep leads active in last 90 days."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from apify_client import ApifyClient

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead

log = logging.getLogger(__name__)

ACTIVITY_DAYS = 90
FB_POSTS_ACTOR = "apify/facebook-posts-scraper"
IG_POSTS_ACTOR = "apify/instagram-post-scraper"


def _parse_date(s: str | None) -> datetime | None:
    """Parse ISO or common date string to datetime."""
    if not s:
        return None
    s = str(s).strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")[:26])
    except ValueError:
        pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except ValueError:
        return None


def _check_facebook_activity(client: ApifyClient, page_url: str) -> tuple[bool, str | None, int | None]:
    """Check if FB page has posts in last 90 days. Returns (active, last_post_date, likes)."""
    if not page_url or "facebook.com" not in page_url:
        return False, None, None
    try:
        actor = client.actor(FB_POSTS_ACTOR)
        run = actor.call(run_input={"startUrls": [{"url": page_url}], "maxPosts": 10}, timeout=60)
        if not run:
            return False, None, None
        dataset = client.dataset(run.default_dataset_id)
        items = list(dataset.iterate_items())
        if not items:
            return False, None, None
        cutoff = datetime.utcnow() - timedelta(days=ACTIVITY_DAYS)
        last_date = None
        for item in items:
            dt_str = item.get("time") or item.get("timestamp") or item.get("created_time")
            dt = _parse_date(dt_str)
            if dt:
                if last_date is None or dt > last_date:
                    last_date = dt
        active = last_date is not None and last_date >= cutoff
        return active, last_date.isoformat() if last_date else None, None
    except Exception as e:
        log.debug("FB activity check failed for %s: %s", page_url, e)
        return False, None, None


def _check_instagram_activity(client: ApifyClient, username: str) -> tuple[bool, str | None, int | None]:
    """Check if IG profile has posts in last 90 days. Returns (active, last_post_date, followers)."""
    if not username:
        return False, None, None
    try:
        actor = client.actor(IG_POSTS_ACTOR)
        run = actor.call(run_input={"directUrls": [f"https://www.instagram.com/{username}/"], "resultsLimit": 10}, timeout=60)
        if not run:
            return False, None, None
        dataset = client.dataset(run.default_dataset_id)
        items = list(dataset.iterate_items())
        if not items:
            return False, None, None
        cutoff = datetime.utcnow() - timedelta(days=ACTIVITY_DAYS)
        last_date = None
        followers = None
        for item in items:
            dt_str = item.get("timestamp") or item.get("taken_at") or item.get("created_at")
            dt = _parse_date(str(dt_str) if dt_str else None)
            if dt:
                if last_date is None or dt > last_date:
                    last_date = dt
            if "owner" in item and "followersCount" in item.get("owner", {}):
                followers = item["owner"].get("followersCount")
        active = last_date is not None and last_date >= cutoff
        return active, last_date.isoformat() if last_date else None, followers
    except Exception as e:
        log.debug("IG activity check failed for %s: %s", username, e)
        return False, None, None


def run_activity_check(lead_id: int | None = None, limit: int | None = None) -> int:
    """Check activity for leads, set primary_social, mark stale if neither active."""
    cfg = Config.load()
    if not cfg.apify_api_token:
        raise RuntimeError("APIFY_API_TOKEN required for activity check.")

    session = get_session(cfg.database_url)
    query = session.query(Lead).filter(Lead.status == "discovered")
    if lead_id:
        query = query.filter(Lead.id == lead_id)
    if limit:
        query = query.limit(limit)
    leads = query.all()

    client = ApifyClient(cfg.apify_api_token)
    checked = 0

    for lead in leads:
        fb_active, fb_date, fb_likes = _check_facebook_activity(client, lead.facebook_url or "")
        ig_active, ig_date, ig_followers = _check_instagram_activity(client, lead.instagram_handle or "")

        lead.facebook_active = fb_active
        lead.facebook_last_post_date = fb_date
        if fb_likes is not None:
            lead.facebook_page_likes = fb_likes
        lead.instagram_active = ig_active
        lead.instagram_last_post_date = ig_date
        if ig_followers is not None:
            lead.instagram_followers = ig_followers

        if fb_active and ig_active:
            lead.primary_social = "both"
        elif fb_active:
            lead.primary_social = "facebook"
        elif ig_active:
            lead.primary_social = "instagram"
        else:
            lead.primary_social = "stale"
            lead.status = "stale"

        checked += 1

    session.commit()
    session.close()
    return checked
