from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.steganography_service import steganography_service
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_optional_user
from app.models.user import User
from typing import Optional
import json

router = APIRouter(prefix="/steganography", tags=["Steganography"])


@router.post("/hide")
async def hide_text(
    image: UploadFile = File(...),
    secret: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Hide secret text inside an image using LSB steganography."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
    result = steganography_service.hide_text(image_bytes, secret)
    if current_user:
        await auth_service.log_operation(db, current_user.id, "Steganography Hide", "steganography")
    return Response(content=result, media_type="image/png", headers={"Content-Disposition": "attachment; filename=stego_image.png"})


@router.post("/extract")
async def extract_text(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Extract hidden text from a steganographic image."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    image_bytes = await image.read()
    try:
        secret = steganography_service.extract_text(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if current_user:
        await auth_service.log_operation(db, current_user.id, "Steganography Extract", "steganography")
    return {"secret": secret}


@router.post("/capacity")
async def get_capacity(image: UploadFile = File(...)):
    """Get the steganographic capacity of an image."""
    image_bytes = await image.read()
    return steganography_service.get_capacity(image_bytes)
