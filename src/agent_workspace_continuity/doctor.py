from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from .markdown import find_section
from .models import Diagnostic, DoctorReport
from .privacy import scan_privacy

REQUIRED_FILES = ("AGENTS.md", "CLAUDE.md", ".agent/brief.md", ".agent/status.md", ".agent/handoff.md")
HEADINGS = {
    ".agent/brief.md": (("Purpose",), ("In scope",), ("Out of scope",), ("Constraints",), ("Acceptance criteria",)),
    ".agent/status.md": (("Current objective",), ("Verified this session",), ("Existing, not re-verified", "Existing, not reverified"), ("Unknowns and risks", "Unknowns / risks", "Risks")),
    ".agent/handoff.md": (("Current objective",), ("Last verified state",), ("Blockers",), ("Next exact action",)),
}
PROFILE_RE = re.compile(r"<!--\s*awc:profile=(project|umbrella)\s+schema=(\d+)\s*-->")
UPDATED_RE = re.compile(r"(?im)^\*\*Last updated:\*\*\s*(\d{4}-\d{2}-\d{2})(?:T[^\s]+)?")


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def detect_profile(root: Path) -> str | None:
    for relative in (".agent/brief.md", "AGENTS.md"):
        text = _read(root / relative)
        match = PROFILE_RE.search(text or "")
        if match:
            return match.group(1)
    return None


def run_doctor(root: Path, *, stale_after_days: int = 30) -> DoctorReport:
    root = root.expanduser().resolve()
    diagnostics: list[Diagnostic] = []
    if not root.exists() or not root.is_dir():
        code = "ROOT.NOT_FOUND" if not root.exists() else "ROOT.NOT_DIRECTORY"
        diagnostics.append(Diagnostic(code, "error", "Workspace root is unavailable.", str(root)))
        return DoctorReport(root, None, diagnostics)
    profile = detect_profile(root)
    diagnostics.append(Diagnostic("PROFILE.DETECTED", "info", f"Detected '{profile}' continuity profile.")) if profile else diagnostics.append(Diagnostic("PROFILE.UNKNOWN", "warning", "Could not detect project or umbrella profile."))
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            diagnostics.append(Diagnostic("STRUCTURE.MISSING_FILE", "error", "Required continuity file is missing.", relative, "Run 'awc init' in preview mode."))
        elif not path.is_file():
            diagnostics.append(Diagnostic("STRUCTURE.NOT_FILE", "error", "Expected a regular file.", relative))
    claude = _read(root / "CLAUDE.md")
    if claude is not None and "@AGENTS.md" not in claude:
        diagnostics.append(Diagnostic("CLAUDE.MISSING_IMPORT", "error", "CLAUDE.md does not import @AGENTS.md.", "CLAUDE.md"))
    agents = _read(root / "AGENTS.md")
    if agents is not None:
        if len(agents.splitlines()) > 200:
            diagnostics.append(Diagnostic("INSTRUCTIONS.TOO_LONG", "warning", "AGENTS.md exceeds 200 lines.", "AGENTS.md"))
        for phrase, code in (("do not rely on chat history", "INSTRUCTIONS.NO_CHAT_HISTORY_RULE"), ("read `.agent/", "INSTRUCTIONS.NO_STATE_READ_RULE")):
            if phrase not in agents.lower():
                diagnostics.append(Diagnostic(code, "warning", f"Expected rule not found: {phrase}", "AGENTS.md"))
    for relative, groups in HEADINGS.items():
        text = _read(root / relative)
        if text is None:
            continue
        for aliases in groups:
            if find_section(text, *aliases) is None:
                diagnostics.append(Diagnostic("STRUCTURE.MISSING_HEADING", "error", f"Missing heading: {aliases[0]}", relative))
    for relative in (".agent/status.md", ".agent/handoff.md"):
        text = _read(root / relative)
        if text is None:
            continue
        match = UPDATED_RE.search(text)
        if not match:
            diagnostics.append(Diagnostic("FRESHNESS.MISSING_DATE", "warning", "No parseable Last updated date.", relative))
        else:
            observed = datetime.fromisoformat(match.group(1)).replace(tzinfo=UTC)
            age = (datetime.now(UTC) - observed).days
            if age > stale_after_days:
                diagnostics.append(Diagnostic("FRESHNESS.STALE", "warning", f"State file is {age} days old.", relative))
    status = _read(root / ".agent/status.md")
    if status is not None and "not re-verified" not in status.lower():
        diagnostics.append(Diagnostic("EVIDENCE.NO_REVERIFICATION_BOUNDARY", "error", "status.md does not distinguish inherited state.", ".agent/status.md"))
    ignore = _read(root / ".agent/.gitignore")
    if ignore is None:
        diagnostics.append(Diagnostic("LOCAL_STATE.NO_GITIGNORE", "warning", ".agent/.gitignore is missing.", ".agent/.gitignore"))
    else:
        for rule in ("local/", "logs/", "backups/", "runtime-snapshot.json"):
            if rule not in ignore:
                diagnostics.append(Diagnostic("LOCAL_STATE.INCOMPLETE_GITIGNORE", "warning", f"Missing ignore rule: {rule}", ".agent/.gitignore"))
    for relative in (".agent/plan.md", ".agent/decisions.md"):
        if (root / relative).exists():
            diagnostics.append(Diagnostic("OPTIONAL.PRESENT", "info", "Optional state file is present.", relative))
    privacy = scan_privacy(root, continuity_only=True, include_placeholders=True)
    diagnostics.extend(privacy.diagnostics)
    if not any(d.severity == "error" for d in diagnostics):
        diagnostics.append(Diagnostic("DOCTOR.HEALTHY", "info", f"Required checks passed ({privacy.files_scanned} files scanned)."))
    return DoctorReport(root, profile, diagnostics)


def render_report(report: DoctorReport) -> str:
    labels = {"info": "INFO", "warning": "WARN", "error": "ERROR"}
    lines = [f"Workspace: {report.root}", f"Profile: {report.profile or 'unknown'}", f"Result: {'HEALTHY' if report.healthy else 'FAILED'}", ""]
    for item in report.diagnostics:
        location = f" [{item.path}]" if item.path else ""
        lines.append(f"{labels[item.severity]:5s} {item.code}{location}: {item.message}")
        if item.remediation:
            lines.append(f"      Fix: {item.remediation}")
    lines += ["", f"Errors: {len(report.errors)} | Warnings: {len(report.warnings)}"]
    return "\n".join(lines)
