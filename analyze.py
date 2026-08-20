#!/usr/bin/env python3
"""RBG pilot — analysis phase: offline stopping rules + blind judging + report.

Usage: python3 analyze.py [--stops-only]
Judging results are checkpointed to judgments.jsonl (resume-safe).
"""
import json, math, sys, urllib.request
from pathlib import Path

BASE = Path(__file__).parent
JUDGE_MODEL = "gemma4:26b-a4b-it-qat"
MAX_ITERS = 8

# --- pre-registered thresholds (DESIGN.md) ---
B_SIM_STOP = 0.98          # arm B: successive similarity
DR_EPS = 0.05              # arm C: d̂_R equilibrium epsilon (2 consecutive)
LOOP_SIM = 0.95            # arm C: non-adjacent recurrence
SAT_THRESHOLD = 0.70       # arm C: change-diversity collapse (inherited from RHL)
W_EMBED, W_NOVEL = 0.6, 0.4

def trigrams(s):
    s = "".join(s.split())
    return {s[i:i+3] for i in range(len(s) - 2)} if len(s) >= 3 else {s}

def cosine(a, b):
    inter = len(a & b)
    return inter / math.sqrt(len(a) * len(b)) if a and b else 0.0

def novelty(cur, prevs):
    seen = set().union(*prevs) if prevs else set()
    cur_t = trigrams(cur)
    return len(cur_t - seen) / len(cur_t) if cur_t else 0.0

def change_type(prev, cur):
    """Coarse change classification for the saturation axis distribution."""
    lp, lc = len(prev), len(cur)
    sim = cosine(trigrams(prev), trigrams(cur))
    if sim >= 0.97: return "no_change"
    if lc > lp * 1.15: return "expand"
    if lc < lp * 0.85: return "compress"
    return "rewrite"

def saturation(types):
    """1 - normalized entropy over the last-3 change-type window."""
    from collections import Counter
    if len(types) < 3: return 0.0
    window = types[-3:]
    counts = Counter(window)
    if len(counts) == 1: return 1.0
    total = len(window)
    ent = -sum((c/total)*math.log(c/total) for c in counts.values())
    return 1.0 - ent/math.log(len(counts))

def compute_stops(seq):
    """seq: list of drafts indexed 0..8 (0=seed). Returns per-arm stop index and signal trace."""
    tris = [trigrams(s) for s in seq]
    trace, types = [], []
    stop_b = stop_c = MAX_ITERS
    dr_consec = 0
    reason_c = "hard_cap"
    for i in range(1, MAX_ITERS + 1):
        sim_prev = cosine(tris[i], tris[i-1])
        d_embed = 1 - sim_prev
        d_novel = novelty(seq[i], [tris[j] for j in range(i)])
        dr = max(0.0, min(1.0, W_EMBED*d_embed + W_NOVEL*d_novel))
        loop_hit = any(cosine(tris[i], tris[j]) >= LOOP_SIM for j in range(max(0, i-6), i-1))
        types.append(change_type(seq[i-1], seq[i]))
        sat = saturation(types)
        trace.append({"iter": i, "sim_prev": round(sim_prev,3), "d_r": round(dr,3),
                      "loop": loop_hit, "saturation": round(sat,3), "type": types[-1]})
        if stop_b == MAX_ITERS and sim_prev >= B_SIM_STOP:
            stop_b = i
        dr_consec = dr_consec + 1 if dr <= DR_EPS else 0
        # amendment 2026-08-15 (pre-data): rewrite-dominance is exploration, not
        # axis saturation — only no_change/compress/expand dominance may trigger.
        from collections import Counter
        dom_type = Counter(types[-3:]).most_common(1)[0][0] if len(types) >= 3 else None
        if stop_c == MAX_ITERS:
            if dr_consec >= 2: stop_c, reason_c = i, "equilibrium_d_r"
            elif loop_hit:     stop_c, reason_c = i, "loop"
            elif sat >= SAT_THRESHOLD and dom_type != "rewrite":
                stop_c, reason_c = i, "saturation"
    return {"A": MAX_ITERS, "B": stop_b, "C": stop_c, "C_reason": reason_c, "trace": trace}

