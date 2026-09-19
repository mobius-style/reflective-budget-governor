#!/usr/bin/env python3
"""Length-matched re-judging per PREREG_MATCHED.md. Subcommands: build | collect | report"""
import json, random, re, sys
from pathlib import Path
HERE = Path(__file__).parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
SENT = re.compile(r'(?<=[.!?])\s+')
def truncate_to(text, max_words):
    sents = SENT.split(text.strip()); out = []; n = 0
    for s in sents:
        w = len(s.split())
        if out and n + w > max_words: break
        out.append(s); n += w
        if n >= max_words: break
    return " ".join(out)
def build():
    tasks = {t["id"]: t for t in json.loads((ROOT/"tasks_n500.json").read_text())}
    verd = json.loads((ROOT/"verdicts.json").read_text()); pool = []
    for tag in ("12b","26b"):
        stops = json.loads((ROOT/f"stops_{tag}.json").read_text()); rolls = {}
        for line in (ROOT/f"rollouts_n500_{tag}.jsonl").read_text().splitlines():
            r = json.loads(line); rolls.setdefault(r["task_id"],{})[r["iteration"]] = r["output"]
        for tid, s in stops.items():
            c = s["stops"]["C"]
            if c == 8 or verd[f"{tag}:{tid}:C"] != "loss": continue
            E, F = rolls[tid][c], rolls[tid][8]; we, wf = len(E.split()), len(F.split())
            if wf and we/wf < 0.80: pool.append((tag, tid, c, E, F, we))
    rng = random.Random(20260919); rng.shuffle(pool); sample = pool[:100]
    pairs = []; key = {}
    for tag, tid, c, E, F, we in sample:
        M = truncate_to(F, we); instr = tasks[tid]["instruction"]
        for arm, chal, inc in (("EvM", E, M), ("MvF", M, F)):
            k = f"lm:{tag}:{tid}:{arm}"; flipped = rng.random() < 0.5; key[k] = flipped
            t1, t2 = (inc, chal) if flipped else (chal, inc)
            pairs.append({"key": k, "instruction": instr, "text1": t1, "text2": t2})
    rng.shuffle(pairs)
    (HERE/"matched_key.json").write_text(json.dumps(key)); (HERE/"matched_sample.json").write_text(json.dumps(
        [{"tag":t,"task":i,"stop":c,"w_early":we,"w_full":len(F.split()),"w_matched":len(truncate_to(F,we).split())} for t,i,c,E,F,we in sample], indent=1))
    bdir = HERE/"matched_batches"; bdir.mkdir(exist_ok=True); (HERE/"matched_verdicts").mkdir(exist_ok=True)
    for i in range(0, len(pairs), 25):
        (bdir/f"mbatch_{i//25:03d}.json").write_text(json.dumps(pairs[i:i+25], ensure_ascii=False, indent=1))
    print("population", len(pool), "sampled", len(sample), "pairs", len(pairs), "batches", (len(pairs)+24)//25)
def collect():
    km = json.loads((HERE/"matched_key.json").read_text()); v = {}
    for fp in sorted((HERE/"matched_verdicts").glob("*.json")):
        for x in json.loads(fp.read_text()):
            v1, v2 = x["vote1"].lower(), x["vote2"].lower()
            s = (1 if v1=="first" else (-1 if v1=="second" else 0)) + (1 if v2=="second" else (-1 if v2=="first" else 0))
            res = "first" if s>=2 else ("second" if s<=-2 else "tie")
            v[x["key"]] = "tie" if res=="tie" else (("win" if res=="second" else "loss") if km[x["key"]] else ("win" if res=="first" else "loss"))
    missing = [k for k in km if k not in v]; print("collected", len(v), "missing", len(missing), missing[:5])
    (HERE/"matched_verdicts.json").write_text(json.dumps(v, indent=0))
def report():
    v = json.loads((HERE/"matched_verdicts.json").read_text()); samp = json.loads((HERE/"matched_sample.json").read_text())
    def tally(arm):
        q = {"win":0,"tie":0,"loss":0}
        for s in samp: q[v[f"lm:{s['tag']}:{s['task']}:{arm}"]] += 1
        return q
    e, m = tally("EvM"), tally("MvF"); n = len(samp)
    lab = ("additional material" if e["loss"]/n <= 0.30 else ("per-length content deficit" if e["loss"]/n >= 0.50 else "mixed"))
    mean_ratio = sum(s["w_matched"]/s["w_early"] for s in samp)/n
    lines = ["# Length-matched re-judging — REPORT (machine-generated)", "",
             f"- sample: {n} governor-loss pairs with early/iter8 length ratio < 0.80; matched text = iter 8 truncated at sentence boundaries to ≤ early word count (mean matched/early word ratio {mean_ratio:.2f})",
             f"- (i) early E vs matched M (E challenger): win/tie/loss = {e['win']}/{e['tie']}/{e['loss']}  → E loss rate {e['loss']/n:.1%}",
             f"- (ii) matched M vs full F (M challenger): win/tie/loss = {m['win']}/{m['tie']}/{m['loss']}  → F preferred in {m['loss']/n:.1%}",
             f"- pre-registered label for (i): **{lab}**", ""]
    (HERE/"MATCHED_REPORT.md").write_text("\n".join(lines)+"\n"); print("\n".join(lines))
if __name__ == "__main__":
    {"build":build,"collect":collect,"report":report}[sys.argv[1]]()
