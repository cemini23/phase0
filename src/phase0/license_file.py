from __future__ import annotations

import re
from pathlib import Path

from phase0.github import normalize_license

LICENSE_FILE_CANDIDATES = (
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "LICENSE-MIT",
    "COPYING",
    "COPYING.md",
    "UNLICENSE",
)

SPDX_LINE_RE = re.compile(
    r"SPDX-License-Identifier:\s*([A-Za-z0-9\.+\-]+)",
    re.IGNORECASE,
)


def detect_license_in_text(text: str) -> str | None:
    spdx = SPDX_LINE_RE.search(text)
    if spdx:
        return normalize_license(spdx.group(1))
    lower = text.lower()
    if "permission is hereby granted" in lower and "mit" in lower[:400]:
        return "MIT"
    if "apache license" in lower and "2.0" in lower:
        return "Apache-2.0"
    if "gnu general public license" in lower and "version 3" in lower:
        return "GPL-3.0"
    if "gnu affero general public license" in lower:
        return "AGPL-3.0"
    return None


def read_license_file(repo_path: Path) -> tuple[str | None, str | None]:
    """Return (normalized license, filename) from repo root."""
    for name in LICENSE_FILE_CANDIDATES:
        path = repo_path / name
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="replace")[:8000]
            except OSError:
                continue
            return detect_license_in_text(text), name
    return None, None
