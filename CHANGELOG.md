# saltstack-age change log

## Unreleased

* feat(renderer): decrypt encrypted values inside YAML lists

## 0.5.0

* feat: publish both wheel and source distribution artifacts
* feat(cli): support encrypting to an age recipient public key with `--recipient`
* feat(renderer): support loading age identities from an external command
* fix(cli): stop CLI logs from reaching Salt's deferred handler
* ci: harden build and release automation
* chore: migrate project management from Rye to uv
* chore: add Lefthook pre-commit checks
* chore: upgrade development tooling for pytest, Ruff, and BasedPyright
* docs: add repository agent and release-management instructions

## 0.4.0

* feat: allow configuration of an identity string using the `AGE_IDENTITY`
  environment variable and the `age_identity` configuration directive

## 0.3.0

* fix: add support for nested pillar data
* fix(cli): write results to stdout
* feat(ci): run tests
