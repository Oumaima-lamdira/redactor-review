# Code map and decisions

`bundle_cli/__main__.py` parses commands, dispatches, and keeps machine-readable results separate from errors. It owns no persistence. `data.py` validates the common shell and provides the version-aware identifier, evidence accessor and summary. Validation intentionally accepts extension fields, which must survive migration. Consumers may add vendor-specific data.

`transform.py` handles migration, tenant-scoped views, a saved scanner adapter, and recursive value redaction. The transformations return new values; callers decide whether and where to save. Redaction recursion is designed for small exports, not hostile deeply nested megabyte payloads. `archive.py` preflights local attachment names and constructs a deterministic uncompressed ZIP, then verifies it without extraction. Fixtures are under a kilobyte each. Uncompressed ZIP avoids trading candidate CPU time for tiny transfer savings.

The CLI interface is stable, but internal functions are not a public API. A candidate may refactor modules, use dataclasses or a dispatcher, or introduce a separate engine while keeping the documented observable contract. Existing smoke tests call only the command interface. Avoid network libraries: remote retrieval and upload are deliberately outside this utility.

Error handling reports invalid input with exit code 2; a normal not_found lookup is a valid JSON response with exit code 0. Invalid ZIP verification reports status invalid when checksums disagree. The program never extracts received ZIP entries, so review code must not add extraction as a shortcut.
