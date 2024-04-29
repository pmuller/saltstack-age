import re
from pathlib import Path

import pyrage


def read_identity_file(path: Path) -> pyrage.x25519.Identity:
    identity_string = re.sub(
        r"^#.*\n?",
        "",
        path.read_text(),
        flags=re.MULTILINE,
    ).rstrip("\n")
    return pyrage.x25519.Identity.from_str(identity_string)
