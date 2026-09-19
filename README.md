# Reflective Budget Governor (RBG)

Equilibrium-based early stopping for iterative LLM refinement — the full
data and analysis package for the paper:

> Toeda, T. (2026). *The Reflective Budget Governor: Equilibrium-Based
> Early Stopping for Iterative LLM Refinement.* Zenodo.
> https://doi.org/10.5281/zenodo.22031366 (concept DOI; v1.0 = 22031367, v1.1 = 22844856, v1.2 = 22845407, v1.3 = 22845998)

A three-signal stopping rule (RZGM-derived equilibrium distance d̂_R,
RHL-derived loop/saturation detectors, MUSE-derived hard reflection cap)
is evaluated pre-registered over 500 English refinement tasks × 8
iterations × 2 generator models (8,000 generations), with 999 blind
position-swapped pairwise judgments, a 30-pair audit, and a full-data
saturation ablation.

**Headline result (the honest version):** the full governor saves
36.6% / 33.1% of refinement tokens (12B / 26B) against an
always-8-iterations baseline but loses 38.0% / 36.6% of judged
comparisons under a strong judge; disabling the saturation signal gives
a conservative operating point (10.8% / 12.0% savings at 8.2% / 11.8%
loss rate). It is a measured two-point dial, not free savings.

## Version 1.1 additions (2026-09-19)

- `math_note/` — what the saturation threshold actually computes (unanimity at
  window 3; general envelope theorem and n*(τ) rule; DOI 10.5281/zenodo.22842506).
- `fourth_signal/` — pre-registered repetition-ratio guard evaluation
  (PREREG.md committed before data; verdict GO: 2/2 real, 200/200 synthetic,
  0/960 held-out, 0/60 stress, 0/7,998 retrospective false alarms).

## Version 1.3 additions (2026-09-19)

- `length_control/PREREG_MATCHED.md`, `matched_judging.py`, `matched_*` —
  pre-registered length-matched re-judging of 100 governor-loss pairs: early
  text vs sentence-truncated final 94/2/4; truncated vs full final 0/0/100.
  Label: the large-gap losses are carried by the additional material.

## Version 1.2 additions (2026-09-19)

- `length_control/` — length-stratified reanalysis of the 621 judged governor
  pairs (loss 92% → 16.1% from large to near-equal length gaps; 31 vs 4 at
  matched length).
- `fourth_signal/heldout_*` — held-out replication on 60 new tasks (34.5% /
  34.5% reduction; 31.7% / 36.7% loss).
- `fourth_signal/governor_online.py`, `online_12b.jsonl` — incremental
  four-signal governor (0 mismatches on 1,000 chains) run as a genuine online
  loop on the held-out tasks (319/480 iterations generated).

## Contents

| File | What it is |
|---|---|
| `DESIGN.md`, `DESIGN_N500.md` | Pre-registration documents (criteria, thresholds, dated pre-data amendments) |
| `JUDGE_PROTOCOL.md` | The blind judging protocol given verbatim to judge agents |
| `tasks.json`, `tasks_n500.json`, `n500_tasks/` | 12-task Japanese pilot set; 500-task English set (10 domains × 50) |
| `runner.py`, `runner_n500.py` | Generation harnesses (local Ollama; gemma4:12b-it-qat / 26b-a4b-it-qat) |
| `rollouts.jsonl`, `rollouts_n500_12b.jsonl`, `rollouts_n500_26b.jsonl` | All 8,096 generations with per-call token accounting |
| `analyze.py`, `analyze_n500.py`, `ablation_nosat.py` | Stopping rules (canonical definitions), pairing, collection, statistics, report generation |
| `stops_*.json` | Offline stop indices and token accounting per arm |
| `verdicts.json`, `judge_verdicts/`, `judge_key.json` | 999 registered blind verdicts + raw votes + position-randomization key |
| `ablation_verdicts*.{json,/}`, `ablation_key.json` | Saturation-ablation verdicts (144 new pairs) |
| `judgments.jsonl`, `results.json` | Pilot verdicts and per-task pilot results |
| `audit_keys.json` | The 30 randomly sampled pair keys re-judged blind by the authoring session |
| `REPORT.md`, `REPORT_N500.md`, `REPORT_ablation.md` | Machine-generated verdict reports |

## Reproducing

Statistics only (no GPU needed):

```bash
python3 analyze_n500.py stops    # recompute stop indices + token accounting
python3 analyze_n500.py report   # recompute all headline numbers from verdicts.json
python3 ablation_nosat.py stops
python3 ablation_nosat.py report
```

Full regeneration requires a local [Ollama](https://ollama.com) with
`gemma4:12b-it-qat` and `gemma4:26b-a4b-it-qat` pulled (no API keys):

```bash
python3 runner_n500.py --model gemma4:12b-it-qat --out rollouts_n500_12b.jsonl
python3 runner_n500.py --model gemma4:26b-a4b-it-qat --out rollouts_n500_26b.jsonl
```

Note: `analyze_n500.py batches` / judging requires an LLM judge; the
protocol in `JUDGE_PROTOCOL.md` is judge-agnostic.

## License

Code, tasks, rollouts and analysis data: **AGPL-3.0-or-later**.
The paper text itself is CC BY-NC-SA 4.0 (see the Zenodo record).
