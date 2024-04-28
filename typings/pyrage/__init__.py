from pyrage import x25519, passphrase


def decrypt(ciphertext: bytes, identities: list[x25519.Identity]) -> bytes: ...
