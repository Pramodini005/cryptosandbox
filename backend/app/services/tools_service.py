import base64
import hashlib
import hmac
import json
import uuid
import secrets
from typing import Optional
from app.schemas.crypto import (
    Base64Request, Base64Response,
    HMACRequest, HMACResponse,
    JWTDecodeRequest, JWTDecodeResponse,
)


class ToolsService:
    def base64_convert(self, req: Base64Request) -> Base64Response:
        if req.action == "encode":
            result = base64.b64encode(req.data.encode("utf-8")).decode("utf-8")
        else:
            try:
                result = base64.b64decode(req.data.encode("utf-8")).decode("utf-8")
            except Exception as e:
                raise ValueError(f"Invalid base64 input: {e}")
        return Base64Response(result=result, action=req.action)

    def compute_hmac(self, req: HMACRequest) -> HMACResponse:
        algo_map = {"SHA-256": "sha256", "SHA-512": "sha512", "SHA3-256": "sha3_256"}
        algo = algo_map.get(req.algorithm, "sha256")
        h = hmac.new(req.key.encode(), req.message.encode(), algo).hexdigest()
        return HMACResponse(hmac=h, algorithm=req.algorithm)

    def decode_jwt(self, req: JWTDecodeRequest) -> JWTDecodeResponse:
        try:
            parts = req.token.split(".")
            if len(parts) != 3:
                return JWTDecodeResponse(header={}, payload={}, is_valid=False, error="Invalid JWT format")

            def decode_part(part: str) -> dict:
                padded = part + "==" * (4 - len(part) % 4)
                return json.loads(base64.urlsafe_b64decode(padded).decode())

            header = decode_part(parts[0])
            payload = decode_part(parts[1])
            return JWTDecodeResponse(header=header, payload=payload, is_valid=True)
        except Exception as e:
            return JWTDecodeResponse(header={}, payload={}, is_valid=False, error=str(e))

    def generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def generate_secure_random(self, length: int = 32) -> str:
        return secrets.token_hex(length)

    def hex_to_text(self, hex_str: str) -> str:
        return bytes.fromhex(hex_str).decode("utf-8", errors="replace")

    def text_to_hex(self, text: str) -> str:
        return text.encode("utf-8").hex()

    def text_to_binary(self, text: str) -> str:
        return " ".join(format(ord(c), "08b") for c in text)

    def compute_checksum(self, text: str, algorithm: str = "SHA-256") -> str:
        algo_map = {"MD5": "md5", "SHA-1": "sha1", "SHA-256": "sha256", "SHA-512": "sha512"}
        algo = algo_map.get(algorithm, "sha256")
        return hashlib.new(algo, text.encode()).hexdigest()


tools_service = ToolsService()
