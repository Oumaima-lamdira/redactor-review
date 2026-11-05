"""File boundaries and explicit bundle validation."""
from __future__ import annotations

import json
import pathlib
import typing

Record = dict[str, typing.Any]
LEVELS = {"critical", "high", "medium", "low", "unknown"}


def load(path: str) -> Record:
    """Read an object, never silently accept an array as a bundle."""
    with pathlib.Path(path).open(encoding="utf-8") as stream:
        value = json.load(stream)
    if isinstance(value, dict) is False:
        raise ValueError("document must be a JSON object")
    return value


def emit(value: Record) -> None:
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))


def check(bundle: Record) -> None:
    if bundle.get("schema") not in (1, 2):
        raise ValueError("unsupported schema")
    if isinstance(bundle.get("findings"), list) is False:
        raise ValueError("findings must be a list")
    for finding in bundle["findings"]:
        if isinstance(finding, dict) is False:
            raise ValueError("finding must be an object")
        key = "finding_id" if bundle["schema"] == 2 else "key"
        for field in (key, "tenant", "title", "severity"):
            if isinstance(finding.get(field), str) is False or finding[field] == "":
                raise ValueError(f"missing {field}")
        if finding["severity"] not in LEVELS:
            raise ValueError("unknown severity value")
        confidence = finding.get("confidence")
        if confidence is not None and (isinstance(confidence, (int, float)) is False or isinstance(confidence, bool) is True):
            raise ValueError("confidence must be a number or null")
        if confidence is not None and (confidence < 0 or confidence > 100):
            raise ValueError("confidence must be between zero and 100")
        if finding.get("verified") not in (True, False, None):
            raise ValueError("verified must be boolean or null")
        proof = finding.get("evidence", [])
        if isinstance(proof, list) is False:
            raise ValueError("evidence must be a list")
        for item in proof:
            if isinstance(item, dict) is False:
                raise ValueError("evidence item must be an object")


def identifier(finding: Record) -> str:
    """Version-aware ID; IDs are tenant-local, never globally unique."""
    value = finding.get("finding_id", finding.get("key"))
    if isinstance(value, str) is False or value == "":
        raise ValueError("missing finding identifier")
    return value


def evidence(finding: Record) -> list[Record]:
    value = finding.get("evidence", [])
    if isinstance(value, list) is False:
        raise ValueError("evidence must be a list")
    return value


def summary(bundle: Record) -> Record:
    counts = {level: 0 for level in sorted(LEVELS)}
    tenants: set[str] = set()
    by_tenant: dict[str, int] = {}
    verification = {"verified": 0, "unverified": 0, "unknown": 0}
    evidence_count = 0
    unknown_confidence = 0
    for finding in bundle["findings"]:
        counts[finding["severity"]] += 1
        tenants.add(finding["tenant"])
        by_tenant[finding["tenant"]] = by_tenant.get(finding["tenant"], 0) + 1
        if finding.get("verified") is True:
            verification["verified"] += 1
        elif finding.get("verified") is False:
            verification["unverified"] += 1
        else:
            verification["unknown"] += 1
        evidence_count += len(evidence(finding))
        if finding.get("confidence") is None:
            unknown_confidence += 1
    return {"schema": bundle["schema"], "findings": len(bundle["findings"]),
            "tenants": sorted(tenants), "by_severity": counts,
            "by_tenant": by_tenant, "verification": verification,
            "evidence_items": evidence_count, "unknown_confidence": unknown_confidence}
