#!/usr/bin/env bash
set -euo pipefail
workspace="${1:-./awc-demo-workspace}"
awc init "$workspace" --profile project
awc init "$workspace" --profile project --include-optional --with-claude-hooks --apply
awc doctor "$workspace" --strict
awc recover "$workspace"
