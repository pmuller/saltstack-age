import json
from pathlib import Path

from saltfactories.cli.call import SaltCall


def test(salt_call_cli: SaltCall, tmp_path: Path) -> None:
    _ = salt_call_cli.run(
        "state.apply",
        pillar=json.dumps({"test": {"prefix": str(tmp_path)}}),
    )
    assert (tmp_path / "test-public").read_text() == "that's not a secret\n"
    assert (tmp_path / "test-private").read_text() == "test-secret-value\n"
