from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .utils import utc_now, utc_now_iso, write_text_atomic


@dataclass(frozen=True, slots=True)
class HandoffInput:
    objective: str
    verified_state: tuple[str, ...]
    blockers: tuple[str, ...]
    next_actions: tuple[str, ...]
    validation: tuple[str, ...] = ()
    changed: tuple[str, ...] = ()


def bullets(items: tuple[str, ...], empty: str) -> list[str]:
    values = [x.strip() for x in items if x.strip()]
    return [f"- {x}" for x in values] or [f"- {empty}"]


def render_handoff(data: HandoffInput) -> str:
    lines = [
        "<!-- awc:state=handoff schema=1 -->", "# Handoff", "", f"**Last updated:** {utc_now_iso()}", "",
        "## Current objective", "", data.objective.strip() or "No objective recorded.", "", "## Last verified state", "", *bullets(data.verified_state, "No verified state recorded."), "",
        "## Changes made", "", *bullets(data.changed, "No changes recorded."), "", "## Blockers", "", *bullets(data.blockers, "No blockers recorded."), "",
        "## Next exact action", "", *bullets(data.next_actions, "Review the state files and define one exact action."), "", "## Validation", "", *bullets(data.validation, "No validation recorded."), "",
    ]
    return "\n".join(lines)


def write_handoff(root: Path, data: HandoffInput) -> Path:
    root = root.expanduser().resolve()
    target = root / ".agent/handoff.md"
    if target.is_file():
        backup = root / ".agent/local/backups" / f"handoff-{utc_now().strftime('%Y%m%dT%H%M%S%fZ')}.md"
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
    write_text_atomic(target, render_handoff(data))
    return target
