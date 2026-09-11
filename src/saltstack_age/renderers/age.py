from collections import OrderedDict
from importlib import import_module
from pathlib import Path
from subprocess import PIPE, TimeoutExpired, run
from typing import cast

import pyrage
from salt.exceptions import SaltRenderError

from saltstack_age.identities import get_identity_from_environment, read_identity_file
from saltstack_age.passphrase import get_passphrase_from_environment
from saltstack_age.secure_value import (
    IdentitySecureValue,
    is_secure_value,
    parse_secure_value,
)

Data = OrderedDict[str, object]
IDENTITY_COMMAND_TIMEOUT_SECONDS = 10
IDENTITY_COMMAND_MAX_OUTPUT_BYTES = 16 * 1024
_CONFIG_MISSING = "__saltstack_age_missing_config__"

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


def _type_name(value: object) -> str:
    return type(value).__name__


def _normalize_identity_command(command: object) -> list[str] | None:
    if command is None:
        return None

    if not isinstance(command, list) or not command:
        raise SaltRenderError(
            "age_identity_command must be a non-empty list of strings"
        )

    normalized_command: list[str] = []
    for argument in cast("list[object]", command):
        if not isinstance(argument, str):
            raise SaltRenderError(
                "age_identity_command must be a non-empty list of strings "
                f"(got {_type_name(argument)} item)"
            )
        normalized_command.append(argument)

    return normalized_command


def _get_identity_from_command(command: list[str]) -> pyrage.x25519.Identity:
    try:
        process = run(
            command,
            stdout=PIPE,
            timeout=IDENTITY_COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as error:
        raise SaltRenderError(
            f"age_identity_command executable not found: {command[0]}"
        ) from error
    except PermissionError as error:
        raise SaltRenderError(
            f"age_identity_command executable is not allowed: {command[0]}"
        ) from error
    except TimeoutExpired as error:
        raise SaltRenderError("age_identity_command timed out") from error
    except OSError as error:
        raise SaltRenderError(
            f"age_identity_command failed to start: {error}"
        ) from error

    if process.returncode != 0:
        raise SaltRenderError(
            f"age_identity_command failed with exit code {process.returncode}"
        )

    if len(process.stdout) > IDENTITY_COMMAND_MAX_OUTPUT_BYTES:
        raise SaltRenderError("age_identity_command output is too large")

    return pyrage.x25519.Identity.from_str(process.stdout.decode().strip())


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

    config_option = __salt__.get("config.option", __salt__["config.get"])
    identity_command_config = config_option(
        "age_identity_command",
        _CONFIG_MISSING,
    )
    identity_command = _normalize_identity_command(
        None if identity_command_config == _CONFIG_MISSING else identity_command_config
    )
    if identity_command:
        return _get_identity_from_command(identity_command)

    raise SaltRenderError("No age identity found in config or environment")


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


def _render_value(value: object) -> object:
    if is_secure_value(value):
        return _decrypt(cast("str", value))
    if isinstance(value, OrderedDict):
        return render(cast("Data", value))
    if isinstance(value, list):
        items = cast("list[object]", value)
        return [_render_value(item) for item in items]
    return value


def render(
    data: Data,
    _saltenv: str = "base",
    _sls: str = "",
    **_kwargs: None,
) -> Data:
    return OrderedDict((key, _render_value(value)) for key, value in data.items())
