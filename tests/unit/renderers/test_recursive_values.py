import pytest

from saltstack_age.renderers import age

SECURE_VALUE = "ENC[age-passphrase,Zm9v]"
DECRYPTED_VALUE = f"decrypted:{SECURE_VALUE}"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(SECURE_VALUE, DECRYPTED_VALUE, id="scalar"),
        pytest.param(
            age.Data(secret=SECURE_VALUE),
            age.Data(secret=DECRYPTED_VALUE),
            id="mapping",
        ),
        pytest.param([SECURE_VALUE], [DECRYPTED_VALUE], id="list-scalar"),
        pytest.param(
            [age.Data(secret=SECURE_VALUE)],
            [age.Data(secret=DECRYPTED_VALUE)],
            id="list-mapping",
        ),
        pytest.param(
            [age.Data(nested=[age.Data(secret=SECURE_VALUE), SECURE_VALUE])],
            [age.Data(nested=[age.Data(secret=DECRYPTED_VALUE), DECRYPTED_VALUE])],
            id="nested-list-mapping",
        ),
    ],
)
def test_render_decrypts_recursive_values(
    monkeypatch: pytest.MonkeyPatch, value: object, expected: object
) -> None:
    def decrypt(value: str) -> str:
        return f"decrypted:{value}"

    monkeypatch.setattr(age, "_decrypt", decrypt)
    assert age.render(age.Data(value=value)) == age.Data(value=expected)
