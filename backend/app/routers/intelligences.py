from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Intelligence
from app.models.schemas import IntelligenceOut

router = APIRouter(prefix="/intelligences", tags=["intelligences"])


@router.get("/", response_model=list[IntelligenceOut])
def list_intelligences(
    category: Optional[str] = None,
    source_name: Optional[str] = None,
    min_rating: Optional[int] = None,
    is_analyzed: Optional[bool] = None,
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
    return q.order_by(Intelligence.collected_at.desc()).offset(skip).limit(limit).all()


@router.get("/{intelligence_id}", response_model=IntelligenceOut)
def get_intelligence(intelligence_id: int, db: Session = Depends(get_db)):
    obj = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    if not obj:
        raise HTTPException(404, "Intelligence not found")
    return obj


@router.get("/search/", response_model=list[IntelligenceOut])
def search_intelligences(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = db.query(Intelligence).filter(
        Intelligence.is_duplicate == False,
        (Intelligence.title.contains(q) | Intelligence.content.contains(q)),
    ).order_by(Intelligence.collected_at.desc()).offset(skip).limit(limit).all()
    return results
