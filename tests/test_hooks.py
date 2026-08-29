from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_hook(root: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(root)
    return subprocess.run(
        [sys.executable, str(root / ".claude/hooks/continuity_hook.py")],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def event_rows(root: Path) -> list[dict]:
    path = root / ".agent/local/hook-events.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_session_start_injects_bounded_context(installed_project: Path) -> None:
    result = run_hook(installed_project, {"hook_event_name": "SessionStart", "source": "resume", "session_id": "private-session"})
    assert result.returncode == 0
    data = json.loads(result.stdout)
    context = data["hookSpecificOutput"]["additionalContext"]
    assert len(context) <= 6000
    assert "Treat this as navigation, not proof" in context
    rows = event_rows(installed_project)
    assert rows[-1]["source"] == "resume"
    assert "private-session" not in (installed_project / ".agent/local/hook-events.jsonl").read_text(encoding="utf-8")


def test_stop_logs_hash_not_message_and_does_not_continue(installed_project: Path) -> None:
    secret_text = "raw assistant output that must not be stored"
    result = run_hook(installed_project, {"hook_event_name": "Stop", "last_assistant_message": secret_text, "stop_hook_active": True})
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}
    log = (installed_project / ".agent/local/hook-events.jsonl").read_text(encoding="utf-8")
    assert secret_text not in log
    assert event_rows(installed_project)[-1]["message_length"] == len(secret_text)


def test_untrusted_enum_values_are_sanitized(installed_project: Path) -> None:
    run_hook(installed_project, {"hook_event_name": "SessionStart", "source": "../../private/path"})
    run_hook(installed_project, {"hook_event_name": "SessionEnd", "reason": "token=do-not-log"})
    rows = event_rows(installed_project)
    assert rows[-2]["source"] == "other"
    assert rows[-1]["reason"] == "other"
    log = (installed_project / ".agent/local/hook-events.jsonl").read_text(encoding="utf-8")
    assert "private/path" not in log
    assert "do-not-log" not in log


def test_hook_fails_open_on_unusable_project_dir(installed_project: Path, tmp_path: Path) -> None:
    hook = installed_project / ".claude/hooks/continuity_hook.py"
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path / "missing" / "child")
    result = subprocess.run([sys.executable, str(hook)], input="not-json", text=True, capture_output=True, env=env, check=False)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


def test_untrusted_event_name_is_not_logged(installed_project: Path) -> None:
    result = run_hook(installed_project, {"hook_event_name": "Stop;token=private-value"})
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}
    row = event_rows(installed_project)[-1]
    assert row["event"] == "Unknown"
    assert "private-value" not in (installed_project / ".agent/local/hook-events.jsonl").read_text(encoding="utf-8")
