# Pre-registration — length-matched re-judging (2026-09-19 JST, before any judging)

## Question
§4a showed governor losses concentrate where the early-stopped text is much
shorter than iteration 8. Is that because the extra material in iteration 8 is
valued, or because the early text is worse per unit of length?

## Design (frozen)
- Population: registered governor-vs-A pairs judged LOSS with length ratio
  early/iter8 < 0.80 (both models). Random sample of 100 (seed 20260919).
- Matched text M: iteration 8 truncated at sentence boundaries to at most the
  early text's word count (greedy sentence accumulation; ≥ 1 sentence).
- Two blind comparisons per sampled pair, position-swapped two votes each, same
  JUDGE_PROTOCOL.md and judge family as the study:
  (i) early E vs matched M  — length-matched quality;
  (ii) matched M vs full iteration 8 F — value of the removed material.
- Outcomes are recorded from the challenger's perspective: (i) E as challenger,
  (ii) M as challenger.

## Interpretation (frozen labels)
- If in (i) E loses to M in ≤ 30% of pairs: the §4 losses on this stratum are
  attributable to the additional material, not to per-length quality.
- If in (i) E loses in ≥ 50%: a per-length content deficit exists at matched
  length on this stratum.
- Between 30% and 50%: mixed; report as such.
- (ii) is reported descriptively (share of pairs where F beats M) and cannot
  separate "valuable" from "judge-preferred bulk"; it bounds how often the judge
  prefers the longer text when content is nested.
No threshold is changed after data contact. Truncation is a proxy for length
matching and can cut mid-argument; this is a limitation, not a tunable.
