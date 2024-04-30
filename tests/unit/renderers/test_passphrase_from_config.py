from types import ModuleType
from typing import Any

import pytest
from saltstack_age.renderers import age

from tests.unit.renderers import _test_passphrase


def _config_get(key: str) -> str:
    assert key == "age_passphrase"
    return "secret-passphrase"


@pytest.fixture()
def configure_loader_modules() -> dict[ModuleType, Any]:
    return {age: {"__salt__": {"config.get": _config_get}}}


def test() -> None:
    _test_passphrase.test()
