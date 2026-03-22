"""Full pipeline orchestrator — discover → scrape → generate → upload → outreach."""

from __future__ import annotations

import logging
import time

from rich.console import Console
from rich.table import Table

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead

console = Console()
log = logging.getLogger(__name__)


def run_pipeline(
    *,
    zip_code: str | None = None,
    city: str | None = None,
    state: str = "OH",
    categories: list[str] | None = None,
    limit: int = 10,
    outreach_dry_run: bool = False,
    skip_activity_check: bool = False,
) -> None:
    """Run full pipeline: discover → scrape → generate → upload → outreach (email only)."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = Config.load()
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    cat_list = categories or ["restaurants", "plumbers", "landscaping"]
    start = time.time()

    try:
        console.rule("[bold blue]1. Discovery[/bold blue]")
        from sitesmyth.discovery.maps_scraper import run_maps_discovery
        added = run_maps_discovery(
            zip_code=zip_code,
            city=city,
            state=state,
            categories=cat_list,
            max_per_search=min(limit * 3, 100),
        )
        console.print(f"  Added {added} leads")

        console.rule("[bold blue]2. Social finder + activity[/bold blue]")
        from sitesmyth.discovery.social_finder import find_social_profiles
        from sitesmyth.discovery.activity_checker import run_activity_check
        find_social_profiles(limit=added + 20)
        if not skip_activity_check:
            run_activity_check(limit=added + 20)

        console.rule("[bold blue]3. Scrape[/bold blue]")
        from sitesmyth.scraper.facebook_scraper import scrape_facebook
        from sitesmyth.scraper.instagram_scraper import scrape_instagram
        from sitesmyth.scraper.content_merger import merge_content

        session = get_session(cfg.database_url)
        to_scrape = session.query(Lead).filter(
            Lead.status == "discovered",
            Lead.primary_social.isnot(None),
            Lead.primary_social != "stale",
        ).limit(limit).all()
        session.close()

        for lead in to_scrape:
            try:
                if lead.facebook_url and lead.facebook_active:
                    scrape_facebook(lead.id)
            except Exception as e:
                log.warning("Facebook scrape failed for %s: %s", lead.business_name, e)
            try:
                if lead.instagram_handle and lead.instagram_active:
                    scrape_instagram(lead.id)
            except Exception as e:
                log.warning("Instagram scrape failed for %s: %s", lead.business_name, e)
            if lead.facebook_url and lead.instagram_handle:
                merge_content(lead.id)

        console.rule("[bold blue]3b. Content scoring[/bold blue]")
        from sitesmyth.scraper.content_scorer import score_lead, THRESHOLD

        session = get_session(cfg.database_url)
        scraped_leads = session.query(Lead).filter(Lead.status == "scraped").all()
        session.close()

        passed = 0
        gated = 0
        for lead in scraped_leads:
            s = score_lead(lead.id)
            if s >= THRESHOLD:
                passed += 1
            else:
                gated += 1
        console.print(f"  Scored {len(scraped_leads)} leads: {passed} passed (>={THRESHOLD}), {gated} gated")

        console.rule("[bold blue]3c. Activity filter[/bold blue]")
        from sitesmyth.scraper.activity_filter import filter_inactive_leads
        activity = filter_inactive_leads()
        console.print(f"  Active: {activity['active']}, Stale: {activity['stale']}")

        console.rule("[bold blue]4a. Plan (vibe check)[/bold blue]")
        from sitesmyth.generator.planner import plan_site

        session = get_session(cfg.database_url)
        to_plan = session.query(Lead).filter(
            Lead.status == "scraped",
            Lead.content_score >= THRESHOLD,
        ).limit(limit).all()
        session.close()

        for lead in to_plan:
            try:
                plan_site(lead.id)
            except Exception as e:
                console.print(f"  [yellow]Plan failed for {lead.business_name}: {e}[/yellow]")

        console.rule("[bold blue]4b. Build (Google Stitch)[/bold blue]")
        from sitesmyth.generator.stitch_builder import build_stitch_site
        from datetime import datetime

        session = get_session(cfg.database_url)
        to_gen = session.query(Lead).filter(
            Lead.status == "scraped",
            Lead.content_score >= THRESHOLD,
        ).limit(limit).all()
        session.close()

        for lead in to_gen:
            try:
                build_stitch_site(lead.id, cfg.output_dir)
                session = get_session(cfg.database_url)
                l = session.query(Lead).filter(Lead.id == lead.id).first()
                if l:
                    l.status = "generated"
                    l.site_generated_at = datetime.utcnow().isoformat()
                    l.site_url = f"{lead.slug}.{cfg.sitesmyth_domain}"
                session.commit()
                session.close()
            except Exception as e:
                console.print(f"  [yellow]Skip {lead.business_name}: {e}[/yellow]")

        console.rule("[bold blue]5. Upload[/bold blue]")
        from sitesmyth.hosting.uploader import upload_site

        session = get_session(cfg.database_url)
        to_upload = session.query(Lead).filter(Lead.status == "generated").limit(limit).all()
        session.close()

        for lead in to_upload:
            site_dir = cfg.output_dir / lead.slug
            dist_dir = site_dir / "dist"
            upload_from = dist_dir if dist_dir.exists() else site_dir
            if (upload_from / "index.html").exists():
                upload_site(lead.slug, upload_from, cfg)
                session = get_session(cfg.database_url)
                l = session.query(Lead).filter(Lead.id == lead.id).first()
                if l:
                    l.status = "hosted"
                    l.site_url = f"{lead.slug}.{cfg.sitesmyth_domain}"
                session.commit()
                session.close()

        console.rule("[bold blue]6. Outreach[/bold blue]")
        from sitesmyth.outreach.orchestrator import run_outreach
        from sitesmyth.outreach.email_sender import send_no_demo_email
        if outreach_dry_run:
            console.print("[yellow]DRY RUN — no emails will be sent[/yellow]")

        session = get_session(cfg.database_url)
        low_content = session.query(Lead).filter(Lead.status == "low_content").limit(limit).all()
        session.close()
        no_demo_sent = 0
        for lead in low_content:
            if outreach_dry_run:
                log.info("DRY RUN: would send no-demo email to %s <%s>", lead.business_name, lead.email)
                no_demo_sent += 1
            elif lead.email:
                if send_no_demo_email(lead, cfg):
                    no_demo_sent += 1
        if no_demo_sent:
            console.print(f"  No-demo emails: {no_demo_sent}")

        stats = run_outreach(channel="email", sequence_number=1, limit=limit, dry_run=outreach_dry_run)
        console.print(f"  Demo emails: {stats.get('sent', 0)}")

        elapsed = time.time() - start
        console.rule("[bold green]Pipeline complete[/bold green]")
        console.print(f"  Elapsed: {elapsed / 60:.1f} min")

        from sqlalchemy import func
        session = get_session(cfg.database_url)
        rows = session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
        session.close()

        table = Table(title="Pipeline status")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right")
        for status, cnt in rows:
            table.add_row(status or "-", str(cnt))
        console.print(table)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Progress saved.[/yellow]")
