import secrets
import string
import math
import hashlib
import os
import bcrypt
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.schemas.crypto import (
    PasswordAnalyzeRequest, PasswordAnalyzeResponse,
    PasswordHashRequest, PasswordHashResponse,
    PasswordVerifyRequest, PasswordVerifyResponse,
    PasswordGenerateRequest, PasswordGenerateResponse,
)

ph = PasswordHasher()

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
    "letmein", "trustno1", "dragon", "baseball", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "passw0rd", "shadow", "123123", "654321", "superman",
    "qazwsx", "michael", "football", "password1", "password123",
}

WORDLIST = [
    "correct", "horse", "battery", "staple", "apple", "river", "mountain",
    "cloud", "sunset", "guitar", "ocean", "thunder", "forest", "castle",
    "silver", "dragon", "shadow", "winter", "summer", "spring", "falcon",
    "phoenix", "tiger", "eagle", "storm", "crystal", "flame", "arrow",
]


class PasswordService:
    def analyze(self, req: PasswordAnalyzeRequest) -> PasswordAnalyzeResponse:
        pw = req.password
        has_upper = bool(re.search(r'[A-Z]', pw))
        has_lower = bool(re.search(r'[a-z]', pw))
        has_digit = bool(re.search(r'\d', pw))
        has_symbol = bool(re.search(r'[^a-zA-Z0-9]', pw))
        is_common = pw.lower() in COMMON_PASSWORDS

        # Calculate character space
        char_space = 0
        if has_lower: char_space += 26
        if has_upper: char_space += 26
        if has_digit: char_space += 10
        if has_symbol: char_space += 32
        if char_space == 0: char_space = 26

        entropy = len(pw) * math.log2(char_space)

        # Crack time estimation (assuming 1 trillion guesses/sec)
        guesses_per_second = 1e12
        possible_combos = char_space ** len(pw)
        seconds = possible_combos / guesses_per_second
        crack_time = self._format_time(seconds)

        # Score
        score = 0
        if len(pw) >= 8: score += 10
        if len(pw) >= 12: score += 15
        if len(pw) >= 16: score += 15
        if has_upper: score += 15
        if has_lower: score += 10
        if has_digit: score += 15
        if has_symbol: score += 20
        if is_common: score = min(score, 10)
        score = min(score, 100)

        if score < 20: strength = "Very Weak"
        elif score < 40: strength = "Weak"
        elif score < 60: strength = "Fair"
        elif score < 80: strength = "Good"
        elif score < 90: strength = "Strong"
        else: strength = "Very Strong"

        suggestions = []
        if len(pw) < 12: suggestions.append("Use at least 12 characters")
        if not has_upper: suggestions.append("Add uppercase letters")
        if not has_lower: suggestions.append("Add lowercase letters")
        if not has_digit: suggestions.append("Add numbers")
        if not has_symbol: suggestions.append("Add special characters")
        if is_common: suggestions.append("This is a commonly used password — change it!")

        return PasswordAnalyzeResponse(
            score=score, strength=strength, entropy_bits=round(entropy, 2),
            estimated_crack_time=crack_time, suggestions=suggestions,
            has_uppercase=has_upper, has_lowercase=has_lower,
            has_digits=has_digit, has_symbols=has_symbol,
            length=len(pw), is_common=is_common,
        )

    def _format_time(self, seconds: float) -> str:
        if seconds < 1: return "Instantly"
        if seconds < 60: return f"{seconds:.0f} seconds"
        if seconds < 3600: return f"{seconds / 60:.0f} minutes"
        if seconds < 86400: return f"{seconds / 3600:.0f} hours"
        if seconds < 31536000: return f"{seconds / 86400:.0f} days"
        if seconds < 3.15e10: return f"{seconds / 31536000:.0f} years"
        if seconds < 3.15e13: return f"{seconds / 3.15e10:.0f} thousand years"
        if seconds < 3.15e16: return f"{seconds / 3.15e13:.0f} million years"
        return "Billions of years"

    def hash_password(self, req: PasswordHashRequest) -> PasswordHashResponse:
        if req.algorithm == "bcrypt":
            rounds = req.cost or 12
            hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt(rounds=rounds)).decode()
            return PasswordHashResponse(hash=hashed, algorithm="bcrypt", params={"rounds": rounds})
        elif req.algorithm == "argon2":
            hashed = ph.hash(req.password)
            return PasswordHashResponse(hash=hashed, algorithm="argon2", params={"time_cost": 2, "memory_cost": 65536})
        elif req.algorithm == "pbkdf2":
            salt = os.urandom(16)
            dk = hashlib.pbkdf2_hmac("sha256", req.password.encode(), salt, 260000)
            result = salt.hex() + ":" + dk.hex()
            return PasswordHashResponse(hash=result, algorithm="pbkdf2", params={"iterations": 260000, "hash": "sha256"})
        elif req.algorithm == "scrypt":
            salt = os.urandom(16)
            dk = hashlib.scrypt(req.password.encode(), salt=salt, n=16384, r=8, p=1)
            result = salt.hex() + ":" + dk.hex()
            return PasswordHashResponse(hash=result, algorithm="scrypt", params={"n": 16384, "r": 8, "p": 1})
        raise ValueError(f"Unsupported algorithm: {req.algorithm}")

    def verify_password(self, req: PasswordVerifyRequest) -> PasswordVerifyResponse:
        try:
            if req.algorithm == "bcrypt":
                valid = bcrypt.checkpw(req.password.encode(), req.hash.encode())
                return PasswordVerifyResponse(valid=valid)
            elif req.algorithm == "argon2":
                try:
                    ph.verify(req.hash, req.password)
                    return PasswordVerifyResponse(valid=True)
                except VerifyMismatchError:
                    return PasswordVerifyResponse(valid=False)
            elif req.algorithm in ("pbkdf2", "scrypt"):
                parts = req.hash.split(":")
                if len(parts) != 2: return PasswordVerifyResponse(valid=False)
                salt = bytes.fromhex(parts[0])
                stored_dk = parts[1]
                if req.algorithm == "pbkdf2":
                    dk = hashlib.pbkdf2_hmac("sha256", req.password.encode(), salt, 260000).hex()
                else:
                    dk = hashlib.scrypt(req.password.encode(), salt=salt, n=16384, r=8, p=1).hex()
                return PasswordVerifyResponse(valid=secrets.compare_digest(dk, stored_dk))
        except Exception:
            return PasswordVerifyResponse(valid=False)

    def generate(self, req: PasswordGenerateRequest) -> PasswordGenerateResponse:
        if req.passphrase:
            words = [secrets.choice(WORDLIST) for _ in range(req.word_count)]
            password = "-".join(words)
        else:
            chars = ""
            if req.use_lowercase: chars += string.ascii_lowercase
            if req.use_uppercase: chars += string.ascii_uppercase
            if req.use_digits: chars += string.digits
            if req.use_symbols: chars += string.punctuation
            if req.exclude_ambiguous:
                chars = "".join(c for c in chars if c not in "0OlI1")
            if not chars: chars = string.ascii_letters + string.digits
            password = "".join(secrets.choice(chars) for _ in range(req.length))

        analyze_result = self.analyze(__import__("app.schemas.crypto", fromlist=["PasswordAnalyzeRequest"]).PasswordAnalyzeRequest(password=password))
        return PasswordGenerateResponse(
            password=password,
            strength=analyze_result.strength,
            entropy_bits=analyze_result.entropy_bits,
        )


password_service = PasswordService()
