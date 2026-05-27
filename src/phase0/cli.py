from __future__ import annotations

import argparse
import sys
from pathlib import Path

from phase0 import __version__
from phase0.audit import audit_repo
from phase0.checks import TOOL_CLASSES
from phase0.github import gh_available
from phase0.report import render_audit, render_json, render_verify_eval
from phase0.verify_eval import verify_eval_file


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="phase0",
        description="Phase-0 source audits for third-party agent tools.",
    )
    p.add_argument("--version", action="version", version=f"phase0 {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    ve = sub.add_parser("verify-eval", help="Re-check license claims in an eval document")
    ve.add_argument("eval_doc", type=Path, help="Markdown/text eval file")
    ve.add_argument("--json", action="store_true")

    aud = sub.add_parser("audit", help="Run Phase-0 audit on a GitHub repository")
    aud.add_argument("url", help="https://github.com/owner/repo")
    aud.add_argument(
        "--class",
        dest="tool_class",
        required=True,
        choices=TOOL_CLASSES,
        help="Tool class checklist to apply",
    )
    aud.add_argument("--json", action="store_true")
    aud.add_argument(
        "--no-clone",
        action="store_true",
        help="GitHub API only — skip clone and class-specific filesystem checks",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not gh_available():
        print(
            "ERROR: GitHub CLI (gh) not found. Install gh and run `gh auth login`.",
            file=sys.stderr,
        )
        return 3

    if args.command == "verify-eval":
        path = args.eval_doc
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 3
        report = verify_eval_file(path)
        if args.json:
            print(render_json(report))
        else:
            print(render_verify_eval(report))
        mismatches = sum(1 for v in report.verifications if v.status == "mismatch")
        has_warn = any(v.status == "warn" for v in report.verifications)
        return 2 if mismatches else (1 if has_warn else 0)

    if args.command == "audit":
        report = audit_repo(args.url, args.tool_class, clone=not args.no_clone)
        if args.json:
            print(render_json(report))
        else:
            print(render_audit(report))
        return {"GO": 0, "CONDITIONAL-GO": 1, "NO-GO": 2, "ERROR": 3}[report.verdict]

    return 3


if __name__ == "__main__":
    raise SystemExit(main())
