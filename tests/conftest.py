from pathlib import Path

import pyrage
import pytest
from saltstack_age.identities import read_identity_file

ROOT = Path(__file__).parent.parent
EXAMPLE_PATH = ROOT / "example"


@pytest.fixture()
def example_age_key_path() -> Path:
    return EXAMPLE_PATH / "config" / "age.key"


@pytest.fixture()
def example_age_key_path_str(example_age_key_path: Path) -> str:
    return str(example_age_key_path)


@pytest.fixture()
def example_age_key(example_age_key_path: Path) -> pyrage.x25519.Identity:
    return read_identity_file(example_age_key_path)


@pytest.fixture()
def example_age_key_str(example_age_key: pyrage.x25519.Identity) -> str:
    return str(example_age_key)
