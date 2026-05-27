from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from phase0.checks import base_checks, run_class_checks
from phase0.github import fetch_repo_meta, parse_github_url, repo_meta_from_api
from phase0.license_file import read_license_file
from phase0.models import AuditReport, CheckResult, Verdict


def _verdict_from_checks(checks: list[CheckResult]) -> Verdict:
    if any(c.status == "fail" for c in checks):
        return "NO-GO"
    if any(c.status == "warn" for c in checks):
        return "CONDITIONAL-GO"
    return "GO"


def audit_repo(url: str, tool_class: str, *, clone: bool = True) -> AuditReport:
    parsed = parse_github_url(url)
    if not parsed:
        return AuditReport(
            url=url,
            owner="",
            repo="",
            tool_class=tool_class,
            verdict="ERROR",
            checks=[
                CheckResult("url", "fail", "Not a valid github.com repository URL")
            ],
            meta=None,
            summary="ERROR — invalid GitHub URL",
        )

    owner, repo = parsed
    canonical = f"https://github.com/{owner}/{repo}"

    try:
        data = fetch_repo_meta(owner, repo)
    except RuntimeError as exc:
        return AuditReport(
            url=canonical,
            owner=owner,
            repo=repo,
            tool_class=tool_class,
            verdict="ERROR",
            checks=[CheckResult("gh_api", "fail", str(exc))],
            meta=None,
            summary=f"ERROR — {exc}",
        )

    meta = repo_meta_from_api(data, canonical)
    checks: list[CheckResult] = []
    file_license: str | None = None
    file_name: str | None = None

    if clone:
        with tempfile.TemporaryDirectory(prefix="phase0-audit-") as tmp:
            dest = Path(tmp) / repo
            proc = subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet", canonical, str(dest)],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                err = (proc.stderr or proc.stdout).strip()
                checks.append(
                    CheckResult("git_clone", "fail", f"Shallow clone failed: {err}")
                )
            else:
                checks.append(CheckResult("git_clone", "pass", "Shallow clone succeeded"))
                file_license, file_name = read_license_file(dest)
                checks.extend(base_checks(meta, file_license, file_name))
                checks.extend(run_class_checks(tool_class, dest))
    else:
        checks.extend(base_checks(meta, None, None))
        checks.append(
            CheckResult(
                "git_clone",
                "warn",
                "Skipped clone (--no-clone); class-specific checks omitted",
            )
        )

    verdict = _verdict_from_checks(checks)
    summary = f"{verdict} — {len(checks)} checks on {owner}/{repo} [{tool_class}]"
    return AuditReport(
        url=canonical,
        owner=owner,
        repo=repo,
        tool_class=tool_class,
        verdict=verdict,
        checks=checks,
        meta=meta,
        summary=summary,
    )
