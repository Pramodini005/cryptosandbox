import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import padding
from app.schemas.crypto import (
    SymmetricEncryptRequest, SymmetricEncryptResponse,
    SymmetricDecryptRequest, SymmetricDecryptResponse,
)


class SymmetricService:
    def encrypt(self, req: SymmetricEncryptRequest) -> SymmetricEncryptResponse:
        plaintext_bytes = req.plaintext.encode("utf-8")
        key_size_bytes = req.key_size // 8

        if req.algorithm == "AES-GCM":
            return self._aes_gcm_encrypt(plaintext_bytes, req.key, key_size_bytes)
        elif req.algorithm == "AES-CBC":
            return self._aes_cbc_encrypt(plaintext_bytes, req.key, key_size_bytes)
        elif req.algorithm == "AES-CTR":
            return self._aes_ctr_encrypt(plaintext_bytes, req.key, key_size_bytes)
        elif req.algorithm == "ChaCha20":
            return self._chacha20_encrypt(plaintext_bytes, req.key)
        elif req.algorithm == "Fernet":
            return self._fernet_encrypt(plaintext_bytes, req.key)
        else:
            raise ValueError(f"Unsupported algorithm: {req.algorithm}")

    def decrypt(self, req: SymmetricDecryptRequest) -> SymmetricDecryptResponse:
        if req.algorithm == "AES-GCM":
            return self._aes_gcm_decrypt(req.ciphertext, req.key, req.iv)
        elif req.algorithm == "AES-CBC":
            return self._aes_cbc_decrypt(req.ciphertext, req.key, req.iv)
        elif req.algorithm == "AES-CTR":
            return self._aes_ctr_decrypt(req.ciphertext, req.key, req.iv)
        elif req.algorithm == "ChaCha20":
            return self._chacha20_decrypt(req.ciphertext, req.key)
        elif req.algorithm == "Fernet":
            return self._fernet_decrypt(req.ciphertext, req.key)
        else:
            raise ValueError(f"Unsupported algorithm: {req.algorithm}")

    def _aes_gcm_encrypt(self, plaintext: bytes, key_hex: str | None, key_size: int) -> SymmetricEncryptResponse:
        key = bytes.fromhex(key_hex) if key_hex else os.urandom(key_size)
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ct = aesgcm.encrypt(nonce, plaintext, None)
        combined = nonce + ct
        return SymmetricEncryptResponse(
            ciphertext=base64.b64encode(combined).decode(),
            ciphertext_hex=combined.hex(),
            ciphertext_base64=base64.b64encode(combined).decode(),
            key=key.hex(),
            iv=nonce.hex(),
            algorithm="AES-GCM",
            key_size=len(key) * 8,
        )

    def _aes_gcm_decrypt(self, ciphertext_b64: str, key_hex: str, iv_hex: str | None) -> SymmetricDecryptResponse:
        combined = base64.b64decode(ciphertext_b64)
        nonce = combined[:12]
        ct = combined[12:]
        key = bytes.fromhex(key_hex)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ct, None)
        return SymmetricDecryptResponse(plaintext=plaintext.decode("utf-8"), algorithm="AES-GCM")

    def _aes_cbc_encrypt(self, plaintext: bytes, key_hex: str | None, key_size: int) -> SymmetricEncryptResponse:
        key = bytes.fromhex(key_hex) if key_hex else os.urandom(key_size)
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded) + encryptor.finalize()
        combined = iv + ct
        return SymmetricEncryptResponse(
            ciphertext=base64.b64encode(combined).decode(),
            ciphertext_hex=combined.hex(),
            ciphertext_base64=base64.b64encode(combined).decode(),
            key=key.hex(),
            iv=iv.hex(),
            algorithm="AES-CBC",
            key_size=len(key) * 8,
        )

    def _aes_cbc_decrypt(self, ciphertext_b64: str, key_hex: str, iv_hex: str | None) -> SymmetricDecryptResponse:
        combined = base64.b64decode(ciphertext_b64)
        iv = combined[:16]
        ct = combined[16:]
        key = bytes.fromhex(key_hex)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ct) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()
        return SymmetricDecryptResponse(plaintext=plaintext.decode("utf-8"), algorithm="AES-CBC")

    def _aes_ctr_encrypt(self, plaintext: bytes, key_hex: str | None, key_size: int) -> SymmetricEncryptResponse:
        key = bytes.fromhex(key_hex) if key_hex else os.urandom(key_size)
        nonce = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(plaintext) + encryptor.finalize()
        combined = nonce + ct
        return SymmetricEncryptResponse(
            ciphertext=base64.b64encode(combined).decode(),
            ciphertext_hex=combined.hex(),
            ciphertext_base64=base64.b64encode(combined).decode(),
            key=key.hex(),
            iv=nonce.hex(),
            algorithm="AES-CTR",
            key_size=len(key) * 8,
        )

    def _aes_ctr_decrypt(self, ciphertext_b64: str, key_hex: str, iv_hex: str | None) -> SymmetricDecryptResponse:
        combined = base64.b64decode(ciphertext_b64)
        nonce = combined[:16]
        ct = combined[16:]
        key = bytes.fromhex(key_hex)
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ct) + decryptor.finalize()
        return SymmetricDecryptResponse(plaintext=plaintext.decode("utf-8"), algorithm="AES-CTR")

    def _chacha20_encrypt(self, plaintext: bytes, key_hex: str | None) -> SymmetricEncryptResponse:
        key = bytes.fromhex(key_hex) if key_hex else os.urandom(32)
        nonce = os.urandom(12)
        chacha = ChaCha20Poly1305(key)
        ct = chacha.encrypt(nonce, plaintext, None)
        combined = nonce + ct
        return SymmetricEncryptResponse(
            ciphertext=base64.b64encode(combined).decode(),
            ciphertext_hex=combined.hex(),
            ciphertext_base64=base64.b64encode(combined).decode(),
            key=key.hex(),
            iv=nonce.hex(),
            algorithm="ChaCha20",
            key_size=256,
        )

    def _chacha20_decrypt(self, ciphertext_b64: str, key_hex: str) -> SymmetricDecryptResponse:
        combined = base64.b64decode(ciphertext_b64)
        nonce = combined[:12]
        ct = combined[12:]
        key = bytes.fromhex(key_hex)
        chacha = ChaCha20Poly1305(key)
        plaintext = chacha.decrypt(nonce, ct, None)
        return SymmetricDecryptResponse(plaintext=plaintext.decode("utf-8"), algorithm="ChaCha20")

    def _fernet_encrypt(self, plaintext: bytes, key_b64: str | None) -> SymmetricEncryptResponse:
        if key_b64:
            fkey = key_b64.encode()
        else:
            fkey = Fernet.generate_key()
        f = Fernet(fkey)
        token = f.encrypt(plaintext)
        return SymmetricEncryptResponse(
            ciphertext=token.decode(),
            ciphertext_hex=token.hex(),
            ciphertext_base64=token.decode(),
            key=fkey.decode(),
            iv=None,
            algorithm="Fernet",
            key_size=256,
        )

    def _fernet_decrypt(self, token: str, key_b64: str) -> SymmetricDecryptResponse:
        f = Fernet(key_b64.encode())
        plaintext = f.decrypt(token.encode())
        return SymmetricDecryptResponse(plaintext=plaintext.decode("utf-8"), algorithm="Fernet")


symmetric_service = SymmetricService()
