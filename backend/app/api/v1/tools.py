from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.crypto import Base64Request, Base64Response, HMACRequest, HMACResponse, JWTDecodeRequest, JWTDecodeResponse
from app.services.tools_service import tools_service
from pydantic import BaseModel
from typing import Literal

router = APIRouter(prefix="/tools", tags=["Security Tools"])


@router.post("/base64", response_model=Base64Response)
async def base64_convert(req: Base64Request):
    """Encode or decode data using Base64."""
    return tools_service.base64_convert(req)


@router.post("/hmac", response_model=HMACResponse)
async def compute_hmac(req: HMACRequest):
    """Compute HMAC using SHA-256, SHA-512, or SHA3-256."""
    return tools_service.compute_hmac(req)


@router.post("/jwt-decode", response_model=JWTDecodeResponse)
async def jwt_decode(req: JWTDecodeRequest):
    """Decode and inspect a JWT token (does not verify signature)."""
    return tools_service.decode_jwt(req)


class UUIDResponse(BaseModel):
    uuid: str


@router.get("/uuid", response_model=UUIDResponse)
async def generate_uuid():
    """Generate a cryptographically secure UUID v4."""
    return UUIDResponse(uuid=tools_service.generate_uuid())


class RandomResponse(BaseModel):
    random_hex: str
    length: int


class ConvertRequest(BaseModel):
    text: str
    to: Literal["hex", "binary", "from_hex"]


class ConvertResponse(BaseModel):
    result: str


@router.get("/random/{length}", response_model=RandomResponse)
async def generate_random(length: int = 32):
    """Generate cryptographically secure random bytes as hex."""
    if length > 256: length = 256
    random_hex = tools_service.generate_secure_random(length)
    return RandomResponse(random_hex=random_hex, length=length)


@router.post("/convert", response_model=ConvertResponse)
async def convert_text(req: ConvertRequest):
    """Convert text to hex, binary, or decode from hex."""
    if req.to == "hex":
        result = tools_service.text_to_hex(req.text)
    elif req.to == "binary":
        result = tools_service.text_to_binary(req.text)
    elif req.to == "from_hex":
        result = tools_service.hex_to_text(req.text)
    else:
        result = req.text
    return ConvertResponse(result=result)
