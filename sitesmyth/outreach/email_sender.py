"""Send cold outreach emails via Resend API (CAN-SPAM compliant)."""

from __future__ import annotations

import logging
from datetime import datetime

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, OutreachLog
from sitesmyth.db.queries import has_been_sent, is_suppressed

log = logging.getLogger(__name__)

SUBJECTS = {
    1: "I built {business_name} a website — take a look",
    2: "Quick follow-up — your demo site is live",
    3: "Last check-in about {business_name}'s website",
}

NO_DEMO_SUBJECT = "A website for {business_name}?"

NO_DEMO_BODY = """Hi {greeting},

I build websites for local businesses like {business_name}. I noticed you don't have one yet — and in 2026, that means AI search engines like ChatGPT, Perplexity, and Google AI Overviews can't find or recommend your business.

I'd love to put together a free demo site for you. Check out what I do at https://sitesmyth.com and reply if you're interested — no commitment, I'll just build one and send you a link.

Best,
Travis
SiteSmyth.com | {physical_address}
Unsubscribe: {unsubscribe_link}"""

BODIES = {
    1: """Hi {greeting},

I noticed {business_name} doesn't have a website yet, but your social media content looks great. I put together a quick demo site using your photos and info:

{site_url}

If you like it, I can have your real site live on your own domain within 48 hours — $1,000 flat, you own it, no monthly fees.

If not, no worries — the demo will stay up for 30 days either way.

Best,
Travis
SiteSmyth.com | {physical_address}
Unsubscribe: {unsubscribe_link}""",
    2: """Hi {greeting},

Quick follow-up — your demo site is still live at {site_url}. Take a look when you have a moment.

If you'd like to get it on your own domain, just reply to this email.

Best,
Travis
SiteSmyth.com | {physical_address}
Unsubscribe: {unsubscribe_link}""",
    3: """Hi {greeting},

Last check-in — the demo for {business_name} at {site_url} will expire in about 3 weeks. If you want to keep it and move it to your own domain, let me know.

Best,
Travis
SiteSmyth.com | {physical_address}
Unsubscribe: {unsubscribe_link}""",
}


def send_no_demo_email(lead: Lead, cfg: Config) -> bool:
    """Send no-demo feeler email to low-content leads. Returns True if sent."""
    session = get_session(cfg.database_url)
    if is_suppressed(session, lead.id, lead.email, "email"):
        session.close()
        return False
    if has_been_sent(session, lead.id, "email", 1):
        session.close()
        return False
    session.close()

    if not lead.email:
        return False

    try:
        import resend
        resend.api_key = cfg.resend_api_key

        greeting = "there"
        if lead.business_name:
            parts = lead.business_name.split()
            if len(parts) >= 2 and len(parts[0]) <= 10:
                greeting = parts[0]

        body = NO_DEMO_BODY.format(
            greeting=greeting,
            business_name=lead.business_name or "",
            physical_address=cfg.physical_address or "",
            unsubscribe_link=_unsubscribe_link(lead.id, cfg),
        )
        subject = NO_DEMO_SUBJECT.format(business_name=lead.business_name or "")

        r = resend.Emails.send({
            "from": f"Travis <{cfg.contact_email}>",
            "to": lead.email,
            "subject": subject,
            "html": body.replace("\n", "<br>"),
        })

        if r and getattr(r, "id", None):
            session = get_session(cfg.database_url)
            log_entry = OutreachLog(
                lead_id=lead.id,
                channel="email",
                message_text=body[:500],
                sequence_number=1,
            )
            session.add(log_entry)
            lead_row = session.query(Lead).filter(Lead.id == lead.id).first()
            if lead_row:
                lead_row.email_sent_at = datetime.utcnow().isoformat()
                lead_row.status = "outreach_sent"
            session.commit()
            session.close()
            return True
    except Exception as e:
        log.error("No-demo email send failed for %s: %s", lead.business_name, e)
    return False


def _unsubscribe_link(lead_id: int, cfg: Config) -> str:
    """Generate unsubscribe URL. In production, wire to a handler that adds to suppressions."""
    return f"https://sitesmyth.com/unsubscribe?id={lead_id}"


def send_email(lead: Lead, sequence_number: int, cfg: Config) -> bool:
    """Send one email to lead. Returns True if sent. Checks suppression and dedup."""
    session = get_session(cfg.database_url)
    if is_suppressed(session, lead.id, lead.email, "email"):
        session.close()
        return False
    if has_been_sent(session, lead.id, "email", sequence_number):
        session.close()
        return False
    session.close()

    if not lead.email or not lead.site_url:
        return False

    try:
        import resend
        resend.api_key = cfg.resend_api_key

        greeting = "there"
        if lead.business_name:
            parts = lead.business_name.split()
            if len(parts) >= 2 and len(parts[0]) <= 10:
                greeting = parts[0]

        body = BODIES.get(sequence_number, BODIES[1]).format(
            greeting=greeting,
            business_name=lead.business_name or "",
            site_url=lead.site_url or "",
            physical_address=cfg.physical_address or "",
            unsubscribe_link=_unsubscribe_link(lead.id, cfg),
        )
        subject = SUBJECTS.get(sequence_number, SUBJECTS[1]).format(business_name=lead.business_name or "")

        r = resend.Emails.send({
            "from": f"Travis <{cfg.contact_email}>",
            "to": lead.email,
            "subject": subject,
            "html": body.replace("\n", "<br>"),
        })

        if r and getattr(r, "id", None):
            session = get_session(cfg.database_url)
            log_entry = OutreachLog(
                lead_id=lead.id,
                channel="email",
                message_text=body[:500],
                sequence_number=sequence_number,
            )
            session.add(log_entry)
            lead_row = session.query(Lead).filter(Lead.id == lead.id).first()
            if lead_row:
                lead_row.email_sent_at = datetime.utcnow().isoformat()
                lead_row.status = "outreach_sent"
            session.commit()
            session.close()
            return True
    except Exception as e:
        log.error("Email send failed for %s: %s", lead.business_name, e)
    return False
