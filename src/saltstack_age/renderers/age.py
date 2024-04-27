import os
from pathlib import Path
from salt.exceptions import SaltRenderError
import subprocess
import pexpect
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


def decrypt_with_passphrase(encrypted_value: str, passphrase: str) -> str:
    process = pexpect.spawn("age", ["-d"], encoding="ascii")
    process.send(encrypted_value)
    process.expect("Enter passphrase: ")
    process.send(f"{passphrase}\n")
    # XXX: WTF is that?
    process.expect("\r\r\n\x1b\\[F\x1b\\[K")
    return process.read()


def decrypt_with_identity(identity_file: str, encrypted_value: str) -> str:
    if not Path(identity_file).is_file():
        raise SaltRenderError(f"age_identity_file not found: {identity_file}")

    return subprocess.run(
        ["age", "-d", "-i", identity_file],
        input=encrypted_value.encode(),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode()


def _decrypt(encrypted_value: str) -> str:
    if "config.get" in __salt__:
        identity_file = __salt__["config.get"]("age_identity_file")
        if identity_file:
            return decrypt_with_identity(identity_file, encrypted_value)

    if "AGE_PASSPHRASE" in os.environ:
        passphrase = _get_passphrase_from_environment()
        return decrypt_with_passphrase(encrypted_value, passphrase)

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
