#!/usr/bin/env python3
"""RBG N500 — analysis pipeline (English environment, Claude judging).

Subcommands:
  stops    — apply the 3 stopping rules offline per model -> stops_<tag>.json
  batches  — build blind judging batch files for Claude agents -> judge_batches/
  collect  — merge judge verdict files -> verdicts.json (validates coverage)
  report   — stats (bootstrap CI, Wilson CI) + REPORT_N500.md
"""
import json, math, random, sys
from pathlib import Path

BASE = Path(__file__).parent
MODELS = {"12b": "rollouts_n500_12b.jsonl", "26b": "rollouts_n500_26b.jsonl"}
MAX_ITERS = 8
BATCH_SIZE = 25

sys.path.insert(0, str(BASE))
from analyze import compute_stops  # amended stopping rules, thresholds unchanged


def load_rollouts(tag):
    rolls = {}
    for line in (BASE / MODELS[tag]).read_text().splitlines():
        r = json.loads(line)
        rolls.setdefault(r["task_id"], {})[r["iteration"]] = r
    return rolls


def cmd_stops():
    tasks = json.loads((BASE / "tasks_n500.json").read_text())
    for tag in MODELS:
        rolls = load_rollouts(tag)
        out = {}
        for t in tasks:
            iters = rolls.get(t["id"], {})
            assert len(iters) == MAX_ITERS, f"{tag}/{t['id']}: {len(iters)}/8"
            seq = [t["seed"]] + [iters[i]["output"] for i in range(1, MAX_ITERS + 1)]
            s = compute_stops(seq)
            tok = lambda n: sum(iters[i]["prompt_tokens"] + iters[i]["eval_tokens"]
                                for i in range(1, n + 1))
            out[t["id"]] = {"stops": {k: s[k] for k in "ABC"},
                            "C_reason": s["C_reason"],
                            "tokens": {k: tok(s[k]) for k in "ABC"}}
        (BASE / f"stops_{tag}.json").write_text(json.dumps(out, indent=1))
        early_b = sum(1 for v in out.values() if v["stops"]["B"] < 8)
        early_c = sum(1 for v in out.values() if v["stops"]["C"] < 8)
        print(f"{tag}: {len(out)} tasks, early stops B={early_b} C={early_c}")


