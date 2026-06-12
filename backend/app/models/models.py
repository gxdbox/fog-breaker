from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SourceType(str, enum.Enum):
    RSS = "rss"
    HACKERNEWS = "hackernews"
    WEIBO = "weibo"


class CategoryType(str, enum.Enum):
    TECH = "tech"
    BUSINESS = "business"
    POLICY = "policy"
    SOCIAL = "social"
    GENERAL = "general"


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    analyzer_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    briefing_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_schema: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    collections: Mapped[List["Collection"]] = relationship(back_populates="profile")
    intelligences: Mapped[List["Intelligence"]] = relationship(back_populates="profile")
    alert_rules: Mapped[List["AlertRule"]] = relationship(back_populates="profile")


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    category: Mapped[str] = mapped_column(String(50), default=CategoryType.GENERAL)
    profile_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=True)
    poll_interval_minutes: Mapped[int] = mapped_column(Integer, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    profile: Mapped[Optional["Profile"]] = relationship(back_populates="collections")
    intelligences: Mapped[List["Intelligence"]] = relationship(back_populates="collection")


class Intelligence(Base):
    __tablename__ = "intelligences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    collection_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("collections.id"), nullable=True)
    profile_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default=CategoryType.GENERAL)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rating_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bullet_summary: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    plain_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_items: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    potential_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    preference: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    collection: Mapped[Optional["Collection"]] = relationship(back_populates="intelligences")
    profile: Mapped[Optional["Profile"]] = relationship(back_populates="intelligences")
    alerts: Mapped[List["AlertLog"]] = relationship(back_populates="intelligence")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), default="keyword")
    conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    channels: Mapped[list] = mapped_column(JSON, default=list)
    profile_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    profile: Mapped[Optional["Profile"]] = relationship(back_populates="alert_rules")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    intelligence_id: Mapped[int] = mapped_column(Integer, ForeignKey("intelligences.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    intelligence: Mapped["Intelligence"] = relationship(back_populates="alerts")
