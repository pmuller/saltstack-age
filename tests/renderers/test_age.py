from pathlib import Path

from saltstack_age.renderers.age import decrypt_with_identity


def test_decrypt_with_identity(tmp_path: Path):
    key_path = tmp_path / "key"
    _ = key_path.write_text(
        "AGE-SECRET-KEY-1CG6803VTTPMA4WKAU0XGK6FU72NQ4JCJUJUJLAC9R5V3CMCJKN2SL9GLCD"
    )
    assert (
        decrypt_with_identity(
            str(key_path),
            """\
-----BEGIN AGE ENCRYPTED FILE-----
YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSB4andCbjFKK296Z2ljTTNH
QjZINHl2a1ZFdC9ZdThPa0hGQkhCL0FXWlZBCmdTejdpbVU1aStGQWJkUVZNTU9Z
RGs5YXQvV2dmcGVBY0JGZldrWXF5YUUKLS0tIHpZcEVLTW9kU1JVL1ZjYVVKQ2Zk
akRidThzbTZPQ2tvZXJEU0FsNWs5MWMKfEetwDxBHPKyPPBKguZSZWn8oypX5bHQ
FCqMT8V+RoIgPPV4ZZPuVa9RN/hmv8dj6Q==
-----END AGE ENCRYPTED FILE-----
""",
        )
        == "test-secret-value"
    )
