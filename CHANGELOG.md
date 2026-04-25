# saltstack-age change log

## Unreleased

* feat(cli): support encrypting to an age recipient public key with `--recipient`
* feat(renderer): support loading age identities from an external command
* chore: migrate project management from Rye to uv
* chore: add Lefthook pre-commit checks
* chore: upgrade development tooling for pytest, Ruff, and BasedPyright
* docs: add repository agent instructions

## 0.4.0

* feat: allow configuration of an identity string using the `AGE_IDENTITY`
  environment variable and the `age_identity` configuration directive

## 0.3.0

* fix: add support for nested pillar data
* fix(cli): write results to stdout
* feat(ci): run tests
