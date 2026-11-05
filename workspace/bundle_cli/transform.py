"""Pure transformations. The CLI also accepts alternative implementations."""
from __future__ import annotations

import copy
import re

from bundle_cli import data


def migrate(bundle: data.Record) -> data.Record:
    """Upgrade the old transport shape without changing evidence semantics."""
    data.check(bundle)
    result = copy.deepcopy(bundle)
    if result["schema"] == 2:
        return result
    result["schema"] = 2
    for finding in result["findings"]:
        finding["finding_id"] = finding.pop("key")
        if "verified" not in finding:
            finding["verified"] = None
        if "confidence" not in finding:
            finding["confidence"] = None
    return result


def lookup(bundle: data.Record, tenant: str, finding_id: str) -> data.Record:
    """Return an evidence view without revealing existence across tenants."""
    data.check(bundle)
    for finding in bundle["findings"]:
        if finding["tenant"] == tenant and data.identifier(finding) == finding_id:
            if finding.get("visibility", "shareable") != "shareable":
                return {"status": "not_found"}
            visible = [copy.deepcopy(item) for item in data.evidence(finding)
                       if item.get("audience", "customer") == "customer"]
            return {"status": "ok", "finding": {
                "finding_id": data.identifier(finding), "tenant": tenant,
                "title": finding["title"], "severity": finding["severity"],
                "evidence": visible}}
    return {"status": "not_found"}


def import_report(report: data.Record, tenant: str) -> data.Record:
    """Bridge Lanternprobe's saved report into bundle schema 2."""
    if report.get("format") != "lanternprobe-1":
        raise ValueError("unsupported scanner format")
    findings: list[data.Record] = []
    positions: dict[tuple[str, str], int] = {}
    levels = {"fatal": "critical", "error": "high", "warning": "medium", "note": "low"}
    for result in report.get("results", []):
        if result.get("suppressed") is True:
            continue
        rule_id = result.get("rule_id", "unknown-rule")
        location = result.get("location", "unknown-location")
        identity = (rule_id, location)
        item: data.Record = {
            "finding_id": f"{rule_id}@{location}", "tenant": tenant,
            "title": result.get("message", rule_id),
            "severity": levels.get(result.get("level"), "unknown"),
            "verified": None, "confidence": result.get("confidence"),
            "visibility": "shareable", "rule_id": rule_id,
            "location": location, "evidence": [{"text": result.get("message", ""), "audience": "customer"}]}
        # Identity excludes message and severity: keep first occurrence, append proof.
        if identity in positions:
            findings[positions[identity]]["evidence"].extend(item["evidence"])
        else:
            positions[identity] = len(findings)
            findings.append(item)
    return {"schema": 2, "scanner": "Lanternprobe", "findings": findings}


def _clean_text(value: str, secrets: list[str]) -> str:
    cleaned = value
    for secret in secrets:
        if secret != "":
            cleaned = re.sub(secret, "[REDACTED]", cleaned)
    return cleaned


def _walk(value: object, secrets: list[str]) -> object:
    if isinstance(value, dict) is True:
        result = {key: _clean_text(item, secrets) if isinstance(item, str) is True else item
                  for key, item in value.items()}
        if isinstance(result.get("findings"), list) is True:
            result["findings"] = [{key: _clean_text(item, secrets) if isinstance(item, str) is True else item
                                   for key, item in finding.items()}
                                  for finding in result["findings"]]
        return result
    return value


def redact(bundle: data.Record, secrets: list[str]) -> data.Record:
    """Remove configured literal secrets from nested values, preserving types."""
    data.check(bundle)
    result = _walk(bundle, secrets)
    if isinstance(result, dict) is False:
        raise ValueError("bundle must remain an object")
    return result
