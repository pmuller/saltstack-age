import logging
import sys
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from base64 import b64encode
from collections.abc import Sequence
from getpass import getpass
from pathlib import Path

import pyrage

from saltstack_age.identities import read_identity_file
from saltstack_age.passphrase import get_passphrase_from_environment
from saltstack_age.secure_value import (
    IdentitySecureValue,
    parse_secure_value,
)

LOGGER = logging.getLogger(__name__)


def normalize_identity(identity: str) -> Path:
    path = Path(identity)

    if path.is_file():
        return path

    raise ArgumentTypeError(f"Identity file does not exist: {identity}")


def parse_cli_arguments(args: Sequence[str] | None = None) -> Namespace:
    parser = ArgumentParser(
        description="Encrypt or decrypt secrets for use with saltstack-age renderer.",
        epilog="When no passphrase or identity is provided, the tool defaults to "
        "passphrase-based encryption and attempts to retrieve the passphrase from "
        "the AGE_PASSPHRASE environment variable.",
    )

    type_parameters = parser.add_mutually_exclusive_group()
    _ = type_parameters.add_argument(
        "-i",
        "--identity",
        type=normalize_identity,
        dest="identities",
        action="append",
        help="The identity file to use. "
        "Can be repeated to encrypt the data for multiple identities.",
    )
    _ = type_parameters.add_argument(
        "-p",
        "--passphrase-from-stdin",
        action="store_true",
        help="Read passphrase from the standard input",
    )
    _ = type_parameters.add_argument(
        "-P",
        "--passphrase",
        metavar="PASSPHRASE",
        help="Pass passphrase as a CLI argument. ",
    )

    _ = parser.add_argument(
        "-D", "--debug", action="store_true", help="Enable debug logging"
    )

    _ = parser.add_argument(
        "mode",
        choices=("encrypt", "decrypt", "enc", "dec"),
        help="Run the tool in encryption or decryption mode",
    )
    _ = parser.add_argument(
        "value",
        nargs="?",
        help="The value that needs to be encrypted or decrypted. "
        "Will be read from the standard input if not provided.",
    )

    return parser.parse_args(args)


def configure_logging(*, debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    format_ = "%(levelname)s:%(name)s:%(message)s" if debug else "%(message)s"
    logging.basicConfig(level=level, format=format_, style="%")


def get_passphrase(arguments: Namespace) -> str:
    passphrase: str | None = None

    if arguments.passphrase_from_stdin:
        passphrase = getpass("Passphrase: ")
    elif arguments.passphrase:
        passphrase = arguments.passphrase
    else:
        passphrase = get_passphrase_from_environment()

    if passphrase is None:
        LOGGER.critical("No age passphrase provided")
        raise SystemExit(-1)

    return passphrase


def get_value(arguments: Namespace) -> str:
    return arguments.value or sys.stdin.read()


def encrypt(arguments: Namespace) -> None:
    value = get_value(arguments).encode()

    if arguments.identities:
        recipients = [
            read_identity_file(identity).to_public()
            for identity in arguments.identities
        ]
        ciphertext = pyrage.encrypt(value, recipients)
        LOGGER.info("ENC[age-identity,%s]", b64encode(ciphertext).decode())

    else:
        ciphertext = pyrage.passphrase.encrypt(value, get_passphrase(arguments))
        LOGGER.info("ENC[age-passphrase,%s]", b64encode(ciphertext).decode())


def decrypt(arguments: Namespace) -> None:
    secure_value = parse_secure_value(get_value(arguments))

    if isinstance(secure_value, IdentitySecureValue):
        if arguments.identities is None:
            LOGGER.critical("An identity is required to decrypt this value")
            raise SystemExit(-1)
        if len(arguments.identities) != 1:
            LOGGER.critical(
                "A single identity must be passed to decrypt this value (got %d)",
                len(arguments.identities),
            )
            raise SystemExit(-1)
        LOGGER.info("%s", secure_value.decrypt(arguments.identities[0]))

    else:  # isinstance(secure_value, PassphraseSecureValue)
        LOGGER.info("%s", secure_value.decrypt(get_passphrase(arguments)))


def main(cli_args: Sequence[str] | None = None) -> None:
    arguments = parse_cli_arguments(cli_args)
    configure_logging(debug=arguments.debug)
    LOGGER.debug("CLI arguments: %r", arguments)
    encrypt(arguments) if arguments.mode.startswith("enc") else decrypt(arguments)
