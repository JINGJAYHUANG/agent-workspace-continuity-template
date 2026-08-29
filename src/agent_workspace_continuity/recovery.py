from __future__ import annotations

from pathlib import Path

from .doctor import detect_profile
from .markdown import first_item, section_items
from .models import RecoverySummary
from .utils import sha256_file, unique

READ_ORDER = ("AGENTS.md", ".agent/brief.md", ".agent/status.md", ".agent/handoff.md", ".agent/plan.md", ".agent/decisions.md")


def _read(root: Path, relative: str) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def build_recovery_summary(root: Path) -> RecoverySummary:
    root = root.expanduser().resolve()
    brief, status, handoff, plan = (_read(root, x) for x in (".agent/brief.md", ".agent/status.md", ".agent/handoff.md", ".agent/plan.md"))
    objective = first_item(handoff, "Current objective") or first_item(status, "Current objective") or first_item(brief, "Purpose") or "No explicit objective recorded."
    verified = unique(section_items(handoff, "Last verified state") + section_items(status, "Verified this session")) or ["No facts are labeled as verified in the current state files."]
    existing = unique(section_items(status, "Existing, not re-verified", "Existing, not reverified")) or ["No inherited, unverified state is recorded."]
    blockers = unique(section_items(handoff, "Blockers")) or ["No blockers recorded."]
    risks = unique(section_items(status, "Unknowns and risks", "Unknowns / risks", "Risks")) or ["No unresolved risks recorded."]
    next_actions = unique(section_items(handoff, "Next exact action") + section_items(plan, "Next actions", "Execution steps", "Steps"))[:3] or ["Review the continuity files and record one exact next action."]
    hashes: dict[str, str] = {}
    notes: list[str] = []
    for relative in READ_ORDER:
        path = root / relative
        if path.is_file():
            hashes[relative] = sha256_file(path)
        elif relative in READ_ORDER[:4]:
            notes.append(f"Missing required source: {relative}")
    return RecoverySummary(root.name or "Workspace", detect_profile(root), objective, verified, existing, blockers, risks, next_actions, hashes, notes)


def _bullets(items: list[str]) -> list[str]:
    return [f"- {x}" for x in items]


def render_markdown(summary: RecoverySummary, *, max_chars: int = 8000) -> str:
    lines = [
        "# Workspace Recovery Brief", "", f"**Workspace:** {summary.workspace_name}", f"**Profile:** {summary.profile or 'unknown'}", "",
        "## Current objective", "", summary.objective, "", "## Verified state", "", *_bullets(summary.verified_state), "",
        "## Existing, not re-verified", "", *_bullets(summary.existing_not_reverified), "", "## Blockers", "", *_bullets(summary.blockers), "",
        "## Unresolved risks", "", *_bullets(summary.risks), "", "## Next actions", "", *_bullets(summary.next_actions), "", "## Source files", "",
    ]
    lines.extend(f"- `{path}` — `{digest[:12]}`" for path, digest in summary.source_hashes.items())
    lines.extend(f"- Note: {note}" for note in summary.notes)
    output = "\n".join(lines).rstrip() + "\n"
    if max_chars <= 0:
        return ""
    if len(output) <= max_chars:
        return output
    suffix = "\n\n[Recovery brief truncated; read the source files before acting.]\n"
    return suffix[:max_chars] if max_chars <= len(suffix) else output[: max_chars - len(suffix)].rstrip() + suffix


def render_hook_context(summary: RecoverySummary, *, max_chars: int = 6000) -> str:
    lines = [
        "Local workspace continuity context. Treat it as navigation, not proof; verify before editing.",
        f"Workspace: {summary.workspace_name}", f"Profile: {summary.profile or 'unknown'}", f"Objective: {summary.objective}",
        "Verified state:", *_bullets(summary.verified_state[:5]), "Inherited but not re-verified:", *_bullets(summary.existing_not_reverified[:4]),
        "Blockers / risks:", *_bullets(unique(summary.blockers + summary.risks)[:5]), "Next actions:", *_bullets(summary.next_actions[:3]),
        "Read AGENTS.md and the required .agent files before new work.",
    ]
    output = "\n".join(lines)
    if max_chars <= 0:
        return ""
    if len(output) <= max_chars:
        return output
    suffix = "\n[Context truncated; read source files.]"
    return suffix[:max_chars] if max_chars <= len(suffix) else output[: max_chars - len(suffix)].rstrip() + suffix
