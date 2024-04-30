import logging
from collections.abc import Sequence

import pytest
from saltstack_age.cli import main


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
                "dec",
                "ENC[age-passphrase,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IHNjcnlwdCB6SVZXRVlTQnFzdWh0VWp2YkFGV2pnIDE4CnNXUEZLdi81WjdmS0JSaFoxRG9md3E1RXMwMUhqVDd2d2lHUFhPUHFvT1EKLS0tIGlEKzg0Qjc4cWM3WEVwOStqZUJNQUc4SXJUSXA0QzNtM21vQUZmSit6ZncKf+ubsIChW5+VqkQMrnaMPbaf4jOHAVRQXU6xWrlGSmoWnq4GuqJzX79fluc4bvPwqQ==]",
            ),
            "test-secret-value",
        ),
    ],
)
def test(
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