def cmd_batches():
    """Blind pairs: opaque keys, challenger/incumbent order randomized per pair
    (agents still cast 2 position-swapped votes; randomization hides which side
    is the early-stop even in aggregate)."""
    tasks = {t["id"]: t for t in json.loads((BASE / "tasks_n500.json").read_text())}
    rng = random.Random(20260815)
    pairs = []
    for tag in MODELS:
        stops = json.loads((BASE / f"stops_{tag}.json").read_text())
        rolls = load_rollouts(tag)
        for tid, s in stops.items():
            seq = [tasks[tid]["seed"]] + [rolls[tid][i]["output"]
                                          for i in range(1, MAX_ITERS + 1)]
            for arm in ("B", "C"):
                if s["stops"][arm] == s["stops"]["A"]:
                    continue  # identical text -> auto-tie at report stage
                challenger, incumbent = seq[s["stops"][arm]], seq[s["stops"]["A"]]
                flipped = rng.random() < 0.5
                t1, t2 = (incumbent, challenger) if flipped else (challenger, incumbent)
                pairs.append({"key": f"{tag}:{tid}:{arm}", "flipped": flipped,
                              "instruction": tasks[tid]["instruction"],
                              "text1": t1, "text2": t2})
    rng.shuffle(pairs)
    bdir = BASE / "judge_batches"
    bdir.mkdir(exist_ok=True)
    # key->flipped mapping stays out of the batch files the judges see
    (BASE / "judge_key.json").write_text(json.dumps(
        {p["key"]: p["flipped"] for p in pairs}, indent=0))
    n = 0
    for i in range(0, len(pairs), BATCH_SIZE):
        batch = [{k: p[k] for k in ("key", "instruction", "text1", "text2")}
                 for p in pairs[i:i + BATCH_SIZE]]
        (bdir / f"batch_{i // BATCH_SIZE:03d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=1))
        n += 1
    print(f"pairs={len(pairs)} batches={n} (size {BATCH_SIZE})")


def cmd_collect():
    key_map = json.loads((BASE / "judge_key.json").read_text())
    verdicts = {}
    vdir = BASE / "judge_verdicts"
    for fp in sorted(vdir.glob("verdicts_*.json")):
        for v in json.loads(fp.read_text()):
            key, v1, v2 = v["key"], v["vote1"].lower(), v["vote2"].lower()
            # vote1: text1 vs text2; vote2: positions swapped
            s = 0
            s += 1 if v1 == "first" else (-1 if v1 == "second" else 0)
            s += 1 if v2 == "second" else (-1 if v2 == "first" else 0)
            res = "first" if s >= 2 else ("second" if s <= -2 else "tie")
            # map back to challenger (early-stop) perspective
            if res == "tie":
                outcome = "tie"
            elif key_map[key]:  # flipped: challenger was text2
                outcome = "win" if res == "second" else "loss"
            else:
                outcome = "win" if res == "first" else "loss"
            verdicts[key] = outcome
    missing = [k for k in key_map if k not in verdicts]
    print(f"collected={len(verdicts)} missing={len(missing)}")
    if missing[:5]:
        print("missing sample:", missing[:5])
    (BASE / "verdicts.json").write_text(json.dumps(verdicts, indent=0))
    return missing


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def cmd_report():
    verdicts = json.loads((BASE / "verdicts.json").read_text())
    rng = random.Random(42)
    lines = ["# RBG N500 — REPORT (machine-generated)", ""]
    overall_pass = {}
    for tag in MODELS:
        stops = json.loads((BASE / f"stops_{tag}.json").read_text())
        tids = sorted(stops)
        n = len(tids)
        red = {}
        for arm in "BC":
            ratios = [1 - stops[t]["tokens"][arm] / stops[t]["tokens"]["A"]
                      for t in tids]
            mean = sum(ratios) / n
            bs = []
            for _ in range(10000):
                sample = [ratios[rng.randrange(n)] for _ in range(n)]
                bs.append(sum(sample) / n)
            bs.sort()
            red[arm] = (mean, bs[249], bs[9749])
        q = {arm: {"win": 0, "tie": 0, "loss": 0} for arm in "BC"}
        for t in tids:
            for arm in "BC":
                if stops[t]["stops"][arm] == stops[t]["stops"]["A"]:
                    q[arm]["tie"] += 1
                else:
                    q[arm][verdicts[f"{tag}:{t}:{arm}"]] += 1
        loss_ci = wilson(q["C"]["loss"], n)
        reasons = {}
        for t in tids:
            reasons[stops[t]["C_reason"]] = reasons.get(stops[t]["C_reason"], 0) + 1
        noninf = (q["C"]["win"] + q["C"]["tie"]) / n >= 0.5
        c_beats_b = (red["C"][0] > red["B"][0]
                     or (q["C"]["win"] - q["C"]["loss"]) > (q["B"]["win"] - q["B"]["loss"]))
        model_pass = red["C"][0] >= 0.15 and red["C"][1] > 0.10 and noninf and c_beats_b
        overall_pass[tag] = model_pass
        lines += [
            f"## Model {tag}", "",
            f"- N={n}",
            f"- Reduction vs A: B={red['B'][0]:.1%} [CI {red['B'][1]:.1%},{red['B'][2]:.1%}]"
            f"  C={red['C'][0]:.1%} [CI {red['C'][1]:.1%},{red['C'][2]:.1%}]",
            f"- Quality vs A (win/tie/loss): B={q['B']['win']}/{q['B']['tie']}/{q['B']['loss']}"
            f"  C={q['C']['win']}/{q['C']['tie']}/{q['C']['loss']}",
            f"- C loss rate: {q['C']['loss']/n:.1%} [Wilson CI {loss_ci[0]:.1%},{loss_ci[1]:.1%}]",
            f"- C stop reasons: {reasons}",
            f"- Criteria (red>=15%, CI_low>10%, non-inferior, beats B): **{'PASS' if model_pass else 'FAIL'}**",
            "",
        ]
    verdict = ("WIN" if all(overall_pass.values())
               else ("PARTIAL (model-dependent)" if any(overall_pass.values()) else "LOSS"))
    lines += [f"## Pre-registered verdict v2: **{verdict}**",
              f"(per-model: {overall_pass})", ""]
    (BASE / "REPORT_N500.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    {"stops": cmd_stops, "batches": cmd_batches,
     "collect": cmd_collect, "report": cmd_report}[sys.argv[1]]()
