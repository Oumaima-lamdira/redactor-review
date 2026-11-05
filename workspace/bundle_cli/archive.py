"""A deterministic, inspectable ZIP handoff; never an upload client."""
from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile

from bundle_cli import data


def _member(source: pathlib.Path, root: pathlib.Path) -> str:
    if source.is_absolute() is True or ".." in source.parts:
        raise ValueError("attachments must be relative paths without traversal")
    resolved_root = root.resolve()
    resolved_source = (root / source).resolve()
    if resolved_source.is_relative_to(resolved_root) is False:
        raise ValueError("attachment escapes source root")
    if source.as_posix() in ("bundle.json", "checksums.json"):
        raise ValueError("reserved attachment name")
    if resolved_source.is_file() is False:
        raise ValueError(f"missing attachment: {source}")
    return source.as_posix()


def build(bundle: data.Record, root: pathlib.Path, output: pathlib.Path) -> data.Record:
    """Preflight every member before opening output, so failure leaves no half ZIP."""
    data.check(bundle)
    members: dict[str, bytes] = {}
    for attachment in bundle.get("attachments", []):
        name = _member(pathlib.Path(attachment), root)
        members[name] = (root / name).read_bytes()
    members["bundle.json"] = (json.dumps(bundle, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    checksums = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(members.items())}
    members["checksums.json"] = json.dumps(checksums, sort_keys=True).encode("utf-8")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, content in sorted(members.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content)
    return {"status": "ok", "members": sorted(members), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def verify(path: pathlib.Path) -> data.Record:
    """Read bytes and compare; untrusted ZIPs are never extracted."""
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            errors.append("duplicate archive member")
        if "checksums.json" not in names:
            return {"status": "invalid", "errors": ["missing checksums"]}
        checksums = json.loads(archive.read("checksums.json"))
        if set(names) != set(checksums) | {"checksums.json"}:
            errors.append("member inventory mismatch")
        for name, expected in checksums.items():
            if name not in names:
                errors.append(f"missing: {name}")
            elif hashlib.sha256(archive.read(name)).hexdigest() != expected:
                errors.append(f"checksum mismatch: {name}")
    return {"status": "ok" if len(errors) == 0 else "invalid", "errors": errors}
