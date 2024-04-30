from types import ModuleType
from typing import Any, Callable

import pytest
from saltstack_age.renderers import age

from tests.unit.renderers import _test_identity


@pytest.fixture()
def config_get(example_age_key_str: str) -> Callable[[str], str]:
    def _config_get(key: str) -> str:
        assert key == "age_identity"
        return example_age_key_str

    return _config_get


@pytest.fixture()
def configure_loader_modules(config_get: Callable[[str], str]) -> dict[ModuleType, Any]:
    return {age: {"__salt__": {"config.get": config_get}}}


def test() -> None:
    _test_identity.test()
