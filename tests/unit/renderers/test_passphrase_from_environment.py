from types import ModuleType

import pytest

from saltstack_age.renderers import age
from tests.unit.renderers import _test_passphrase


def _config_get_none(_key: str) -> None:
    return None


@pytest.fixture
def configure_loader_modules() -> dict[ModuleType, object]:
    return {age: {"__salt__": {"config.get": _config_get_none}}}


def test(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGE_PASSPHRASE", "secret-passphrase")
    _test_passphrase.test()
