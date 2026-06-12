from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Collection
from app.models.schemas import CollectionCreate, CollectionOut

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/", response_model=list[CollectionOut])
def list_collections(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Collection)
    if profile_id is not None:
        q = q.filter(Collection.profile_id == profile_id)
    return q.order_by(Collection.created_at.desc()).all()


@router.post("/", response_model=CollectionOut)
def create_collection(data: CollectionCreate, db: Session = Depends(get_db)):
    obj = Collection(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{collection_id}", response_model=CollectionOut)
def get_collection(collection_id: int, db: Session = Depends(get_db)):
    obj = db.query(Collection).filter(Collection.id == collection_id).first()
    if not obj:
        raise HTTPException(404, "Collection not found")
    return obj


@router.patch("/{collection_id}/toggle", response_model=CollectionOut)
def toggle_collection(collection_id: int, db: Session = Depends(get_db)):
    obj = db.query(Collection).filter(Collection.id == collection_id).first()
    if not obj:
        raise HTTPException(404, "Collection not found")
    obj.is_active = not obj.is_active
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{collection_id}")
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    obj = db.query(Collection).filter(Collection.id == collection_id).first()
    if not obj:
        raise HTTPException(404, "Collection not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
