from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def installed_project(tmp_path: Path) -> Path:
    from agent_workspace_continuity.installer import apply_install

    root = tmp_path / "orbit-notes"
    apply_install(root, profile="project", include_optional=True, with_claude_hooks=True)
    return root


@pytest.fixture
def run_cli():
    def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
        return subprocess.run(
            [sys.executable, "-m", "agent_workspace_continuity", *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    return _run
