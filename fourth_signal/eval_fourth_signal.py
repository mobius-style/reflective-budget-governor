#!/usr/bin/env python3
"""Fourth-signal (repetition-ratio guard) evaluation — implements PREREG.md verbatim.

Subcommands:
  retro     — TP-real + FP-retro on the 8,000 published generations
  synth     — TP-synthetic (200 inflations) + FP-stress (60 legitimate expansions)
  heldout   — FP-heldout on rollouts_heldout_{12b,26b}.jsonl (960 generations)
  replay    — four-signal governor policy replay on the retrospective corpus
  verdict   — apply the frozen criteria to results/*.json and write REPORT.md
Standard library only. Signal parameters are frozen: MIN_LEN=400, W=64, THRESH=0.50.
"""
import json, random, sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
RES = HERE / "results"; RES.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT))
MIN_LEN, W, THRESH = 400, 64, 0.50
KNOWN = {("26b", "hr_027", 6), ("26b", "acad_015", 8)}


def dup_ratio(text: str) -> float:
    s = "".join(text.split())
    if len(s) < MIN_LEN:
        return 0.0
    n = len(s) - W + 1
    distinct = len({s[i:i + W] for i in range(n)})
    return 1.0 - distinct / n


def fires(text: str) -> bool:
    return dup_ratio(text) >= THRESH


def load_rollouts(path):
    rolls = {}
    for line in Path(path).read_text().splitlines():
        r = json.loads(line)
        rolls.setdefault(r["task_id"], {})[r["iteration"]] = r
    return rolls


def cmd_retro():
    out = {"known_fired": {}, "fp_retro": [], "n_generations": 0}
    for tag in ("12b", "26b"):
        rolls = load_rollouts(ROOT / f"rollouts_n500_{tag}.jsonl")
        for tid, its in rolls.items():
            for i, r in its.items():
                out["n_generations"] += 1
                f = fires(r["output"])
                key = (tag, tid, i)
                if key in KNOWN:
                    out["known_fired"][f"{tag}:{tid}:{i}"] = {"fired": f, "dup": round(dup_ratio(r["output"]), 4)}
                elif f:
                    out["fp_retro"].append({"tag": tag, "task": tid, "iter": i, "dup": round(dup_ratio(r["output"]), 4),
                                            "chars": len(r["output"])})
    out["tp_real"] = sum(v["fired"] for v in out["known_fired"].values())
    out["fp_retro_count"] = len(out["fp_retro"])
    (RES / "retro.json").write_text(json.dumps(out, indent=1))
    print("TP-real", out["tp_real"], "/2 ; FP-retro", out["fp_retro_count"], "/", out["n_generations"] - 2)


def cmd_synth():
    rng = random.Random(20260919)
    rolls = load_rollouts(ROOT / "rollouts_n500_26b.jsonl")
    clean = [r["output"] for its in rolls.values() for r in its.values()
             if len("".join(r["output"].split())) >= MIN_LEN and dup_ratio(r["output"]) < 0.10]
    rng.shuffle(clean)
    base = clean[:50]
    synth = []
    for j, txt in enumerate(base):
        for k in (3, 5, 10, 50):
            sep = "\n\n***\n\n" if (j + k) % 2 == 0 else "\n\n"
            synth.append({"base": j, "k": k, "sep": bool(sep.strip()), "fired": fires(sep.join([txt] * k))})
    tp = sum(s["fired"] for s in synth)
    stress_base = clean[50:110]
    stress = []
    for j, txt in enumerate(stress_base):
        items = "\n".join(f"- Item {n}: {rng.choice(['Review', 'Confirm', 'Update', 'Schedule', 'Audit'])} "
                          f"the {rng.choice(['budget', 'roster', 'timeline', 'vendor list', 'policy draft', 'risk log'])} "
                          f"for {rng.choice(['Q1', 'Q2', 'Q3', 'Q4'])} with {rng.choice(['finance', 'legal', 'ops', 'HR'])} "
                          f"by {rng.choice(['Monday', 'Wednesday', 'Friday'])} (ref {rng.randint(1000, 9999)})."
                          for n in range(1, 9))
        ext = txt + "\n\n" + items
        stress.append({"base": j, "dup": round(dup_ratio(ext), 4), "fired": fires(ext)})
    fp = sum(s["fired"] for s in stress)
    out = {"tp_synthetic": tp, "n_synthetic": len(synth), "fp_stress": fp, "n_stress": len(stress),
           "synthetic": synth, "stress": stress}
    (RES / "synth.json").write_text(json.dumps(out, indent=1))
    print("TP-synth", tp, "/", len(synth), "; FP-stress", fp, "/", len(stress))


def cmd_heldout():
    out = {"n": 0, "fired": []}
    for tag in ("12b", "26b"):
        p = HERE / f"rollouts_heldout_{tag}.jsonl"
        for line in p.read_text().splitlines():
            r = json.loads(line); out["n"] += 1
            if fires(r["output"]):
                out["fired"].append({"tag": tag, "task": r["task_id"], "iter": r["iteration"],
                                     "dup": round(dup_ratio(r["output"]), 4), "chars": len(r["output"])})
    out["fp_heldout_count"] = len(out["fired"])
    out["fp_heldout_rate"] = out["fp_heldout_count"] / out["n"] if out["n"] else None
    (RES / "heldout.json").write_text(json.dumps(out, indent=1))
    print("FP-heldout", out["fp_heldout_count"], "/", out["n"])


