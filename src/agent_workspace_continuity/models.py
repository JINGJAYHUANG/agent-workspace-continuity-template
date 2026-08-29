from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

Severity = Literal["info", "warning", "error"]
OperationKind = Literal["create", "unchanged", "conflict", "proposal"]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    severity: Severity
    message: str
    path: str | None = None
    remediation: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InstallOperation:
    kind: OperationKind
    relative_path: str
    reason: str
    proposed_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class DoctorReport:
    root: Path
    profile: str | None
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == "error"]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == "warning"]

    @property
    def healthy(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "profile": self.profile,
            "healthy": self.healthy,
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "info": sum(d.severity == "info" for d in self.diagnostics),
            },
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }


@dataclass(slots=True)
class RecoverySummary:
    workspace_name: str
    profile: str | None
    objective: str
    verified_state: list[str]
    existing_not_reverified: list[str]
    blockers: list[str]
    risks: list[str]
    next_actions: list[str]
    source_hashes: dict[str, str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
