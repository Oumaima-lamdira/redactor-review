"""Public interface: one JSON result on stdout; diagnostic errors on stderr."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import zipfile

from bundle_cli import archive
from bundle_cli import data
from bundle_cli import transform


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Morrowbyte local evidence bundles")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("selfcheck", help="check runtime and bundled fixture, no installs")
    for operation in ("migrate", "summary"):
        command = commands.add_parser(operation)
        command.add_argument("source")
    lookup = commands.add_parser("lookup")
    lookup.add_argument("source")
    lookup.add_argument("--tenant", required=True)
    lookup.add_argument("--finding", required=True)
    bridge = commands.add_parser("import")
    bridge.add_argument("source")
    bridge.add_argument("--tenant", required=True)
    redact = commands.add_parser("redact")
    redact.add_argument("source")
    redact.add_argument("--secrets", required=True, help="JSON object with values list")
    pack = commands.add_parser("pack")
    pack.add_argument("source")
    pack.add_argument("--root", required=True)
    pack.add_argument("--output", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("source")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "selfcheck":
            if sys.version_info < (3, 11):
                raise ValueError("Python 3.11 or newer is required")
            sample = pathlib.Path(__file__).parent.parent / "fixtures/current.json"
            data.check(data.load(str(sample)))
            result: data.Record = {"status": "ready", "network": "unused"}
        elif args.command == "verify":
            result = archive.verify(pathlib.Path(args.source))
        else:
            source = data.load(args.source)
            if args.command == "migrate":
                result = transform.migrate(source)
            elif args.command == "summary":
                data.check(source)
                result = data.summary(source)
            elif args.command == "lookup":
                result = transform.lookup(source, args.tenant, args.finding)
            elif args.command == "import":
                result = transform.import_report(source, args.tenant)
            elif args.command == "redact":
                result = transform.redact(source, data.load(args.secrets)["values"])
            else:
                result = archive.build(source, pathlib.Path(args.root), pathlib.Path(args.output))
        data.emit(result)
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
