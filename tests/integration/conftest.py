import os

import pytest
from saltfactories.cli.call import SaltCall
from saltfactories.daemons.minion import SaltMinion

from tests.conftest import EXAMPLE_PATH, ROOT

MINION_CONFIG = {
    "file_client": "local",
    "master_type": "disable",
    "pillar_roots": {"base": [str(EXAMPLE_PATH / "pillar")]},
    "file_roots": {"base": [str(EXAMPLE_PATH / "states")]},
}


@pytest.fixture(scope="session")
def salt_factories_config() -> dict[str, str | int | bool | None]:
    coverage_rc_path = os.environ.get("COVERAGE_PROCESS_START")
    coverage_db_path = str(ROOT / ".coverage") if coverage_rc_path else None
    return {
        "code_dir": str(EXAMPLE_PATH),
        "coverage_rc_path": coverage_rc_path,
        "coverage_db_path": coverage_db_path,
        "inject_sitecustomize": "COVERAGE_PROCESS_START" in os.environ,
        "start_timeout": 120 if os.environ.get("CI") else 60,
    }


@pytest.fixture()
def salt_call_cli(minion: SaltMinion) -> SaltCall:
    return minion.salt_call_cli()
