from pydantic import BaseModel, Field
from typing import Optional, Literal


# Symmetric
class SymmetricEncryptRequest(BaseModel):
    plaintext: str = Field(..., max_length=100000)
    algorithm: Literal["AES-GCM", "AES-CBC", "AES-CTR", "ChaCha20", "Fernet"] = "AES-GCM"
    key: Optional[str] = None  # hex string; if None, auto-generate
    key_size: Literal[128, 192, 256] = 256


class SymmetricEncryptResponse(BaseModel):
    ciphertext: str
    ciphertext_hex: str
    ciphertext_base64: str
    key: str  # hex
    iv: Optional[str] = None
    algorithm: str
    key_size: int


class SymmetricDecryptRequest(BaseModel):
    ciphertext: str
    algorithm: Literal["AES-GCM", "AES-CBC", "AES-CTR", "ChaCha20", "Fernet"]
    key: str
    iv: Optional[str] = None


class SymmetricDecryptResponse(BaseModel):
    plaintext: str
    algorithm: str


# Asymmetric
class AsymmetricKeyGenRequest(BaseModel):
    algorithm: Literal["RSA", "ECC", "Ed25519"] = "RSA"
    key_size: Literal[1024, 2048, 4096] = 2048
    curve: Literal["P-256", "P-384", "P-521"] = "P-256"


class AsymmetricKeyGenResponse(BaseModel):
    public_key: str  # PEM
    private_key: str  # PEM
    algorithm: str
    fingerprint: str


class AsymmetricEncryptRequest(BaseModel):
    plaintext: str = Field(..., max_length=10000)
    public_key: str


class AsymmetricEncryptResponse(BaseModel):
    ciphertext: str  # base64


class AsymmetricDecryptRequest(BaseModel):
    ciphertext: str  # base64
    private_key: str


class AsymmetricDecryptResponse(BaseModel):
    plaintext: str


class SignRequest(BaseModel):
    message: str = Field(..., max_length=100000)
    private_key: str
    algorithm: Literal["RSA", "ECC", "Ed25519"] = "RSA"


class SignResponse(BaseModel):
    signature: str  # base64
    algorithm: str


class VerifyRequest(BaseModel):
    message: str
    signature: str  # base64
    public_key: str
    algorithm: Literal["RSA", "ECC", "Ed25519"] = "RSA"


class VerifyResponse(BaseModel):
    valid: bool
    message: str


# Hashing
class HashRequest(BaseModel):
    text: str = Field(..., max_length=100000)
    algorithm: Literal["MD5", "SHA-1", "SHA-224", "SHA-256", "SHA-384", "SHA-512", "SHA3-256", "SHA3-512", "BLAKE2b", "BLAKE2s"] = "SHA-256"


class HashResponse(BaseModel):
    hash: str
    algorithm: str
    length: int
    hex: str
    binary: str


class HashCompareRequest(BaseModel):
    text: str
    algorithms: list[str] = ["MD5", "SHA-256", "SHA-512", "BLAKE2b"]


class HashCompareResponse(BaseModel):
    results: dict[str, dict]


# Password
class PasswordAnalyzeRequest(BaseModel):
    password: str = Field(..., max_length=1000)


class PasswordAnalyzeResponse(BaseModel):
    score: int  # 0-100
    strength: str  # Weak/Fair/Good/Strong/Very Strong
    entropy_bits: float
    estimated_crack_time: str
    suggestions: list[str]
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_symbols: bool
    length: int
    is_common: bool


class PasswordHashRequest(BaseModel):
    password: str = Field(..., max_length=1000)
    algorithm: Literal["bcrypt", "argon2", "pbkdf2", "scrypt"] = "bcrypt"
    cost: Optional[int] = 12  # bcrypt rounds / argon2 time cost


class PasswordHashResponse(BaseModel):
    hash: str
    algorithm: str
    params: dict


class PasswordVerifyRequest(BaseModel):
    password: str
    hash: str
    algorithm: Literal["bcrypt", "argon2", "pbkdf2", "scrypt"]


class PasswordVerifyResponse(BaseModel):
    valid: bool


class PasswordGenerateRequest(BaseModel):
    length: int = Field(16, ge=8, le=256)
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = False
    passphrase: bool = False
    word_count: int = Field(4, ge=3, le=10)


class PasswordGenerateResponse(BaseModel):
    password: str
    strength: str
    entropy_bits: float


# Classical
class ClassicalEncryptRequest(BaseModel):
    plaintext: str = Field(..., max_length=10000)
    algorithm: Literal["Caesar", "Vigenere", "OTP", "RailFence", "Playfair", "Columnar"] = "Caesar"
    key: Optional[str] = None
    shift: Optional[int] = None
    rails: Optional[int] = None


class ClassicalEncryptResponse(BaseModel):
    ciphertext: str
    algorithm: str
    key: Optional[str] = None
    steps: list[str] = []


class ClassicalDecryptRequest(BaseModel):
    ciphertext: str = Field(..., max_length=10000)
    algorithm: Literal["Caesar", "Vigenere", "OTP", "RailFence", "Playfair", "Columnar"]
    key: Optional[str] = None
    shift: Optional[int] = None
    rails: Optional[int] = None


class ClassicalDecryptResponse(BaseModel):
    plaintext: str
    algorithm: str


# Key Exchange
class DHKeyExchangeRequest(BaseModel):
    bits: Literal[512, 1024, 2048] = 512


class DHKeyExchangeResponse(BaseModel):
    p: str  # prime hex
    g: str  # generator hex
    alice_private: str
    alice_public: str
    bob_private: str
    bob_public: str
    alice_shared_secret: str
    bob_shared_secret: str
    secrets_match: bool


# Tools
class Base64Request(BaseModel):
    data: str = Field(..., max_length=100000)
    action: Literal["encode", "decode"]


class Base64Response(BaseModel):
    result: str
    action: str


class HMACRequest(BaseModel):
    message: str = Field(..., max_length=100000)
    key: str
    algorithm: Literal["SHA-256", "SHA-512", "SHA3-256"] = "SHA-256"


class HMACResponse(BaseModel):
    hmac: str
    algorithm: str


class JWTDecodeRequest(BaseModel):
    token: str


class JWTDecodeResponse(BaseModel):
    header: dict
    payload: dict
    is_valid: bool
    error: Optional[str] = None
