# Pre-registration — repetition-ratio guard as a fourth RBG signal

Registered 2026-09-19 (JST) BEFORE any evaluation data was computed. The commit
carrying this file is the timestamp. Nothing below may be changed after data
contact except by a dated amendment appended at the end.

## Motivation
The RBG study (DOI 10.5281/zenodo.22031367) found two verbatim collapses in
8,000 generations that none of its three signals could see; the companion note
(DOI 10.5281/zenodo.22842506) proves set-based trigram features are structurally
blind to within-output repetition and that any detector separating the collision
class must use a feature varying within it. This study evaluates the simplest
such feature.

## Signal (frozen)
For a generation x, strip whitespace, and if len < 400 chars the signal is 0.
Otherwise take all character shingles of length w = 64 at stride 1 and define
  dup(x) = 1 − |distinct shingles| / |shingles|.
The fourth signal FIRES iff dup(x) ≥ 0.50 (a majority of the text is verbatim
repeated material). No other parameter.

Governor integration (offline policy): if the fourth signal fires at iteration
t, the governor stops and RETURNS x_{t−1} (the last non-flagged iterate), i.e. a
roll-back stop, not "stop and ship x_t". If it fires at t = 1 the seed is
returned. Fourth signal has priority over the other three.

## Data
- Retrospective: the 8,000 published generations (rollouts_n500_{12b,26b}.jsonl),
  containing the two known collapses (26b hr_027 iter 6; 26b acad_015 iter 8).
- Held-out: 60 NEW English tasks (6 per domain, authored after this
  registration, never used before) × 8 iterations × 2 models = 960 generations,
  generated with the published runner_n500.py, same settings.
- Synthetic positives: 200 items = 50 clean generations (random from the
  retrospective corpus, dup < 0.1) × inflation factors k ∈ {3, 5, 10, 50},
  half with a "***" separator between copies, half without.
- Legitimate-expansion stress set: 60 items = 60 clean generations each extended
  with 8 DISTINCT list items sharing a template prefix ("- Item n: <unique
  sentence>"); these must NOT fire.

## Criteria (frozen)
- TP-real: both known collapses fire (2/2). Required.
- TP-synthetic: ≥ 95% of the 200 synthetic positives fire. Required.
- FP-heldout: ≤ 0.5% of the 960 held-out generations fire. Required.
- FP-stress: 0/60 legitimate expansions fire. Required.
- FP-retro (reported, not gating): firing count on the 7,998 non-collapse
  retrospective generations.
Verdict: GO iff all four Required criteria hold; otherwise NO-GO, reported as
such. No threshold retuning after data contact.

## Policy replay (reported)
Offline replay of the four-signal governor on the retrospective corpus: number
of chains whose stop index or returned iterate changes vs. the published
three-signal governor; token effect; the returned iterate for hr_027 and
acad_015.

## What this does not test
Quality of returned iterates (no judging), online intervention, other
repetition modes (paraphrastic loops), or other languages.
