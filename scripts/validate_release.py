#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_workspace_continuity.doctor import run_doctor
from agent_workspace_continuity.privacy import scan_privacy


def run(args: list[str], *, cwd: Path = ROOT) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(args),
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--json-output")
    args = parser.parse_args()

    failures: list[str] = []
    checks: dict[str, object] = {}

    compile_check = run([sys.executable, "-m", "compileall", "-q", "src", "scripts"])
    checks["compileall"] = compile_check
    require(compile_check["returncode"] == 0, "compileall failed", failures)

    if not args.skip_tests:
        tests = run([sys.executable, "-m", "pytest", "-q"])
        checks["pytest"] = tests
        require(tests["returncode"] == 0, "pytest failed", failures)

    example_tests = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT / "examples/synthetic_project")
    checks["synthetic_project_tests"] = example_tests
    require(example_tests["returncode"] == 0, "synthetic project tests failed", failures)

    doctor_results: dict[str, object] = {}
    for name, path in {
        "repository": ROOT,
        "synthetic_project": ROOT / "examples/synthetic_project",
        "synthetic_umbrella": ROOT / "examples/synthetic_umbrella",
    }.items():
        report = run_doctor(path)
        doctor_results[name] = report.to_dict()
        require(report.healthy, f"doctor failed for {name}", failures)
        require(not report.warnings, f"doctor warnings for {name}", failures)
    checks["doctor"] = doctor_results

    privacy = scan_privacy(ROOT)
    checks["privacy"] = {
        "files_scanned": privacy.files_scanned,
        "diagnostics": [item.to_dict() for item in privacy.diagnostics],
    }
    require(not privacy.diagnostics, "privacy scan reported findings", failures)

    settings_path = ROOT / "src/agent_workspace_continuity/template_data/claude/.claude/continuity.settings.example.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        settings = None
        failures.append(f"Claude settings JSON invalid: {exc}")
    checks["claude_settings_json"] = {"valid": settings is not None}
    if settings:
        events = set(settings.get("hooks", {}))
        require(events == {"SessionStart", "PostCompact", "Stop", "SessionEnd"}, "unexpected Claude hook event set", failures)

    required_docs = {
        "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md",
        "docs/architecture.md", "docs/evidence-model.md", "docs/claude-code-hooks.md",
        "docs/threat-model.md", "docs/design-decisions.md", "docs/migration.md", "docs/compatibility.md",
    }
    missing = sorted(relative for relative in required_docs if not (ROOT / relative).is_file())
    checks["required_docs"] = {"missing": missing}
    require(not missing, f"missing release documents: {missing}", failures)

    runtime_dependencies = []
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    require("dependencies = []" in pyproject, "runtime dependency declaration is not empty", failures)
    checks["runtime_dependencies"] = runtime_dependencies

    summary = {
        "schema": 1,
        "status": "pass" if not failures else "fail",
        "python": sys.version.split()[0],
        "checks": checks,
        "failures": failures,
    }
    payload = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True)
    if args.json_output:
        output = Path(args.json_output)
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
