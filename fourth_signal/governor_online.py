#!/usr/bin/env python3
"""Online (incremental) four-signal governor + runner.

The governor decides after each generated iterate using only the prefix
x_0..x_t, so an online run cannot differ from the offline policy on the same
prefix. `verify` proves this on the 1,000 published chains: the incremental
decision equals analyze.compute_stops for every chain (three-signal part) and
eval_fourth_signal's replay (four-signal part).

Usage:
  python3 governor_online.py verify
  python3 governor_online.py run --model gemma4:12b-it-qat --tasks heldout_tasks.json --out online_12b.jsonl
"""
import argparse, json, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import analyze as A                      # canonical thresholds/functions
from eval_fourth_signal import fires as guard_fires

MAX_ITERS = 8


class OnlineGovernor:
    """Feed iterates one at a time; .decision is None until a stop fires."""

    def __init__(self, seed: str):
        self.seq = [seed]; self.tris = [A.trigrams(seed)]
        self.types = []; self.dr_consec = 0
        self.decision = None  # (stop_index, returned_index, reason)

    def push(self, x: str):
        if self.decision is not None:
            return self.decision
        i = len(self.seq)
        self.seq.append(x); self.tris.append(A.trigrams(x))
        # fourth signal: repetition guard, priority over the rest, roll-back
        if guard_fires(x):
            self.decision = (i, i - 1, "repetition_guard_rollback"); return self.decision
        sim_prev = A.cosine(self.tris[i], self.tris[i - 1])
        d_embed = 1 - sim_prev
        d_novel = A.novelty(x, [self.tris[j] for j in range(i)])
        dr = max(0.0, min(1.0, A.W_EMBED * d_embed + A.W_NOVEL * d_novel))
        loop_hit = any(A.cosine(self.tris[i], self.tris[j]) >= A.LOOP_SIM
                       for j in range(max(0, i - 6), i - 1))
        self.types.append(A.change_type(self.seq[i - 1], x))
        sat = A.saturation(self.types)
        from collections import Counter
        dom = Counter(self.types[-3:]).most_common(1)[0][0] if len(self.types) >= 3 else None
        self.dr_consec = self.dr_consec + 1 if dr <= A.DR_EPS else 0
        if self.dr_consec >= 2:
            self.decision = (i, i, "equilibrium_d_r")
        elif loop_hit:
            self.decision = (i, i, "loop")
        elif sat >= A.SAT_THRESHOLD and dom != "rewrite":
            self.decision = (i, i, "saturation")
        elif i == MAX_ITERS:
            self.decision = (i, i, "hard_cap")
        return self.decision


def cmd_verify():
    tasks = {t["id"]: t for t in json.loads((ROOT / "tasks_n500.json").read_text())}
    mism = 0; n = 0
    for tag in ("12b", "26b"):
        rolls = {}
        for line in (ROOT / f"rollouts_n500_{tag}.jsonl").read_text().splitlines():
            r = json.loads(line); rolls.setdefault(r["task_id"], {})[r["iteration"]] = r["output"]
        for tid, its in rolls.items():
            seq = [tasks[tid]["seed"]] + [its[i] for i in range(1, 9)]
            off = A.compute_stops(seq)
            fire_at = next((i for i in range(1, 9) if guard_fires(seq[i])), None)
            if fire_at is not None and fire_at <= off["C"]:
                exp = (fire_at, fire_at - 1, "repetition_guard_rollback")
            else:
                exp = (off["C"], off["C"], off["C_reason"])
            g = OnlineGovernor(seq[0]); dec = None
            for i in range(1, 9):
                dec = g.push(seq[i])
                if dec: break
            n += 1
            if dec != exp:
                mism += 1; print("MISMATCH", tag, tid, dec, exp)
    print(f"online==offline on {n} chains, mismatches={mism}")
    (HERE / "results" / "online_verify.json").write_text(json.dumps({"chains": n, "mismatches": mism}))
    return mism


def chat(model, system, user):
    payload = {"model": model, "stream": False, "think": False,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
               "options": {"num_ctx": 8192, "temperature": 0.7}}
    req = urllib.request.Request("http://localhost:11434/api/chat", json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    return d["message"]["content"].strip(), d.get("prompt_eval_count", 0), d.get("eval_count", 0)


SYSTEM = ("You are an expert editor. Improve the given draft according to the "
          "instruction. Output only the improved text — no preamble, no notes, "
          "no explanation of changes.")


def cmd_run(model, tasks_file, out_file):
    tasks = json.loads((HERE / tasks_file).read_text())
    out = HERE / out_file
    done = {json.loads(l)["task_id"] for l in out.read_text().splitlines()} if out.exists() else set()
    with out.open("a") as f:
        for t in tasks:
            if t["id"] in done: continue
            g = OnlineGovernor(t["seed"]); drafts = [t["seed"]]; toks = 0; dec = None; t0 = time.time()
            for i in range(1, MAX_ITERS + 1):
                user = (f"Instruction: {t['instruction']}\n\nCurrent draft:\n{drafts[-1]}\n\nImprove this draft "
                        "further. Even if it already seems good, attempt every improvement you can. Output only the improved text.")
                x, p, e = chat(model, SYSTEM, user)
                toks += p + e; drafts.append(x)
                dec = g.push(x)
                if dec: break
            rec = {"task_id": t["id"], "model": model, "stop": dec[0], "returned": dec[1], "reason": dec[2],
                   "iterations_generated": len(drafts) - 1, "tokens": toks, "seconds": round(time.time() - t0, 1),
                   "drafts": drafts}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(t["id"], "stop", dec, "tokens", toks, flush=True)
    print("DONE")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("verify")
    r = sub.add_parser("run"); r.add_argument("--model", required=True); r.add_argument("--tasks", default="heldout_tasks.json"); r.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "verify": sys.exit(1 if cmd_verify() else 0)
    else: cmd_run(a.model, a.tasks, a.out)
