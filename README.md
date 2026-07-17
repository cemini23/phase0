# phase0

[![CI](https://github.com/cemini23/phase0/actions/workflows/ci.yml/badge.svg)](https://github.com/cemini23/phase0/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Phase-0 **source audits** for third-party agent tools — the second gate after doc-level LLM evaluation.

Part of the [agent toolkit](https://github.com/cemini23/agent-toolkit-demo): **vet** → **phase0** → **wikilint**.

Requires [GitHub CLI](https://cli.github.com/) (`gh auth login`) and `git`. Stdlib-only Python.

## Install

```bash
pip install git+https://github.com/cemini23/phase0.git
pip install -e .
```

## Commands

```bash
# Skeptic-check license column in an eval doc
phase0 verify-eval tool-eval.md

# Phase-0 audit before adoption
phase0 audit https://github.com/org/repo --class mcp-server
phase0 audit URL --class oauth-proxy --no-clone
```

### Tool classes

`mcp-server` · `skill-library` · `wiki-tool` · `oauth-proxy` · `trading-bot` (engineering only)

### Verdicts

`GO` · `CONDITIONAL-GO` · `NO-GO` · `ERROR`

## GitHub Action

```yaml
- uses: actions/checkout@v4
- uses: cemini23/phase0@v0.2.0
  with:
    command: verify-eval
    target: evals/tool-eval.md
```

Audit mode:

```yaml
- uses: cemini23/phase0@v0.2.0
  with:
    command: audit
    target: https://github.com/org/mcp-server
    tool-class: mcp-server
```

Uses `github.token` for `gh api` in Actions.

## Two-gate pattern

| Gate | Tool | Catches |
|------|------|---------|
| Doc-level eval | human / LLM | Stack fit, coarse license |
| Phase-0 | **phase0** | False NO-LICENSE, OAuth grafting, missing LICENSE, hardcoded layouts |

## Related

- Methodology newsletter: [Outlier Weekly](https://outlierweekly.substack.com)
- YouTube: [@Cemini23](https://www.youtube.com/@Cemini23)
- Agent meta-wiki: [cemini-claude-code-CCC](https://github.com/cemini23/cemini-claude-code-CCC)
- Toolkit: [vet](https://github.com/cemini23/vet) · [wikilint](https://github.com/cemini23/wikilint) · [agent-toolkit-demo](https://github.com/cemini23/agent-toolkit-demo) · [ara-schema](https://github.com/cemini23/ara-schema)


## Support

Voluntary tips fund open research and tooling. **Donation-only addresses** — not trading or production wallets.

| Chain family | Address |
|--------------|---------|
| **EVM** (Ethereum, Polygon, Base, Arbitrum, …) | `0x444C5C2eC439E0382aa5a17F70313c536BcC5D58` |
| **Solana / SVM** | `J4zNn4hK9jTrKBFY8sbAGJHLoZvXvQf4B9pQSbSrocZE` |
| **Polymarket** (referral) | [polymarket.com/?r=Cemini23](https://polymarket.com/?r=Cemini23) |


## License

MIT
