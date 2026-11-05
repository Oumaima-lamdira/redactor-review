# Offline help available to every candidate

No internet or assistant subscription is needed to use these materials. If AI is available, ask it to explain the public command and identify contract edge cases, then check its answer against the actual docs. If it is unavailable, use the same questions yourself. Tool outages do not reduce the process score.

1. Run `python3 -B -m bundle_cli --help`, then the active command's `--help`.
2. Read the matching heading in `docs/contracts.md` and the small active ticket. Write two examples that would distinguish correct output from a plausible shortcut.
3. Run `python3 -B -m unittest discover -s tests -v`. These are examples, not an exhaustive proof.
4. Put a small new JSON example in a temporary directory, run the command against it, and compare the result with your expected value. Use `python3 -B -m json.tool path.json` to inspect JSON offline.
5. Check source bytes before and after any command intended to be read-only. For ZIPs, `python3 -B -m zipfile -l output.zip` lists names without extracting.
6. Record what you checked, what remains unknown, and the smallest next test in CHOICES.md. A precise partial result is useful.
