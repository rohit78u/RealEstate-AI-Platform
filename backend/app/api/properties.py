import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import Property, PropertyImage, User
from app.schemas import PropertyCreate, PropertyListResponse, PropertyResponse, PropertyUpdate
from app.services.property_service import create_property, delete_property, get_properties, update_property
from app.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("", response_model=PropertyListResponse)
def list_properties(
    city: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    bathrooms: int | None = None,
    min_area: float | None = None,
    sort: str = Query("created_desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_properties(
        db,
        city=city,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        min_area=min_area,
        sort=sort,
        page=page,
        limit=limit,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = (
        db.query(Property)
        .options(joinedload(Property.images))
        .filter(Property.id == property_id)
        .first()
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def add_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return create_property(db, data, admin)


@router.put("/{property_id}", response_model=PropertyResponse)
def edit_property(
    property_id: int,
    data: PropertyUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return update_property(db, prop, data)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_property(
    property_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    delete_property(db, prop)


@router.post("/{property_id}/images", response_model=PropertyResponse)
async def upload_images(
    property_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    prop = (
        db.query(Property)
        .options(joinedload(Property.images))
        .filter(Property.id == property_id)
        .first()
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    upload_dir = Path(settings.upload_dir) / str(property_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    for i, file in enumerate(files):
        ext = Path(file.filename or "image.jpg").suffix or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = upload_dir / filename

        async with aiofiles.open(filepath, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        image = PropertyImage(
            property_id=property_id,
            image_path=f"/uploads/{property_id}/{filename}",
            is_primary=(len(prop.images) == 0 and i == 0),
        )
        db.add(image)

    db.commit()
    db.refresh(prop)
    return prop
