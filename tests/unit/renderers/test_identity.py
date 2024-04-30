from collections import OrderedDict
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

import pytest
from saltstack_age.renderers import age


@pytest.fixture()
def age_identity_path(tmp_path: Path) -> Path:
    key_path = tmp_path / "key"
    _ = key_path.write_text(
        """\
# created: 2024-04-23T19:20:16+08:00
# public key: age1xujsmd5ecq5h68yvv5hae55ltxr7h6ws3ut99c3jpcpxpax7kp3s9g6xpe
AGE-SECRET-KEY-1CG6803VTTPMA4WKAU0XGK6FU72NQ4JCJUJUJLAC9R5V3CMCJKN2SL9GLCD
"""
    )
    return key_path


@pytest.fixture()
def config_get(age_identity_path: Path) -> Callable[[str], str]:
    def _config_get(key: str) -> str:
        assert key == "age_identity_file"
        return str(age_identity_path)

    return _config_get


@pytest.fixture()
def configure_loader_modules(config_get: Callable[[str], str]) -> dict[ModuleType, Any]:
    return {age: {"__salt__": {"config.get": config_get}}}


def test() -> None:
    assert age.render(
        OrderedDict(
            (
                ("foo", "bar"),
                (
                    "secret",
                    "ENC[age-identity,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBkWHZYRkU2bjc4M2VtaElEZGxudmkwNW95ZHlNZy84K3U4MmlXejIzRkJNCktPbkhLU0h4VXBFYTZUUDlzbFFzdUx5R1VyaDZhd2doNkE2QnFpUmV6OFEKLS0tIFd3Wlg1UWQ3NHEwKyt6bTZkdmp3bWRCTTZkakppTFovbkhBcDhFeGdJazgKnf48DyGjBm2wOpM11YZ0+1btASDDSdgqXiM4SXXEMHhylmW8G9pSoTtovj0aZu9QVA==]",
                ),
            )
        )
    ) == OrderedDict(
        (
            ("foo", "bar"),
            ("secret", "test-secret-value"),
        )
    )
