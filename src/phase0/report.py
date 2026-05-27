from __future__ import annotations

import json
from dataclasses import asdict

from phase0.models import AuditReport, VerifyEvalReport


def render_verify_eval(report: VerifyEvalReport) -> str:
    lines = [
        "=" * 78,
        f"phase0 verify-eval  ::  {report.source}",
        "=" * 78,
        "",
        report.summary,
        "",
    ]
    for v in report.verifications:
        glyph = {"match": "+", "warn": "!", "mismatch": "x", "unavailable": "?"}[v.status]
        lines.append(f"{glyph} {v.entry.owner}/{v.entry.repo}")
        lines.append(f"    claimed: {v.entry.claimed_license}")
        lines.append(f"    github:  {v.gh_license or '—'}")
        lines.append(f"    file:    {v.file_license or '—'}")
        lines.append(f"    => {v.status.upper()}: {v.detail}")
        lines.append(f"    line: {v.entry.source_line}")
        lines.append("")
    return "\n".join(lines)


def render_audit(report: AuditReport) -> str:
    lines = [
        "=" * 78,
        f"phase0 audit  ::  {report.url}  [{report.tool_class}]",
        "=" * 78,
        "",
        f"VERDICT: {report.verdict}",
        "",
    ]
    if report.meta:
        m = report.meta
        lines.append(
            f"Meta: {m.stars} stars, {m.forks} forks, pushed {m.pushed_at}, "
            f"license {m.license_spdx or '—'}"
        )
        lines.append("")
    lines.append("CHECKS:")
    for c in report.checks:
        glyph = {"pass": "+", "warn": "!", "fail": "x"}[c.status]
        lines.append(f"  {glyph} [{c.status.upper():4}] {c.name}: {c.detail}")
        for e in c.evidence[:5]:
            lines.append(f"      - {e}")
    lines.extend(["", f"=> {report.summary}"])
    return "\n".join(lines)


def render_json(obj: VerifyEvalReport | AuditReport) -> str:
    return json.dumps(asdict(obj), indent=2)
