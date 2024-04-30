import logging
import sys
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from base64 import b64encode
from collections.abc import Sequence
from getpass import getpass
from pathlib import Path
from typing import Literal

import pyrage

from saltstack_age.identities import get_identity_from_environment, read_identity_file
from saltstack_age.passphrase import get_passphrase_from_environment
from saltstack_age.secure_value import (
    IdentitySecureValue,
    parse_secure_value,
)

LOGGER = logging.getLogger(__name__)


def normalize_identity(identity: str) -> pyrage.x25519.Identity:
    path = Path(identity)

    if path.is_file():
        return read_identity_file(path)

    raise ArgumentTypeError(f"Identity file does not exist: {identity}")


def parse_cli_arguments(args: Sequence[str] | None = None) -> Namespace:
    parser = ArgumentParser(
        description="Encrypt or decrypt secrets for use with saltstack-age renderer.",
        epilog="When no passphrase or identity is provided, the tool tries to "
        "retrieve a passphrase from the AGE_PASSPHRASE environment variable, "
        "or an identity using the AGE_IDENTITY_FILE variable.",
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


def get_identities(arguments: Namespace) -> list[pyrage.x25519.Identity]:
    identities: list[pyrage.x25519.Identity] = arguments.identities or []

    # When no identity is provided on the CLI, try to get one from the environment
    if not identities:
        identity_from_environment = get_identity_from_environment()
        if identity_from_environment:
            LOGGER.debug("Found identity file in environment")
            identities.append(identity_from_environment)

    return identities


def get_value(arguments: Namespace) -> str:
    return arguments.value or sys.stdin.read()


def determine_encryption_type(
    arguments: Namespace,
) -> Literal["identity", "passphrase"]:
    if arguments.passphrase or arguments.passphrase_from_stdin:
        return "passphrase"
    if arguments.identities:
        return "identity"

    # We want the tool to be easy to use, so there is a lot of guesswork.
    # But we also want to avoid inconsistent behaviors.
    # So in case no passphrase or identity is passed to CLI,
    # but both are configured in the environment, we raise an error.
    identities = get_identities(arguments)
    passphrase = get_passphrase(arguments)
    if identities and passphrase:
        LOGGER.critical("Error: Found both passphrase and identity file in environment")
        raise SystemExit(-1)

    if identities:
        return "identity"

    return "passphrase"


def encrypt(arguments: Namespace) -> None:
    value = get_value(arguments).encode()
    type_ = determine_encryption_type(arguments)

    if type_ == "identity":
        recipients = [identity.to_public() for identity in get_identities(arguments)]
        ciphertext = pyrage.encrypt(value, recipients)
    else:
        ciphertext = pyrage.passphrase.encrypt(value, get_passphrase(arguments))

    _ = sys.stdout.write(f"ENC[age-{type_},{b64encode(ciphertext).decode()}]\n")


def decrypt(arguments: Namespace) -> None:
    secure_value = parse_secure_value(get_value(arguments))

    if isinstance(secure_value, IdentitySecureValue):
        identities = get_identities(arguments)

        if not identities:
            LOGGER.critical("An identity is required to decrypt this value")
            raise SystemExit(-1)

        if len(identities) != 1:
            LOGGER.critical(
                "A single identity must be passed to decrypt this value (got %d)",
                len(arguments.identities),
            )
            raise SystemExit(-1)

        _ = sys.stdout.write(secure_value.decrypt(identities[0]))

    else:  # isinstance(secure_value, PassphraseSecureValue)
        _ = sys.stdout.write(secure_value.decrypt(get_passphrase(arguments)))


def main(cli_args: Sequence[str] | None = None) -> None:
    arguments = parse_cli_arguments(cli_args)
    configure_logging(debug=arguments.debug)
    LOGGER.debug("CLI arguments: %r", arguments)
    encrypt(arguments) if arguments.mode.startswith("enc") else decrypt(arguments)
