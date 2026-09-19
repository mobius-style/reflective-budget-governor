#!/usr/bin/env python3
"""Held-out replication of the main trade-off: offline 3-signal stops on the 960 held-out
generations, token reduction per model, and blind judging batches (C vs A) for Claude judges.
Subcommands: stops | batches | collect | report"""
import json, random, sys, math
from pathlib import Path
HERE = Path(__file__).parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from analyze import compute_stops
from analyze_n500 import wilson
tasks = {t["id"]: t for t in json.loads((HERE/"heldout_tasks.json").read_text())}
def load(tag):
    rolls = {}
    for line in (HERE/f"rollouts_heldout_{tag}.jsonl").read_text().splitlines():
        r = json.loads(line); rolls.setdefault(r["task_id"],{})[r["iteration"]] = r
    return rolls
def cmd_stops():
    out = {}
    for tag in ("12b","26b"):
        rolls = load(tag); out[tag] = {}
        for tid, its in rolls.items():
            seq = [tasks[tid]["seed"]] + [its[i]["output"] for i in range(1,9)]
            s = compute_stops(seq)
            tok = lambda n: sum(its[i]["prompt_tokens"]+its[i]["eval_tokens"] for i in range(1,n+1))
            out[tag][tid] = {"stops":{k:s[k] for k in "ABC"}, "C_reason":s["C_reason"], "tokens":{k:tok(s[k]) for k in "ABC"}}
        early = sum(1 for v in out[tag].values() if v["stops"]["C"]<8)
        red = sum(1 - v["tokens"]["C"]/v["tokens"]["A"] for v in out[tag].values())/len(out[tag])
        print(tag, "early C stops", early, "/60; mean reduction", f"{red:.1%}")
    (HERE/"heldout_stops.json").write_text(json.dumps(out, indent=1))
def cmd_batches():
    st = json.loads((HERE/"heldout_stops.json").read_text()); rng = random.Random(20260919)
    pairs = []
    for tag in ("12b","26b"):
        rolls = load(tag)
        for tid, s in st[tag].items():
            c = s["stops"]["C"]
            if c == 8: continue
            seq = [tasks[tid]["seed"]] + [rolls[tid][i]["output"] for i in range(1,9)]
            flipped = rng.random() < 0.5
            t1, t2 = (seq[8], seq[c]) if flipped else (seq[c], seq[8])
            pairs.append({"key":f"ho:{tag}:{tid}:C","flipped":flipped,"instruction":tasks[tid]["instruction"],"text1":t1,"text2":t2})
    rng.shuffle(pairs)
    (HERE/"heldout_judge_key.json").write_text(json.dumps({p["key"]:p["flipped"] for p in pairs}))
    bdir = HERE/"heldout_batches"; bdir.mkdir(exist_ok=True)
    for i in range(0, len(pairs), 25):
        (bdir/f"hbatch_{i//25:03d}.json").write_text(json.dumps([{k:p[k] for k in ("key","instruction","text1","text2")} for p in pairs[i:i+25]], ensure_ascii=False, indent=1))
    print("pairs", len(pairs), "batches", math.ceil(len(pairs)/25))
def cmd_collect():
    km = json.loads((HERE/"heldout_judge_key.json").read_text()); v = {}
    for fp in sorted((HERE/"heldout_verdicts").glob("*.json")):
        for x in json.loads(fp.read_text()):
            v1, v2 = x["vote1"].lower(), x["vote2"].lower()
            s = (1 if v1=="first" else (-1 if v1=="second" else 0)) + (1 if v2=="second" else (-1 if v2=="first" else 0))
            res = "first" if s>=2 else ("second" if s<=-2 else "tie")
            v[x["key"]] = "tie" if res=="tie" else (("win" if res=="second" else "loss") if km[x["key"]] else ("win" if res=="first" else "loss"))
    missing = [k for k in km if k not in v]; print("collected", len(v), "missing", missing)
    (HERE/"heldout_verdicts.json").write_text(json.dumps(v, indent=0))
def cmd_report():
    st = json.loads((HERE/"heldout_stops.json").read_text()); v = json.loads((HERE/"heldout_verdicts.json").read_text())
    lines = ["# Held-out replication (60 new tasks × 8 iterations × 2 models; three-signal governor C vs fixed cap A)", ""]
    for tag in ("12b","26b"):
        n = len(st[tag]); q = {"win":0,"tie":0,"loss":0}; early = 0
        for tid, s in st[tag].items():
            if s["stops"]["C"]==8: q["tie"] += 1
            else: early += 1; q[v[f"ho:{tag}:{tid}:C"]] += 1
        red = sum(1 - s["tokens"]["C"]/s["tokens"]["A"] for s in st[tag].values())/n
        lo, hi = wilson(q["loss"], n)
        qi = {k: q[k] - (n-early if k=="tie" else 0) for k in q}
        lines += [f"## {tag}", f"- N={n}, early stops {early}", f"- mean token reduction vs A: {red:.1%}",
                  f"- quality vs A (win/tie/loss, all tasks): {q['win']}/{q['tie']}/{q['loss']}; loss rate {q['loss']/n:.1%} [Wilson {lo:.1%},{hi:.1%}]",
                  f"- intervention-conditional (early stops only): {qi['win']}/{qi['tie']}/{qi['loss']}", ""]
    (HERE/"HELDOUT_REPORT.md").write_text("\n".join(lines)+"\n"); print("\n".join(lines))
if __name__ == "__main__":
    {"stops":cmd_stops,"batches":cmd_batches,"collect":cmd_collect,"report":cmd_report}[sys.argv[1]]()
