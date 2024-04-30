import logging
from collections.abc import Sequence
from pathlib import Path

import pyrage
import pytest
from saltstack_age.cli import main
from saltstack_age.identities import read_identity_file
from saltstack_age.secure_value import (
    IdentitySecureValue,
    PassphraseSecureValue,
    parse_secure_value,
)


def test_encrypt__passphrase(caplog: pytest.LogCaptureFixture) -> None:
    # Only keep INFO log records
    caplog.set_level(logging.INFO)
    # Run the CLI tool
    main(["-P", "woah that is so secret", "enc", "another secret"])
    # Ensure we get a passphrase secure value string
    secure_value_string = caplog.record_tuples[0][2]
    secure_value = parse_secure_value(secure_value_string)
    assert isinstance(secure_value, PassphraseSecureValue)
    # Ensure we can decrypt it
    assert secure_value.decrypt("woah that is so secret") == "another secret"


def test_encrypt__single_recipient(caplog: pytest.LogCaptureFixture) -> None:
    # Only keep INFO log records
    caplog.set_level(logging.INFO)
    # Run the CLI tool
    main(["-i", "example/config/age.key", "enc", "foo"])
    # Ensure we get an identity secure value string
    secure_value_string = caplog.record_tuples[0][2]
    secure_value = parse_secure_value(secure_value_string)
    assert isinstance(secure_value, IdentitySecureValue)
    # Ensure we can decrypt it using the same identity
    assert secure_value.decrypt(read_identity_file("example/config/age.key")) == "foo"


def test_encrypt__multiple_recipients(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    # Only keep INFO log records
    caplog.set_level(logging.INFO)
    # Generate identities
    identity1 = pyrage.x25519.Identity.generate()
    identity1_path = tmp_path / "identity1"
    _ = identity1_path.write_text(str(identity1))
    identity2 = pyrage.x25519.Identity.generate()
    identity2_path = tmp_path / "identity2"
    _ = identity2_path.write_text(str(identity2))
    # Run the CLI tool
    main(
        [
            "-i",
            str(identity1_path),
            "--identity",
            str(identity2_path),
            "encrypt",
            "foo",
        ]
    )
    # Ensure we get an identity secure value string
    secure_value_string = caplog.record_tuples[0][2]
    secure_value = parse_secure_value(secure_value_string)
    assert isinstance(secure_value, IdentitySecureValue)
    # Ensure we can decrypt it using all the recipient identities
    for identity_path in (identity1_path, identity2_path):
        assert secure_value.decrypt(read_identity_file(identity_path)) == "foo"


@pytest.mark.parametrize(
    ("environment", "args", "result"),
    [
        # Test decryption using a single identity file
        (
            None,
            (
                "-i",
                "example/config/age.key",
                "dec",
                "ENC[age-identity,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBkWHZYRkU2bjc4M2VtaElEZGxudmkwNW95ZHlNZy84K3U4MmlXejIzRkJNCktPbkhLU0h4VXBFYTZUUDlzbFFzdUx5R1VyaDZhd2doNkE2QnFpUmV6OFEKLS0tIFd3Wlg1UWQ3NHEwKyt6bTZkdmp3bWRCTTZkakppTFovbkhBcDhFeGdJazgKnf48DyGjBm2wOpM11YZ0+1btASDDSdgqXiM4SXXEMHhylmW8G9pSoTtovj0aZu9QVA==]",
            ),
            "test-secret-value",
        ),
        # Test decryption using a passphrase passed through CLI argument
        (
            None,
            (
                "-P",
                "secret-passphrase",
                "dec",
                "ENC[age-passphrase,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IHNjcnlwdCB6SVZXRVlTQnFzdWh0VWp2YkFGV2pnIDE4CnNXUEZLdi81WjdmS0JSaFoxRG9md3E1RXMwMUhqVDd2d2lHUFhPUHFvT1EKLS0tIGlEKzg0Qjc4cWM3WEVwOStqZUJNQUc4SXJUSXA0QzNtM21vQUZmSit6ZncKf+ubsIChW5+VqkQMrnaMPbaf4jOHAVRQXU6xWrlGSmoWnq4GuqJzX79fluc4bvPwqQ==]",
            ),
            "test-secret-value",
        ),
        # Test decryption using a passphrase passed through environment
        (
            {"AGE_PASSPHRASE": "secret-passphrase"},
            (
                "decrypt",
                "ENC[age-passphrase,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IHNjcnlwdCB6SVZXRVlTQnFzdWh0VWp2YkFGV2pnIDE4CnNXUEZLdi81WjdmS0JSaFoxRG9md3E1RXMwMUhqVDd2d2lHUFhPUHFvT1EKLS0tIGlEKzg0Qjc4cWM3WEVwOStqZUJNQUc4SXJUSXA0QzNtM21vQUZmSit6ZncKf+ubsIChW5+VqkQMrnaMPbaf4jOHAVRQXU6xWrlGSmoWnq4GuqJzX79fluc4bvPwqQ==]",
            ),
            "test-secret-value",
        ),
    ],
)
def test_decrypt(
    environment: None | dict[str, str],
    args: Sequence[str],
    result: str,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Setup environment variables
    for name, value in (environment or {}).items():
        monkeypatch.setenv(name, value)
    # Only keep INFO log records
    caplog.set_level(logging.INFO)
    # Run the CLI tool
    main(args)
    # Ensure we get the expected result
    assert caplog.record_tuples == [("saltstack_age.cli", logging.INFO, result)]
