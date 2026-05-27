from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Status = Literal["pass", "warn", "fail"]
Verdict = Literal["GO", "CONDITIONAL-GO", "NO-GO", "ERROR"]


@dataclass
class CheckResult:
    name: str
    status: Status
    detail: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class RepoMeta:
    owner: str
    repo: str
    url: str
    stars: int
    forks: int
    pushed_at: str
    license_spdx: str | None
    default_branch: str
    archived: bool


@dataclass
class EvalEntry:
    url: str
    owner: str
    repo: str
    claimed_license: str
    source_line: str


@dataclass
class EvalVerification:
    entry: EvalEntry
    gh_license: str | None
    file_license: str | None
    status: Literal["match", "mismatch", "warn", "unavailable"]
    detail: str


@dataclass
class VerifyEvalReport:
    source: str
    verifications: list[EvalVerification]
    summary: str


@dataclass
class AuditReport:
    url: str
    owner: str
    repo: str
    tool_class: str
    verdict: Verdict
    checks: list[CheckResult]
    meta: RepoMeta | None
    summary: str
