from pathlib import Path

from saltfactories.cli.call import SaltCall


def test_age_identity(salt_call_cli: SaltCall, tmp_path: Path):
    _ = salt_call_cli.run("state.apply", pillar=f'{{"prefix": "{tmp_path}"}}')
    assert (tmp_path / "test-public").read_text() == "that's not a secret\n"
    assert (tmp_path / "test-private").read_text() == "test-secret-value\n"
