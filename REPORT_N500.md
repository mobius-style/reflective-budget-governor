# RBG N500 — REPORT (machine-generated)

## Model 12b

- N=500
- Reduction vs A: B=10.7% [CI 9.2%,12.2%]  C=36.6% [CI 33.6%,39.5%]
- Quality vs A (win/tie/loss): B=6/454/40  C=17/293/190
- C loss rate: 38.0% [Wilson CI 33.9%,42.3%]
- C stop reasons: {'saturation': 206, 'hard_cap': 156, 'equilibrium_d_r': 131, 'loop': 7}
- Criteria (red>=15%, CI_low>10%, non-inferior, beats B): **PASS**

## Model 26b

- N=500
- Reduction vs A: B=14.9% [CI 13.1%,16.8%]  C=33.1% [CI 30.3%,35.9%]
- Quality vs A (win/tie/loss): B=12/420/68  C=12/305/183
- C loss rate: 36.6% [Wilson CI 32.5%,40.9%]
- C stop reasons: {'equilibrium_d_r': 160, 'hard_cap': 161, 'loop': 11, 'saturation': 168}
- Criteria (red>=15%, CI_low>10%, non-inferior, beats B): **PASS**

## Pre-registered verdict v2: **WIN**
(per-model: {'12b': True, '26b': True})

## Main-session audit (pre-registered, 30 random pairs)

- Auditor: main Claude session, blind (verdicts and flip-map hidden during judging)
- Exact agreement with delegated judges: 27/30 (90%)
- Direction flips (first vs second reversal): 0/30 — all 3 mismatches were tie-vs-lean
- Notable observation: one sampled pair (game-dev interview intro) showed catastrophic
  degeneration at the fixed-cap arm — the model output the same paragraph ~25 times.
  The clean early-stopped text won decisively. Repetitive collapse is a real failure
  mode of unbounded refinement that the governor's signals target.

## Honest reading (beyond the pre-registered letter)

The pre-registered non-inferiority bar (win+tie >= 50%) passed at 62-63%, but the
Claude judge — far more discerning than the pilot's gemma judge — reveals a real
quality cost: C loses ~37% of judged comparisons vs always-8-iterations. The correct
release framing is a tunable compute/quality trade-off (35% tokens saved, parity on
~63% of tasks, mostly-mild regression on the rest), NOT "free savings". Saturation
was the most frequent early-stop trigger (206/500 on 12b) and is the first candidate
for recalibration.

## CORRECTION (2026-08-20, from pre-release adversarial verification)

The audit note above misattributed the degeneration case. Primary-data
recomputation (task hr_027, 26B) shows: the ~50x verbatim collapse
occurred at iteration 6 (45,152 chars); iterations 5, 7, 8 are clean
(899 chars); the governor stopped ON the degenerate iteration 6 via
equilibrium_d_r (set-based trigrams are blind to verbatim repetition);
arm B stopped at clean iteration 5; the fixed cap ended clean at 8; the
registered verdict for 26b:hr_027:C is loss. The original note's claim
that the fixed-cap side collapsed and the early stop won is inverted
and is retracted. The paper reports the corrected version.
