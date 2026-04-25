# Agent Instructions

## Scope

These instructions apply to the entire repository.

Work from the repository root. Do not read or edit parent worktree directories
unless the user explicitly asks for that.

## Project Shape

This is a `uv`-managed Python package for a SaltStack renderer and CLI that
decrypts age-encrypted secrets.

Important paths:

* `src/saltstack_age/` contains package code.
* `src/saltstack_age/renderers/age.py` is the Salt renderer entry point.
* `tests/unit/` contains fast renderer/unit coverage.
* `tests/integration/` contains Salt and CLI integration coverage.
* `typings/` contains local stubs for external packages with incomplete types.
* `example/` contains user-facing Salt configuration examples.

## Preserve Conventions

* Keep the project managed by `uv`; do not introduce `pip`, `poetry`, `tox`,
  `nox`, or ad-hoc virtualenv workflows.
* Do not hand-edit `uv.lock`. Use `uv add`, `uv lock`, or another `uv` command
  that updates both `pyproject.toml` and `uv.lock` consistently.
* Keep direct dev dependency floors in `pyproject.toml` aligned with deliberate
  tool upgrades.
* Preserve the `src/` package layout and Hatchling build configuration.
* Keep Salt-specific globals such as `__salt__` compatible with the current
  Ruff configuration.
* Keep external typing workarounds in `typings/` instead of weakening project
  type checking globally.
* Do not remove the explicit Salt runtime dependency pins unless Salt packaging
  has been verified to declare those dependencies itself.
* Do not commit real secrets, private age identities, passphrases, or realistic
  credentials. Use throwaway test values only.

## Python Style

Follow the existing Ruff and BasedPyright settings in `pyproject.toml`.

* Prefer small, typed functions with explicit return annotations.
* Use `pathlib.Path` for filesystem paths.
* Use specific exceptions and preserve useful error messages for Salt users.
* Keep `__init__.py` files minimal.
* Keep comments rare and useful; avoid comments that restate the code.
* Add or update tests with behavior changes.

## Tests And Validation

Before finishing a code or dependency change, run:

```sh
uv run lefthook run pre-commit --all-files
```

The individual checks are:

```sh
uv run ruff format --check
uv run ruff check
uv run basedpyright
uv run pytest
```

Fix all errors and warnings from these tools. Do not leave the repository in a
state where the configured checks fail.

## Lefthook

Lefthook is the configured Git hook runner. Keep checks in `pre-commit` unless
the user asks for a different hook split.

If the command names are changed, verify the resolved order with:

```sh
uv run lefthook dump
```

## Documentation

* Keep README examples accurate for the CLI and renderer behavior.
* Use Markdown links for URLs; do not add bare URLs.
* Update `example/` when a behavior change affects documented Salt
  configuration.

## Git Hygiene

* Inspect `git status --short` before editing and before committing.
* Do not revert unrelated user changes.
* Keep commits focused and use conventional commit messages like
  `fix: ...`, `feat: ...`, and `chore: ...`.
