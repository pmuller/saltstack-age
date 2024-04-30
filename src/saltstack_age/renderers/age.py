from collections import OrderedDict
from importlib import import_module
from pathlib import Path
from typing import Any, cast

import pyrage
from salt.exceptions import SaltRenderError

from saltstack_age.identities import get_identity_from_environment, read_identity_file
from saltstack_age.passphrase import get_passphrase_from_environment
from saltstack_age.secure_value import (
    IdentitySecureValue,
    is_secure_value,
    parse_secure_value,
)

Data = OrderedDict[str, Any]

__virtualname__ = "age"


def __virtual__() -> str | tuple[bool, str]:  # noqa: N807
    if "config.get" not in __salt__:
        # Not sure how/when that happens?
        return (False, '"config.get" is not available')

    try:
        _ = import_module("pyrage")
    except ModuleNotFoundError:
        return (False, "pyrage is not installed")

    return __virtualname__


def _get_identity() -> pyrage.x25519.Identity:
    # Try to get identity string from Salt configuration
    identity_string: str | None = __salt__["config.get"]("age_identity")
    if identity_string:
        return pyrage.x25519.Identity.from_str(identity_string.strip())

    # Try to get identity file from Salt configuration
    identity_file_string: str | None = __salt__["config.get"]("age_identity_file")
    if identity_file_string:
        identity_file_path = Path(identity_file_string)

        if not identity_file_path.is_file():
            raise SaltRenderError(
                f"age_identity file does not exist: {identity_file_string}"
            )

        return read_identity_file(identity_file_path)

    # Try to get identity from the environment
    identity = get_identity_from_environment()
    if identity:
        return identity

    raise SaltRenderError("No age identity file found in config or environment")


def _get_passphrase() -> str:
    passphrase: str | None = (
        __salt__["config.get"]("age_passphrase") or get_passphrase_from_environment()
    )

    if passphrase is None:
        raise SaltRenderError("No age passphrase found in config or environment")

    return passphrase


def _decrypt(string: str) -> str:
    secure_value = parse_secure_value(string)

    if isinstance(secure_value, IdentitySecureValue):
        return secure_value.decrypt(_get_identity())

    return secure_value.decrypt(_get_passphrase())


def _render_value(value: Any) -> Any:  # noqa: ANN401
    if is_secure_value(value):
        return _decrypt(value)
    if isinstance(value, OrderedDict):
        return render(cast(Data, value))
    return value


def render(
    data: Data,
    _saltenv: str = "base",
    _sls: str = "",
    **_kwargs: None,
) -> Data:
    return OrderedDict((key, _render_value(value)) for key, value in data.items())
