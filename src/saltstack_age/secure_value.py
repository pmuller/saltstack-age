import re
from base64 import b64decode
from dataclasses import dataclass
from typing import Any

import pyrage

RE_SECURE_VALUE = re.compile(
    r"""
ENC\[
age-(?P<type>passphrase|identity)
,
(?P<base64CipherText>
    (?:[A-Za-z0-9+/]{4})*
    (?:
        [A-Za-z0-9+/]{2}==
        |
        [A-Za-z0-9+/]{3}=
    )?
)
\]
\s*
""",
    re.VERBOSE,
)


def is_secure_value(value: Any) -> bool:  # noqa: ANN401
    return bool(RE_SECURE_VALUE.match(value)) if isinstance(value, str) else False


@dataclass
class SecureValue:
    ciphertext: bytes


class PassphraseSecureValue(SecureValue):
    def decrypt(self, passphrase: str) -> str:
        return pyrage.passphrase.decrypt(self.ciphertext, passphrase).decode()


class IdentitySecureValue(SecureValue):
    def decrypt(self, identity: pyrage.x25519.Identity) -> str:
        return pyrage.decrypt(self.ciphertext, [identity]).decode()


def parse_secure_value(string: str) -> PassphraseSecureValue | IdentitySecureValue:
    match = RE_SECURE_VALUE.match(string)

    if not match:
        raise ValueError(f"Invalid secure value: {string}")

    type_, base64_ciphertext = match.groups()
    ciphertext = b64decode(base64_ciphertext)

    return (
        PassphraseSecureValue(ciphertext=ciphertext)
        if type_ == "passphrase"
        else IdentitySecureValue(ciphertext=ciphertext)
    )
