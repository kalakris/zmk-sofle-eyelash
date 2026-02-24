#!/usr/bin/env bash
set -euo pipefail

# Download built firmware from GitHub Actions, organized by branch name.
# Usage:
#   ./scripts/download-firmware.sh          # current branch only
#   ./scripts/download-firmware.sh --all    # all remote branches

cd "$(git rev-parse --show-toplevel)"

if [[ "${1:-}" == "--all" ]]; then
  git fetch --prune
  branches=$(git branch -r | sed 's|origin/||' | grep -v 'HEAD' | xargs)
else
  branches=$(git branch --show-current)
fi

for branch in $branches; do
  run_id=$(gh run list --branch "$branch" --workflow "Build and Draw" --status success --limit 1 --json databaseId --jq '.[0].databaseId')

  if [[ -z "$run_id" || "$run_id" == "null" ]]; then
    echo "SKIP $branch — no successful build"
    continue
  fi

  echo "Downloading $branch (run $run_id)..."
  rm -rf "firmware/$branch"
  mkdir -p "firmware/$branch"
  gh run download "$run_id" --dir "firmware/$branch"
  echo "  OK"
done

echo "Done."
