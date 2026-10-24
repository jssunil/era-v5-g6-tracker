# ⚡ ERA V5 Capstone — Team G6 (Performance & Kernels) Public Tracker

Public, forkable progress tracker for **Team G6: Performance and Kernels** (`teams/06-performance/`) in the **ERA V5 Capstone** (`theschoolofai/era-v5-lab`).

- 📋 **Live Markdown Dashboard:** [TRACKER.md](./TRACKER.md) (renders directly on GitHub with tables & Mermaid Gantt chart)
- 🌐 **Interactive HTML Dashboard:** `dist/index.html` (built from `tracker/*.json` via `python scripts/build.py` using the `era-v5-capstone-tracker` template)

---

## 🛠️ How Team Members Update Progress

Every G6 team member (Core, Week 2 Rotation, and Week 3 Rotation) can fork this repository (or edit directly if added as a collaborator) and update progress in **2 minutes**:

1. **Edit the JSON files in `tracker/`:**
   - `tracker/members.json` — Add your GitHub handle, Data Diagnosis `pack_id`, `diag_150` / `diag_500` status (`planned`, `active`, `at-risk`, `blocked`, `done`), and PR links.
   - `tracker/milestones.json` — Update task `status`, `owner`, or `evidence` (link to your PR or commit in `theschoolofai/era-v5-lab`).
   - `tracker/measurements.json` — Record kernel timings (`ms`), baseline timings (`baseline_ms`), run spread (`spread_pct`), `parity` (`pass`/`fail`), `mutation_101` (`pass`/`fail`), and `deterministic` (`pass`/`fail`).
   - `tracker/decisions.json` & `tracker/questions.json` — Log team design decisions and cross-team questions for G4, G5, and G8.

2. **Rebuild & Validate Locally:**
   ```bash
   python scripts/build.py
   ```
   This validates all JSON schemas and automatically regenerates both:
   - `TRACKER.md` (the GitHub Markdown view)
   - `dist/index.html` (the standalone interactive HTML report with SVG Gantt timeline)

3. **Commit & Open a Pull Request:**
   ```bash
   git add tracker/ TRACKER.md dist/index.html
   git commit -m "Update G6-W1-06 status and benchmark numbers"
   git push
   ```
   GitHub Actions (`.github/workflows/build.yml`) automatically validates the schema on every push and PR.

---

## 📁 Repository Layout

```text
era-v5-g6-tracker/
├── TRACKER.md                   # Auto-generated GitHub Markdown dashboard
├── README.md                    # Usage & collaboration guide
├── tracker/
│   ├── members.json             # Core G6 roster, W2/W3 rotations & Data Diagnosis status
│   ├── milestones.json          # Week 1–4 G6 deliverables, gates & cross-team dependencies
│   ├── measurements.json        # Kernel benchmarks, parity, 1.01x mutation & determinism results
│   ├── decisions.json           # Team G6 engineering decisions
│   └── questions.json           # Cross-team (G4/G5/G8) & internal open questions
├── templates/
│   ├── head.part                # IBM Plex CSS & layout (light/dark mode)
│   └── body.part                # Interactive HTML + SVG Gantt renderer
├── scripts/
│   └── build.py                 # Validator + HTML & Markdown generator
├── dist/
│   └── index.html               # Built standalone HTML dashboard
└── .github/workflows/
    └── build.yml                # CI validation & artifact upload on every PR/push
```
