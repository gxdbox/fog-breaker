from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Profile
from app.models.schemas import ProfileCreate, ProfileOut, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/", response_model=list[ProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(Profile).order_by(Profile.is_default.desc(), Profile.id.asc()).all()


@router.post("/", response_model=ProfileOut)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    if db.query(Profile).filter(Profile.name == data.name).first():
        raise HTTPException(400, "Profile name already exists")
    obj = Profile(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    obj = db.query(Profile).filter(Profile.id == profile_id).first()
    if not obj:
        raise HTTPException(404, "Profile not found")
    return obj


@router.patch("/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    obj = db.query(Profile).filter(Profile.id == profile_id).first()
    if not obj:
        raise HTTPException(404, "Profile not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    obj = db.query(Profile).filter(Profile.id == profile_id).first()
    if not obj:
        raise HTTPException(404, "Profile not found")
    if obj.is_default:
        raise HTTPException(400, "Default profile cannot be deleted")
    db.delete(obj)
    db.commit()
    return {"ok": True}
