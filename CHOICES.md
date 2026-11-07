# CHOICES — EB-65 redaction review

## Decision

**Ship** for the bounded configured-token contract (docs/contracts.md, Redaction) only. Not a certification that any bundle is safe to publish.

## What changed and why

- `_clean_text`: literal `str.replace` instead of `re.sub` ("Secrets are literal strings, not regular expressions"), longest token first ("Process longer tokens first…"), empty entries skipped.
- `_walk`: recursive over dict values and lists ("at any depth"); keys, booleans, nulls and numbers unchanged.
- `redact`: rejects `values` that is not a list of strings (JSON error, exit 2); previously a string was applied per character, exit 0.
- New `tests/test_redaction.py` (10 CLI tests). CLI and fixtures unchanged.

## Checks

- 26 contract cases via the CLI on temporary files: 10 FAIL on the original code (`axb` over-redacted, `tok(` crashed with `re.error`/exit 1, `-long` suffix exposed, nested evidence in clear), 26 PASS after; input sha256 always unchanged.
- New tests: 5 failed before their fix; now 18/18 pass (10 new + 8 smoke).

## Limits and assumptions

- Only explicitly configured literal values (case-sensitive). No detection of unknown secrets; images and binary attachments are not processed.
- Keys are never rewritten (per contract): a secret used as a key stays visible.
- Equal-length overlapping tokens can leak (`abcdef`+`cdefgh` → `[REDACTED]gh`); unspecified.
- Assumed: `[REDACTED]` label kept; `" "` is not "empty".
- Left out: tests for CLI usage errors and schema-1 input (checked manually).

## AI suggestions corrected or rejected

- The generated helper used `re.sub`, treating secrets as regex. Replaced because the contract requires literal strings; verified by `tok(` crashing (exit 1) before and redacting after, and `a.b` no longer hiding `axb`.
- The assistant split the test helper `redact` without my approval. I rejected it to keep the helper intact; reverted, test made standalone, 18/18 still pass.
