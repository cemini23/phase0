# phase0

Phase-0 **source audits** for third-party agent tools — the second gate after doc-level LLM evaluation.

Requires [GitHub CLI](https://cli.github.com/) (`gh`) authenticated (`gh auth login`). Stdlib-only Python; clones are shallow and ephemeral.

Companion: [vet](https://github.com/cemini23/vet) audits **your** skills and briefs before they ship. phase0 audits **their** repos before you adopt them.

## Install

```bash
pip install git+https://github.com/cemini23/phase0.git
# or from clone:
pip install -e .
```

## Commands

### verify-eval — catch false license claims in eval docs

```bash
phase0 verify-eval tool-eval.md
phase0 verify-eval eval.md --json
```

Parses `github.com/owner/repo` URLs, reads claimed licenses from table rows / nearby prose, then verifies via `gh api` + optional shallow `LICENSE` file read.

Exit codes: `0` all match, `1` warnings, `2` mismatches, `3` error.

### audit — Phase-0 checklist on a live repo

```bash
phase0 audit https://github.com/org/mcp-server --class mcp-server
phase0 audit https://github.com/org/skills --class skill-library
phase0 audit URL --class oauth-proxy --no-clone   # API-only, faster
```

**Tool classes:**

| Class | Checks |
|-------|--------|
| `mcp-server` | MCP surface patterns, readOnly/destructive annotations |
| `skill-library` | SKILL.md presence, frontmatter |
| `wiki-tool` | Hardcoded `wiki/` path literals |
| `oauth-proxy` | Credential/OAuth grafting patterns (fail) |
| `trading-bot` | Generic engineering only (manifest, tests/) — **no strategy review** |

**Verdicts:** `GO` · `CONDITIONAL-GO` (warnings) · `NO-GO` (fail) · `ERROR`

## Two-gate pattern

| Gate | Tool | Catches |
|------|------|---------|
| Doc-level eval | (human / LLM) | Stack fit, coarse license field |
| Phase-0 | **phase0** | False NO-LICENSE, OAuth grafting, missing LICENSE file, hardcoded wiki layouts, star inflation |

## Example workflow

```bash
# 1. Vet your adoption brief before writing the eval handoff
vet briefs/adopt-foo.md --strict

# 2. Skeptic-check the eval's license column
phase0 verify-eval inbox/tool-eval-v4.md

# 3. Phase-0 the one Adopt candidate
phase0 audit https://github.com/org/foo --class mcp-server
```

## Prerequisites

```bash
gh auth status   # must be logged in
git --version    # used for shallow clones
```

## License

MIT — see [LICENSE](LICENSE).
