from collections import OrderedDict
from pathlib import Path
from typing import Callable

import pytest
from saltstack_age.renderers import age


@pytest.fixture()
def age_identity_path(tmp_path: Path):
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
def config_get(age_identity_path: Path):
    def _config_get(key: str):
        assert key == "age_identity_file"
        return str(age_identity_path)

    return _config_get


@pytest.fixture()
def configure_loader_modules(config_get: Callable[[str], str]):
    return {
        age: {
            "__salt__": {
                "config.get": config_get,
            }
        }
    }


def test_render__identity():
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


def test_render__passphrase(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AGE_PASSPHRASE", "secret-passphrase")
    assert age.render(
        OrderedDict(
            (
                ("foo", "bar"),
                (
                    "secret",
                    "ENC[age-passphrase,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IHNjcnlwdCB6SVZXRVlTQnFzdWh0VWp2YkFGV2pnIDE4CnNXUEZLdi81WjdmS0JSaFoxRG9md3E1RXMwMUhqVDd2d2lHUFhPUHFvT1EKLS0tIGlEKzg0Qjc4cWM3WEVwOStqZUJNQUc4SXJUSXA0QzNtM21vQUZmSit6ZncKf+ubsIChW5+VqkQMrnaMPbaf4jOHAVRQXU6xWrlGSmoWnq4GuqJzX79fluc4bvPwqQ==]",
                ),
            )
        )
    ) == OrderedDict(
        (
            ("foo", "bar"),
            ("secret", "test-secret-value"),
        )
    )
