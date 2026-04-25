import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

from saltstack_age.renderers import age
from tests.unit.renderers import _test_identity


@pytest.fixture
def identity_command(tmp_path: Path, example_age_key_str: str) -> list[str]:
    script_path = tmp_path / "print_identity.py"
    _ = script_path.write_text(f"print({example_age_key_str!r})")
    return [sys.executable, str(script_path)]


@pytest.fixture
def config_get(identity_command: list[str]) -> Callable[[str], str | list[str] | None]:
    def _config_get(key: str, _default: object = None) -> str | list[str] | None:
        if key in {"age_identity", "age_identity_file"}:
            return None
        assert key == "age_identity_command"
        return identity_command

    return _config_get


@pytest.fixture
def configure_loader_modules(
    config_get: Callable[[str], str | list[str] | None],
) -> dict[ModuleType, object]:
    return {age: {"__salt__": {"config.get": config_get}}}


def test() -> None:
    _test_identity.test()
