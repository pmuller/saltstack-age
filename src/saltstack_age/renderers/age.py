import os
import re
from base64 import b64decode
from collections import OrderedDict
from pathlib import Path
from typing import Any

import pyrage
from salt.exceptions import SaltRenderError

Data = OrderedDict[str, Any]


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


def _decrypt_with_identity(ciphertext: bytes) -> str:
    identity_file: str | None = __salt__["config.get"]("age_identity_file")

    if not identity_file:
        raise SaltRenderError("age_identity_file is not defined")

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


def _decrypt(secure_value: str) -> str:
    match = RE_SECURE_VALUE.match(secure_value)

    if not match:
        # Should _never_ happen as we match against the regex in render()
        raise SaltRenderError(f"Invalid age secure value: {secure_value}")

    type_, base64_ciphertext = match.groups()
    ciphertext = b64decode(base64_ciphertext)

    if type_ == "identity":
        if "config.get" in __salt__:
            return _decrypt_with_identity(ciphertext)

        # Not sure how/when that happens...
        raise RuntimeError('__salt__["config.get"] is not available')

    if type_ == "passphrase":
        if "AGE_PASSPHRASE" in os.environ:
            return pyrage.passphrase.decrypt(
                ciphertext,
                os.environ["AGE_PASSPHRASE"],
            ).decode()

        raise SaltRenderError("The AGE_PASSPHRASE environment variable is not defined")

    # This can only happen if we change the regex without updating this function
    raise SaltRenderError(f"Invalid age encryption type: {type_}")


def render(
    data: Data,
    _saltenv: str = "base",
    _sls: str = "",
    **_kwargs: None,
) -> Data:
    return OrderedDict(
        (key, _decrypt(value) if RE_SECURE_VALUE.match(value) else value)
        for key, value in data.items()
    )
