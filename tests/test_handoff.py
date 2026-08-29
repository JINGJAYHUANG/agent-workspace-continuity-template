from __future__ import annotations

from pathlib import Path

from agent_workspace_continuity.handoff import HandoffInput, write_handoff


def sample() -> HandoffInput:
    return HandoffInput(
        objective="Ship a validated parser.",
        verified_state=("Parser tests passed.",),
        blockers=("Fixture license needs review.",),
        next_actions=("Review the fixture license.",),
        validation=("pytest passed.",),
        changed=("Added parser module.",),
    )


def test_handoff_contains_required_sections(installed_project: Path) -> None:
    path = write_handoff(installed_project, sample())
    text = path.read_text(encoding="utf-8")
    for heading in ("Current objective", "Last verified state", "Changes made", "Blockers", "Next exact action", "Validation"):
        assert f"## {heading}" in text


def test_handoff_backs_up_previous_file(installed_project: Path) -> None:
    original = (installed_project / ".agent/handoff.md").read_text(encoding="utf-8")
    write_handoff(installed_project, sample())
    backups = list((installed_project / ".agent/local/backups").glob("handoff-*.md"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == original


def test_rapid_handoffs_create_distinct_backups(installed_project: Path) -> None:
    write_handoff(installed_project, sample())
    write_handoff(installed_project, sample())
    backups = list((installed_project / ".agent/local/backups").glob("handoff-*.md"))
    assert len(backups) == 2
    assert len({path.name for path in backups}) == 2
