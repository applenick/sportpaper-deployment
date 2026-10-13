#!/usr/bin/env bash
set -euo pipefail

upstream_sha="${1:?Usage: record-success.sh <40-character-upstream-sha>}"
state_file="${2:-state/sportpaper-main.sha}"

if [[ ! "${upstream_sha}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Refusing to record invalid commit SHA: ${upstream_sha}" >&2
  exit 1
fi

printf '%s\n' "${upstream_sha}" > "${state_file}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -- "${state_file}"

if git diff --cached --quiet; then
  echo "Publication state is already ${upstream_sha}."
  exit 0
fi

git commit -m "Record published SportPaper commit ${upstream_sha:0:12} [skip ci]"
git push

