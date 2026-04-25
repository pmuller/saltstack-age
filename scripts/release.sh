#!/usr/bin/env bash
set -euo pipefail

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage: scripts/release.sh [VERSION]

Fetch origin, fast-forward local main, verify release metadata, create the
annotated release tag, and push it to origin.

VERSION is optional. When provided, it must match project.version in
pyproject.toml.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 1 ]]; then
  usage >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
cd "${repo_root}"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
  die "not inside a Git worktree"

if [[ -n "$(git status --porcelain)" ]]; then
  die "worktree is dirty; commit or stash changes before releasing"
fi

expected_version="${1:-}"

printf 'Fetching origin/main and tags...\n'
git fetch origin main --tags

printf 'Switching to main...\n'
git switch main

printf 'Fast-forwarding main from origin/main...\n'
git pull --ff-only origin main

local_main="$(git rev-parse main)"
remote_main="$(git rev-parse origin/main)"
[[ "${local_main}" == "${remote_main}" ]] ||
  die "local main does not match origin/main after pull"

version="$(
  sed -nE 's/^version = "([0-9]+\.[0-9]+\.[0-9]+)"$/\1/p' pyproject.toml |
    head -n 1
)"
[[ -n "${version}" ]] || die "could not read project.version from pyproject.toml"

if [[ -z "${expected_version}" ]]; then
  expected_version="${version}"
fi

[[ "${version}" == "${expected_version}" ]] ||
  die "main has version ${version}, expected ${expected_version}"

grep -F "## ${version}" CHANGELOG.md >/dev/null ||
  die "CHANGELOG.md does not contain section ## ${version}"

if git rev-parse --verify --quiet "refs/tags/${version}" >/dev/null; then
  die "local tag ${version} already exists"
fi

if git ls-remote --exit-code --tags origin "refs/tags/${version}" >/dev/null 2>&1; then
  die "remote tag ${version} already exists"
fi

printf 'Creating annotated tag %s...\n' "${version}"
git tag -a "${version}" -m "Release ${version}"

printf 'Pushing tag %s to origin...\n' "${version}"
git push origin "${version}"

printf 'Release tag %s pushed. Watch the GitHub Release workflow.\n' "${version}"
