"""SiteSmyth CLI — discover, scrape, generate, upload, outreach."""

from __future__ import annotations

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead

console = Console()


@click.group()
def cli() -> None:
    """SiteSmyth — find local businesses without websites, build demo sites from social content."""


@cli.command()
@click.option("--zip-code", "--zip", "zip_code", default=None, help="Zip code")
@click.option("--city", default=None, help="City name")
@click.option("--state", default="OH", help="State")
@click.option("--categories", default="restaurants,plumbers", help="Comma-separated categories")
@click.option("--limit", default=5, type=int, help="Max leads per stage")
@click.option("--dry-run-outreach", is_flag=True, help="Skip sending real emails in outreach step")
@click.option("--skip-activity-check", is_flag=True, help="Skip activity check (for demo with manual leads)")
def run(zip_code: str | None, city: str | None, state: str, categories: str, limit: int, dry_run_outreach: bool, skip_activity_check: bool) -> None:
    """Run full pipeline: discover → scrape → generate → upload → outreach."""
    from sitesmyth.pipeline import run_pipeline
    cat_list = [c.strip() for c in categories.split(",") if c.strip()]
    run_pipeline(zip_code=zip_code, city=city, state=state, categories=cat_list, limit=limit, outreach_dry_run=dry_run_outreach, skip_activity_check=skip_activity_check)


@cli.command()
@click.option("--zip-code", "--zip", "zip_code", default=None, help="Zip code (e.g. 45202)")
@click.option("--city", default=None, help="City name (use with --state)")
@click.option("--state", default="OH", help="State abbreviation")
@click.option("--categories", default="restaurants,plumbers,landscaping", help="Comma-separated categories")
@click.option("--max", "max_per_search", default=100, type=int, help="Max places per search")
@click.option("--find-social", is_flag=True, help="Run social profile finder after discovery")
@click.option("--check-activity", is_flag=True, help="Run activity check after (requires Apify)")
def discover(
    zip_code: str | None,
    city: str | None,
    state: str,
    categories: str,
    max_per_search: int,
    find_social: bool,
    check_activity: bool,
) -> None:
    """Discover local businesses without websites via Google Maps (Apify)."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cat_list = [c.strip() for c in categories.split(",") if c.strip()]
    console.rule("[bold blue]Discovery")
    from sitesmyth.discovery.maps_scraper import run_maps_discovery

    added = run_maps_discovery(
        zip_code=zip_code,
        city=city,
        state=state,
        categories=cat_list,
        max_per_search=max_per_search,
    )
    console.print(f"  [green]Added {added} new leads[/green]")
    if find_social:
        console.rule("[bold blue]Social profile finder")
        from sitesmyth.discovery.social_finder import find_social_profiles
        updated = find_social_profiles(limit=added + 50)
        console.print(f"  [green]Updated {updated} leads with social profiles[/green]")
    if check_activity:
        console.rule("[bold blue]Activity check")
        from sitesmyth.discovery.activity_checker import run_activity_check
        checked = run_activity_check(limit=added + 50)
        console.print(f"  [green]Checked {checked} leads[/green]")
    console.rule("[bold green]Done[/bold green]")


@cli.command()
@click.option("--lead-id", type=int, default=None, help="Scrape single lead by ID")
@click.option("--all-pending", is_flag=True, help="Scrape all leads with status discovered (active social)")
def scrape(lead_id: int | None, all_pending: bool) -> None:
    """Scrape Facebook/Instagram content for leads."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = Config.load()

    session = get_session(cfg.database_url)
    if lead_id:
        leads = session.query(Lead).filter(Lead.id == lead_id).all()
    elif all_pending:
        leads = session.query(Lead).filter(
            Lead.status == "discovered",
            (Lead.facebook_url.isnot(None)) | (Lead.instagram_handle.isnot(None)),
        ).limit(50).all()
    else:
        console.print("[red]Provide --lead-id or --all-pending[/red]")
        session.close()
        raise SystemExit(1)
    session.close()

    if not leads:
        console.print("[yellow]No leads to scrape[/yellow]")
        return

    from sitesmyth.scraper.facebook_scraper import scrape_facebook
    from sitesmyth.scraper.instagram_scraper import scrape_instagram
    from sitesmyth.scraper.content_merger import merge_content

    for lead in leads:
        console.rule(f"[bold blue]{lead.business_name}[/bold blue]")
        total = 0
        if lead.facebook_url and lead.facebook_active:
            n = scrape_facebook(lead.id)
            total += n
            console.print(f"  Facebook: {n} items")
        if lead.instagram_handle and lead.instagram_active:
            n = scrape_instagram(lead.id)
            total += n
            console.print(f"  Instagram: {n} items")
        if lead.facebook_url and lead.instagram_handle:
            merge_content(lead.id)
        console.print(f"  [green]Total: {total}[/green]")
    console.rule("[bold green]Done[/bold green]")


