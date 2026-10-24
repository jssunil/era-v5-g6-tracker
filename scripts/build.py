#!/usr/bin/env python3
"""Build the public Team G6 HTML dashboard (dist/index.html) and Markdown tracker (TRACKER.md) from tracker/*.json.

Usage:  python scripts/build.py [--snapshot YYYY-MM-DD] [--repo-url URL]

Validates all JSON schemas in tracker/*.json, embeds the current git commit SHA,
and generates:
  1. dist/index.html (Interactive HTML dashboard with SVG Gantt chart, modeled after era-v5-capstone-tracker)
  2. TRACKER.md      (GitHub-native Markdown dashboard for direct viewing on GitHub)
"""
import argparse
import datetime as dt
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
COLLECTIONS = ["members", "milestones", "measurements", "decisions", "questions"]
REQUIRED = {
    "members": ["id", "name", "role", "weeks", "assigned_tasks", "pack_id", "diag_150", "diag_500"],
    "milestones": ["id", "code", "title", "lane", "owner", "start", "due", "gate", "status"],
    "measurements": ["id", "date", "task", "shape"],
    "decisions": ["id", "code", "date", "decision", "state"],
    "questions": ["id", "topic", "question", "status"],
}
STATUSES = {"planned", "active", "at-risk", "blocked", "done"}
STATUS_BADGE = {
    "done": "🟢 Done",
    "active": "🔵 In Progress",
    "at-risk": "🟠 At Risk",
    "blocked": "🔴 Blocked",
    "planned": "⚪ Planned",
}
YN_BADGE = {
    "pass": "🟢 Pass",
    "fail": "🔴 Fail",
    "pending": "⚪ Pending",
}


def load():
    data = {}
    for col in COLLECTIONS:
        path = ROOT / "tracker" / f"{col}.json"
        items = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        ids = set()
        for it in items:
            missing = [k for k in REQUIRED[col] if it.get(k) in (None, "")]
            if missing:
                raise SystemExit(f"{col}: item {it.get('id', '?')} is missing {missing}")
            if it["id"] in ids:
                raise SystemExit(f"{col}: duplicate id {it['id']}")
            ids.add(it["id"])
            if col == "milestones" and it["status"] not in STATUSES:
                raise SystemExit(f"milestones: {it['id']} has unknown status {it['status']}")
            if col == "members":
                for dk in ("diag_150", "diag_500"):
                    if it[dk] not in STATUSES:
                        raise SystemExit(f"members: {it['id']} has unknown {dk} status {it[dk]}")
        data[col] = items
    return data


def commit():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "tracker"], cwd=ROOT, text=True).strip()
        return sha + ("+uncommitted" if dirty else "")
    except Exception:
        return "no-git"


def render_html(data, sha, snapshot, repo_url):
    head = (ROOT / "templates" / "head.part").read_text(encoding="utf-8")
    body = (ROOT / "templates" / "body.part").read_text(encoding="utf-8")
    title = "ERA V5 Capstone · Team G6 (Performance & Kernels) Tracker"
    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (
        head.replace("__TITLE__", title)
        + "\n"
        + body.replace("__COMMIT__", sha)
        .replace("__GENERATED__", generated)
        .replace("__SNAPSHOT__", snapshot)
        .replace("__REPO_URL__", repo_url)
        .replace("__DATA__", payload)
    )


