from base64 import b64decode
from pathlib import Path

from saltstack_age.renderers.age import decrypt_with_identity, decrypt_with_passphrase


def test_decrypt_with_identity(tmp_path: Path):
    key_path = tmp_path / "key"
    _ = key_path.write_text(
        """\
# created: 2024-04-23T19:20:16+08:00
# public key: age1xujsmd5ecq5h68yvv5hae55ltxr7h6ws3ut99c3jpcpxpax7kp3s9g6xpe
AGE-SECRET-KEY-1CG6803VTTPMA4WKAU0XGK6FU72NQ4JCJUJUJLAC9R5V3CMCJKN2SL9GLCD
"""
    )
    assert (
        decrypt_with_identity(
            b64decode(
                "YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBkWHZYRkU2bjc4M2VtaElEZGxudmkwNW95ZHlNZy84K3U4MmlXejIzRkJNCktPbkhLU0h4VXBFYTZUUDlzbFFzdUx5R1VyaDZhd2doNkE2QnFpUmV6OFEKLS0tIFd3Wlg1UWQ3NHEwKyt6bTZkdmp3bWRCTTZkakppTFovbkhBcDhFeGdJazgKnf48DyGjBm2wOpM11YZ0+1btASDDSdgqXiM4SXXEMHhylmW8G9pSoTtovj0aZu9QVA=="
            ),
            str(key_path),
        )
        == "test-secret-value"
    )


def test_decrypt_with_passphrase():
    assert (
        decrypt_with_passphrase(
            b64decode(
                "YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IHNjcnlwdCB6SVZXRVlTQnFzdWh0VWp2YkFGV2pnIDE4CnNXUEZLdi81WjdmS0JSaFoxRG9md3E1RXMwMUhqVDd2d2lHUFhPUHFvT1EKLS0tIGlEKzg0Qjc4cWM3WEVwOStqZUJNQUc4SXJUSXA0QzNtM21vQUZmSit6ZncKf+ubsIChW5+VqkQMrnaMPbaf4jOHAVRQXU6xWrlGSmoWnq4GuqJzX79fluc4bvPwqQ=="
            ),
            "secret-passphrase",
        )
        == "test-secret-value"
    )
