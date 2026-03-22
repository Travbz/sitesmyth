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
def run(zip_code: str | None, city: str | None, state: str, categories: str, limit: int, dry_run_outreach: bool) -> None:
    """Run full pipeline: discover → scrape → generate → upload → outreach."""
    from sitesmyth.pipeline import run_pipeline
    cat_list = [c.strip() for c in categories.split(",") if c.strip()]
    run_pipeline(zip_code=zip_code, city=city, state=state, categories=cat_list, limit=limit, outreach_dry_run=dry_run_outreach)


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
    cfg.data_dir.mkdir(parents=True, exist_ok=True)

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
    from sitesmyth.scraper.image_downloader import optimize_images

    for lead in leads:
        console.rule(f"[bold blue]{lead.business_name}[/bold blue]")
        total = 0
        if lead.facebook_url and lead.facebook_active:
            n = scrape_facebook(lead.id, cfg.data_dir)
            total += n
            console.print(f"  Facebook: {n} items")
        if lead.instagram_handle and lead.instagram_active:
            n = scrape_instagram(lead.id, cfg.data_dir)
            total += n
            console.print(f"  Instagram: {n} items")
        if lead.facebook_url and lead.instagram_handle:
            merge_content(lead.id, cfg.data_dir)
        optimize_images(lead.id, cfg.data_dir)
        console.print(f"  [green]Total: {total}[/green]")
    console.rule("[bold green]Done[/bold green]")


@cli.command()
@click.option("--lead-id", type=int, default=None, help="Generate site for single lead")
@click.option("--all-scraped", is_flag=True, help="Generate for all scraped leads")
def generate(lead_id: int | None, all_scraped: bool) -> None:
    """Generate static site from scraped content (Gemini Flash)."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = Config.load()
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
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

    from sitesmyth.generator.content_generator import generate_content
    from sitesmyth.generator.site_builder import build_site

    for lead in leads:
        console.rule(f"[bold blue]{lead.business_name}[/bold blue]")
        try:
            content = generate_content(lead.id, cfg.data_dir, cfg.output_dir)
            site_dir = build_site(lead.id, content, cfg.data_dir, cfg.output_dir, cfg)
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


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
