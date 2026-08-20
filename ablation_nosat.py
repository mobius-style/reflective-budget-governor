#!/usr/bin/env python3
"""RBG ablation: saturation signal disabled (d_r + loop + hard cap only).

Subcommands: stops | batches | collect | report
Reuses existing judgments where the variant stop index matches the registered
config's stop index; only newly-differing pairs are judged.
"""
import json, math, random, sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
import analyze
import analyze_n500 as base_run

MODELS = base_run.MODELS
MAX_ITERS = 8
BATCH_SIZE = 25


def variant_stops():
    analyze.SAT_THRESHOLD = 9.9  # saturation can never fire
    tasks = json.loads((BASE / "tasks_n500.json").read_text())
    out_all = {}
    for tag in MODELS:
        rolls = base_run.load_rollouts(tag)
        out = {}
        for t in tasks:
            iters = rolls[t["id"]]
            seq = [t["seed"]] + [iters[i]["output"] for i in range(1, MAX_ITERS + 1)]
            s = analyze.compute_stops(seq)
            tok = lambda n: sum(iters[i]["prompt_tokens"] + iters[i]["eval_tokens"]
                                for i in range(1, n + 1))
            out[t["id"]] = {"stop_C": s["C"], "C_reason": s["C_reason"],
                            "tok_C": tok(s["C"]), "tok_A": tok(MAX_ITERS)}
        out_all[tag] = out
    (BASE / "stops_nosat.json").write_text(json.dumps(out_all, indent=1))
    return out_all


def cmd_stops():
    out_all = variant_stops()
    for tag, out in out_all.items():
        base_stops = json.loads((BASE / f"stops_{tag}.json").read_text())
        changed = sum(1 for tid in out
                      if out[tid]["stop_C"] != base_stops[tid]["stops"]["C"])
        early = sum(1 for v in out.values() if v["stop_C"] < 8)
        red = 1 - sum(v["tok_C"] for v in out.values()) / sum(v["tok_A"] for v in out.values())
        print(f"{tag}: early={early}/500 changed_vs_registered={changed} reduction={red:.1%}")


def cmd_batches():
    tasks = {t["id"]: t for t in json.loads((BASE / "tasks_n500.json").read_text())}
    nosat = json.loads((BASE / "stops_nosat.json").read_text())
    verdicts = json.loads((BASE / "verdicts.json").read_text())
    base_stops = {tag: json.loads((BASE / f"stops_{tag}.json").read_text()) for tag in MODELS}
    rng = random.Random(20260820)
    pairs = []
    for tag in MODELS:
        rolls = base_run.load_rollouts(tag)
        for tid, v in nosat[tag].items():
            if v["stop_C"] == 8:
                continue  # identical to A -> auto tie
            if (v["stop_C"] == base_stops[tag][tid]["stops"]["C"]
                    and f"{tag}:{tid}:C" in verdicts):
                continue  # reuse registered judgment
            seq = [tasks[tid]["seed"]] + [rolls[tid][i]["output"] for i in range(1, 9)]
            challenger, incumbent = seq[v["stop_C"]], seq[8]
            flipped = rng.random() < 0.5
            t1, t2 = (incumbent, challenger) if flipped else (challenger, incumbent)
            pairs.append({"key": f"nosat:{tag}:{tid}", "flipped": flipped,
                          "instruction": tasks[tid]["instruction"],
                          "text1": t1, "text2": t2})
    rng.shuffle(pairs)
    bdir = BASE / "ablation_batches"; bdir.mkdir(exist_ok=True)
    (BASE / "ablation_key.json").write_text(json.dumps(
        {p["key"]: p["flipped"] for p in pairs}, indent=0))
    for i in range(0, len(pairs), BATCH_SIZE):
        batch = [{k: p[k] for k in ("key", "instruction", "text1", "text2")}
                 for p in pairs[i:i + BATCH_SIZE]]
        (bdir / f"abatch_{i // BATCH_SIZE:03d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=1))
    print(f"new pairs={len(pairs)} batches={math.ceil(len(pairs)/BATCH_SIZE) if pairs else 0}")


def cmd_collect():
    key_map = json.loads((BASE / "ablation_key.json").read_text())
    verdicts = {}
    for fp in sorted((BASE / "ablation_verdicts").glob("averdicts_*.json")):
        for v in json.loads(fp.read_text()):
            key, v1, v2 = v["key"], v["vote1"].lower(), v["vote2"].lower()
            s = (1 if v1 == "first" else (-1 if v1 == "second" else 0)) \
                + (1 if v2 == "second" else (-1 if v2 == "first" else 0))
            res = "first" if s >= 2 else ("second" if s <= -2 else "tie")
            if res == "tie":
                outcome = "tie"
            elif key_map[key]:
                outcome = "win" if res == "second" else "loss"
            else:
                outcome = "win" if res == "first" else "loss"
            verdicts[key] = outcome
    missing = [k for k in key_map if k not in verdicts]
    print(f"collected={len(verdicts)} missing={len(missing)}", missing[:5])
    (BASE / "ablation_verdicts.json").write_text(json.dumps(verdicts, indent=0))


def cmd_report():
    nosat = json.loads((BASE / "stops_nosat.json").read_text())
    abl_v = json.loads((BASE / "ablation_verdicts.json").read_text())
    reg_v = json.loads((BASE / "verdicts.json").read_text())
    base_stops = {tag: json.loads((BASE / f"stops_{tag}.json").read_text()) for tag in MODELS}
    lines = ["# RBG N500 — Ablation: saturation disabled", ""]
    for tag in MODELS:
        q = {"win": 0, "tie": 0, "loss": 0}
        n = len(nosat[tag])
        for tid, v in nosat[tag].items():
            if v["stop_C"] == 8:
                q["tie"] += 1
            elif f"nosat:{tag}:{tid}" in abl_v:
                q[abl_v[f"nosat:{tag}:{tid}"]] += 1
            else:  # reused registered judgment (same stop index)
                q[reg_v[f"{tag}:{tid}:C"]] += 1
        red = 1 - sum(v["tok_C"] for v in nosat[tag].values()) \
                / sum(v["tok_A"] for v in nosat[tag].values())
        early = sum(1 for v in nosat[tag].values() if v["stop_C"] < 8)
        lo, hi = base_run.wilson(q["loss"], n)
        lines += [f"## Model {tag} (saturation OFF)",
                  f"- early stops: {early}/500, reduction vs A: {red:.1%}",
                  f"- quality vs A (win/tie/loss): {q['win']}/{q['tie']}/{q['loss']}",
                  f"- loss rate: {q['loss']/n:.1%} [Wilson CI {lo:.1%},{hi:.1%}]", ""]
    (BASE / "REPORT_ablation.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    {"stops": cmd_stops, "batches": cmd_batches,
     "collect": cmd_collect, "report": cmd_report}[sys.argv[1]]()
