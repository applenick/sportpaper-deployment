#!/usr/bin/env bash
set -euo pipefail

upstream_directory="${1:-.work/upstream}"
state_file="${2:-state/sportpaper-main.sha}"

if [[ ! -d "${upstream_directory}/.git" ]]; then
  echo "Upstream checkout not found at ${upstream_directory}" >&2
  exit 1
fi

upstream_sha="$(git -C "${upstream_directory}" rev-parse HEAD)"
published_sha=""

if [[ -f "${state_file}" ]]; then
  published_sha="$(tr -d '[:space:]' < "${state_file}")"
fi

if [[ -n "${published_sha}" && ! "${published_sha}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Invalid commit SHA in ${state_file}: ${published_sha}" >&2
  exit 1
fi

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "upstream_sha=${upstream_sha}"
    if [[ "${FORCE_PUBLISH:-false}" != "true" && "${upstream_sha}" == "${published_sha}" ]]; then
      echo "should_publish=false"
    else
      echo "should_publish=true"
    fi
  } >> "${GITHUB_OUTPUT}"
fi

if [[ "${FORCE_PUBLISH:-false}" == "true" ]]; then
  echo "Forcing rebuild and publication of SportPaper ${upstream_sha}."
elif [[ "${upstream_sha}" == "${published_sha}" ]]; then
  echo "SportPaper ${upstream_sha} is already published."
else
  echo "SportPaper ${upstream_sha} needs publication (last successful: ${published_sha:-none})."
fi

