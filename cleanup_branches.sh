#!/usr/bin/env bash
#
# cleanup_branches.sh
# Deletes ALL branches except 'main' (both local and remote).
# Run this from the root of the repository after merging this PR.
#
# Usage:
#   chmod +x cleanup_branches.sh
#   ./cleanup_branches.sh
#

set -euo pipefail

PROTECTED_BRANCH="main"

echo "=== Branch Cleanup Script ==="
echo ""

# Step 1: Check for uncommitted changes, then checkout main and pull latest
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: You have uncommitted changes. Please commit or stash them first."
  exit 1
fi
echo ">> Checking out '${PROTECTED_BRANCH}' and pulling latest..."
git checkout "${PROTECTED_BRANCH}"
git pull origin "${PROTECTED_BRANCH}"
echo ""

# Step 2: Prune stale remote tracking branches
echo ">> Pruning stale remote-tracking references..."
git fetch --prune
echo ""

# Step 3: Delete local branches (except main)
echo ">> Deleting local branches (except '${PROTECTED_BRANCH}')..."
LOCAL_BRANCHES=$(git branch | grep -v "^\*\?\s*${PROTECTED_BRANCH}$" | sed 's/^[ *]*//' || true)
if [ -z "${LOCAL_BRANCHES}" ]; then
  echo "   No local branches to delete."
else
  echo "${LOCAL_BRANCHES}" | while IFS= read -r branch; do
    branch=$(echo "${branch}" | xargs)
    if [ -n "${branch}" ]; then
      echo "   Deleting local branch: ${branch}"
      git branch -D "${branch}"
    fi
  done
fi
echo ""

# Step 4: Delete remote branches (except main)
# Uses git ls-remote to reliably detect all remote branches (works even with single-branch clones)
echo ">> Deleting remote branches (except '${PROTECTED_BRANCH}')..."
REMOTE_BRANCHES=$(git ls-remote --heads origin | awk '{print $2}' | sed 's|refs/heads/||' | grep -v "^${PROTECTED_BRANCH}$" || true)
if [ -z "${REMOTE_BRANCHES}" ]; then
  echo "   No remote branches to delete."
else
  echo "${REMOTE_BRANCHES}" | while IFS= read -r branch; do
    branch=$(echo "${branch}" | xargs)
    if [ -n "${branch}" ]; then
      echo "   Deleting remote branch: origin/${branch}"
      git push origin --delete "${branch}"
    fi
  done
fi
echo ""

# Step 5: Verify
echo ">> Verification — remaining branches:"
git branch -a
echo ""
echo "=== Cleanup complete! Only '${PROTECTED_BRANCH}' should remain. ==="
