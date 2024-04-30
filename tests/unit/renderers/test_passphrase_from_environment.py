from types import ModuleType
from typing import Any

import pytest
from saltstack_age.renderers import age

from tests.unit.renderers import _test_passphrase


@pytest.fixture()
def configure_loader_modules() -> dict[ModuleType, Any]:
    return {age: {"__salt__": {"config.get": lambda _key: None}}}


def test(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGE_PASSPHRASE", "secret-passphrase")
    _test_passphrase.test()
