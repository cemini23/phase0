from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from phase0.github import GITHUB_URL_RE, normalize_license
from phase0.models import EvalEntry, EvalVerification, VerifyEvalReport

NO_LICENSE_MARKERS = (
    "no license",
    "no license found",
    "unlicensed",
    "none",
    "unavailable",
    "unknown",
    "not found",
)

LICENSE_IN_TEXT_RE = re.compile(
    r"\b(MIT|Apache-?2\.0|AGPL-?3\.0|GPL-?3\.0|GPL-?2\.0|BSD|"
    r"MPL-?2\.0|ISC|Unlicense|NO LICENSE(?: FOUND)?|UNAVAILABLE|UNLICENSED)\b",
    re.IGNORECASE,
)


def _claimed_from_context(snippet: str) -> str:
    if "|" in snippet:
        cells = [c.strip() for c in snippet.split("|") if c.strip()]
        for cell in reversed(cells):
            norm = normalize_license(cell)
            if norm and norm not in {"UNAVAILABLE", "UNKNOWN"}:
                return norm
            lower = cell.lower()
            if any(m in lower for m in NO_LICENSE_MARKERS):
                return "NONE"
    m = LICENSE_IN_TEXT_RE.search(snippet)
    if m:
        return normalize_license(m.group(0)) or m.group(0)
    return "UNKNOWN"


def extract_eval_entries(text: str) -> list[EvalEntry]:
    entries: list[EvalEntry] = []
    seen: set[tuple[str, str]] = set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        for m in GITHUB_URL_RE.finditer(line):
            owner, repo = m.group("owner"), m.group("repo").removesuffix(".git")
            key = (owner.lower(), repo.lower())
            if key in seen:
                continue
            seen.add(key)
            window = "\n".join(lines[max(0, i - 1) : min(len(lines), i + 2)])
            claimed = _claimed_from_context(window)
            entries.append(
                EvalEntry(
                    url=f"https://github.com/{owner}/{repo}",
                    owner=owner,
                    repo=repo,
                    claimed_license=claimed,
                    source_line=line.strip()[:200],
                )
            )
    return entries


def compare_licenses(claimed: str, gh: str | None, file_lic: str | None) -> tuple[str, str]:
    """Return (status, detail)."""
    c = normalize_license(claimed) or "UNKNOWN"
    g = normalize_license(gh) if gh else None
    f = normalize_license(file_lic) if file_lic else None

    if c == "UNAVAILABLE":
        return "unavailable", "Eval marked repo unavailable — skipped"

    if g is None and f is None:
        if c in {"NONE", "UNKNOWN"}:
            return "match", "No license on GitHub API and eval claims none/unknown"
        return "mismatch", f"Eval claims {c} but GitHub API reports no license"

    if c in {"NONE", "UNKNOWN"} and (g or f):
        found = g or f
        return "mismatch", f"Eval claims no license but source shows {found}"

    truth = g or f
    if c == truth:
        return "match", f"License {c} confirmed"
    if f and g and f != g:
        return "warn", f"GitHub API ({g}) differs from LICENSE file ({f}); eval claimed {c}"
    if truth and c != truth:
        return "mismatch", f"Eval claims {c} but source shows {truth}"
    return "warn", f"Could not fully confirm eval claim {c}"


def verify_eval_file(path: Path) -> VerifyEvalReport:
    from phase0.github import fetch_repo_meta, repo_meta_from_api
    from phase0.license_file import read_license_file

    text = path.read_text(encoding="utf-8")
    entries = extract_eval_entries(text)
    verifications: list[EvalVerification] = []

    with tempfile.TemporaryDirectory(prefix="phase0-verify-") as tmp:
        tmp_path = Path(tmp)
        for entry in entries:
            gh_lic: str | None = None
            file_lic: str | None = None
            try:
                data = fetch_repo_meta(entry.owner, entry.repo)
                meta = repo_meta_from_api(data, entry.url)
                gh_lic = meta.license_spdx
                clone_dir = tmp_path / f"{entry.owner}-{entry.repo}"
                proc = subprocess.run(
                    [
                        "git",
                        "clone",
                        "--depth",
                        "1",
                        "--quiet",
                        entry.url,
                        str(clone_dir),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if proc.returncode == 0:
                    file_lic, _ = read_license_file(clone_dir)
                    shutil.rmtree(clone_dir, ignore_errors=True)
            except RuntimeError as exc:
                verifications.append(
                    EvalVerification(
                        entry=entry,
                        gh_license=None,
                        file_license=None,
                        status="unavailable",
                        detail=str(exc),
                    )
                )
                continue

            status, detail = compare_licenses(entry.claimed_license, gh_lic, file_lic)
            verifications.append(
                EvalVerification(
                    entry=entry,
                    gh_license=gh_lic,
                    file_license=file_lic,
                    status=status,
                    detail=detail,
                )
            )

    mismatches = sum(1 for v in verifications if v.status == "mismatch")
    warns = sum(1 for v in verifications if v.status == "warn")
    matches = sum(1 for v in verifications if v.status == "match")
    summary = (
        f"{len(verifications)} repos: {matches} match, {warns} warn, "
        f"{mismatches} mismatch"
    )
    return VerifyEvalReport(source=str(path), verifications=verifications, summary=summary)
