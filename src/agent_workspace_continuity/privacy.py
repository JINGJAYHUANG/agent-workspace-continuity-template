from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import Diagnostic

TEXT_EXTENSIONS = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".py", ".sh", ".ps1", ".ini", ".cfg", ".env"}
EXCLUDED = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
ALLOWED_RUNTIME_TOKENS = ("${CLAUDE_PROJECT_DIR}", "${CLAUDE_ENV_FILE}")
PACKAGE_TEMPLATE_TOKENS = tuple("${" + name + "}" for name in ("WORKSPACE_NAME", "PROFILE", "GENERATED_DATE", "GENERATED_AT", "ROOT_BASENAME"))
SECRET_PATTERNS = (
    ("SECRET.PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "Remove and rotate the private key."),
    ("SECRET.GITHUB_TOKEN", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "Remove and rotate the GitHub token."),
    ("SECRET.OPENAI_KEY", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"), "Remove and rotate the API key."),
    ("SECRET.AWS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "Remove and rotate the AWS key."),
    ("SECRET.GENERIC_ASSIGNMENT", re.compile(r"(?im)^\s*(?:api[_-]?key|token|secret|password|webhook[_-]?url)\s*[:=]\s*['\"]?(?!<|\$\{|example|changeme|redacted)[^\s'\"]{12,}"), "Replace with a documented placeholder."),
)
PATH_PATTERNS = (
    ("PRIVACY.WINDOWS_USER_PATH", re.compile(r"(?i)\b[A-Z]:\\" + r"Users\\" + r"[^\\\s]+"), "Use a relative path or placeholder."),
    ("PRIVACY.MAC_USER_PATH", re.compile(r"/" + r"Users/" + r"[^/\s]+"), "Use a relative path or placeholder."),
    ("PRIVACY.LINUX_USER_PATH", re.compile(r"/" + r"home/" + r"[^/\s]+"), "Use a relative path or placeholder."),
)
PLACEHOLDER_PATTERNS = (
    ("PLACEHOLDER.TEMPLATE_TOKEN", re.compile(r"\$\{?[A-Z][A-Z0-9_]{2,}\}?")),
    ("PLACEHOLDER.ANGLE", re.compile(r"<(?:replace|your|todo)[^>]*>", re.I)),
    ("PLACEHOLDER.CURLY", re.compile(r"\{\{[^}]+\}\}")),
)


@dataclass(frozen=True, slots=True)
class ScanResult:
    files_scanned: int
    diagnostics: tuple[Diagnostic, ...]


def iter_text_files(root: Path, *, continuity_only: bool = False) -> Iterable[Path]:
    if continuity_only:
        candidates = [
            "AGENTS.md", "CLAUDE.md", ".agent/brief.md", ".agent/status.md", ".agent/handoff.md",
            ".agent/plan.md", ".agent/decisions.md", ".claude/continuity.settings.example.json",
            ".claude/hooks/continuity_hook.py",
        ]
        yield from (root / p for p in candidates if (root / p).is_file())
        return
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED for part in path.parts):
            continue
        if ".agent" in path.parts and "local" in path.parts:
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name in {"AGENTS.md", "CLAUDE.md", "LICENSE", "Makefile"}:
            yield path


def scan_privacy(root: Path, *, continuity_only: bool = False, include_placeholders: bool = True) -> ScanResult:
    root = root.expanduser().resolve()
    diagnostics: list[Diagnostic] = []
    count = 0
    for path in iter_text_files(root, continuity_only=continuity_only):
        count += 1
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            diagnostics.append(Diagnostic("SCAN.UNREADABLE", "warning", "Could not decode UTF-8 text.", relative))
            continue
        for code, pattern, remediation in SECRET_PATTERNS + PATH_PATTERNS:
            if pattern.search(text):
                diagnostics.append(Diagnostic(code, "error" if code.startswith("SECRET") else "warning", f"Potential sensitive value found in {relative}.", relative, remediation))
        if include_placeholders:
            candidate = text
            for allowed in ALLOWED_RUNTIME_TOKENS:
                candidate = candidate.replace(allowed, "")
            if "template_data" in path.parts:
                for allowed in PACKAGE_TEMPLATE_TOKENS:
                    candidate = candidate.replace(allowed, "")
            if ".github" in path.parts and "workflows" in path.parts:
                candidate = re.sub(r"\$\{\{.*?\}\}", "", candidate)
            for code, pattern in PLACEHOLDER_PATTERNS:
                if pattern.search(candidate):
                    diagnostics.append(Diagnostic(code, "warning", f"Unresolved template placeholder found in {relative}.", relative, "Replace it with an explicit non-sensitive value."))
    return ScanResult(count, tuple(diagnostics))
