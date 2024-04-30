import os


def get_passphrase_from_environment() -> str | None:
    return os.environ.get("AGE_PASSPHRASE")
