from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from agent_workspace_continuity.doctor import run_doctor
from agent_workspace_continuity.installer import apply_install


def codes(report) -> set[str]:
    return {item.code for item in report.diagnostics}


def test_healthy_scaffold_has_no_errors(installed_project: Path) -> None:
    report = run_doctor(installed_project)
    assert report.healthy
    assert not report.warnings
    assert "DOCTOR.HEALTHY" in codes(report)


def test_missing_required_file_is_error(installed_project: Path) -> None:
    (installed_project / ".agent/handoff.md").unlink()
    report = run_doctor(installed_project)
    assert "STRUCTURE.MISSING_FILE" in codes(report)
    assert not report.healthy


def test_claude_import_is_required(installed_project: Path) -> None:
    (installed_project / "CLAUDE.md").write_text("# Claude\n", encoding="utf-8")
    assert "CLAUDE.MISSING_IMPORT" in codes(run_doctor(installed_project))


def test_evidence_boundary_is_required(installed_project: Path) -> None:
    path = installed_project / ".agent/status.md"
    text = path.read_text(encoding="utf-8").replace("Existing, not re-verified", "Prior state")
    path.write_text(text, encoding="utf-8")
    report = run_doctor(installed_project)
    assert "EVIDENCE.NO_REVERIFICATION_BOUNDARY" in codes(report)


def test_stale_state_is_warning(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    apply_install(root, profile="project")
    path = root / ".agent/status.md"
    old = (datetime.now(UTC) - timedelta(days=90)).date().isoformat()
    path.write_text(path.read_text(encoding="utf-8").replace(datetime.now(UTC).date().isoformat(), old), encoding="utf-8")
    assert "FRESHNESS.STALE" in codes(run_doctor(root, stale_after_days=30))


def test_incomplete_local_gitignore_is_warning(installed_project: Path) -> None:
    (installed_project / ".agent/.gitignore").write_text("local/\n", encoding="utf-8")
    assert "LOCAL_STATE.INCOMPLETE_GITIGNORE" in codes(run_doctor(installed_project))
