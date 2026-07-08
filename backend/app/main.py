from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1 import auth, symmetric, asymmetric, hashing, passwords, classical, steganography, key_exchange, tools, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Cryptography Learning Sandbox API...")
    await create_tables()
    logger.info("Database tables created/verified.")
    yield
    logger.info("Shutting down API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# Cryptography Learning Sandbox & Cybersecurity Toolkit

A production-grade, enterprise-quality Cryptography & Cybersecurity Learning Sandbox.

## Features

- **Symmetric Cryptography**: AES-GCM, AES-CBC, AES-CTR, ChaCha20, Fernet
- **Asymmetric Cryptography**: RSA, ECC, Ed25519 key generation, encryption, signatures
- **Hashing**: MD5, SHA family, SHA-3, BLAKE2
- **Password Security**: bcrypt, Argon2, PBKDF2, Scrypt + strength analysis
- **Classical Ciphers**: Caesar, Vigenère, Playfair, Rail Fence, OTP, Columnar
- **Steganography**: LSB image steganography (hide/extract)
- **Key Exchange**: Diffie-Hellman simulation
- **Security Tools**: JWT decoder, Base64, HMAC, UUID, Hex/Binary converter
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


# Routers
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(symmetric.router, prefix=API_PREFIX)
app.include_router(asymmetric.router, prefix=API_PREFIX)
app.include_router(hashing.router, prefix=API_PREFIX)
app.include_router(passwords.router, prefix=API_PREFIX)
app.include_router(classical.router, prefix=API_PREFIX)
app.include_router(steganography.router, prefix=API_PREFIX)
app.include_router(key_exchange.router, prefix=API_PREFIX)
app.include_router(tools.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
