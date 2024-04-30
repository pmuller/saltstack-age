from collections import OrderedDict

from saltstack_age.renderers import age


def test() -> None:
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
