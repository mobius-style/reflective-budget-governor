#!/usr/bin/env python3
"""RBG N500 — generation phase, English-only. Resume-safe JSONL checkpointing.

Usage: python3 runner_n500.py --model gemma4:12b-it-qat --out rollouts_n500_12b.jsonl
"""
import argparse, json, time, urllib.request
from pathlib import Path

BASE = Path(__file__).parent
MAX_ITERS = 8
OLLAMA = "http://localhost:11434/api/chat"

SYSTEM = ("You are an expert editor. Improve the given draft according to the "
          "instruction. Output only the improved text — no preamble, no notes, "
          "no explanation of changes.")

def chat(model, system, user, num_ctx=8192, temperature=0.7):
    payload = {"model": model, "stream": False, "think": False,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}],
               "options": {"num_ctx": num_ctx, "temperature": temperature}}
    req = urllib.request.Request(OLLAMA, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    return (d["message"]["content"].strip(),
            d.get("prompt_eval_count", 0), d.get("eval_count", 0))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tasks", default="tasks_n500.json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    tasks = json.loads((BASE / args.tasks).read_text())
    out = BASE / args.out
    done, drafts_by_task = set(), {}
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            done.add((r["task_id"], r["iteration"]))
            drafts_by_task.setdefault(r["task_id"], {})[r["iteration"]] = r["output"]
    n_total = len(tasks) * MAX_ITERS
    n_done = len(done)
    with out.open("a") as f:
        for t in tasks:
            drafts = {0: t["seed"], **drafts_by_task.get(t["id"], {})}
            for i in range(1, MAX_ITERS + 1):
                if (t["id"], i) in done:
                    continue
                user = (f"Instruction: {t['instruction']}\n\nCurrent draft:\n"
                        f"{drafts[i-1]}\n\nImprove this draft further. Even if it "
                        "already seems good, attempt every improvement you can. "
                        "Output only the improved text.")
                t0 = time.time()
                for attempt in range(3):
                    try:
                        outp, ptok, etok = chat(args.model, SYSTEM, user)
                        if outp:
                            break
                    except Exception as e:
                        if attempt == 2:
                            raise
                        time.sleep(10)
                if not outp:
                    raise RuntimeError(f"empty output {t['id']} iter {i}")
                rec = {"task_id": t["id"], "iteration": i, "output": outp,
                       "prompt_tokens": ptok, "eval_tokens": etok,
                       "seconds": round(time.time() - t0, 1)}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                drafts[i] = outp
                n_done += 1
                if n_done % 50 == 0:
                    print(f"progress {n_done}/{n_total}", flush=True)
    print(f"DONE {args.model} -> {args.out}")

if __name__ == "__main__":
    main()
