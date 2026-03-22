"""Reusable database query functions."""

from __future__ import annotations

from sqlalchemy.orm import Session

from sitesmyth.db.models import Lead, OutreachLog, Suppression


def get_sendable_leads(
    session: Session,
    channel: str,
    sequence_number: int = 1,
    limit: int | None = None,
) -> list[Lead]:
    """Return hosted leads that have NOT been sent this sequence on this channel
    AND are NOT suppressed. email_sender also checks is_suppressed(lead_id, email) before sending.
    """
    already_sent_subq = (
        session.query(OutreachLog.lead_id)
        .filter_by(channel=channel, sequence_number=sequence_number)
    )
    suppressed_lead_ids = session.query(Suppression.lead_id).filter(
        Suppression.lead_id.isnot(None),
        (Suppression.channel == channel) | (Suppression.channel.is_(None)),
    )
    query = (
        session.query(Lead)
        .filter(
            Lead.status.in_(["hosted", "outreach_sent"]),
            Lead.id.notin_(already_sent_subq),
            Lead.id.notin_(suppressed_lead_ids),
        )
        .order_by(Lead.id)
    )
    if limit is not None:
        query = query.limit(limit)
    return list(query.all())


def is_suppressed(session: Session, lead_id: int | None, email: str | None, channel: str) -> bool:
    """Check if this lead or email is suppressed for the given channel."""
    q = session.query(Suppression).filter(
        (Suppression.channel == channel) | (Suppression.channel.is_(None))
    )
    if lead_id is not None:
        q = q.filter(Suppression.lead_id == lead_id)
    if email:
        q = q.filter(Suppression.email == email)
    return q.first() is not None


def has_been_sent(session: Session, lead_id: int, channel: str, sequence_number: int) -> bool:
    """Check if we've already sent this sequence to this lead on this channel."""
    return (
        session.query(OutreachLog.id)
        .filter_by(lead_id=lead_id, channel=channel, sequence_number=sequence_number)
        .first()
        is not None
    )


def add_suppression(
    session: Session,
    *,
    lead_id: int | None = None,
    email: str | None = None,
    phone: str | None = None,
    reason: str,
    channel: str | None = None,
) -> Suppression:
    """Add a suppression record. Caller must commit."""
    supp = Suppression(
        lead_id=lead_id,
        email=email,
        phone=phone,
        reason=reason,
        channel=channel,
    )
    session.add(supp)
    return supp
