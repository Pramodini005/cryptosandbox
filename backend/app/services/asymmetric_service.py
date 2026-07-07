import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, padding as asym_padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key as rsa_gen
from cryptography.hazmat.primitives.asymmetric.ec import generate_private_key as ec_gen, ECDSA, SECP256R1, SECP384R1, SECP521R1
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.schemas.crypto import (
    AsymmetricKeyGenRequest, AsymmetricKeyGenResponse,
    AsymmetricEncryptRequest, AsymmetricEncryptResponse,
    AsymmetricDecryptRequest, AsymmetricDecryptResponse,
    SignRequest, SignResponse, VerifyRequest, VerifyResponse,
)


CURVE_MAP = {"P-256": SECP256R1(), "P-384": SECP384R1(), "P-521": SECP521R1()}


class AsymmetricService:
    def generate_keys(self, req: AsymmetricKeyGenRequest) -> AsymmetricKeyGenResponse:
        if req.algorithm == "RSA":
            private_key = rsa_gen(
                public_exponent=65537,
                key_size=req.key_size,
                backend=default_backend(),
            )
        elif req.algorithm == "ECC":
            curve = CURVE_MAP.get(req.curve, SECP256R1())
            private_key = ec_gen(curve, backend=default_backend())
        elif req.algorithm == "Ed25519":
            private_key = Ed25519PrivateKey.generate()
        else:
            raise ValueError(f"Unsupported algorithm: {req.algorithm}")

        private_pem = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        public_pem = private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

        pub_der = private_key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        fingerprint = hashlib.sha256(pub_der).hexdigest()

        return AsymmetricKeyGenResponse(
            public_key=public_pem,
            private_key=private_pem,
            algorithm=req.algorithm,
            fingerprint=fingerprint,
        )

    def encrypt(self, req: AsymmetricEncryptRequest) -> AsymmetricEncryptResponse:
        public_key = serialization.load_pem_public_key(req.public_key.encode())
        ciphertext = public_key.encrypt(
            req.plaintext.encode(),
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return AsymmetricEncryptResponse(ciphertext=base64.b64encode(ciphertext).decode())

    def decrypt(self, req: AsymmetricDecryptRequest) -> AsymmetricDecryptResponse:
        private_key = serialization.load_pem_private_key(req.private_key.encode(), password=None)
        ciphertext = base64.b64decode(req.ciphertext)
        plaintext = private_key.decrypt(
            ciphertext,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return AsymmetricDecryptResponse(plaintext=plaintext.decode())

    def sign(self, req: SignRequest) -> SignResponse:
        private_key = serialization.load_pem_private_key(req.private_key.encode(), password=None)
        message = req.message.encode()
        if req.algorithm == "RSA":
            signature = private_key.sign(
                message,
                asym_padding.PSS(mgf=asym_padding.MGF1(hashes.SHA256()), salt_length=asym_padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
        elif req.algorithm == "ECC":
            signature = private_key.sign(message, ECDSA(hashes.SHA256()))
        elif req.algorithm == "Ed25519":
            signature = private_key.sign(message)
        else:
            raise ValueError(f"Unsupported algorithm: {req.algorithm}")
        return SignResponse(signature=base64.b64encode(signature).decode(), algorithm=req.algorithm)

    def verify(self, req: VerifyRequest) -> VerifyResponse:
        try:
            public_key = serialization.load_pem_public_key(req.public_key.encode())
            message = req.message.encode()
            signature = base64.b64decode(req.signature)
            if req.algorithm == "RSA":
                public_key.verify(
                    signature, message,
                    asym_padding.PSS(mgf=asym_padding.MGF1(hashes.SHA256()), salt_length=asym_padding.PSS.MAX_LENGTH),
                    hashes.SHA256(),
                )
            elif req.algorithm == "ECC":
                public_key.verify(signature, message, ECDSA(hashes.SHA256()))
            elif req.algorithm == "Ed25519":
                public_key.verify(signature, message)
            return VerifyResponse(valid=True, message="Signature is valid")
        except Exception as e:
            return VerifyResponse(valid=False, message=f"Signature verification failed: {str(e)}")


asymmetric_service = AsymmetricService()
