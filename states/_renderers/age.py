import os
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


def _decrypt(encrypted_value: str) -> str:
    passphrase = _get_passphrase_from_environment()
    process = pexpect.spawn("age", ["-d"], encoding="ascii")
    process.send(encrypted_value)
    process.expect("Enter passphrase: ")
    process.send(f"{passphrase}\n")
    # XXX: WTF is that?
    process.expect("\r\r\n\x1b\\[F\x1b\\[K")
    return process.read()


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
