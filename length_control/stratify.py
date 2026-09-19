#!/usr/bin/env python3
"""Length-stratified reanalysis of the 999 registered verdicts (governor arm C vs A).
For each judged C-vs-A pair: delta = words(early) - words(iter8). Strata by |delta| and by
relative length ratio. Reports loss/tie/win per stratum, so the reader can see whether
losses persist when lengths are nearly equal (content) or vanish (length preference)."""
import json
from pathlib import Path
ROOT = Path(__file__).parent.parent
tasks = {t["id"]: t for t in json.loads((ROOT/"tasks_n500.json").read_text())}
verd = json.loads((ROOT/"verdicts.json").read_text())
rows = []
for tag in ("12b","26b"):
    stops = json.loads((ROOT/f"stops_{tag}.json").read_text())
    rolls = {}
    for line in (ROOT/f"rollouts_n500_{tag}.jsonl").read_text().splitlines():
        r = json.loads(line); rolls.setdefault(r["task_id"],{})[r["iteration"]] = r["output"]
    for tid, s in stops.items():
        c = s["stops"]["C"]
        if c == 8: continue
        we, w8 = len(rolls[tid][c].split()), len(rolls[tid][8].split())
        rows.append({"tag":tag,"task":tid,"stop":c,"w_early":we,"w_8":w8,"delta":we-w8,
                     "ratio":we/w8 if w8 else None,"outcome":verd[f"{tag}:{tid}:C"]})
def table(key, bins, label):
    out = []
    for lo, hi in bins:
        sel = [r for r in rows if lo <= r[key] < hi]
        n = len(sel)
        if not n: out.append({"stratum":f"{label} [{lo},{hi})","n":0}); continue
        cnt = {o: sum(1 for r in sel if r["outcome"]==o) for o in ("win","tie","loss")}
        out.append({"stratum":f"{label} [{lo},{hi})","n":n, **cnt, "loss_rate":round(cnt["loss"]/n,3)})
    return out
abs_bins = [(0,10),(10,25),(25,50),(50,100),(100,10**6)]
for r in rows: r["absd"] = abs(r["delta"])
res = {"n_pairs":len(rows), "by_ratio": None}
res["by_abs_delta_words"] = table("absd", abs_bins, "|Δwords|")
ratio_bins = [(0.0,0.6),(0.6,0.8),(0.8,0.95),(0.95,1.05),(1.05,10.0)]
res["by_ratio"] = table("ratio", ratio_bins, "early/iter8 length ratio")
# matched subset: near-equal length (ratio 0.95..1.05)
m = [r for r in rows if 0.95 <= (r["ratio"] or 0) < 1.05]
res["matched_subset"] = {"n":len(m), **{o: sum(1 for r in m if r["outcome"]==o) for o in ("win","tie","loss")}}
# sign test on matched subset: is loss rate significantly above win rate?
w, l = res["matched_subset"]["win"], res["matched_subset"]["loss"]
res["matched_subset"]["note"] = "wins vs losses among near-equal-length pairs; ties excluded"
(Path(__file__).parent/"stratified.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k:v for k,v in res.items() if k!="n_pairs"}, indent=1))
print("n_pairs", res["n_pairs"])