def render_markdown(data, sha, snapshot, repo_url):
    ms = data["milestones"]
    members = data["members"]
    meas = data["measurements"]
    decs = data["decisions"]
    qs = data["questions"]

    w1 = [m for m in ms if m["lane"] == "Week 1"]
    w1_done = sum(1 for m in w1 if m["status"] == "done")
    core_members = [m for m in members if m["id"].startswith("M")]
    diag_150_done = sum(1 for m in core_members if m["diag_150"] == "done")
    diag_500_done = sum(1 for m in core_members if m["diag_500"] == "done")

    lines = [
        "# ⚡ ERA V5 Capstone — Team G6 (Performance & Kernels) Public Tracker",
        "",
        f"> **Snapshot Date:** `{snapshot}` · **Commit:** `{sha}` · **Team Folder:** `teams/06-performance/` · **Team Lead:** Vaibhav Lohar",
        ">",
        "> **How to Update:** Edit `tracker/*.json` (or submit a PR) and run `python scripts/build.py` to regenerate both `TRACKER.md` and `dist/index.html`.",
        "",
        "## 📊 Summary Strip",
        "",
        "| Metric | Progress | Next Hard Gate | Target |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Week 1 G6 Tasks** | **{w1_done} / {len(w1)}** Done | **Tue 27 Oct, 23:59 IST** (3-Day Rule) | 150 Diagnosis rows + 90% Week 1 G6 task |",
        f"| **Core Data Diagnosis (150 rows)** | **{diag_150_done} / {len(core_members)}** Done | **Sat 31 Oct, 23:59 IST** (Gate 1) | 500 Diagnosis rows + `medicine.md` + G6 Gate 1 |",
        f"| **Core Data Diagnosis (500 rows + Med)** | **{diag_500_done} / {len(core_members)}** Done | **Sat 14 Nov** (Gate 2) / **23 Nov** (Freeze) | Shared H100 Baseline, 2 Speedups, Kernel Freeze |",
        "",
        "---",
        "",
        "## 🚨 Week 1 Gate 1 Acceptance Criteria (Sat 31 Oct, 23:59 IST)",
        "",
        "1. **Zero Test Failures:** `pytest teams/06-performance/correctness -q` returns `0` failures.",
        "2. **1.01× Broken Function Check:** Multiplying any fast output by `1.01` causes the correctness suite to **FAIL**.",
        "3. **≤ 5% Baseline Repeatability:** Two consecutive baseline runs agree within `<= 5%` for every part of the training step (`results/baseline_v0.md`).",
        "4. **Individual Data Diagnosis:** Every member has merged `150` rows by **27 Oct** and all `500` rows + `medicine.md` (with `<= 1%` gold drop harm test) by **31 Oct**.",
        "",
        "---",
        "",
        "## 🗓️ Week 1 Deliverables & Cross-Team Gates (24–31 Oct 2026)",
        "",
        "| Code | Deliverable & Gate | Owner | Due | Status | Evidence / PR |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for m in ms:
        if m["lane"] in ("Data Diagnosis", "Week 1", "Cross-Team"):
            hard_tag = " **[HARD GATE]**" if m.get("hard") else ""
            ev = m.get("evidence") or "_Pending PR_"
            lines.append(
                f"| `{m['code']}` | **{m['title']}**{hard_tag}<br><sub>Gate: {m['gate']}</sub> | {m['owner']} | `{m['due']}` | {STATUS_BADGE.get(m['status'], m['status'])} | {ev} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## 👥 Team G6 Roster, Task Ownership & Data Diagnosis Tracker",
        "",
        "### Core Team (Weeks 1–4)",
        "",
        "| ID | Member | GitHub | Role & Rotations | Assigned G6 Tasks | Diagnosis Pack | 27 Oct (150) | 31 Oct (500+Med) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for m in core_members:
        gh = f"[@{m['handle']}](https://github.com/{m['handle']})" if m.get("handle") else "_TBD_"
        lines.append(
            f"| `{m['id']}` | **{m['name']}** | {gh} | {m['role']} | {m['assigned_tasks']} | `{m['pack_id']}` | {STATUS_BADGE.get(m['diag_150'], m['diag_150'])} | {STATUS_BADGE.get(m['diag_500'], m['diag_500'])} |"
        )

    rot_members = [m for m in members if not m["id"].startswith("M")]
    lines.extend([
        "",
        "### Incoming Rotation Members (Week 2 & Week 3)",
        "",
        "| ID | Member | Rotation Window | Rotation Task in Team G6 | Status / Link |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for m in rot_members:
        ev = m.get("evidence") or "_Scheduled_"
        lines.append(
            f"| `{m['id']}` | **{m['name']}** | {m['weeks']} | {m['assigned_tasks']} | {ev} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 🚀 Weeks 2–4 Capstone Roadmap (Gates 2, 3 & 4)",
        "",
        "| Code | Milestone & Gate | Owner | Window | Status | Evidence |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for m in ms:
        if m["lane"] in ("Week 2", "Week 3", "Week 4"):
            ev = m.get("evidence") or "_Planned_"
            lines.append(
                f"| `{m['code']}` | **{m['title']}**<br><sub>Gate: {m['gate']}</sub> | {m['owner']} | `{m['start']}` → `{m['due']}` | {STATUS_BADGE.get(m['status'], m['status'])} | {ev} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## 📈 Timeline (Mermaid Gantt)",
        "",
        "```mermaid",
        "gantt",
        "    title Team G6 (Performance & Kernels) — Weeks 1 to 4 Schedule",
        "    dateFormat  YYYY-MM-DD",
        "    axisFormat  %d %b",
        "    section Data Diagnosis",
        "    DIAG-150 (150 Rows + 90% W1 Task) :active, d01, 2026-10-24, 2026-10-27",
        "    DIAG-500 (500 Rows + medicine.md) :d02, 2026-10-24, 2026-10-31",
        "    section Week 1 (Gate 1)",
        "    G6-W1-01 perfkit/timer.py (Sunil) :active, w101, 2026-10-24, 2026-10-27",
        "    G6-W1-02 perfkit/bench.py (Sunil) :active, w102, 2026-10-24, 2026-10-28",
        "    G6-W1-03 correctness/framework.py :active, w103, 2026-10-24, 2026-10-27",
        "    G6-W1-06 test_moe.py 384+1 (Sunil):active, w106, 2026-10-24, 2026-10-28",
        "    G6-W1-07 test_reversible.py (Sunil):active, w107, 2026-10-25, 2026-10-29",
        "    G6-W1-04 test_ke.py (Adinath)     :w104, 2026-10-25, 2026-10-29",
        "    G6-W1-05 test_attention.py (Shashank):w105, 2026-10-25, 2026-10-29",
        "    G6-W1-08 baseline_v0.md           :w108, 2026-10-27, 2026-10-30",
        "    G6-W1-09 slowest5_v0.md           :w109, 2026-10-28, 2026-10-30",
        "    G6-W1-10 G8 Handoff & Gate 1      :crit, w110, 2026-10-29, 2026-10-31",
        "    section Weeks 2-4",
        "    G6-W2-01 H100 Baseline & 2 Speedups:w201, 2026-11-01, 2026-11-14",
        "    G6-W3-01 Dry Run 1 Full Profile   :w301, 2026-11-15, 2026-11-21",
        "    G6-W4-01 Kernel Freeze & Dry Run 2:crit, w401, 2026-11-22, 2026-11-26",
        "    G6-W4-02 Launch Check (Gate 4)    :crit, w402, 2026-11-26, 2026-11-28",
        "```",
        "",
        "---",
        "",
        "## ⏱️ Benchmark, Parity & 1.01× Mutation Test Results",
        "",
        "> A speedup is only valid when **Forward/Backward Parity** passes, the **1.01× Perturbation Check** fails as expected, **Bit-Determinism** holds, and **2 Baseline Runs** agree within `<= 5%`.",
        "",
        "| Date | Component / Kernel | Shape | Fast (ms) | Baseline (ms) | Speedup | Run Spread | Parity | 1.01× Check | Deterministic | GPU |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for r in meas:
        t = float(r.get("ms") or 0)
        b = float(r.get("baseline_ms") or 0)
        sp = f"{b / t:.2f}×" if t > 0 and b > 0 else "—"
        t_str = f"{t:.2f}" if t > 0 else "—"
        b_str = f"{b:.2f}" if b > 0 else "—"
        lines.append(
            f"| `{r['date']}` | **{r['task']}**<br><sub>{r.get('notes', '')}</sub> | `{r['shape']}` | `{t_str}` | `{b_str}` | **{sp}** | `{r.get('spread_pct', '—')}` | {YN_BADGE.get(r.get('parity', 'pending'), '⚪ Pending')} | {YN_BADGE.get(r.get('mutation_101', 'pending'), '⚪ Pending')} | {YN_BADGE.get(r.get('deterministic', 'pending'), '⚪ Pending')} | {r.get('gpu', '—')} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 🧭 Engineering Decisions",
        "",
        "| Code | Date | Decision | Rationale | State |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for d in decs:
        st = "🟢 Decided" if d["state"] == "decided" else "⚪ Proposed"
        lines.append(f"| `{d['code']}` | `{d['date']}` | {d['decision']} | {d.get('reason', '')} | {st} |")

    lines.extend([
        "",
        "---",
        "",
        "## ❓ Cross-Team & Internal Questions",
        "",
        "| ID | Target | Question | Answer / Resolution | Status |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for q in qs:
        st = "🟢 Answered" if q["status"] == "answered" else "⚪ Open"
        ans = q.get("answer") or "_Pending_"
        lines.append(f"| `{q['id']}` | **{q['topic']}** | {q['question']} | {ans} | {st} |")

    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=dt.date.today().isoformat(),
                    help="date that 'days left' is measured from (default: today)")
    ap.add_argument("--repo-url", default="https://github.com/jssunil/era-v5-g6-tracker",
                    help="GitHub repository URL for links in the rendered tracker")
    args = ap.parse_args()

    data = load()
    sha = commit()

    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    html = render_html(data, sha, args.snapshot, args.repo_url)
    (out / "index.html").write_text(html, encoding="utf-8")

    md = render_markdown(data, sha, args.snapshot, args.repo_url)
    (ROOT / "TRACKER.md").write_text(md, encoding="utf-8")

    # Also keep parent capstone/TRACKER.md synced if inside capstone workspace
    parent_tracker = ROOT.parent / "TRACKER.md"
    if ROOT.parent.name == "capstone":
        parent_tracker.write_text(md, encoding="utf-8")

    total = sum(len(data[c]) for c in COLLECTIONS)
    print(f"built dist/index.html and TRACKER.md ({total} items) from {sha}")


if __name__ == "__main__":
    main()
