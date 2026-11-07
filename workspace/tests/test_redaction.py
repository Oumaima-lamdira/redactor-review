"""Regressions for the configured-token redaction contract (docs/contracts.md, Redaction)."""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


def bundle(**extra: object) -> dict[str, object]:
    finding = {"finding_id": "F-1", "tenant": "cedar", "title": "plain", "severity": "low"}
    finding.update(extra)
    return {"schema": 2, "findings": [finding]}


class RedactionTests(unittest.TestCase):
    def redact(self, source: dict[str, object], secrets: list[object]) -> tuple[dict[str, object], bool]:
        """Run the public command on temp files; return output and whether the source bytes are unchanged."""
        with tempfile.TemporaryDirectory() as directory:
            source_path = pathlib.Path(directory) / "bundle.json"
            secrets_path = pathlib.Path(directory) / "secrets.json"
            source_path.write_text(json.dumps(source), encoding="utf-8")
            secrets_path.write_text(json.dumps({"values": secrets}), encoding="utf-8")
            before = hashlib.sha256(source_path.read_bytes()).hexdigest()
            process = subprocess.run(
                [sys.executable, "-B", "-m", "bundle_cli", "redact", str(source_path), "--secrets", str(secrets_path)],
                capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            unchanged = before == hashlib.sha256(source_path.read_bytes()).hexdigest()
            return json.loads(process.stdout), unchanged

    # C1, R2b: literal strings, not regular expressions.
    def testRedact_whenPunctuation_matchesLiterally(self) -> None:
        result, _ = self.redact(bundle(title="x a.b+c* y", note="a.b axb", other="abc", paren="tok(1"),
                                ["a.b+c*", "a.b", ".*", "tok("])
        finding = result["findings"][0]
        self.assertEqual(finding["title"], "x [REDACTED] y")
        self.assertEqual(finding["note"], "[REDACTED] axb")
        self.assertEqual(finding["other"], "abc")
        self.assertEqual(finding["paren"], "[REDACTED]1")

    # C2, R2c: longer tokens first, whatever the order in the secrets file.
    def testRedact_whenShorterTokenListedFirst_longerWins(self) -> None:
        result, _ = self.redact(bundle(title="x DEMO-plain-long and DEMO-plain"), ["DEMO-plain", "DEMO-plain-long"])
        self.assertEqual(result["findings"][0]["title"], "x [REDACTED] and [REDACTED]")

    # C3: empty entries are ignored.
    def testRedact_whenEmptyEntry_ignoresIt(self) -> None:
        result, _ = self.redact(bundle(title="abc"), [""])
        self.assertEqual(result["findings"][0]["title"], "abc")

    # C3 (A1): an empty entry next to a real secret does not disturb it.
    def testRedact_whenEmptyEntryMixedWithSecret_redactsSecretOnly(self) -> None:
        result, _ = self.redact(bundle(title="x DEMO-plain y"), ["", "DEMO-plain"])
        self.assertEqual(result["findings"][0]["title"], "x [REDACTED] y")

    # B1 + C6 (A2): a malformed secrets list is rejected (JSON error, exit 2), not applied
    # character by character, and the source stays untouched on failure.
    def testRedact_whenValuesNotListOfStrings_failsCleanly(self) -> None:
        for values in ("DEMO-plain", ["DEMO-plain", 123]):
            with self.subTest(values=values), tempfile.TemporaryDirectory() as directory:
                source_path = pathlib.Path(directory) / "bundle.json"
                secrets_path = pathlib.Path(directory) / "secrets.json"
                source_path.write_text(json.dumps(bundle(title="DEMO-plain")), encoding="utf-8")
                secrets_path.write_text(json.dumps({"values": values}), encoding="utf-8")
                before = hashlib.sha256(source_path.read_bytes()).hexdigest()
                process = subprocess.run(
                    [sys.executable, "-B", "-m", "bundle_cli", "redact", str(source_path), "--secrets", str(secrets_path)],
                    capture_output=True, text=True)
                self.assertEqual(process.returncode, 2, process.stderr)
                self.assertEqual(process.stdout, "")
                self.assertIn("error", json.loads(process.stderr))
                self.assertEqual(before, hashlib.sha256(source_path.read_bytes()).hexdigest())

    # C4a, R2d: strings at any depth in dictionary values and lists.
    def testRedact_whenNestedValues_redactsAtAnyDepth(self) -> None:
        source = bundle(evidence=[{"text": "DEMO-plain", "meta": {"h": ["a", "DEMO-plain"]}}])
        source["notes"] = [["DEMO-plain"]]
        source["extra"] = {"deep": {"v": "DEMO-plain"}}
        result, _ = self.redact(source, ["DEMO-plain"])
        self.assertNotIn("DEMO-plain", json.dumps(result))
        self.assertEqual(result["findings"][0]["evidence"],
                         [{"text": "[REDACTED]", "meta": {"h": ["a", "[REDACTED]"]}}])
        self.assertEqual(result["notes"], [["[REDACTED]"]])
        self.assertEqual(result["extra"], {"deep": {"v": "[REDACTED]"}})

    # C4b, R8: booleans, nulls and numbers preserved exactly (guard rail).
    def testRedact_whenNonStringData_preservesExactly(self) -> None:
        source = bundle(verified=False, confidence=0, label="0",
                        evidence=[{"meta": {"vals": [0, False, None, 1.5, True]}}])
        result, _ = self.redact(source, ["0", "1", "true", "false", "null"])
        finding = result["findings"][0]
        # json.dumps keeps true/1 and 0/"0" distinct, unlike Python ==.
        self.assertEqual(json.dumps(finding["evidence"]), json.dumps([{"meta": {"vals": [0, False, None, 1.5, True]}}]))
        self.assertIs(finding["verified"], False)
        self.assertEqual(json.dumps(finding["confidence"]), "0")
        self.assertEqual(finding["label"], "[REDACTED]")

    # C5: object keys are not rewritten, even when nested.
    def testRedact_whenSecretIsKey_keepsKey(self) -> None:
        source = bundle(evidence=[{"DEMO-plain": "DEMO-plain", "kept": "x"}])
        result, _ = self.redact(source, ["DEMO-plain"])
        self.assertEqual(result["findings"][0]["evidence"], [{"DEMO-plain": "[REDACTED]", "kept": "x"}])

    # C7: only configured values are touched (guard rail).
    def testRedact_whenUnconfiguredValue_leavesIt(self) -> None:
        result, _ = self.redact(bundle(title="saved response DEMO-other"), ["DEMO-plain"])
        self.assertEqual(result["findings"][0]["title"], "saved response DEMO-other")

    # R7, C6: the source file is never modified (guard rail).
    def testRedact_always_leavesSourceBytesUnchanged(self) -> None:
        _, unchanged = self.redact(bundle(title="DEMO-plain", evidence=[{"text": "DEMO-plain"}]), ["DEMO-plain"])
        self.assertTrue(unchanged)


if __name__ == "__main__":
    unittest.main()
