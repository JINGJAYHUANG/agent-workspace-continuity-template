from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .doctor import render_report, run_doctor
from .handoff import HandoffInput, write_handoff
from .installer import apply_install, plan_install
from .privacy import scan_privacy
from .recovery import build_recovery_summary, render_markdown
from .snapshot import capture_snapshot, render_snapshot, write_snapshot
from .utils import json_dumps, write_text_atomic


def _root(value: str) -> Path:
    return Path(value).expanduser()


def _print_operations(operations: Sequence[object], *, json_output: bool) -> None:
    if json_output:
        print(json_dumps([op.to_dict() for op in operations]))
        return
    for op in operations:
        suffix = f" -> {op.proposed_path}" if getattr(op, "proposed_path", None) else ""
        print(f"{op.kind.upper():9s} {op.relative_path}{suffix}\n           {op.reason}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="awc", description="Local-first, evidence-labeled continuity for coding-agent workspaces.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Preview or install a continuity scaffold.")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--profile", choices=("project", "umbrella"), default="project")
    init.add_argument("--name")
    init.add_argument("--include-optional", action="store_true", help="Add plan.md and decisions.md.")
    init.add_argument("--with-claude-hooks", action="store_true", help="Add opt-in Claude Code hook examples.")
    init.add_argument("--apply", action="store_true", help="Write files. Without this flag, init is preview-only.")
    init.add_argument("--no-proposals", action="store_true", help="Do not write proposal copies for conflicts.")
    init.add_argument("--json", action="store_true")

    doctor = sub.add_parser("doctor", help="Validate structure, evidence labels, freshness and privacy.")
    doctor.add_argument("path", nargs="?", default=".")
    doctor.add_argument("--stale-after-days", type=int, default=30)
    doctor.add_argument("--strict", action="store_true", help="Treat warnings as a failing exit status.")
    doctor.add_argument("--json", action="store_true")

    recover = sub.add_parser("recover", help="Build a bounded, deterministic recovery brief.")
    recover.add_argument("path", nargs="?", default=".")
    recover.add_argument("--max-chars", type=int, default=8000)
    recover.add_argument("--format", choices=("markdown", "json"), default="markdown")
    recover.add_argument("--output")

    handoff = sub.add_parser("handoff", help="Write an explicit handoff and back up the previous one locally.")
    handoff.add_argument("path", nargs="?", default=".")
    handoff.add_argument("--objective", required=True)
    handoff.add_argument("--verified", action="append", default=[])
    handoff.add_argument("--changed", action="append", default=[])
    handoff.add_argument("--blocker", action="append", default=[])
    handoff.add_argument("--next", dest="next_actions", action="append", default=[])
    handoff.add_argument("--validation", action="append", default=[])

    snapshot = sub.add_parser("snapshot", help="Capture privacy-minimized runtime and Git counts.")
    snapshot.add_argument("path", nargs="?", default=".")
    snapshot.add_argument("--output")
    snapshot.add_argument("--stdout", action="store_true")

    privacy = sub.add_parser("privacy", help="Scan public text for common secrets, user paths and unresolved placeholders.")
    privacy.add_argument("path", nargs="?", default=".")
    privacy.add_argument("--continuity-only", action="store_true")
    privacy.add_argument("--allow-placeholders", action="store_true")
    privacy.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            root = _root(args.path)
            if args.apply:
                result = apply_install(
                    root,
                    profile=args.profile,
                    name=args.name,
                    include_optional=args.include_optional,
                    with_claude_hooks=args.with_claude_hooks,
                    write_proposals=not args.no_proposals,
                )
                _print_operations(result.operations, json_output=args.json)
                return 2 if any(op.kind in {"conflict", "proposal"} for op in result.operations) else 0
            operations = plan_install(
                root,
                profile=args.profile,
                name=args.name,
                include_optional=args.include_optional,
                with_claude_hooks=args.with_claude_hooks,
            )
            _print_operations(operations, json_output=args.json)
            return 2 if any(op.kind == "conflict" for op in operations) else 0

        if args.command == "doctor":
            report = run_doctor(_root(args.path), stale_after_days=max(0, args.stale_after_days))
            print(json_dumps(report.to_dict()) if args.json else render_report(report))
            return 1 if report.errors or (args.strict and report.warnings) else 0

        if args.command == "recover":
            summary = build_recovery_summary(_root(args.path))
            payload = json_dumps(summary.to_dict()) if args.format == "json" else render_markdown(summary, max_chars=max(0, args.max_chars))
            if args.output:
                write_text_atomic(Path(args.output).expanduser(), payload)
            else:
                print(payload, end="" if payload.endswith("\n") else "\n")
            return 0

        if args.command == "handoff":
            target = write_handoff(
                _root(args.path),
                HandoffInput(
                    objective=args.objective,
                    verified_state=tuple(args.verified),
                    blockers=tuple(args.blocker),
                    next_actions=tuple(args.next_actions),
                    validation=tuple(args.validation),
                    changed=tuple(args.changed),
                ),
            )
            print(target)
            return 0

        if args.command == "snapshot":
            root = _root(args.path)
            if args.stdout:
                print(render_snapshot(capture_snapshot(root)))
            else:
                output = Path(args.output).expanduser() if args.output else None
                print(write_snapshot(root, output))
            return 0

        if args.command == "privacy":
            result = scan_privacy(
                _root(args.path),
                continuity_only=args.continuity_only,
                include_placeholders=not args.allow_placeholders,
            )
            if args.json:
                print(json_dumps({"files_scanned": result.files_scanned, "diagnostics": [d.to_dict() for d in result.diagnostics]}))
            else:
                print(f"Files scanned: {result.files_scanned}")
                for item in result.diagnostics:
                    print(f"{item.severity.upper():7s} {item.code} [{item.path or '-'}]: {item.message}")
                if not result.diagnostics:
                    print("No findings.")
            return 1 if result.diagnostics else 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"awc: {exc}", file=sys.stderr)
        return 2
    return 2
