from __future__ import annotations

from pathlib import Path


def test_cli_init_is_preview_then_apply(tmp_path: Path, run_cli) -> None:
    root = tmp_path / "demo"
    preview = run_cli("init", str(root), "--profile", "project")
    assert preview.returncode == 0
    assert "CREATE" in preview.stdout
    assert not root.exists()
    applied = run_cli("init", str(root), "--profile", "project", "--apply")
    assert applied.returncode == 0
    assert (root / "AGENTS.md").is_file()


def test_cli_doctor_and_recover(installed_project: Path, run_cli) -> None:
    doctor = run_cli("doctor", str(installed_project), "--strict")
    assert doctor.returncode == 0
    assert "HEALTHY" in doctor.stdout
    recover = run_cli("recover", str(installed_project), "--max-chars", "1200")
    assert recover.returncode == 0
    assert "Workspace Recovery Brief" in recover.stdout
    assert len(recover.stdout) <= 1201


def test_cli_privacy_returns_failure_on_finding(tmp_path: Path, run_cli) -> None:
    (tmp_path / "bad.md").write_text("token" + "=" + "super-secret-value-123456\n", encoding="utf-8")
    result = run_cli("privacy", str(tmp_path))
    assert result.returncode == 1
    assert "SECRET" in result.stdout
