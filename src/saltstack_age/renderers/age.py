import os
import re
from base64 import b64decode
from collections import OrderedDict
from pathlib import Path
from typing import Any

import pyrage
import pyrage.passphrase
import pyrage.x25519
from salt.exceptions import SaltRenderError

Data = OrderedDict[str, Any]


def _is_encrypted_value(value: str) -> bool:
    return value.startswith("-----BEGIN AGE ENCRYPTED FILE-----")


def decrypt_with_passphrase(ciphertext: bytes, passphrase: str) -> str:
    return pyrage.passphrase.decrypt(ciphertext, passphrase).decode()


def decrypt_with_identity(ciphertext: bytes, identity_file: str) -> str:
    identity_path = Path(identity_file)

    if not identity_path.is_file():
        raise SaltRenderError(f"age_identity_file not found: {identity_file}")

    identity_string = re.sub(
        r"^#.*\n?",
        "",
        identity_path.read_text(),
        flags=re.MULTILINE,
    ).rstrip("\n")
    identity = pyrage.x25519.Identity.from_str(identity_string)

    return pyrage.decrypt(ciphertext, [identity]).decode()


def _decrypt(encrypted_string: str) -> str:
    ciphertext = b64decode(encrypted_string)

    if "config.get" in __salt__:
        identity_file: str | None = __salt__["config.get"]("age_identity_file")
        if identity_file:
            return decrypt_with_identity(ciphertext, identity_file)

    if "AGE_PASSPHRASE" in os.environ:
        return decrypt_with_passphrase(ciphertext, os.environ["AGE_PASSPHRASE"])

    raise SaltRenderError("No age identity file or passphrase configured")


def render(
    data: Data,
    _saltenv: str = "base",
    _sls: str = "",
    **_kwargs: None,
) -> Data:
    return OrderedDict(
        (key, _decrypt(value) if _is_encrypted_value(value) else value)
        for key, value in data.items()
    )
