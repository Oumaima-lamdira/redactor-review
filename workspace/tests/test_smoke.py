"""Fast local examples; read docs/contracts.md for edge cases not covered here."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


class SmokeTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> dict[str, object]:
        process = subprocess.run([sys.executable, "-B", "-m", "bundle_cli", *arguments], capture_output=True, text=True, check=True)
        return json.loads(process.stdout)

    def testRuntime_whenOffline_reportsReady(self) -> None:
        self.assertEqual(self.run_cli("selfcheck")["status"], "ready")

    def testSummary_whenCurrentFixture_countsMedium(self) -> None:
        self.assertEqual(self.run_cli("summary", "fixtures/current.json")["findings"], 1)

    def testSummary_whenUnverified_distinguishesUnknown(self) -> None:
        result = self.run_cli("summary", "fixtures/current.json")
        self.assertEqual(result["verification"], {"verified": 0, "unverified": 1, "unknown": 0})
        self.assertEqual(result["unknown_confidence"], 0)
        self.assertEqual(result["evidence_items"], 1)

    def testMigration_whenVersionOne_renamesIdentifier(self) -> None:
        result = self.run_cli("migrate", "fixtures/legacy.json")
        self.assertEqual(result["schema"], 2)
        self.assertEqual(result["findings"][0]["finding_id"], "F-11")

    def testLookup_whenCustomerEvidence_returnsRecord(self) -> None:
        self.assertEqual(self.run_cli("lookup", "fixtures/current.json", "--tenant", "cedar", "--finding", "F-11")["status"], "ok")

    def testImport_whenSingleResult_mapsWarning(self) -> None:
        result = self.run_cli("import", "fixtures/scanner.json", "--tenant", "cedar")
        self.assertEqual(result["findings"][0]["severity"], "medium")

    def testRedaction_whenPlainSecret_removesValue(self) -> None:
        result = self.run_cli("redact", "fixtures/current.json", "--secrets", "fixtures/secrets.json")
        self.assertNotIn("DEMO-plain", json.dumps(result))

    def testPack_whenPlainAttachment_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = str(pathlib.Path(directory) / "proof.zip")
            self.run_cli("pack", "fixtures/current.json", "--root", "fixtures", "--output", output)
            self.assertEqual(self.run_cli("verify", output)["status"], "ok")


if __name__ == "__main__":
    unittest.main()
