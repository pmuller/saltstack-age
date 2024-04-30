from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
EXAMPLE_PATH = ROOT / "example"


@pytest.fixture()
def example_age_key() -> str:
    return str(EXAMPLE_PATH / "config" / "age.key")
