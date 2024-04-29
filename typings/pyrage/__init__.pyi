from pyrage import passphrase, x25519

__all__ = ["x25519", "passphrase"]


def decrypt(ciphertext: bytes, identities: list[x25519.Identity]) -> bytes: ...
