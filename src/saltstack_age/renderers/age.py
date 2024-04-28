from base64 import b64decode
import pyrage
import os
from pathlib import Path
from salt.exceptions import SaltRenderError
import collections
import typing


Data = typing.OrderedDict[str, typing.Any]


def _is_encrypted_value(value: str) -> bool:
    return value.startswith("-----BEGIN AGE ENCRYPTED FILE-----")


def _get_passphrase_from_environment() -> str:
    passphrase = os.environ.get("AGE_PASSPHRASE")

    if not passphrase:
        raise RuntimeError("AGE_PASSPHRASE is not defined")

    return passphrase


def decrypt_with_passphrase(ciphertext: bytes, passphrase: str) -> str:
    return pyrage.passphrase.decrypt(ciphertext, passphrase).decode()


def decrypt_with_identity(ciphertext: bytes, identity_file: str) -> str:
    identity_path = Path(identity_file)

    if not identity_path.is_file():
        raise SaltRenderError(f"age_identity_file not found: {identity_file}")

    identity = pyrage.x25519.Identity.from_str(identity_path.read_text())

    return pyrage.decrypt(ciphertext, [identity]).decode()


def _decrypt(encrypted_string: str) -> str:
    ciphertext = b64decode(encrypted_string)

    if "config.get" in __salt__:
        identity_file = __salt__["config.get"]("age_identity_file")
        if identity_file:
            return decrypt_with_identity(ciphertext, identity_file)

    if "AGE_PASSPHRASE" in os.environ:
        passphrase = _get_passphrase_from_environment()
        return decrypt_with_passphrase(ciphertext, passphrase)

    raise SaltRenderError("No age identity file or passphrase configured")


def render(
    data: Data,
    _saltenv: str = "base",
    _sls: str = "",
    **_kwargs: None,
) -> Data:
    return collections.OrderedDict(
        (key, _decrypt(value) if _is_encrypted_value(value) else value)
        for key, value in data.items()
    )
