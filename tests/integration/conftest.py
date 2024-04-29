import os
from pathlib import Path

import pytest
from saltfactories.cli.call import SaltCall
from saltfactories.daemons.minion import SaltMinion
from saltfactories.manager import FactoriesManager
from saltfactories.utils import random_string

ROOT = Path(__file__).parent.parent.parent
EXAMPLE_PATH = ROOT / "example"


@pytest.fixture(scope="session")
def salt_factories_config():
    coverage_rc_path = os.environ.get("COVERAGE_PROCESS_START")
    coverage_db_path = ROOT / ".coverage" if coverage_rc_path else None
    return {
        "code_dir": str(EXAMPLE_PATH),
        "coverage_rc_path": coverage_rc_path,
        "coverage_db_path": coverage_db_path,
        "inject_sitecustomize": "COVERAGE_PROCESS_START" in os.environ,
        "start_timeout": 120 if os.environ.get("CI") else 60,
    }


@pytest.fixture(scope="package")
def minion(salt_factories: FactoriesManager) -> SaltMinion:
    return salt_factories.salt_minion_daemon(
        random_string("minion-"),
        overrides={
            "file_client": "local",
            "master_type": "disable",
            "pillar_roots": {"base": [str(EXAMPLE_PATH / "pillar")]},
            "file_roots": {"base": [str(EXAMPLE_PATH / "states")]},
            "age_identity_file": str(EXAMPLE_PATH / "config" / "age.key"),
        },
    )


@pytest.fixture()
def salt_call_cli(minion: SaltMinion) -> SaltCall:
    return minion.salt_call_cli()
