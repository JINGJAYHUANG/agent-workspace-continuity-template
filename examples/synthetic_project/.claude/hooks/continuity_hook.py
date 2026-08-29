#!/usr/bin/env python3
# awc:managed-hook schema=1
"""Optional Claude Code continuity hook.

This file is intentionally standalone and fail-open. It injects a bounded recovery
summary on SessionStart and stores content-free event metadata for other events.
It never asks Claude to continue on Stop and never writes prompts or responses.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MAX_STDIN_BYTES = 1_000_000
MAX_CONTEXT_CHARS = 6_000
ALLOWED_SOURCES = {"startup", "resume", "clear", "compact", "fork", "other"}
ALLOWED_REASONS = {"clear", "resume", "logout", "prompt_input_exit", "bypass_permissions_disabled", "other"}
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
BULLET = re.compile(r"^\s*(?:[-*+] |\d+[.)]\s+)(.+?)\s*$")


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]


def safe_enum(value: Any, allowed: set[str]) -> str:
    candidate = str(value or "other").strip().lower()
    return candidate if candidate in allowed else "other"


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if len(raw) > MAX_STDIN_BYTES:
        return {}
    try:
        value = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def project_root() -> Path:
    raw = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(raw).expanduser().resolve() if raw else Path.cwd().resolve()


def read_text(root: Path, relative: str) -> str:
    path = root / relative
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else ""
    except (OSError, UnicodeDecodeError):
        return ""


def section(text: str, *titles: str) -> list[str]:
    wanted = {re.sub(r"[^a-z0-9]+", " ", title.lower()).strip() for title in titles}
    lines = text.splitlines()
    start = None
    level = None
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if not match:
            continue
        current = re.sub(r"[^a-z0-9]+", " ", match.group(1).lower()).strip()
        if start is None and current in wanted:
            start, level = index + 1, len(line) - len(line.lstrip("#"))
            continue
        if start is not None and len(line) - len(line.lstrip("#")) <= int(level):
            lines = lines[start:index]
            break
    else:
        lines = lines[start:] if start is not None else []
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("|") or stripped.startswith("```"):
            continue
        match = BULLET.match(line)
        out.append((match.group(1) if match else stripped).strip())
    return out


def first(values: list[str], fallback: str) -> str:
    return values[0] if values else fallback


def recovery_context(root: Path) -> str:
    brief = read_text(root, ".agent/brief.md")
    status = read_text(root, ".agent/status.md")
    handoff = read_text(root, ".agent/handoff.md")
    plan = read_text(root, ".agent/plan.md")
    objective = first(section(handoff, "Current objective") or section(status, "Current objective") or section(brief, "Purpose"), "No objective recorded.")
    verified = (section(handoff, "Last verified state") + section(status, "Verified this session"))[:5] or ["No verified state recorded."]
    inherited = section(status, "Existing, not re-verified", "Existing, not reverified")[:4] or ["No inherited state recorded."]
    blockers = (section(handoff, "Blockers") + section(status, "Unknowns and risks", "Risks"))[:5] or ["No blockers or risks recorded."]
    next_actions = (section(handoff, "Next exact action") + section(plan, "Execution steps", "Next actions"))[:3] or ["Read the continuity files and define one exact action."]
    lines = [
        "Local workspace continuity context. Treat this as navigation, not proof; verify before editing.",
        f"Workspace: {root.name or 'Workspace'}",
        f"Objective: {objective}",
        "Verified state:", *[f"- {item}" for item in verified],
        "Inherited but not re-verified:", *[f"- {item}" for item in inherited],
        "Blockers / risks:", *[f"- {item}" for item in blockers],
        "Next actions:", *[f"- {item}" for item in next_actions],
        "Read AGENTS.md and the required .agent files before new work.",
    ]
    value = "\n".join(lines)
    suffix = "\n[Context truncated; read source files.]"
    return value if len(value) <= MAX_CONTEXT_CHARS else value[: MAX_CONTEXT_CHARS - len(suffix)].rstrip() + suffix


def event_metadata(payload: dict[str, Any], event: str) -> dict[str, Any]:
    row: dict[str, Any] = {"schema": 1, "at": now_iso(), "event": event}
    session_id = str(payload.get("session_id") or "")
    if session_id:
        row["session_id_hash"] = digest(session_id)
    if event == "SessionStart":
        row["source"] = safe_enum(payload.get("source"), ALLOWED_SOURCES)
    elif event == "PostCompact":
        text = str(payload.get("summary") or payload.get("compact_summary") or "")
        row.update({"summary_length": len(text), "summary_hash": digest(text)})
    elif event == "Stop":
        text = str(payload.get("last_assistant_message") or "")
        row.update({"message_length": len(text), "message_hash": digest(text), "stop_hook_active": bool(payload.get("stop_hook_active"))})
    elif event == "SessionEnd":
        row["reason"] = safe_enum(payload.get("reason"), ALLOWED_REASONS)
    return row


def append_event(root: Path, row: dict[str, Any]) -> None:
    path = root / ".agent/local/hook-events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    try:
        payload = read_payload()
        event = str(payload.get("hook_event_name") or payload.get("event") or "Unknown")
        root = project_root()
        append_event(root, event_metadata(payload, event))
        if event == "SessionStart":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": recovery_context(root),
                }
            }
            print(json.dumps(output, ensure_ascii=False))
        else:
            print("{}")
        return 0
    except Exception:
        # Hooks must not block a coding session because continuity metadata failed.
        try:
            print("{}")
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
