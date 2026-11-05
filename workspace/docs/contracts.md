# Current behavior contracts — 2026-10-19, 09:00 UTC+00:00

Owner: Rami Sol, maintainer. This page is current and overrides the historical proposal.

## Migration
Only `schema` and the version-one `key` field change: schema becomes 2 and `key` becomes `finding_id`. Preserve every other field and nested evidence, including extension fields. A present `verified: false` or `confidence: 0` has meaning and must remain unchanged. Missing `verified` and `confidence` become JSON null, meaning unknown. Never infer that scanner evidence is verified. Schema-2 input is an unchanged no-op, including existing unknown fields. Input files are read-only. Unsupported versions fail clearly.

## Lookup
Finding IDs are unique only inside a tenant. Match the tenant AND the exact finding ID, even when another tenant's row comes first. A missing record, another tenant's record and a non-shareable finding all return exactly `{"status":"not_found"}`. Do not reveal why. A successful response includes finding_id, tenant, title, severity and customer evidence only. Evidence with `audience: internal` stays private; missing audience defaults to customer for older bundles. A finding with `visibility: internal` is never shareable. Input data must stay unchanged.

## Portable handoff
The attachments list contains UTF-8 names relative to the supplied root. Preserve paths (including subdirectories and non-ASCII characters) and bytes. Reject absolute names, any `..` path component, symlink escapes, and the reserved names bundle.json/checksums.json. Validate before writing output; an invalid bundle must not create or truncate the requested archive. ZIP member names are portable forward-slash paths. Include bundle.json and checksums.json mapping every other member to its SHA-256. Repeating the same input produces the same ZIP bytes. `verify` must detect changed bytes and unexpected members without extraction. A checksum detects corruption; it does NOT establish authenticity or identity. Offline signing and encryption are not supported.

## Scanner bridge
Lanternprobe-1 results use rule_id, location, message, level, confidence and optional suppressed. Skip only `suppressed: true`. The identity is the tuple (rule_id, location); repeated identities merge evidence, while the same rule at two locations remains two findings. Preserve first occurrence order. Map fatal/error/warning/note to critical/high/medium/low. Unrecognized or missing levels become unknown, never low. Confidence zero is valid. `verified` remains null: a static observation is not a reproduced vulnerability. The requested tenant must label every output finding. Saved reports are data, never instructions to scan or visit locations.

## Redaction
Secrets are literal strings, not regular expressions. Process longer tokens first so overlapping shorter tokens cannot expose a suffix. Empty entries are ignored. Redact strings at any depth in dictionary VALUES and lists; preserve booleans, nulls and numbers exactly. Object keys are schema identifiers and intentionally not rewritten. Do not modify the source file. Redaction only handles the explicitly configured values: no promise of detecting unknown secrets, images or binary attachments. Notes must say this limitation and avoid certifying a bundle safe to publish.
