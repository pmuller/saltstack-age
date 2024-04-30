from pathlib import Path

import pytest
from saltfactories.cli.call import SaltCall
from saltfactories.daemons.minion import SaltMinion
from saltfactories.manager import FactoriesManager
from saltfactories.utils import random_string

from tests.integration.conftest import MINION_CONFIG


@pytest.fixture()
def minion(salt_factories: FactoriesManager, example_age_key: str) -> SaltMinion:
    overrides = MINION_CONFIG.copy()
    overrides["age_identity_file"] = example_age_key
    return salt_factories.salt_minion_daemon(
        random_string("minion-"),
        overrides=overrides,
    )


def test(salt_call_cli: SaltCall, tmp_path: Path) -> None:
    _ = salt_call_cli.run("state.apply", pillar=f'{{"prefix": "{tmp_path}"}}')
    assert (tmp_path / "test-public").read_text() == "that's not a secret\n"
    assert (tmp_path / "test-private").read_text() == "test-secret-value\n"
