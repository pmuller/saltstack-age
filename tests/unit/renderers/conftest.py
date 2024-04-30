from pathlib import Path

import pytest


@pytest.fixture()
def age_identity_path(tmp_path: Path) -> str:
    key_path = tmp_path / "key"
    _ = key_path.write_text(
        """\
# created: 2024-04-23T19:20:16+08:00
# public key: age1xujsmd5ecq5h68yvv5hae55ltxr7h6ws3ut99c3jpcpxpax7kp3s9g6xpe
AGE-SECRET-KEY-1CG6803VTTPMA4WKAU0XGK6FU72NQ4JCJUJUJLAC9R5V3CMCJKN2SL9GLCD
"""
    )
    return str(key_path)
