import os
import re
from pathlib import Path

import pyrage


def read_identity_file(path: Path | str) -> pyrage.x25519.Identity:
    if isinstance(path, str):
        path = Path(path)

    # Remove comments
    identity_string = re.sub(
        r"^#.*\n?",
        "",
        path.read_text(),
        flags=re.MULTILINE,
    ).rstrip("\n")

    return pyrage.x25519.Identity.from_str(identity_string)


def get_identity_file_from_environment() -> pyrage.x25519.Identity | None:
    path_string = os.environ.get("AGE_IDENTITY_FILE")

    if path_string is None:
        return None

    path = Path(path_string)

    if not path.is_file():
        raise FileNotFoundError(f"AGE_IDENTITY_FILE does not exist: {path}")

    return read_identity_file(path)


def get_identity_string_from_environment() -> pyrage.x25519.Identity | None:
    identity_string = os.environ.get("AGE_IDENTITY")

    if identity_string is None:
        return None

    return pyrage.x25519.Identity.from_str(identity_string.strip())


def get_identity_from_environment() -> pyrage.x25519.Identity | None:
    return (
        get_identity_string_from_environment() or get_identity_file_from_environment()
    )
