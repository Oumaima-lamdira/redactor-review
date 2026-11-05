# Morrowbyte evidence bundles

Morrowbyte helps small teams move saved scanner evidence between disconnected review laptops. This repository is a local command-line utility, not a scanner or a server. Everything is fictional. It never requests a URL or uploads files.

Requires Python 3.11+ only. No pip, virtual environment, Docker, database or administrator access. From this directory run `python3 -B -m bundle_cli selfcheck`. From the exported project root run `cd workspace && python3 -B -m bundle_cli selfcheck`. Run examples/tests here with `python3 -B -m unittest discover -s tests -v`. Commands finish in a single process; there is nothing to restart.

Start with `docs/handoff.md`, then `docs/contracts.md` and the active ticket `docs/request.md` when present. `docs/architecture.md` maps the small modules. `docs/local-hints.md` gives offline exploration prompts and commands; these are available to everyone.

Examples: `python3 -B -m bundle_cli migrate fixtures/legacy.json`; `python3 -B -m bundle_cli lookup fixtures/current.json --tenant cedar --finding F-11`; `python3 -B -m bundle_cli import fixtures/scanner.json --tenant cedar`.

`pack` takes a JSON bundle, an attachment root and an output ZIP. `verify` reads a ZIP without extracting it. `redact` takes a JSON secrets list via `--secrets fixtures/secrets.json`. Use `--help` on any command. JSON results go to stdout, errors to stderr with exit code 2. Redirect stdout to save a transformed document. Never redirect to the input path, because the shell truncates it before the program starts.

The included tests cover ordinary examples. Green examples do not prove every contract or the active ticket is satisfied. Keep input fixtures unchanged when checking behavior; use temporary output files.
