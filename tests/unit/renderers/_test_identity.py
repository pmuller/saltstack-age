from collections import OrderedDict

from saltstack_age.renderers import age


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