def chat(model, system, user):
    payload = {"model": model, "stream": False, "think": False,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}],
               "options": {"num_ctx": 8192, "temperature": 0.0}}
    req = urllib.request.Request("http://localhost:11434/api/chat",
                                 json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["message"]["content"].strip()

JUDGE_SYS = ("あなたは厳格な品質審査員です。同じ指示に対する2つの成果物を比較し、"
             "指示への適合・具体性・読みやすさ・プロらしさで優れている方を選びます。"
             "回答は「1」「2」「TIE」のいずれか1語のみ。")

def judge_pair(instruction, text1, text2):
    user = (f"【指示】{instruction}\n\n【成果物1】\n{text1}\n\n【成果物2】\n{text2}\n\n"
            "優れている方を「1」「2」「TIE」のいずれか1語で答えよ。")
    v = chat(JUDGE_MODEL, JUDGE_SYS, user).upper()
    if "TIE" in v: return "tie"
    if v.startswith("1") or "成果物1" in v: return "first"
    if v.startswith("2") or "成果物2" in v: return "second"
    return "tie"

def blind_judge(instruction, challenger, incumbent, key, cache, fh):
    """Position-swapped 2 votes. Returns win/tie/loss for challenger."""
    if key in cache: return cache[key]["result"]
    v1 = judge_pair(instruction, challenger, incumbent)   # challenger=1
    v2 = judge_pair(instruction, incumbent, challenger)   # challenger=2
    s = 0
    s += 1 if v1 == "first" else (-1 if v1 == "second" else 0)
    s += 1 if v2 == "second" else (-1 if v2 == "first" else 0)
    result = "win" if s >= 2 else ("loss" if s <= -2 else "tie")
    rec = {"key": key, "votes": [v1, v2], "result": result}
    fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
    cache[key] = rec
    return result

def main():
    stops_only = "--stops-only" in sys.argv
    tasks = {t["id"]: t for t in json.loads((BASE/"tasks.json").read_text())}
    rolls = {}
    for line in (BASE/"rollouts.jsonl").read_text().splitlines():
        r = json.loads(line)
        rolls.setdefault(r["task_id"], {})[r["iteration"]] = r
    results = []
    cache = {}
    jfile = BASE/"judgments.jsonl"
    if jfile.exists():
        for line in jfile.read_text().splitlines():
            rec = json.loads(line); cache[rec["key"]] = rec
    fh = jfile.open("a")
    for tid, t in tasks.items():
        iters = rolls.get(tid, {})
        assert len(iters) == MAX_ITERS, f"{tid}: {len(iters)}/{MAX_ITERS} iterations"
        seq = [t["seed"]] + [iters[i]["output"] for i in range(1, MAX_ITERS+1)]
        stops = compute_stops(seq)
        tok = lambda n: sum(iters[i]["prompt_tokens"] + iters[i]["eval_tokens"]
                            for i in range(1, n+1))
        row = {"task": tid, "stops": {k: stops[k] for k in "ABC"},
               "C_reason": stops["C_reason"],
               "tokens": {k: tok(stops[k]) for k in "ABC"},
               "trace": stops["trace"]}
        if not stops_only:
            for arm in ("B", "C"):
                if stops[arm] == stops["A"]:
                    row[f"{arm}_vs_A"] = "tie"  # identical final text
                else:
                    row[f"{arm}_vs_A"] = blind_judge(
                        t["instruction"], seq[stops[arm]], seq[stops["A"]],
                        f"{tid}:{arm}{stops[arm]}_vs_A{stops['A']}", cache, fh)
        results.append(row)
        print(f"{tid} stops A={stops['A']} B={stops['B']} C={stops['C']}"
              f"({stops['C_reason']}) " +
              (f"B_vs_A={row.get('B_vs_A')} C_vs_A={row.get('C_vs_A')}"
               if not stops_only else ""), flush=True)
    (BASE/"results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1))
    if not stops_only:
        write_report(results)

def write_report(results):
    n = len(results)
    tA = sum(r["tokens"]["A"] for r in results)
    tB = sum(r["tokens"]["B"] for r in results)
    tC = sum(r["tokens"]["C"] for r in results)
    redB, redC = 1 - tB/tA, 1 - tC/tA
    count = lambda arm, v: sum(1 for r in results if r.get(f"{arm}_vs_A") == v)
    qB = {v: count("B", v) for v in ("win","tie","loss")}
    qC = {v: count("C", v) for v in ("win","tie","loss")}
    noninf_C = (qC["win"] + qC["tie"]) / n >= 0.5
    c_beats_b = redC > redB or (qC["win"]-qC["loss"]) > (qB["win"]-qB["loss"])
    verdict = "WIN" if (redC >= 0.15 and noninf_C and c_beats_b) else "LOSS"
    reasons = {}
    for r in results:
        reasons[r["C_reason"]] = reasons.get(r["C_reason"], 0) + 1
    lines = [
        "# RBG Pilot — REPORT (machine-generated)", "",
        f"- N tasks: {n}",
        f"- Tokens A(fixed-cap)={tA}  B(single)={tB}  C(governor)={tC}",
        f"- Reduction vs A: B={redB:.1%}  C={redC:.1%}",
        f"- Quality vs A (win/tie/loss): B={qB['win']}/{qB['tie']}/{qB['loss']}"
        f"  C={qC['win']}/{qC['tie']}/{qC['loss']}",
        f"- C non-inferiority (win+tie >= 50%): {noninf_C}",
        f"- C beats B (reduction or quality): {c_beats_b}",
        f"- C stop reasons: {reasons}",
        f"- Mean stop iter: B={sum(r['stops']['B'] for r in results)/n:.2f}"
        f"  C={sum(r['stops']['C'] for r in results)/n:.2f}", "",
        f"## Pre-registered verdict: **{verdict}**",
        "(criteria: C reduction >=15% AND C non-inferior AND C beats B)", "",
        "## Per-task", "",
        "| task | stopB | stopC | C reason | tokA | tokC | B_vs_A | C_vs_A |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['task']} | {r['stops']['B']} | {r['stops']['C']} "
                     f"| {r['C_reason']} | {r['tokens']['A']} | {r['tokens']['C']} "
                     f"| {r.get('B_vs_A')} | {r.get('C_vs_A')} |")
    (BASE/"REPORT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:14]))

if __name__ == "__main__":
    main()
