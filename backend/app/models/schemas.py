from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class CollectionCreate(BaseModel):
    name: str
    source_type: str
    config: dict = {}
    category: str = "general"
    poll_interval_minutes: int = 30


class CollectionOut(BaseModel):
    id: int
    name: str
    source_type: str
    config: dict
    category: str
    poll_interval_minutes: int
    is_active: bool
    last_fetched_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class IntelligenceOut(BaseModel):
    id: int
    title: str
    content: str
    url: Optional[str] = None
    source_name: str
    collection_id: Optional[int] = None
    category: str
    published_at: Optional[datetime] = None
    collected_at: datetime
    rating: Optional[int] = None
    rating_reason: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[list] = None
    potential_impact: Optional[str] = None
    is_analyzed: bool
    is_duplicate: bool

    model_config = {"from_attributes": True}


class AlertRuleCreate(BaseModel):
    name: str
    rule_type: str = "keyword"
    conditions: dict = {}
    channels: List[str] = []


class AlertRuleOut(BaseModel):
    id: int
    name: str
    rule_type: str
    conditions: dict
    channels: list
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertLogOut(BaseModel):
    id: int
    alert_rule_id: int
    intelligence_id: int
    message: str
    triggered_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}


class DailyBriefing(BaseModel):
    date: str
    total_count: int
    avg_rating: Optional[float] = None
    top_intelligences: List[IntelligenceOut]
    category_distribution: Dict[str, int]
    source_distribution: Dict[str, int]
    ai_summary: Optional[str] = None


class DashboardStats(BaseModel):
    total_intelligences: int
    today_new: int
    today_analyzed: int
    today_alerts: int
    avg_rating: Optional[float] = None
    category_distribution: Dict[str, int]
