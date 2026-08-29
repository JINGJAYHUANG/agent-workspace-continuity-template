from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .models import InstallOperation
from .templates import CLAUDE, SUPPORTED_PROFILES, paths, render
from .utils import read_text, sha256_text, utc_now, write_text_atomic

SAFE_NAME = re.compile(r"[^A-Za-z0-9._ -]+")


@dataclass(frozen=True, slots=True)
class InstallResult:
    root: Path
    profile: str
    operations: tuple[InstallOperation, ...]

    @property
    def created(self) -> tuple[InstallOperation, ...]:
        return tuple(o for o in self.operations if o.kind == "create")


def workspace_name(root: Path, requested: str | None = None) -> str:
    value = (requested or root.name or "Workspace").strip()
    return SAFE_NAME.sub("-", value).strip(" .-") or "Workspace"


def _context(root: Path, profile: str, name: str) -> dict[str, str]:
    now = utc_now().replace(microsecond=0)
    return {
        "WORKSPACE_NAME": name,
        "PROFILE": profile,
        "GENERATED_DATE": now.date().isoformat(),
        "GENERATED_AT": now.isoformat().replace("+00:00", "Z"),
        "ROOT_BASENAME": root.name or name,
    }


def _existing_profile(root: Path) -> str | None:
    marker = re.compile(r"awc:profile=(project|umbrella)")
    for relative in ("AGENTS.md", ".agent/brief.md"):
        path = root / relative
        if path.is_file():
            try:
                match = marker.search(read_text(path))
            except (OSError, UnicodeDecodeError):
                continue
            if match:
                return match.group(1)
    return None


def _managed(relative: str, text: str, profile: str) -> bool:
    if relative in {"AGENTS.md", ".agent/brief.md"}:
        return f"awc:profile={profile}" in text
    if relative in {".agent/status.md", ".agent/handoff.md", ".agent/plan.md", ".agent/decisions.md"}:
        return "<!-- awc:state=" in text
    if relative == "CLAUDE.md":
        return "@AGENTS.md" in text and "awc" in text.lower()
    if relative == ".agent/.gitignore":
        return all(x in text for x in ("local/", "logs/", "backups/", "runtime-snapshot.json"))
    if relative.endswith("continuity_hook.py"):
        return "awc:managed-hook schema=1" in text
    if relative.endswith("continuity.settings.example.json"):
        return "continuity_hook.py" in text and "SessionStart" in text
    return False


def plan_install(
    root: Path,
    *,
    profile: str,
    name: str | None = None,
    include_optional: bool = False,
    with_claude_hooks: bool = False,
) -> tuple[InstallOperation, ...]:
    root = root.expanduser().resolve()
    if profile not in SUPPORTED_PROFILES:
        raise ValueError(f"profile must be one of: {', '.join(SUPPORTED_PROFILES)}")
    context = _context(root, profile, workspace_name(root, name))
    old_profile = _existing_profile(root)
    out: list[InstallOperation] = []
    for relative in paths(include_optional=include_optional, with_claude_hooks=with_claude_hooks):
        target = root / relative
        expected = render(profile=profile, relative=relative, context=context)
        if not target.exists():
            out.append(InstallOperation("create", relative, "required template is missing"))
            continue
        if not target.is_file():
            out.append(InstallOperation("conflict", relative, "target exists but is not a regular file"))
            continue
        existing = read_text(target)
        profile_specific = relative not in {".agent/.gitignore", *CLAUDE}
        if old_profile and old_profile != profile and profile_specific:
            out.append(InstallOperation("conflict", relative, f"existing workspace uses '{old_profile}'; requested '{profile}'"))
        elif sha256_text(existing.rstrip() + "\n") == sha256_text(expected.rstrip() + "\n"):
            out.append(InstallOperation("unchanged", relative, "existing file matches template"))
        elif _managed(relative, existing, profile):
            out.append(InstallOperation("unchanged", relative, "existing AWC-managed file is preserved"))
        else:
            out.append(InstallOperation("conflict", relative, "existing content differs; it will not be overwritten"))
    return tuple(out)


def apply_install(
    root: Path,
    *,
    profile: str,
    name: str | None = None,
    include_optional: bool = False,
    with_claude_hooks: bool = False,
    write_proposals: bool = True,
) -> InstallResult:
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    resolved_name = workspace_name(root, name)
    context = _context(root, profile, resolved_name)
    plan = plan_install(
        root,
        profile=profile,
        name=resolved_name,
        include_optional=include_optional,
        with_claude_hooks=with_claude_hooks,
    )
    out: list[InstallOperation] = []
    proposal_root: Path | None = None
    for op in plan:
        target = root / op.relative_path
        expected = render(profile=profile, relative=op.relative_path, context=context)
        if op.kind == "create":
            write_text_atomic(target, expected)
            if target.name == "continuity_hook.py":
                try:
                    target.chmod(target.stat().st_mode | 0o111)
                except OSError:
                    pass
            out.append(op)
        elif op.kind == "conflict" and write_proposals:
            if proposal_root is None:
                proposal_root = root / ".agent" / "local" / "proposals" / utc_now().strftime("%Y%m%dT%H%M%S%fZ")
            proposal = proposal_root / op.relative_path
            write_text_atomic(proposal, expected)
            out.append(InstallOperation("proposal", op.relative_path, op.reason, proposal.relative_to(root).as_posix()))
        else:
            out.append(op)
    return InstallResult(root, profile, tuple(out))
