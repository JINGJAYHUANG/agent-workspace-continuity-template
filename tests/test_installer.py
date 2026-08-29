from __future__ import annotations

from pathlib import Path

from agent_workspace_continuity.installer import apply_install, plan_install


def test_preview_is_read_only(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    operations = plan_install(root, profile="project")
    assert len(operations) == 6
    assert all(op.kind == "create" for op in operations)
    assert not root.exists()


def test_apply_creates_minimum_scaffold(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    result = apply_install(root, profile="project")
    assert len(result.created) == 6
    assert (root / "AGENTS.md").is_file()
    assert (root / "CLAUDE.md").is_file()
    assert (root / ".agent/handoff.md").is_file()
    assert not (root / ".agent/plan.md").exists()


def test_optional_files_and_hooks_are_opt_in(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    apply_install(root, profile="project", include_optional=True, with_claude_hooks=True)
    assert (root / ".agent/plan.md").is_file()
    assert (root / ".agent/decisions.md").is_file()
    assert (root / ".claude/hooks/continuity_hook.py").is_file()
    assert (root / ".claude/continuity.settings.example.json").is_file()


def test_unrelated_existing_file_is_not_overwritten(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    root.mkdir()
    original = "# My rules\n"
    (root / "AGENTS.md").write_text(original, encoding="utf-8")
    result = apply_install(root, profile="project")
    assert (root / "AGENTS.md").read_text(encoding="utf-8") == original
    proposal = next(op for op in result.operations if op.relative_path == "AGENTS.md")
    assert proposal.kind == "proposal"
    assert proposal.proposed_path
    assert (root / proposal.proposed_path).is_file()


def test_umbrella_profile_has_non_recursive_rule(tmp_path: Path) -> None:
    root = tmp_path / "studio-hub"
    apply_install(root, profile="umbrella")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert "awc:profile=umbrella" in agents
    assert "Do not recursively scan" in agents


def test_reinstall_preserves_edited_managed_state(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    apply_install(root, profile="project")
    status = root / ".agent/status.md"
    status.write_text(status.read_text(encoding="utf-8") + "\n- User-authored verified note.\n", encoding="utf-8")
    second = apply_install(root, profile="project")
    op = next(item for item in second.operations if item.relative_path == ".agent/status.md")
    assert op.kind == "unchanged"
    assert "User-authored verified note" in status.read_text(encoding="utf-8")


def test_profile_switch_requires_manual_merge(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    apply_install(root, profile="project")
    result = apply_install(root, profile="umbrella")
    profile_specific = [op for op in result.operations if op.relative_path in {"AGENTS.md", "CLAUDE.md", ".agent/brief.md"}]
    assert all(op.kind == "proposal" for op in profile_specific)
    assert "awc:profile=project" in (root / "AGENTS.md").read_text(encoding="utf-8")


def test_no_proposals_leaves_conflict_as_conflict(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    root.mkdir()
    (root / "AGENTS.md").write_text("custom\n", encoding="utf-8")
    result = apply_install(root, profile="project", write_proposals=False)
    op = next(item for item in result.operations if item.relative_path == "AGENTS.md")
    assert op.kind == "conflict"
    assert not (root / ".agent/local/proposals").exists()
