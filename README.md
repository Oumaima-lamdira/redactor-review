# Review Ivo’s generated evidence redactor

**2026-10-21, 10:00 UTC+00:00.** You are an intern at fictional Morrowbyte, which moves saved scanner evidence between disconnected review laptops. Ivo needs a review decision and a working configured-token redaction pass before sharing text evidence with a colleague.

## Your mission

Deliver a small working improvement that gives Ivo that outcome. The active ticket is `workspace/docs/request.md`; use the current contracts to decide what correct means.

At minimum, the existing redact command removes configured literal secrets from nested values without damaging other values, with a short evidence-backed ship/hold decision in CHOICES.md. Add focused regressions or a reusable local review checklist for the next generated patch.

There is no single right answer. You choose the implementation, structure and supporting evidence; explain your choices in `CHOICES.md`. Keep the documented command interface so existing consumers can use your result.

## What you have

`workspace/` contains a small Python CLI, tiny fictional fixtures, local tests, current contracts and a historical proposal. Start with its README and active ticket. `docs/local-hints.md` gives reusable offline help. You can focus on the requested behavior rather than reading every module.

Setup from this exported directory: `cd workspace && python3 -B -m bundle_cli selfcheck`. Requires Python 3.11+ standard library only; no installs, Docker, account or network. Run tests from workspace: `python3 -B -m unittest discover -s tests -v`. Commands exit after each run; no restart is needed. Everything here is fictional and is the exercise's source of truth.

## Rules

- You have **50 minutes** after setup succeeds. The session is recorded. Aim for a useful result by minute 35, verify during minutes 35–45, and package during minutes 45–50.
- We expect you to use AI when available and encourage you to check its output. Any editor or assistant is welcome. No penalty for an unavailable tool, subscription or internet outage; local hints and manual work are equally valid.
- The engineer helps with setup, audio and time only. Note reasonable assumptions in `CHOICES.md`. Environment and connection incidents pause the clock.
- Work locally. Do not contact real systems, publish, upload or use real credentials. All sample secret values are nonfunctional DEMO strings.

## What to send at minute 50

Your changed workspace and `CHOICES.md` (at most 300 words): what you changed and why, what you left out, checks and limits, and an AI suggestion you corrected or rejected if you used AI. Otherwise describe a decision you checked yourself. Send partial work with the next useful step if unfinished.

## How it is assessed

Result 35 (useful working behavior for Ivo), accuracy 25 (correct against the material), judgment 20 (scope and trade-offs), process 20 (exploration and verification on the recording). Every valid approach can earn full marks. We do not score typing speed, tool brand, polish or volume.
