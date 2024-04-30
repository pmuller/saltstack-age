import pytest
from saltfactories.daemons.minion import SaltMinion
from saltfactories.manager import FactoriesManager
from saltfactories.utils import random_string

from tests.integration import _test_renderer_identity
from tests.integration.conftest import MINION_CONFIG


@pytest.fixture()
def minion(
    salt_factories: FactoriesManager,
    example_age_key_path_str: str,
) -> SaltMinion:
    overrides = MINION_CONFIG.copy()
    overrides["age_identity_file"] = example_age_key_path_str
    return salt_factories.salt_minion_daemon(
        random_string("minion-"),
        overrides=overrides,
    )


test = _test_renderer_identity.test
