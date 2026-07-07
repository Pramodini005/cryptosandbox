import hashlib
from app.schemas.crypto import HashRequest, HashResponse, HashCompareRequest, HashCompareResponse

ALGO_MAP = {
    "MD5": "md5",
    "SHA-1": "sha1",
    "SHA-224": "sha224",
    "SHA-256": "sha256",
    "SHA-384": "sha384",
    "SHA-512": "sha512",
    "SHA3-256": "sha3_256",
    "SHA3-512": "sha3_512",
    "BLAKE2b": "blake2b",
    "BLAKE2s": "blake2s",
}


class HashService:
    def compute(self, req: HashRequest) -> HashResponse:
        algo = ALGO_MAP.get(req.algorithm)
        if not algo:
            raise ValueError(f"Unsupported algorithm: {req.algorithm}")
        h = hashlib.new(algo, req.text.encode("utf-8")).hexdigest()
        binary = bin(int(h, 16))[2:].zfill(len(h) * 4)
        return HashResponse(
            hash=h,
            algorithm=req.algorithm,
            length=len(h) * 4,
            hex=h,
            binary=binary[:64] + "...",
        )

    def compare(self, req: HashCompareRequest) -> HashCompareResponse:
        results = {}
        for alg in req.algorithms:
            algo = ALGO_MAP.get(alg)
            if not algo:
                continue
            h = hashlib.new(algo, req.text.encode("utf-8")).hexdigest()
            results[alg] = {
                "hash": h,
                "length_bits": len(h) * 4,
                "length_hex": len(h),
            }
        return HashCompareResponse(results=results)


hash_service = HashService()
