# Saltstack renderer for age-encrypted secrets

This project introduces a [SaltStack](https://saltproject.io/) renderer
integrated with [age](https://age-encryption.org/),
a modern and simple encryption tool.
SaltStack is an open-source configuration management system that allows you to
automate the setup, deployment, and management of your infrastructure.
Integrating age encryption enhances SaltStack by providing a secure method to
handle secrets.

By using age, this renderer allows you to securely store encrypted secrets
directly in your source control.
This is particularly useful for environments where security and privacy are
paramount.
Only Salt masters (or masterless minions) configured with the appropriate age
identity or passphrase can decrypt these secrets, ensuring that sensitive
information remains protected even if source control is compromised.

The typical use case for this extension involves encrypting secrets stored in
Salt's pillar data,
enhancing security without sacrificing convenience or functionality.

## Requirements

This package has been tested with Saltstack 3007.0 on Ubuntu 22.04.4 LTS
(Jammy Jellyfish).

## Installation

If you use the [official Saltstack package](https://repo.saltproject.io/),
you can simply install it using:

```sh
sudo salt-pip install saltstack-age
```

## Configuration

age can be used to encrypt data using either a passphrase or an identity file.
This extension supports both, and they can be defined either in the Saltstack
daemon configuration file, or in the daemon environment.

| Type         | Configuration directive | Environment variable | Expected value               |
| ------------ | ----------------------- | -------------------- | ---------------------------- |
| identity     | `age_identity_file`     | `AGE_IDENTITY_FILE`  | Path of an age identity file |
| identity     | `age_identity`          | `AGE_IDENTITY`       | An age identity string       |
| passphrase   | `age_passphrase`        | `AGE_PASSPHRASE`     | An age passphrase            |

You can check this [example configuration](./example/config/minion).

## Secret encryption

Encrypted secrets are formatted as `ENC[age-passphrase,CIPHERTEXT]` or
`ENC[age-identity,CIPHERTEXT]`, depending on the encryption type.
`CIPHERTEXT` is the age-encrypted value, encoded with base64.

This package provides a handy CLI tool to make it easier:

```sh
$ saltstack-age -P secret-passphrase enc secret-value
ENC[age-passphrase,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IHNjcnlwdCB1QndwT3dJejhaSEtZZlIxeFEvZk5RIDIwCmhrcm9OY0tTOWdwNkhWbDdadlNIOHRFYmFLdkpZSjhLTktTWXhZVHFHKzgKLS0tIHFJWVRNc0JzTkpKNHJ1TFBuZ2tybWt0WWVQR0wrbjVnMmlZYzRaWVlBbFkKPWQu4lawaAu1owDXPDwwmj9/tN9/5NF/Avd4jPrLoy/ugUb0ciqm8H5My44=]
```

> [!CAUTION]
> While it is convenient to pass all arguments to the command-line,
> be careful to not leak credentials while doing it.

The tool exposes multiple options to provide the passphrase and identity files.
You can see them in details by reading its help: `saltstack-age --help`.

## Pillar data formatting

The renderer must be specified on the first line of the pillar data files that
contain encrypted values:

```yaml
#!yaml|age
```

Then you can define your secret values as:

```yaml
#!yaml|age
secret: ENC[age-passphrase,YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IHNjcnlwdCB1QndwT3dJejhaSEtZZlIxeFEvZk5RIDIwCmhrcm9OY0tTOWdwNkhWbDdadlNIOHRFYmFLdkpZSjhLTktTWXhZVHFHKzgKLS0tIHFJWVRNc0JzTkpKNHJ1TFBuZ2tybWt0WWVQR0wrbjVnMmlZYzRaWVlBbFkKPWQu4lawaAu1owDXPDwwmj9/tN9/5NF/Avd4jPrLoy/ugUb0ciqm8H5My44=]
```

For reference, you can read this [example](./example/).

## FAQ

### Why did you write this extension?

As a fan of GPG, I explored the
[GPG renderer](https://docs.saltproject.io/en/latest/ref/renderers/all/salt.renderers.gpg.html)
offered by SaltStack.
While GPG is robust, I found it somewhat cumbersome for smaller projects.
The simplicity and effectiveness of age encryption inspired me to develop this
extension,
providing a straightforward solution for managing secrets in Salt environments.

### Do I need to install age separately?

No, there's no need to install age separately.
This extension utilizes [pyrage](https://github.com/woodruffw/pyrage),
a Python wrapper that embeds [rage](https://github.com/str4d/rage),
a Rust implementation of age.
It simplifies the installation process by embedding all necessary functionality
within the extension itself.

### How do I ensure my secrets are secure when using this extension?

To maximize security:
- Always use secure channels for transferring sensitive information,
  including age identities and passphrases.
- Store your age identities and passphrases securely, using environment
  variables or secure files that are not checked into source control.
- Be cautious with logging and command-line usage as these can inadvertently
  expose sensitive information if not handled properly.

To ensure calls to the `saltstack-age` command are never logged in your
bash history, add it to your
[HISTIGNORE](https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html#index-HISTIGNORE)
variable.

### What should I do if I encounter errors during encryption or decryption?

First, verify that your age identities and passphrases are correctly configured
and accessible to the Salt master or minion. Check for typos or incorrect paths
in your configuration.
If the issue persists, refer to the detailed error messages provided by Salt and
age for further troubleshooting.
You can also seek help from the Salt community
or the issue tracker for this project.
Please provide your entire configuration so we can reproduce the error
(and use throwaway credentials to do so).

### Where can I find more resources?

For more detailed guidance on using age,
visit the official [age documentation](https://age-encryption.org/).
For SaltStack, consult the
[SaltStack documentation](https://docs.saltproject.io/) and community forums.
These resources offer comprehensive information and community-driven support
that can help you effectively utilize age encryption in your SaltStack projects.

## Development

* Environment is managed with [rye](https://rye-up.com/)
* Create a virtualenv: `rye sync`
* Check typing: `rye run basedpyright`
* Check formatting with ruff: `rye fmt -- --check`
* Check linting with ruff: `rye check`
* Run tests: `rye run pytest`

See [workflow](./.github/workflows/build.yaml) for reference.

## Release

* Build package: `rye build --clean --wheel`
* Publish package: `rye publish`

See [workflow](./.github/workflows/release.yaml) for reference.
