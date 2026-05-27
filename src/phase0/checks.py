from __future__ import annotations

import re
from pathlib import Path

from phase0.models import CheckResult, RepoMeta

TOOL_CLASSES = (
    "mcp-server",
    "skill-library",
    "wiki-tool",
    "oauth-proxy",
    "trading-bot",
)


def base_checks(
    meta: RepoMeta, file_license: str | None, file_name: str | None
) -> list[CheckResult]:
    checks: list[CheckResult] = []

    if meta.archived:
        checks.append(
            CheckResult("archived", "fail", "Repository is archived on GitHub")
        )
    else:
        checks.append(CheckResult("archived", "pass", "Repository is active"))

    if meta.license_spdx and meta.license_spdx != "NOASSERTION":
        checks.append(
            CheckResult(
                "gh_license",
                "pass",
                f"GitHub API license: {meta.license_spdx}",
            )
        )
    else:
        checks.append(
            CheckResult(
                "gh_license",
                "warn",
                "GitHub API reports no SPDX license (NOASSERTION or missing)",
            )
        )

    if file_license:
        checks.append(
            CheckResult(
                "license_file",
                "pass",
                f"LICENSE file detected ({file_name}): {file_license}",
            )
        )
    else:
        checks.append(
            CheckResult(
                "license_file",
                "fail",
                "No LICENSE/COPYING file found in repository root",
            )
        )

    if (
        meta.license_spdx
        and file_license
        and meta.license_spdx not in {file_license, "NOASSERTION"}
    ):
        if meta.license_spdx.replace("-", "") != file_license.replace("-", ""):
            checks.append(
                CheckResult(
                    "license_consistency",
                    "warn",
                    f"GitHub ({meta.license_spdx}) vs file ({file_license}) differ",
                )
            )
        else:
            checks.append(
                CheckResult("license_consistency", "pass", "GitHub and file licenses align")
            )
    else:
        checks.append(
            CheckResult("license_consistency", "pass", "No license consistency conflict")
        )

    if meta.stars >= 1000 and meta.forks > 0:
        ratio = meta.stars / max(meta.forks, 1)
        if ratio > 50:
            checks.append(
                CheckResult(
                    "star_fork_ratio",
                    "warn",
                    (
                        f"High star/fork ratio ({meta.stars}/{meta.forks} = "
                        f"{ratio:.0f}:1) — verify organic growth"
                    ),
                )
            )
        else:
            checks.append(
                CheckResult(
                    "star_fork_ratio",
                    "pass",
                    f"Star/fork ratio {meta.stars}/{meta.forks} within normal band",
                )
            )
    else:
        checks.append(
            CheckResult(
                "star_fork_ratio",
                "pass",
                f"Stars={meta.stars}, forks={meta.forks} (ratio check skipped)",
            )
        )

    return checks


