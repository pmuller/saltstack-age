from types import ModuleType
from typing import Any

import pytest
from saltstack_age.renderers import age

from tests.unit.renderers import _test_identity


@pytest.fixture()
def configure_loader_modules() -> dict[ModuleType, Any]:
    return {age: {"__salt__": {"config.get": lambda _key: None}}}


def test(monkeypatch: pytest.MonkeyPatch, age_identity_path: str) -> None:
    monkeypatch.setenv("AGE_IDENTITY_FILE", age_identity_path)
    _test_identity.test()
