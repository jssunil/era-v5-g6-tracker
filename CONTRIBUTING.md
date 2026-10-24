# Contributing to the Team G6 Tracker

## Status Values
All milestone `status` fields and member `diag_150` / `diag_500` fields must use one of:
- `"planned"` — Not started yet
- `"active"` — Currently in progress
- `"at-risk"` — At risk of missing the gate deadline
- `"blocked"` — Blocked on an external dependency (e.g., G4 or G5 handoff)
- `"done"` — Completed with a PR/commit link in `"evidence"`

## Measurement Values
In `tracker/measurements.json`, `parity`, `mutation_101`, and `deterministic` must be one of:
- `"pass"`
- `"fail"`
- `"pending"`

## Running the Builder
Always run:
```bash
python scripts/build.py
```
before committing so `TRACKER.md` and `dist/index.html` stay synchronized with `tracker/*.json`.
