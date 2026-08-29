from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def packaged_hook_path() -> Path:
    return Path(str(files("agent_workspace_continuity").joinpath("template_data/claude/.claude/hooks/continuity_hook.py")))


def packaged_settings_path() -> Path:
    return Path(str(files("agent_workspace_continuity").joinpath("template_data/claude/.claude/continuity.settings.example.json")))
