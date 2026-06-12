from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Intelligence
from app.models.schemas import IntelligenceOut, PreferenceUpdate

router = APIRouter(prefix="/intelligences", tags=["intelligences"])


def _preference_score(
    item: Intelligence,
    liked_categories: set[str],
    disliked_categories: set[str],
    liked_sources: set[str],
    disliked_sources: set[str],
    liked_tags: set[str],
    disliked_tags: set[str],
) -> int:
    score = item.rating or 0
    if item.preference == 1:
        score += 100
    elif item.preference == -1:
        score -= 100
    if item.category in liked_categories:
        score += 8
    if item.category in disliked_categories:
        score -= 8
    if item.source_name in liked_sources:
        score += 5
    if item.source_name in disliked_sources:
        score -= 5
    tags = set(item.tags or [])
    score += len(tags & liked_tags) * 3
    score -= len(tags & disliked_tags) * 3
    return score


@router.get("/", response_model=list[IntelligenceOut])
def list_intelligences(
    category: Optional[str] = None,
    source_name: Optional[str] = None,
    min_rating: Optional[int] = None,
    is_analyzed: Optional[bool] = None,
    profile_id: Optional[int] = None,
    personalized: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Intelligence).filter(Intelligence.is_duplicate == False)
    if category:
        q = q.filter(Intelligence.category == category)
    if source_name:
        q = q.filter(Intelligence.source_name == source_name)
    if min_rating:
        q = q.filter(Intelligence.rating >= min_rating)
    if is_analyzed is not None:
        q = q.filter(Intelligence.is_analyzed == is_analyzed)
    if profile_id is not None:
        q = q.filter(Intelligence.profile_id == profile_id)
    if personalized:
        liked_q = db.query(Intelligence).filter(Intelligence.preference == 1)
        disliked_q = db.query(Intelligence).filter(Intelligence.preference == -1)
        if profile_id is not None:
            liked_q = liked_q.filter(Intelligence.profile_id == profile_id)
            disliked_q = disliked_q.filter(Intelligence.profile_id == profile_id)
        liked = liked_q.all()
        disliked = disliked_q.all()
        liked_categories = {i.category for i in liked if i.category}
        disliked_categories = {i.category for i in disliked if i.category}
        liked_sources = {i.source_name for i in liked if i.source_name}
        disliked_sources = {i.source_name for i in disliked if i.source_name}
        liked_tags = {tag for i in liked for tag in (i.tags or [])}
        disliked_tags = {tag for i in disliked for tag in (i.tags or [])}
        items = q.order_by(Intelligence.collected_at.desc()).offset(skip).limit(limit * 3).all()
        ranked = sorted(
            items,
            key=lambda item: _preference_score(
                item,
                liked_categories,
                disliked_categories,
                liked_sources,
                disliked_sources,
                liked_tags,
                disliked_tags,
            ),
            reverse=True,
        )
        return ranked[:limit]
    return q.order_by(Intelligence.collected_at.desc()).offset(skip).limit(limit).all()


@router.get("/search", response_model=list[IntelligenceOut])
def search_intelligences(
    q: str = Query(..., min_length=1),
    profile_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Intelligence).filter(
        Intelligence.is_duplicate == False,
        (Intelligence.title.contains(q) | Intelligence.content.contains(q)),
    )
    if profile_id is not None:
        query = query.filter(Intelligence.profile_id == profile_id)
    return query.order_by(Intelligence.collected_at.desc()).offset(skip).limit(limit).all()


@router.patch("/{intelligence_id}/preference", response_model=IntelligenceOut)
def update_preference(intelligence_id: int, data: PreferenceUpdate, db: Session = Depends(get_db)):
    obj = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    if not obj:
        raise HTTPException(404, "Intelligence not found")
    obj.preference = data.preference if data.preference in (-1, 1) else None
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{intelligence_id}", response_model=IntelligenceOut)
def get_intelligence(intelligence_id: int, db: Session = Depends(get_db)):
    obj = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    if not obj:
        raise HTTPException(404, "Intelligence not found")
    return obj
