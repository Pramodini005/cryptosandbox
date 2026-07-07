import re
import os
from app.schemas.crypto import (
    ClassicalEncryptRequest, ClassicalEncryptResponse,
    ClassicalDecryptRequest, ClassicalDecryptResponse,
)


class ClassicalService:
    def encrypt(self, req: ClassicalEncryptRequest) -> ClassicalEncryptResponse:
        if req.algorithm == "Caesar":
            shift = req.shift or 3
            ct, steps = self._caesar(req.plaintext, shift)
            return ClassicalEncryptResponse(ciphertext=ct, algorithm="Caesar", key=str(shift), steps=steps)
        elif req.algorithm == "Vigenere":
            key = req.key or "KEY"
            ct, steps = self._vigenere_encrypt(req.plaintext, key)
            return ClassicalEncryptResponse(ciphertext=ct, algorithm="Vigenere", key=key, steps=steps)
        elif req.algorithm == "OTP":
            ct, key_used = self._otp_encrypt(req.plaintext)
            return ClassicalEncryptResponse(ciphertext=ct, algorithm="OTP", key=key_used, steps=["Random key XORed with plaintext"])
        elif req.algorithm == "RailFence":
            rails = req.rails or 3
            ct = self._rail_fence_encrypt(req.plaintext, rails)
            return ClassicalEncryptResponse(ciphertext=ct, algorithm="RailFence", key=str(rails), steps=[f"Text arranged across {rails} rails"])
        elif req.algorithm == "Playfair":
            key = req.key or "PLAYFAIR"
            ct = self._playfair_encrypt(req.plaintext, key)
            return ClassicalEncryptResponse(ciphertext=ct, algorithm="Playfair", key=key, steps=[])
        elif req.algorithm == "Columnar":
            key = req.key or "CRYPTO"
            ct = self._columnar_encrypt(req.plaintext, key)
            return ClassicalEncryptResponse(ciphertext=ct, algorithm="Columnar", key=key, steps=["Text written row-by-row, read column-by-column based on key order"])
        raise ValueError(f"Unsupported: {req.algorithm}")

    def decrypt(self, req: ClassicalDecryptRequest) -> ClassicalDecryptResponse:
        if req.algorithm == "Caesar":
            shift = req.shift or 3
            pt, _ = self._caesar(req.ciphertext, -shift)
            return ClassicalDecryptResponse(plaintext=pt, algorithm="Caesar")
        elif req.algorithm == "Vigenere":
            key = req.key or "KEY"
            pt = self._vigenere_decrypt(req.ciphertext, key)
            return ClassicalDecryptResponse(plaintext=pt, algorithm="Vigenere")
        elif req.algorithm == "OTP":
            key = req.key or ""
            pt = self._otp_decrypt(req.ciphertext, key)
            return ClassicalDecryptResponse(plaintext=pt, algorithm="OTP")
        elif req.algorithm == "RailFence":
            rails = req.rails or 3
            pt = self._rail_fence_decrypt(req.ciphertext, rails)
            return ClassicalDecryptResponse(plaintext=pt, algorithm="RailFence")
        elif req.algorithm == "Playfair":
            key = req.key or "PLAYFAIR"
            pt = self._playfair_decrypt(req.ciphertext, key)
            return ClassicalDecryptResponse(plaintext=pt, algorithm="Playfair")
        elif req.algorithm == "Columnar":
            key = req.key or "CRYPTO"
            pt = self._columnar_decrypt(req.ciphertext, key)
            return ClassicalDecryptResponse(plaintext=pt, algorithm="Columnar")
        raise ValueError(f"Unsupported: {req.algorithm}")

    def _caesar(self, text: str, shift: int):
        result = []
        steps = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                new_char = chr((ord(char) - base + shift) % 26 + base)
                steps.append(f"{char} -> {new_char} (shift {shift})")
                result.append(new_char)
            else:
                result.append(char)
        return "".join(result), steps[:10]

    def _vigenere_encrypt(self, text: str, key: str):
        key = key.upper()
        result = []
        steps = []
        ki = 0
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(key[ki % len(key)]) - ord('A')
                new_char = chr((ord(char) - base + shift) % 26 + base)
                steps.append(f"{char} + key[{key[ki % len(key)]}] -> {new_char}")
                result.append(new_char)
                ki += 1
            else:
                result.append(char)
        return "".join(result), steps[:10]

    def _vigenere_decrypt(self, text: str, key: str) -> str:
        key = key.upper()
        result = []
        ki = 0
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(key[ki % len(key)]) - ord('A')
                new_char = chr((ord(char) - base - shift) % 26 + base)
                result.append(new_char)
                ki += 1
            else:
                result.append(char)
        return "".join(result)

    def _otp_encrypt(self, text: str):
        text_bytes = text.encode('utf-8')
        key_bytes = os.urandom(len(text_bytes))
        ct_bytes = bytes(a ^ b for a, b in zip(text_bytes, key_bytes))
        return ct_bytes.hex(), key_bytes.hex()

    def _otp_decrypt(self, ct_hex: str, key_hex: str) -> str:
        try:
            ct_bytes = bytes.fromhex(ct_hex)
            key_bytes = bytes.fromhex(key_hex)
            pt_bytes = bytes(a ^ b for a, b in zip(ct_bytes, key_bytes))
            return pt_bytes.decode('utf-8', errors='replace')
        except Exception:
            return "[Decryption error - check key]"

    def _rail_fence_encrypt(self, text: str, rails: int) -> str:
        fence = [[] for _ in range(rails)]
        rail, step = 0, 1
        for char in text:
            fence[rail].append(char)
            if rail == 0: step = 1
            elif rail == rails - 1: step = -1
            rail += step
        return "".join("".join(r) for r in fence)

    def _rail_fence_decrypt(self, text: str, rails: int) -> str:
        n = len(text)
        pattern = []
        rail, step = 0, 1
        for i in range(n):
            pattern.append(rail)
            if rail == 0: step = 1
            elif rail == rails - 1: step = -1
            rail += step
        indices = sorted(range(n), key=lambda i: (pattern[i], i))
        result = [''] * n
        for i, ch in zip(indices, text):
            result[i] = ch
        return "".join(result)

    def _make_playfair_matrix(self, key: str):
        key = re.sub(r'[^A-Za-z]', '', key.upper()).replace('J', 'I')
        seen = set()
        chars = []
        for c in key + 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
            if c not in seen:
                seen.add(c)
                chars.append(c)
        return [chars[i*5:(i+1)*5] for i in range(5)]

    def _playfair_pos(self, matrix, char):
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                if val == char: return r, c
        return 0, 0

    def _playfair_encrypt(self, text: str, key: str) -> str:
        matrix = self._make_playfair_matrix(key)
        text = re.sub(r'[^A-Za-z]', '', text.upper()).replace('J', 'I')
        pairs = []
        i = 0
        while i < len(text):
            a = text[i]
            b = text[i+1] if i+1 < len(text) else 'X'
            if a == b: b = 'X'
            else: i += 1
            pairs.append((a, b))
            i += 1
        result = []
        for a, b in pairs:
            r1, c1 = self._playfair_pos(matrix, a)
            r2, c2 = self._playfair_pos(matrix, b)
            if r1 == r2: result += [matrix[r1][(c1+1)%5], matrix[r2][(c2+1)%5]]
            elif c1 == c2: result += [matrix[(r1+1)%5][c1], matrix[(r2+1)%5][c2]]
            else: result += [matrix[r1][c2], matrix[r2][c1]]
        return "".join(result)

    def _playfair_decrypt(self, text: str, key: str) -> str:
        matrix = self._make_playfair_matrix(key)
        text = re.sub(r'[^A-Za-z]', '', text.upper())
        pairs = [(text[i], text[i+1]) for i in range(0, len(text)-1, 2)]
        result = []
        for a, b in pairs:
            r1, c1 = self._playfair_pos(matrix, a)
            r2, c2 = self._playfair_pos(matrix, b)
            if r1 == r2: result += [matrix[r1][(c1-1)%5], matrix[r2][(c2-1)%5]]
            elif c1 == c2: result += [matrix[(r1-1)%5][c1], matrix[(r2-1)%5][c2]]
            else: result += [matrix[r1][c2], matrix[r2][c1]]
        return "".join(result)

    def _columnar_encrypt(self, text: str, key: str) -> str:
        key = key.upper()
        n = len(key)
        text = text.replace(' ', '_')
        padded = text + 'X' * (-len(text) % n)
        rows = [padded[i:i+n] for i in range(0, len(padded), n)]
        order = sorted(range(n), key=lambda i: key[i])
        return "".join("".join(row[i] for row in rows) for i in order)

    def _columnar_decrypt(self, text: str, key: str) -> str:
        key = key.upper()
        n = len(key)
        nrows = len(text) // n
        order = sorted(range(n), key=lambda i: key[i])
        cols = {}
        idx = 0
        for col in order:
            cols[col] = list(text[idx:idx+nrows])
            idx += nrows
        result = []
        for r in range(nrows):
            for c in range(n):
                result.append(cols[c][r])
        return "".join(result).replace('_', ' ').rstrip('X')


classical_service = ClassicalService()