@cli.command()
@click.option("--lead-id", type=int, default=None, help="Generate site for single lead")
@click.option("--all-scraped", is_flag=True, help="Generate for all scraped leads")
def generate(lead_id: int | None, all_scraped: bool) -> None:
    """Generate static site from scraped content (Gemini Flash)."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = Config.load()
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    session = get_session(cfg.database_url)
    if lead_id:
        leads = session.query(Lead).filter(Lead.id == lead_id).all()
    elif all_scraped:
        leads = session.query(Lead).filter(Lead.status == "scraped").limit(50).all()
    else:
        console.print("[red]Provide --lead-id or --all-scraped[/red]")
        session.close()
        raise SystemExit(1)
    session.close()

    if not leads:
        console.print("[yellow]No leads to generate[/yellow]")
        return

    from sitesmyth.generator.planner import plan_site
    from sitesmyth.generator.stitch_builder import build_stitch_site

    for lead in leads:
        console.rule(f"[bold blue]{lead.business_name}[/bold blue]")
        try:
            console.print("  Planning (vibe check)...")
            plan_site(lead.id)
            console.print("  Building (Google Stitch)...")
            site_dir = build_stitch_site(lead.id, cfg.output_dir)
            from datetime import datetime
            session = get_session(cfg.database_url)
            l = session.query(Lead).filter(Lead.id == lead.id).first()
            if l:
                l.status = "generated"
                l.site_generated_at = datetime.utcnow().isoformat()
                l.site_url = f"{lead.slug}.{cfg.sitesmyth_domain}"
                session.commit()
            session.close()
            console.print(f"  [green]Built {site_dir}[/green]")
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")
    console.rule("[bold green]Done[/bold green]")


@cli.command()
@click.option("--lead-id", type=int, default=None, help="Upload single lead's site")
@click.option("--all-generated", is_flag=True, help="Upload all generated sites")
def upload(lead_id: int | None, all_generated: bool) -> None:
    """Upload generated sites to Cloudflare R2."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = Config.load()

    session = get_session(cfg.database_url)
    if lead_id:
        leads = session.query(Lead).filter(Lead.id == lead_id).all()
    elif all_generated:
        leads = session.query(Lead).filter(Lead.status == "generated").limit(50).all()
    else:
        console.print("[red]Provide --lead-id or --all-generated[/red]")
        session.close()
        raise SystemExit(1)
    session.close()

    if not leads:
        console.print("[yellow]No sites to upload[/yellow]")
        return

    from sitesmyth.hosting.uploader import upload_site

    for lead in leads:
        site_dir = cfg.output_dir / lead.slug
        if not (site_dir / "index.html").exists():
            console.print(f"  [yellow]Skip {lead.business_name}: no index.html[/yellow]")
            continue
        console.rule(f"[bold blue]{lead.business_name}[/bold blue]")
        try:
            n = upload_site(lead.slug, site_dir, cfg)
            session = get_session(cfg.database_url)
            l = session.query(Lead).filter(Lead.id == lead.id).first()
            if l:
                l.status = "hosted"
                l.site_url = f"{lead.slug}.{cfg.sitesmyth_domain}"
                session.commit()
            session.close()
            console.print(f"  [green]Uploaded {n} files → {lead.slug}.{cfg.sitesmyth_domain}[/green]")
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")
    console.rule("[bold green]Done[/bold green]")


@cli.command()
def upload_landing() -> None:
    """Upload Astro landing page to R2 _marketing/."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = Config.load()
    dist = Path(__file__).resolve().parent.parent / "landing" / "dist"
    if not dist.exists():
        console.print("[red]Landing page not built. Run: cd landing && npm run build[/red]")
        raise SystemExit(1)
    from sitesmyth.hosting.uploader import upload_landing_page
    n = upload_landing_page(dist, cfg)
    console.print(f"[green]Uploaded {n} files to _marketing/[/green]")


@cli.command()
@click.option("--lead-id", type=int, default=None, help="Send to single lead")
@click.option("--all-hosted", is_flag=True, help="Send to all hosted leads (respects suppression)")
@click.option("--channel", type=click.Choice(["email", "instagram_dm"]), default="email")
@click.option("--sequence", default=1, type=int, help="Email sequence 1/2/3 (Day 1/3/7)")
@click.option("--limit", default=None, type=int)
@click.option("--dry-run", is_flag=True, help="Log what would be sent without sending")
def outreach(
    lead_id: int | None, all_hosted: bool, channel: str, sequence: int, limit: int | None, dry_run: bool
) -> None:
    """Send cold outreach (email or generate IG DM queue)."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if dry_run:
        console.print("[yellow]DRY RUN — no emails will be sent[/yellow]")
    from sitesmyth.outreach.orchestrator import run_outreach

    if not all_hosted and not lead_id:
        console.print("[red]Provide --lead-id or --all-hosted[/red]")
        raise SystemExit(1)

    stats = run_outreach(
        channel=channel,
        sequence_number=sequence,
        limit=limit,
        lead_id=lead_id,
        dry_run=dry_run,
    )
    if dry_run:
        console.print("[dim]Dry run — no emails sent[/dim]")
    if "dm_queue_path" in stats:
        console.print(f"[green]DM queue: {stats['dm_queue_path']}[/green]")
    else:
        console.print(f"  Sent: {stats.get('sent', 0)}, Skipped: {stats.get('skipped', 0)}, Failed: {stats.get('failed', 0)}")


