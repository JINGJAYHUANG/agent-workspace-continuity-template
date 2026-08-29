from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from string import Template

SUPPORTED_PROFILES = ("project", "umbrella")
REQUIRED = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agent/brief.md",
    ".agent/status.md",
    ".agent/handoff.md",
    ".agent/.gitignore",
)
OPTIONAL = (".agent/plan.md", ".agent/decisions.md")
CLAUDE = (".claude/hooks/continuity_hook.py", ".claude/continuity.settings.example.json")


def _root() -> Path:
    return Path(str(files("agent_workspace_continuity").joinpath("template_data")))


def paths(*, include_optional: bool = False, with_claude_hooks: bool = False) -> tuple[str, ...]:
    out = list(REQUIRED)
    if include_optional:
        out.extend(OPTIONAL)
    if with_claude_hooks:
        out.extend(CLAUDE)
    return tuple(out)


def render(*, profile: str, relative: str, context: dict[str, str]) -> str:
    if profile not in SUPPORTED_PROFILES:
        raise ValueError(f"unsupported profile: {profile}")
    group = profile
    if relative in OPTIONAL:
        group = "optional"
    elif relative in CLAUDE:
        group = "claude"
    target = _root() / group / relative
    if not target.is_file():
        raise FileNotFoundError(target)
    return Template(target.read_text(encoding="utf-8")).safe_substitute(context)
