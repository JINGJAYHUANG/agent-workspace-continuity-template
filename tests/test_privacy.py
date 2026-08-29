from __future__ import annotations

from pathlib import Path

from agent_workspace_continuity.privacy import scan_privacy


def test_detects_common_secret(tmp_path: Path) -> None:
    (tmp_path / "bad.md").write_text("api_key = '" + "sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz123456'\n", encoding="utf-8")
    result = scan_privacy(tmp_path)
    assert any(item.code.startswith("SECRET") for item in result.diagnostics)


def test_detects_user_home_paths(tmp_path: Path) -> None:
    (tmp_path / "bad.md").write_text("C:\\" + "Users\\private-user\\work\n/" + "Users/private-user/work\n/" + "home/private-user/work\n", encoding="utf-8")
    result = scan_privacy(tmp_path)
    codes = {item.code for item in result.diagnostics}
    assert {"PRIVACY.WINDOWS_USER_PATH", "PRIVACY.MAC_USER_PATH", "PRIVACY.LINUX_USER_PATH"} <= codes


def test_clean_relative_content_passes(tmp_path: Path) -> None:
    (tmp_path / "good.md").write_text("Read `.agent/status.md` and use environment variables for secrets.\n", encoding="utf-8")
    assert not scan_privacy(tmp_path).diagnostics


def test_claude_runtime_tokens_are_allowed(tmp_path: Path) -> None:
    (tmp_path / "settings.json").write_text('{"command":"python ${CLAUDE_PROJECT_DIR}/hook.py","env":"${CLAUDE_ENV_FILE}"}\n', encoding="utf-8")
    assert not scan_privacy(tmp_path).diagnostics


def test_packaged_template_tokens_are_allowed_only_in_template_data(tmp_path: Path) -> None:
    template = tmp_path / "template_data" / "project"
    template.mkdir(parents=True)
    (template / "brief.md").write_text("Workspace: ${" + "WORKSPACE_NAME} on ${" + "GENERATED_DATE}\n", encoding="utf-8")
    assert not scan_privacy(tmp_path).diagnostics
    (tmp_path / "ordinary.md").write_text("Workspace: ${" + "WORKSPACE_NAME}\n", encoding="utf-8")
    assert any(item.code == "PLACEHOLDER.TEMPLATE_TOKEN" for item in scan_privacy(tmp_path).diagnostics)


def test_github_actions_expressions_are_not_template_residue(tmp_path: Path) -> None:
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    expression = "$" + "{" + "{ matrix.python-version }" + "}"
    (workflow / "ci.yml").write_text("python-version: " + expression + "\n", encoding="utf-8")
    assert not scan_privacy(tmp_path).diagnostics
