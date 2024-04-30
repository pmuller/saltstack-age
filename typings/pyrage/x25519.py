class Recipient:
    pass


class Identity:
    @classmethod
    def generate(cls) -> "Identity": ...

    @classmethod
    def from_str(cls, identity_string: str) -> "Identity": ...

    def to_public(self) -> Recipient: ...
