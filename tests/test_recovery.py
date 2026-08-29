from __future__ import annotations

from pathlib import Path

from agent_workspace_continuity.recovery import build_recovery_summary, render_markdown


def test_recovery_is_deterministic(installed_project: Path) -> None:
    first = render_markdown(build_recovery_summary(installed_project))
    second = render_markdown(build_recovery_summary(installed_project))
    assert first == second
    assert "Existing, not re-verified" in first


def test_recovery_respects_normal_bound(installed_project: Path) -> None:
    value = render_markdown(build_recovery_summary(installed_project), max_chars=500)
    assert len(value) <= 500
    assert "truncated" in value.lower()


def test_recovery_respects_tiny_bound(installed_project: Path) -> None:
    value = render_markdown(build_recovery_summary(installed_project), max_chars=10)
    assert len(value) <= 10


def test_recovery_records_missing_required_sources(installed_project: Path) -> None:
    (installed_project / ".agent/status.md").unlink()
    summary = build_recovery_summary(installed_project)
    assert any(".agent/status.md" in note for note in summary.notes)
