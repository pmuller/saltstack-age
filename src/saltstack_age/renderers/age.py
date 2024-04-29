from collections import OrderedDict
from typing import Any

from salt.exceptions import SaltRenderError

from saltstack_age.secure_value import (
    IdentitySecureValue,
    is_secure_value,
    parse_secure_value,
)

Data = OrderedDict[str, Any]


def _decrypt(string: str) -> str:
    secure_value = parse_secure_value(string)

    if isinstance(secure_value, IdentitySecureValue):
        if "config.get" in __salt__:
            identity_file: str | None = __salt__["config.get"]("age_identity_file")

            if not identity_file:
                raise SaltRenderError("age_identity_file is not defined")

            return secure_value.decrypt(identity_file)

        # Not sure how/when that happens...
        raise RuntimeError('__salt__["config.get"] is not available')

    return secure_value.decrypt()


def render(
    data: Data,
    _saltenv: str = "base",
    _sls: str = "",
    **_kwargs: None,
) -> Data:
    return OrderedDict(
        (key, _decrypt(value) if is_secure_value(value) else value)
        for key, value in data.items()
    )
