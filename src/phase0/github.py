from __future__ import annotations

import json
import re
import shutil
import subprocess
from typing import Any

from phase0.models import RepoMeta

GITHUB_URL_RE = re.compile(
    r"https?://github\.com/(?P<owner>[^/\s\)\"']+)/(?P<repo>[^/\s\)\"'#?]+)"
)

LICENSE_ALIASES: dict[str, str] = {
    "mit": "MIT",
    "apache-2.0": "Apache-2.0",
    "apache2.0": "Apache-2.0",
    "apache 2.0": "Apache-2.0",
    "agpl-3.0": "AGPL-3.0",
    "agpl3.0": "AGPL-3.0",
    "gpl-3.0": "GPL-3.0",
    "gpl-2.0": "GPL-2.0",
    "bsd-2-clause": "BSD-2-Clause",
    "bsd-3-clause": "BSD-3-Clause",
    "mpl-2.0": "MPL-2.0",
    "isc": "ISC",
    "unlicense": "Unlicense",
    "unlicensed": "UNLICENSED",
    "no license": "NONE",
    "no license found": "NONE",
    "none": "NONE",
    "unavailable": "UNAVAILABLE",
    "unknown": "UNKNOWN",
}


def parse_github_url(url: str) -> tuple[str, str] | None:
    m = GITHUB_URL_RE.search(url)
    if not m:
        return None
    owner = m.group("owner")
    repo = m.group("repo").removesuffix(".git")
    return owner, repo


def normalize_license(raw: str | None) -> str | None:
    if raw is None:
        return None
    cleaned = raw.strip().strip("`").strip("*")
    if not cleaned:
        return None
    key = cleaned.lower().replace("_", "-")
    if key in LICENSE_ALIASES:
        return LICENSE_ALIASES[key]
    upper = cleaned.upper()
    if upper in {"MIT", "ISC", "UNLICENSE"}:
        return "MIT" if upper == "MIT" else upper
    if "APACHE" in upper:
        return "Apache-2.0"
    if "AGPL" in upper:
        return "AGPL-3.0"
    if "GPL-3" in upper or upper == "GPL-3.0":
        return "GPL-3.0"
    if "NO LICENSE" in upper or upper == "NONE":
        return "NONE"
    return cleaned


def gh_available() -> bool:
    return shutil.which("gh") is not None


def gh_api(path: str) -> dict[str, Any]:
    if not gh_available():
        raise RuntimeError("GitHub CLI (gh) not found on PATH — install and run `gh auth login`")
    proc = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"gh api {path} failed: {err}")
    return json.loads(proc.stdout)


def fetch_repo_meta(owner: str, repo: str) -> dict[str, Any]:
    return gh_api(f"repos/{owner}/{repo}")


def repo_meta_from_api(data: dict[str, Any], url: str) -> RepoMeta:
    lic = data.get("license") or {}
    return RepoMeta(
        owner=data["owner"]["login"],
        repo=data["name"],
        url=url,
        stars=int(data.get("stargazers_count") or 0),
        forks=int(data.get("forks_count") or 0),
        pushed_at=str(data.get("pushed_at") or ""),
        license_spdx=lic.get("spdx_id"),
        default_branch=str(data.get("default_branch") or "main"),
        archived=bool(data.get("archived")),
    )
