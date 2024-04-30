import re
from base64 import b64decode
from dataclasses import dataclass
from pathlib import Path

import pyrage

from saltstack_age.identities import read_identity_file

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


def is_secure_value(string: str) -> bool:
    return bool(RE_SECURE_VALUE.match(string))


@dataclass
class SecureValue:
    ciphertext: bytes


class PassphraseSecureValue(SecureValue):
    def decrypt(self, passphrase: str) -> str:
        return pyrage.passphrase.decrypt(self.ciphertext, passphrase).decode()


class IdentitySecureValue(SecureValue):
    def decrypt(self, identity: Path | str) -> str:
        if isinstance(identity, str):
            identity = Path(identity)
        if not identity.is_file():
            raise FileNotFoundError(f"Identity file does not exist: {identity}")
        return pyrage.decrypt(self.ciphertext, [read_identity_file(identity)]).decode()


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
