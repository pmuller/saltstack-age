class SaltException(Exception): ...  # noqa: N818

class SaltRenderError(SaltException):
    def __init__(self, message: str) -> None: ...