def check_mcp_server(repo_path: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []
    py_files = list(repo_path.rglob("*.py"))[:400]
    joined = ""
    for p in py_files:
        try:
            joined += p.read_text(encoding="utf-8", errors="replace")[:5000]
        except OSError:
            continue

    has_mcp = bool(re.search(r"@mcp\.tool|FastMCP|mcp\.server", joined))
    if has_mcp:
        checks.append(CheckResult("mcp_surface", "pass", "MCP tool/server patterns found"))
    else:
        checks.append(
            CheckResult(
                "mcp_surface",
                "warn",
                "No @mcp.tool / FastMCP patterns detected in Python sources",
            )
        )

    if re.search(r"readOnly|destructive", joined):
        checks.append(
            CheckResult(
                "mcp_annotations",
                "pass",
                "Tool annotation hints (readOnly/destructive) present",
            )
        )
    else:
        checks.append(
            CheckResult(
                "mcp_annotations",
                "warn",
                "No readOnly/destructive annotation patterns found",
            )
        )
    return checks


def check_skill_library(repo_path: Path) -> list[CheckResult]:
    skills = list(repo_path.rglob("SKILL.md")) + list(repo_path.rglob("*.skill.md"))
    if skills:
        checks = [
            CheckResult(
                "skill_files",
                "pass",
                f"Found {len(skills)} SKILL.md file(s)",
            )
        ]
    else:
        checks = [
            CheckResult(
                "skill_files",
                "warn",
                "No SKILL.md files found — confirm this is a skill library repo",
            )
        ]

    for skill in skills[:5]:
        text = skill.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---") and "description:" in text[:800]:
            checks.append(
                CheckResult(
                    "skill_frontmatter",
                    "pass",
                    f"{skill.relative_to(repo_path)} has frontmatter",
                )
            )
            break
    else:
        if skills:
            checks.append(
                CheckResult(
                    "skill_frontmatter",
                    "warn",
                    "SKILL files lack expected YAML frontmatter",
                )
            )
    return checks


def check_wiki_tool(repo_path: Path) -> list[CheckResult]:
    hits: list[str] = []
    patterns = (
        r'["\']wiki/[^"\']+["\']',
        r'["\']/wiki["\']',
        r'Path\(["\']wiki',
        r"hardcoded.*wiki",
    )
    for path in list(repo_path.rglob("*.py"))[:200]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                hits.append(f"{path.name}: {pat}")
                break
    if hits:
        return [
            CheckResult(
                "wiki_hardcoded_paths",
                "warn",
                f"{len(hits)} file(s) may hardcode wiki directory layout",
                evidence=hits[:5],
            )
        ]
    return [
        CheckResult(
            "wiki_hardcoded_paths",
            "pass",
            "No obvious hardcoded wiki/ path literals detected",
        )
    ]


def check_oauth_proxy(repo_path: Path) -> list[CheckResult]:
    flags: list[str] = []
    needles = (
        "credentials.json",
        "oauth/token",
        "anthropic.com/oauth",
        "tokenRefresh",
        "OAUTH_CLIENT_ID",
        ".credentials.json",
    )
    for path in list(repo_path.rglob("*"))[:500]:
        if not path.is_file() or path.suffix in {".png", ".jpg", ".woff", ".ico"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:8000]
        except OSError:
            continue
        for needle in needles:
            if needle in text:
                flags.append(f"{path.relative_to(repo_path)}: {needle}")
                break
    if flags:
        return [
            CheckResult(
                "oauth_grafting",
                "fail",
                f"OAuth/credential grafting patterns detected ({len(flags)} hit(s))",
                evidence=flags[:8],
            )
        ]
    return [
        CheckResult(
            "oauth_grafting",
            "pass",
            "No OAuth grafting patterns detected",
        )
    ]


def check_trading_bot(repo_path: Path) -> list[CheckResult]:
    """Generic engineering checks only — no strategy logic review."""
    checks: list[CheckResult] = []
    has_pyproject = (repo_path / "pyproject.toml").is_file()
    has_requirements = (repo_path / "requirements.txt").is_file()
    if has_pyproject or has_requirements:
        checks.append(
            CheckResult("dependency_manifest", "pass", "Dependency manifest present")
        )
    else:
        checks.append(
            CheckResult(
                "dependency_manifest",
                "warn",
                "No pyproject.toml or requirements.txt at repo root",
            )
        )

    tests_dir = repo_path / "tests"
    if tests_dir.is_dir() and any(tests_dir.rglob("test_*.py")):
        checks.append(CheckResult("tests_present", "pass", "tests/ with test_*.py found"))
    else:
        checks.append(
            CheckResult(
                "tests_present",
                "warn",
                "No tests/ tree detected — treat claims as unverified",
            )
        )
    return checks


CLASS_CHECKS = {
    "mcp-server": check_mcp_server,
    "skill-library": check_skill_library,
    "wiki-tool": check_wiki_tool,
    "oauth-proxy": check_oauth_proxy,
    "trading-bot": check_trading_bot,
}


def run_class_checks(tool_class: str, repo_path: Path) -> list[CheckResult]:
    fn = CLASS_CHECKS.get(tool_class)
    if fn is None:
        return [
            CheckResult(
                "tool_class",
                "fail",
                f"Unknown tool class {tool_class!r}. Choose: {', '.join(TOOL_CLASSES)}",
            )
        ]
    return fn(repo_path)
