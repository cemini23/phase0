# phase0

CLI for **third-party tool adoption audits** — the second gate after doc-level evaluation.

> **Status:** Planned. [vet](https://github.com/cemini23/vet) ships first.

## Problem

LLM-generated tool evaluations systematically mis-report licenses, maturity, and fit. Doc-level "Adopt" verdicts fail Phase-0 source audits at high rates when someone actually clones the repo.

## Planned interface

```bash
phase0 audit https://github.com/org/repo --class mcp-server
phase0 audit https://github.com/org/repo --class skill-library
phase0 verify-eval eval.md          # re-check license claims via gh api
```

## Two-gate pattern

| Gate | Cost | Catches |
|------|------|---------|
| Doc-level eval | ~5 min / URL | Stack fit, coarse license field |
| Phase-0 source audit | ~30–60 min / URL | Parallel implementations, TOS chains, OAuth grafting, GPL poison, star inflation, hardcoded layouts |

## Tool classes (planned)

- `mcp-server` — schema surface, destructive annotations, auth patterns
- `skill-library` — SKILL.md injection risk, catalog churn, license files
- `wiki-tool` — hardcoded directory layouts, nested-wiki support
- `oauth-proxy` — credential file reads, undocumented token endpoints
- `trading-bot` — generic engineering checks only (no strategy IP)

## Related

- [vet](https://github.com/cemini23/vet) — static audit for skills and briefs (available now)
- [OSS roadmap](https://github.com/cemini23/vet#related) — full agent toolkit sequence

## License

MIT (will match `vet` on first release)
