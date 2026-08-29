param([string]$Workspace = ".\\awc-demo-workspace")
$ErrorActionPreference = "Stop"
awc init $Workspace --profile project
awc init $Workspace --profile project --include-optional --with-claude-hooks --apply
awc doctor $Workspace --strict
awc recover $Workspace
