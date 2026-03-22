"""SQLAlchemy ORM models for SiteSmyth."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    type_annotation_map = {
        dict[str, Any]: Text,  # JSON stored as text for SQLite
    }


class Lead(Base):
    """A local business lead without a website, discovered via Google Maps."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_maps_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    facebook_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    facebook_active: Mapped[bool] = mapped_column(Boolean, default=False)
    facebook_last_post_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    facebook_page_likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    instagram_handle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instagram_active: Mapped[bool] = mapped_column(Boolean, default=False)
    instagram_followers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    instagram_last_post_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    primary_social: Mapped[str | None] = mapped_column(String(20), nullable=True)  # facebook, instagram, both
    has_website: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[str] = mapped_column(String(30), default="discovered", nullable=False, index=True)
    site_generated_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    site_url: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. cincy-fence-co.sitesmyth.com

    email_sent_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email_opened_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sms_sent_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dm_sent_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    replied_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    converted_at: Mapped[str | None] = mapped_column(String(30), nullable=True)

    deal_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_recurring: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())
    updated_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())

    scraped_content: Mapped[list[ScrapedContent]] = relationship("ScrapedContent", back_populates="lead")
    outreach_logs: Mapped[list[OutreachLog]] = relationship("OutreachLog", back_populates="lead")
    suppressions: Mapped[list[Suppression]] = relationship("Suppression", back_populates="lead")


class ScrapedContent(Base):
    """Scraped content from Facebook, Instagram, or Google Maps."""

    __tablename__ = "scraped_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # facebook, instagram, google_maps
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # bio, post_caption, image, review
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # logo, product, storefront, team, general
    scraped_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())

    lead: Mapped[Lead] = relationship("Lead", back_populates="scraped_content")


class OutreachLog(Base):
    """Log of outreach sent to leads. UNIQUE prevents duplicate sends."""

    __tablename__ = "outreach_log"
    __table_args__ = (
        UniqueConstraint("lead_id", "channel", "sequence_number", name="uq_outreach_lead_channel_seq"),
        Index("idx_outreach_lead_channel", "lead_id", "channel"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), nullable=False)  # email, sms, instagram_dm
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())
    delivered: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    opened: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    opened_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    replied: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    replied_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    bounced: Mapped[bool] = mapped_column(Boolean, default=False)
    sequence_number: Mapped[int] = mapped_column(Integer, default=1)  # 1=initial, 2=followup1, 3=followup2

    lead: Mapped[Lead] = relationship("Lead", back_populates="outreach_logs")


class Suppression(Base):
    """Unsubscribes, bounces, complaints — never send to these again."""

    __tablename__ = "suppressions"
    __table_args__ = (
        Index("idx_suppressions_email", "email"),
        Index("idx_suppressions_lead", "lead_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("leads.id"), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reason: Mapped[str] = mapped_column(String(30), nullable=False)  # unsubscribe, bounce, complaint, manual
    channel: Mapped[str | None] = mapped_column(String(30), nullable=True)  # email, sms, instagram_dm, or NULL = all
    created_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())

    lead: Mapped[Lead | None] = relationship("Lead", back_populates="suppressions")


class SiteAnalytics(Base):
    """Analytics per hosted demo site."""

    __tablename__ = "site_analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id"), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    page_views: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    cta_clicks: Mapped[int] = mapped_column(Integer, default=0)
    last_viewed_at: Mapped[str | None] = mapped_column(String(30), nullable=True)


class Run(Base):
    """Pipeline run tracking."""

    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())
    finished_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    params: Mapped[str] = mapped_column(Text, default="{}")  # JSON
    stats: Mapped[str] = mapped_column(Text, default="{}")  # JSON