def cmd_replay():
    from analyze import compute_stops
    tasks = {t["id"]: t for t in json.loads((ROOT / "tasks_n500.json").read_text())}
    out = {}
    for tag in ("12b", "26b"):
        rolls = load_rollouts(ROOT / f"rollouts_n500_{tag}.jsonl")
        changed = []
        tokA = tok3 = tok4 = 0
        for tid, its in rolls.items():
            seq = [tasks[tid]["seed"]] + [its[i]["output"] for i in range(1, 9)]
            s = compute_stops(seq)
            stop3 = s["C"]
            # fourth signal: first iteration that fires, priority over the others
            fire_at = next((i for i in range(1, 9) if fires(seq[i])), None)
            if fire_at is not None and fire_at <= stop3:
                stop4, ret4, reason4 = fire_at, fire_at - 1, "repetition_guard_rollback"
            else:
                stop4, ret4, reason4 = stop3, stop3, s["C_reason"]
            tok = lambda n: sum(its[i]["prompt_tokens"] + its[i]["eval_tokens"] for i in range(1, n + 1))
            tokA += tok(8); tok3 += tok(stop3); tok4 += tok(stop4)
            if (stop4, ret4) != (stop3, stop3):
                changed.append({"task": tid, "stop3": stop3, "reason3": s["C_reason"], "stop4": stop4,
                                "returned4": ret4, "reason4": reason4})
        out[tag] = {"chains_changed": len(changed), "changed": changed,
                    "tokens": {"A": tokA, "three_signal": tok3, "four_signal": tok4}}
    (RES / "replay.json").write_text(json.dumps(out, indent=1))
    for tag, v in out.items():
        print(tag, "chains changed:", v["chains_changed"], [(c["task"], c["stop3"], "->", c["returned4"]) for c in v["changed"]])


def cmd_verdict():
    retro = json.loads((RES / "retro.json").read_text())
    synth = json.loads((RES / "synth.json").read_text())
    held = json.loads((RES / "heldout.json").read_text())
    replay = json.loads((RES / "replay.json").read_text())
    c = {
        "TP-real (2/2)": retro["tp_real"] == 2,
        "TP-synthetic (>=95%)": synth["tp_synthetic"] / synth["n_synthetic"] >= 0.95,
        "FP-heldout (<=0.5%)": held["fp_heldout_rate"] is not None and held["fp_heldout_rate"] <= 0.005,
        "FP-stress (0/60)": synth["fp_stress"] == 0,
    }
    verdict = "GO" if all(c.values()) else "NO-GO"
    lines = ["# Fourth signal (repetition-ratio guard) — REPORT (machine-generated)", "",
             f"Signal: dup(x) = 1 - distinct/total 64-char shingles on whitespace-stripped text, MIN_LEN 400, fires at >= 0.50.", "",
             "| criterion | value | pass |", "|---|---|---|",
             f"| TP-real | {retro['tp_real']}/2 ({retro['known_fired']}) | {c['TP-real (2/2)']} |",
             f"| TP-synthetic | {synth['tp_synthetic']}/{synth['n_synthetic']} | {c['TP-synthetic (>=95%)']} |",
             f"| FP-heldout | {held['fp_heldout_count']}/{held['n']} ({(held['fp_heldout_rate'] or 0):.2%}) | {c['FP-heldout (<=0.5%)']} |",
             f"| FP-stress | {synth['fp_stress']}/{synth['n_stress']} | {c['FP-stress (0/60)']} |",
             f"| FP-retro (reported) | {retro['fp_retro_count']}/{retro['n_generations'] - 2} | — |", "",
             f"## Pre-registered verdict: **{verdict}**", "", "## Policy replay (retrospective corpus)", ""]
    for tag, v in replay.items():
        t = v["tokens"]
        lines.append(f"- {tag}: chains changed {v['chains_changed']} ; tokens A={t['A']} three-signal={t['three_signal']} four-signal={t['four_signal']}")
        for ch in v["changed"]:
            lines.append(f"  - {ch['task']}: three-signal stop {ch['stop3']} ({ch['reason3']}) -> four-signal returns iterate {ch['returned4']} ({ch['reason4']})")
    if held.get("fired"):
        lines += ["", "## Held-out firings", ""] + [f"- {f}" for f in held["fired"]]
    if retro.get("fp_retro"):
        lines += ["", "## Retrospective firings (non-collapse)", ""] + [f"- {f}" for f in retro["fp_retro"]]
    (HERE / "REPORT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:16]))


if __name__ == "__main__":
    {"retro": cmd_retro, "synth": cmd_synth, "heldout": cmd_heldout,
     "replay": cmd_replay, "verdict": cmd_verdict}[sys.argv[1]]()
