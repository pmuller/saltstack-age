import logging
from pathlib import Path

import pyrage
import pytest

from saltstack_age.identities import read_identity_file


def pytest_configure(config: pytest.Config) -> None:
    # Salt installs a DeferredStreamHandler on the root logger that buffers
    # records until salt's logging is fully configured, then flushes them at
    # interpreter shutdown. Under pytest the buffered records would be flushed
    # to streams that capsys has already closed, producing spurious
    # "I/O operation on closed file" tracebacks. Drop the handler entirely:
    # buffered records are discarded along with it.
    _ = config
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if type(handler).__name__ == "DeferredStreamHandler":
            root_logger.removeHandler(handler)


ROOT = Path(__file__).parent.parent
EXAMPLE_PATH = ROOT / "example"


@pytest.fixture
def example_age_key_path() -> Path:
    return EXAMPLE_PATH / "config" / "age.key"


@pytest.fixture
def example_age_key_path_str(example_age_key_path: Path) -> str:
    return str(example_age_key_path)


@pytest.fixture
def example_age_key(example_age_key_path: Path) -> pyrage.x25519.Identity:
    return read_identity_file(example_age_key_path)


@pytest.fixture
def example_age_key_str(example_age_key: pyrage.x25519.Identity) -> str:
    return str(example_age_key)
