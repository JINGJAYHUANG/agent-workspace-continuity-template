from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agent_workspace_continuity.snapshot import capture_snapshot, write_snapshot


def test_snapshot_omits_absolute_paths_and_file_names(installed_project: Path) -> None:
    snapshot = capture_snapshot(installed_project)
    payload = json.dumps(snapshot)
    assert str(installed_project) not in payload
    assert "AGENTS.md" not in payload
    assert snapshot["privacy"]["absolute_paths_included"] is False


def test_snapshot_reports_git_counts_without_changed_names(installed_project: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=installed_project, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=installed_project, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=installed_project, check=True)
    subprocess.run(["git", "add", "."], cwd=installed_project, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=installed_project, check=True)
    (installed_project / "secret-filename.txt").write_text("local\n", encoding="utf-8")
    target = write_snapshot(installed_project)
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["git"]["changes"]["untracked"] == 1
    assert "secret-filename" not in target.read_text(encoding="utf-8")
