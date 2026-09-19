# Fourth signal (repetition-ratio guard) — REPORT (machine-generated)

Signal: dup(x) = 1 - distinct/total 64-char shingles on whitespace-stripped text, MIN_LEN 400, fires at >= 0.50.

| criterion | value | pass |
|---|---|---|
| TP-real | 2/2 ({'26b:acad_015:8': {'fired': True, 'dup': 0.9736}, '26b:hr_027:6': {'fired': True, 'dup': 0.9799}}) | True |
| TP-synthetic | 200/200 | True |
| FP-heldout | 0/960 (0.00%) | True |
| FP-stress | 0/60 | True |
| FP-retro (reported) | 0/7998 | — |

## Pre-registered verdict: **GO**

## Policy replay (retrospective corpus)

- 12b: chains changed 0 ; tokens A=3076576 three-signal=1714164 four-signal=1714164
- 26b: chains changed 1 ; tokens A=2893461 three-signal=1724595 four-signal=1724595
  - hr_027: three-signal stop 6 (equilibrium_d_r) -> four-signal returns iterate 5 (repetition_guard_rollback)
