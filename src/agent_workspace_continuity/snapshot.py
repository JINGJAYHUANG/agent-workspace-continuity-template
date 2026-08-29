from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

from .doctor import detect_profile
from .templates import OPTIONAL, REQUIRED
from .utils import json_dumps, run_command, utc_now_iso, write_text_atomic


def _git_value(root: Path, *args: str) -> str | None:
    result = run_command(["git", *args], cwd=root)
    if result is None or result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _git_snapshot(root: Path) -> dict[str, Any]:
    inside = _git_value(root, "rev-parse", "--is-inside-work-tree") == "true"
    if not inside:
        return {"available": _git_value(root, "--version") is not None, "is_repository": False}
    status = run_command(["git", "status", "--porcelain=v1", "--untracked-files=normal"], cwd=root)
    rows = [] if status is None or status.returncode != 0 else [line for line in status.stdout.splitlines() if line]
    staged = sum(bool(line[:1].strip() and line[:1] != "?") for line in rows)
    unstaged = sum(bool(len(line) > 1 and line[1:2].strip() and line[:2] != "??") for line in rows)
    untracked = sum(line.startswith("??") for line in rows)
    head = _git_value(root, "rev-parse", "HEAD")
    return {
        "available": True,
        "is_repository": True,
        "branch": _git_value(root, "branch", "--show-current") or "detached",
        "head": head[:12] if head else None,
        "changes": {"total": len(rows), "staged": staged, "unstaged": unstaged, "untracked": untracked},
    }


def capture_snapshot(root: Path) -> dict[str, Any]:
    """Capture a privacy-minimized workspace snapshot.

    The result intentionally omits the absolute root path, user name, host name,
    environment variables, file names, command output, and file contents.
    """

    root = root.expanduser().resolve()
    required_present = sum((root / relative).is_file() for relative in REQUIRED)
    optional_present = sum((root / relative).is_file() for relative in OPTIONAL)
    child_directories = 0
    try:
        child_directories = sum(
            path.is_dir() and path.name not in {".git", ".agent", ".claude", ".venv", "node_modules"}
            for path in root.iterdir()
        )
    except OSError:
        pass
    return {
        "schema": 1,
        "captured_at": utc_now_iso(),
        "workspace": {
            "name": root.name or "Workspace",
            "profile": detect_profile(root),
            "required_files_present": required_present,
            "required_files_expected": len(REQUIRED),
            "optional_files_present": optional_present,
            "first_level_child_directory_count": child_directories,
        },
        "runtime": {
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "implementation": platform.python_implementation(),
            "os_family": os.name,
        },
        "git": _git_snapshot(root),
        "privacy": {
            "absolute_paths_included": False,
            "file_names_included": False,
            "environment_values_included": False,
            "file_contents_included": False,
        },
    }


def write_snapshot(root: Path, output: Path | None = None) -> Path:
    root = root.expanduser().resolve()
    target = output or root / ".agent/runtime-snapshot.json"
    if not target.is_absolute():
        target = root / target
    write_text_atomic(target, json_dumps(capture_snapshot(root)))
    return target


def render_snapshot(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True)