@cli.command()
def status() -> None:
    """Show pipeline stats — lead counts by status."""
    cfg = Config.load()
    session = get_session(cfg.database_url)

    from sqlalchemy import func
    rows = (
        session.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .order_by(func.count(Lead.id).desc())
        .all()
    )

    table = Table(title="Pipeline Status")
    table.add_column("Status", style="cyan")
    table.add_column("Count", justify="right", style="green")

    for status_name, count in rows:
        table.add_row(status_name or "(empty)", str(count))

    total = sum(c for _, c in rows)
    table.add_section()
    table.add_row("Total", str(total))

    console.print(table)
    session.close()


@cli.command()
@click.option("--name", required=True, help="Business name")
@click.option("--category", default=None, help="Business category (e.g. Restaurant, Barber shop)")
@click.option("--address", default=None, help="Street address")
@click.option("--city", default=None, help="City")
@click.option("--state", default=None, help="State abbreviation")
@click.option("--zip", "zip_code", default=None, help="Zip code")
@click.option("--phone", default=None, help="Phone number")
@click.option("--email", default=None, help="Business email")
@click.option("--facebook", default=None, help="Facebook page URL")
@click.option("--instagram", default=None, help="Instagram handle (without @)")
@click.option("--maps-url", default=None, help="Google Maps URL")
@click.option("--brief", default=None, help="Site brief / description of the business")
def add_lead(
    name: str, category: str | None, address: str | None, city: str | None,
    state: str | None, zip_code: str | None, phone: str | None, email: str | None,
    facebook: str | None, instagram: str | None, maps_url: str | None, brief: str | None,
) -> None:
    """Manually create a lead for building a demo site."""
    import re
    cfg = Config.load()
    session = get_session(cfg.database_url)

    slug = re.sub(r"[^a-z0-9]+", "-", name.lower().strip()).strip("-")[:80]
    existing = session.query(Lead).filter(Lead.slug == slug).first()
    if existing:
        console.print(f"[yellow]Lead already exists: ID={existing.id} ({existing.business_name})[/yellow]")
        session.close()
        return

    lead = Lead(
        business_name=name.strip(),
        slug=slug,
        category=category,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        phone=phone,
        email=email,
        google_maps_url=maps_url,
        facebook_url=facebook,
        instagram_handle=instagram,
        has_website=False,
        status="scraped",
        site_brief=brief,
    )
    session.add(lead)
    session.commit()
    console.print(f"[green]Created lead ID={lead.id}: {lead.business_name} (slug: {lead.slug})[/green]")
    session.close()


@cli.command()
@click.option("--lead-id", type=int, required=True, help="Lead ID to attach photos to")
@click.argument("photo_urls", nargs=-1)
def add_photos(lead_id: int, photo_urls: tuple[str, ...]) -> None:
    """Attach Google Business Profile photo URLs to a lead for Stitch theming."""
    import json
    cfg = Config.load()
    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        console.print(f"[red]Lead {lead_id} not found[/red]")
        session.close()
        raise SystemExit(1)

    existing = json.loads(lead.gbp_photo_urls) if lead.gbp_photo_urls else []
    existing.extend(photo_urls)
    lead.gbp_photo_urls = json.dumps(existing)
    session.commit()
    console.print(f"[green]{lead.business_name}: {len(existing)} photos attached[/green]")
    session.close()


@cli.command()
@click.confirmation_option(prompt="Delete ALL demo sites from R2?")
def nuke_sites() -> None:
    """Delete all demo sites from R2 (keeps _marketing/)."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = Config.load()
    from sitesmyth.hosting.uploader import _get_r2_client

    client = _get_r2_client(cfg)
    bucket = cfg.cloudflare_r2_bucket
    paginator = client.get_paginator("list_objects_v2")
    deleted = 0

    for page in paginator.paginate(Bucket=bucket, Prefix="sites/"):
        objects = page.get("Contents", [])
        if not objects:
            continue
        batch = [{"Key": obj["Key"]} for obj in objects]
        client.delete_objects(Bucket=bucket, Delete={"Objects": batch})
        deleted += len(batch)

    console.print(f"[green]Deleted {deleted} objects from R2 sites/[/green]")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
