#!/usr/bin/env python3
"""RBG pilot — generation phase: 12 tasks x 8 refinement iterations, checkpointed JSONL.

Resume-safe: skips (task, iteration) pairs already present in rollouts.jsonl.
"""
import json, sys, time, urllib.request
from pathlib import Path

BASE = Path(__file__).parent
GEN_MODEL = "gemma4:12b-it-qat"
MAX_ITERS = 8
OLLAMA = "http://localhost:11434/api/chat"
OUT = BASE / "rollouts.jsonl"

def chat(model, system, user, num_ctx=8192, temperature=0.7):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "stream": False,
        "think": False,
        "options": {"num_ctx": num_ctx, "temperature": temperature},
    }
    req = urllib.request.Request(OLLAMA, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    return (d["message"]["content"].strip(),
            d.get("prompt_eval_count", 0), d.get("eval_count", 0))

SYSTEM = ("あなたは優れた編集者です。与えられた下書きを、指示に従って改善してください。"
          "改善後の本文のみを出力し、前置き・解説・箇条書きの変更点説明は一切付けないこと。")

def main():
    tasks = json.loads((BASE / "tasks.json").read_text())
    done = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            r = json.loads(line)
            done.add((r["task_id"], r["iteration"]))
    with OUT.open("a") as f:
        for t in tasks:
            drafts = {0: t["seed"]}
            if OUT.exists():
                for line in OUT.read_text().splitlines():
                    r = json.loads(line)
                    if r["task_id"] == t["id"]:
                        drafts[r["iteration"]] = r["output"]
            for i in range(1, MAX_ITERS + 1):
                if (t["id"], i) in done:
                    continue
                prev = drafts[i - 1]
                user = (f"【指示】{t['instruction']}\n\n【現在の下書き】\n{prev}\n\n"
                        "この下書きをさらに改善してください。既に十分な品質でも、"
                        "可能な限りの改善を試みてください。改善後の本文のみを出力。")
                t0 = time.time()
                out, ptok, etok = chat(GEN_MODEL, SYSTEM, user)
                if not out:
                    raise RuntimeError(f"empty output at {t['id']} iter {i}")
                rec = {"task_id": t["id"], "iteration": i, "output": out,
                       "prompt_tokens": ptok, "eval_tokens": etok,
                       "seconds": round(time.time() - t0, 1)}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                drafts[i] = out
                print(f"{t['id']} iter {i}/{MAX_ITERS} etok={etok} "
                      f"{rec['seconds']}s", flush=True)
    print("DONE")

if __name__ == "__main__":
    main()
