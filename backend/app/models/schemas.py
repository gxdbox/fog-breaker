from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str
    source_type: str
    config: dict = {}
    category: str = "general"
    profile_id: Optional[int] = None
    poll_interval_minutes: int = 30


class CollectionOut(BaseModel):
    id: int
    name: str
    source_type: str
    config: dict
    category: str
    profile_id: Optional[int] = None
    poll_interval_minutes: int
    is_active: bool
    last_fetched_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    analyzer_prompt: Optional[str] = None
    briefing_prompt: Optional[str] = None
    category_schema: Optional[List[dict]] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    analyzer_prompt: Optional[str] = None
    briefing_prompt: Optional[str] = None
    category_schema: Optional[List[dict]] = None
    is_active: Optional[bool] = None


class ProfileOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    analyzer_prompt: Optional[str] = None
    briefing_prompt: Optional[str] = None
    category_schema: Optional[list] = None
    is_active: bool
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class IntelligenceOut(BaseModel):
    id: int
    title: str
    content: str
    url: Optional[str] = None
    source_name: str
    collection_id: Optional[int] = None
    profile_id: Optional[int] = None
    category: str
    language: Optional[str] = None
    published_at: Optional[datetime] = None
    collected_at: datetime
    rating: Optional[int] = None
    rating_reason: Optional[str] = None
    summary: Optional[str] = None
    bullet_summary: Optional[list] = None
    plain_explanation: Optional[str] = None
    action_items: Optional[list] = None
    tags: Optional[list] = None
    potential_impact: Optional[str] = None
    is_analyzed: bool
    is_duplicate: bool
    preference: Optional[int] = None

    model_config = {"from_attributes": True}


class PreferenceUpdate(BaseModel):
    preference: Optional[int] = Field(default=None, ge=-1, le=1)


class AlertRuleCreate(BaseModel):
    name: str
    rule_type: str = "keyword"
    conditions: dict = {}
    channels: List[str] = []
    profile_id: Optional[int] = None


class AlertRuleOut(BaseModel):
    id: int
    name: str
    rule_type: str
    conditions: dict
    channels: list
    profile_id: Optional[int] = None
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
