from cryptography.hazmat.primitives.asymmetric.dh import generate_parameters, DHParameterNumbers, DHPublicNumbers, DHPrivateNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os
import hashlib
from app.schemas.crypto import DHKeyExchangeRequest, DHKeyExchangeResponse


class KeyExchangeService:
    def diffie_hellman(self, req: DHKeyExchangeRequest) -> DHKeyExchangeResponse:
        # Use small safe primes for demonstration (512 bits for speed)
        parameters = generate_parameters(generator=2, key_size=req.bits, backend=default_backend())
        pn = parameters.parameter_numbers()

        alice_priv = parameters.generate_private_key()
        bob_priv = parameters.generate_private_key()

        alice_pub = alice_priv.public_key()
        bob_pub = bob_priv.public_key()

        alice_shared = alice_priv.exchange(bob_pub)
        bob_shared = bob_priv.exchange(alice_pub)

        alice_shared_hex = hashlib.sha256(alice_shared).hexdigest()
        bob_shared_hex = hashlib.sha256(bob_shared).hexdigest()

        alice_pub_num = alice_pub.public_numbers()
        bob_pub_num = bob_pub.public_numbers()
        alice_priv_num = alice_priv.private_numbers()
        bob_priv_num = bob_priv.private_numbers()

        return DHKeyExchangeResponse(
            p=hex(pn.p),
            g=hex(pn.g),
            alice_private=hex(alice_priv_num.x),
            alice_public=hex(alice_pub_num.y),
            bob_private=hex(bob_priv_num.x),
            bob_public=hex(bob_pub_num.y),
            alice_shared_secret=alice_shared_hex,
            bob_shared_secret=bob_shared_hex,
            secrets_match=alice_shared_hex == bob_shared_hex,
        )


key_exchange_service = KeyExchangeService()
