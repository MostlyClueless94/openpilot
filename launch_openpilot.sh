#!/usr/bin/env bash
# BluePilot: bridge the standard comma installer to the BluePilot custom1 branch.
set -euo pipefail

install_bluepilot() {
  cd "$(dirname "$0")"
  local expected_commit="021405516531eb53e9ab2a2828355965cfa74c2c"
  git remote set-url origin https://github.com/MostlyClueless94/bluepilot.git
  git config remote.origin.fetch '+refs/heads/custom1:refs/remotes/origin/custom1'
  git fetch --depth=1 origin custom1
  if [ "$(git rev-parse refs/remotes/origin/custom1)" != "$expected_commit" ]; then
    echo "BluePilot custom1 changed unexpectedly; stopping installation."
    return 1
  fi
  # This replaces this bootstrap checkout with the reviewed prototype.
  git checkout -B custom1 refs/remotes/origin/custom1
  git submodule sync --recursive
  git submodule update --init --recursive
  exec ./launch_openpilot.sh
}

install_bluepilot
