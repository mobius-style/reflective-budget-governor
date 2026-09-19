# v1.1 brush-up — 2026-09-19 (second session, Claude Fable 5.1)

## What changed
- NOTE_v1_1.md / README_JA_v1_1.md added; v1.0 files untouched (bundle rule: new version, no overwrite).
- Structure: design findings first (F1-F3), then propositions, then implications; removed repeated disclaimers, kept every scope limit.
- New corollary (window range): for every window 2..18, S >= 0.70 iff unanimity; first non-unanimous breach at window 19 (18:1). Machine-checked by envelope_windows.py (envelope over all k, n <= 25; exact integer certificate at the maximizer) -> results/envelope_windows.json.
- Explicit implications for (a) the published RBG paper section 2/5 wording, (b) the live secretary RHL detector (0.70 is a no-op tunable; sat=0.19 reading semantics), (c) the minimal feature needed to break the repetition-collision class.
- hr_027 placed in the Proposition B regime (a in the hundreds; boundary grams cannot move cosine off 1) rather than only "consistent with".

## What was independently re-verified in this session
- Propositions E, R, B and all boundary integers (27/32/49), n=19 breach value, (910,89,1)/(910,45,45) counterexample: re-derived by hand.
- run_all.py --finalize-only: PASS, all negative controls REJECTED.
- results/lean.log axiom lines: only propext / Quot.sound; toolchain Lean 4.32.2.
- review/final_integration.md: both open items CLOSED on persisted evidence.

## Not changed
- No mathematics weakened or strengthened beyond the added corollary. No live code, kernel, paper, or raw data touched. No publication.

## Recommended next actions (owner decision)
1. Add NOTE_v1_1.md (or a condensed docs/MATH_NOTE.md) to github.com/mobius-style/reflective-budget-governor as the paper's clarification of "saturation".
2. Decide whether the secretary RHL saturation should stay unanimity-only (document it) or become graded (window >= 19 / fixed-alphabet normalization / explicit max-frequency rule) - a design review, not a constant tweak.
3. Fourth-signal (repetition ratio) study per NOTE_v1_1 section 5.4.
