# What the RBG/RHL saturation and similarity signals can and cannot see

**Finite-window saturation and repetition blindness — implementation note, v1.1 (2026-09-19)**

Brushed-up edition of NOTE.md. Same mathematics, same evidence; restructured so the
design findings lead, with one new corollary (window-length range) and its machine check.
Local, exploratory, internally reviewed; not externally peer reviewed; no priority claim
for the general mathematics (see §7). All definitions are bound to SHA-256-pinned
snapshots of the live sources (`sources/manifest.json`).

## 0. Three findings, in plain terms

**F1 — The "saturation" threshold is not a threshold at the deployed windows.**
Both detectors compute `S = 1 − H/log k` over the *observed* categories of a short
window and fire at `S ≥ 0.70`. For every window length up to 18, that condition is
*equivalent to unanimity*: every item in the window has the same category. So

- in RBG (window 3), "saturation" means *three consecutive identical change types*
  (with `rewrite` excluded by a separate rule);
- in the live secretary's RHL detector (window ≤ 8, ≥ 5 proposals), it means *every
  recent proposal shares one value axis*.

Any threshold in `(0.0817, 1]` gives the same RBG predicate and any threshold in
`(0.4564, 1]` the same RHL predicate; raising 0.70 to 0.90 changes nothing. Replacing
the numeric score by the Boolean "all equal" reproduced every stop index and reason
across all 1,000 real chains. The first window length at which a non-unanimous window
can breach 0.70 is 19 (histogram 18:1).

**F2 — Set-based trigram features cannot see verbatim repetition, and the blindness
is quantitative.** Repeating a word of length ≥ 3 adds at most two new trigrams (the
two boundary grams), however many copies are made. If the word already has `a ≥ 49`
distinct trigrams, its cosine similarity to *any* number of copies is ≥ 0.98 (arm B's
stop threshold); `a ≥ 32` already forces RBG's `no_change` branch, and `a ≥ 27` pushes
`d̂_R` under its 0.05 equilibrium epsilon. Because RBG tests similarity *before* it
looks at length, a sequence that doubles in length every step and a sequence that
never changes can produce byte-identical governor traces — a witness is executed, not
merely argued. The hr_027 collapse reported in the RBG paper (≈50 copies, similarity
0.996) sits squarely in this regime.

**F3 — There is no new termination theorem here.** Well-founded descent, and the
failure of a step-local guard, already exist in the portfolio's T1 Lean file. The
live secretary's M guard serializes unsealed generations; it does not compute a
descending semantic rank, so nothing about it follows from T1 without further
assumptions.

## 1. Setting

- `analyze.py` (RBG): text is whitespace-stripped; `trigrams` returns the *set* of
  length-3 factors (a string shorter than 3 gives the singleton `{s}`); `cosine` is the
  set-indicator cosine `|A∩B|/√(|A||B|)`; `novelty(x_t)` is the fraction of `x_t`'s
  trigrams unseen in `x_0..x_{t−1}`; `change_type` tests `cosine ≥ 0.97 → no_change`
  *before* its length-ratio branches; `saturation` is `S` over the last three change
  types with observed-support normalization; `compute_stops` runs an 8-iteration cap
  and records the first firing signal (equilibrium `d̂_R ≤ 0.05` twice → loop → saturation
  with dominant type ≠ rewrite).
- `detectors.py` (RHL, live secretary): `saturation_score` is `S` over the `value_axis`
  of the last 8 proposals, returns 0 below 5 proposals, threshold 0.70. It is one
  input to `assess()`, alongside loop state and lens injection.
- `guard.py`: `check_m_guard` refuses to open a generation while another is unsealed.
- `T1.lean`: existing well-founded descent theorem and step-local oscillator
  counterexample; recompiled here, unchanged.

Notation: a window of `n` items occupies `k` observed categories with positive counts
`c_1..c_k`, `Σc_i = n`; `S(c) = 1 − H(c/n)/log k` for `k ≥ 2`, `S = 1` for `k = 1`
(as the code does).

## 2. Result 1 — saturation at short windows is unanimity

**Proposition E (sharp envelope).** For fixed `n ≥ k ≥ 2`,
`max_c S(c) = 1 − [log n − ((n−k+1)/n)·log(n−k+1)] / log k`, attained exactly at
permutations of `(n−k+1, 1, …, 1)`.

*Proof.* `H = log n − (1/n)Σ c_i log c_i`, so minimizing `H` maximizes `Σ c_i log c_i`.
For two cells `a ≥ b ≥ 2`, moving one unit from `b` to `a` strictly increases the sum
(`x log x` has strictly increasing derivative); iterate until a single cell exceeds 1.
This is a standard Schur-concavity/majorization argument. ∎

**Exact certificate.** For `k ≥ 2`,
`S(c) ≥ 7/10 ⇔ n^(10n) ≤ k^(3n) · Π c_i^(10 c_i)` — an integer comparison, so no
floating logarithm enters the decision.

**Corollary (window range).** For every window length `2 ≤ n ≤ 18`, `S ≥ 0.70` holds
iff `k = 1`. The first `n` admitting a non-unanimous breach is 19, with `(18, 1)`
(`S ≈ 0.70253`). *Evidence:* the envelope maximum over all `k` is at `k = 2` for each
`n ≤ 25` (`envelope_windows.py`, `results/envelope_windows.json`); the `n ≤ 8` case is
additionally exhaustive over all 255 positive compositions in `verify.py` and universal
in Lean (`Pilot.exact_small_unanimity`, via generator completeness
`Pilot.compositions_complete`).

| n | largest non-unanimous S | histogram |
|---:|---:|---|
| 3 (RBG) | 0.081704 | (2,1) |
| 5 (RHL min.) | 0.278072 | (4,1) |
| 8 (RHL default) | 0.456436 | (7,1) |
| 18 | 0.690457 | (17,1) |
| 19 | 0.702528 | (18,1) |

**Consequences.**
- RBG score breach ⇔ the last three change types are identical. Saturation-triggered
  *stopping* additionally requires dominant type ≠ `rewrite` and loses priority to the
  equilibrium and loop branches; replay shows that with the Boolean substituted for the
  score, all 1,000 chains keep their stop index and reason (`results/replay.json`).
- RHL score breach at default settings ⇔ one observed axis among the last
  `min(total, 8)` proposals (≥ 5). Whether `assess()` acts still depends on loop state
  and lens history.
- The inherited constant 0.70 is therefore not a tunable in `(E(w), 1]`. If a *graded*
  dominance detector was intended, one of three changes is required: window ≥ 19; a
  fixed-alphabet denominator (`log |axes|` instead of `log k` — then `(7,1)/log 8`
  gives `S ≈ 0.819`); or an explicit maximum-frequency rule. Note the last is *not*
  equivalent to an entropy rule in general: `(910, 89, 1)` and `(910, 45, 45)` share
  `n`, `k` and maximum count yet have `S ≈ 0.7196` and `0.6678`.

## 3. Result 2 — repetition and n-gram sets

Let `u` be a nonempty word of length `L`, `q ≥ 1` the gram order, `G_q(v)` the set of
length-`q` factors of `v`.

**Proposition R (stabilization).** With `m_0 = ⌈(q+L−1)/L⌉`, `G_q(u^m) = G_q(u^{m_0})`
for all `m ≥ m_0`. *Proof.* A factor occurrence in the periodic word is determined by its
start phase mod `L`; a prefix of length `mL ≥ q+L−1` contains every phase; later starts
repeat a phase. ∎ The bound is sharp when `u` has `L` distinct symbols. For trigrams:
two copies suffice for `L ≥ 2`, three for `L = 1`. The naive "invariant from the first
copy" claim is false: `G_3(abc) = {abc}` but `G_3(abcabc) = {abc, bca, cab}`.
(Lean: `Pilot.repetition_stability`, over finite windows of a periodic sequence.)

**Proposition B (bounded boundary change).** For `L ≥ q`, `a = |G_q(u)|`, and `m ≥ 2`:
`G_q(u^m) = G_q(u) ∪ B` with `|B| ≤ q−1`, independent of `m`. Hence
`cos(G_q(u), G_q(u^m)) = √(a/(a+b))`, `novelty(u^m) ≤ b/(a+b)` once `G_q(u)` is in the
seen history, while `|u^m|/|u| = m` is unbounded. When the immediately preceding set is
`G_q(u)`, the ideal RBG distance obeys
`d̂_R ≤ (3/5)(1 − √(a/(a+q−1))) + (2/5)(q−1)/(a+q−1)`.

Worst case `q = 3, b = 2` (integer boundaries certified in Lean):

| condition | sufficient `a` |
|---|---:|
| `d̂_R ≤ 0.05` (equilibrium step) | 27 |
| `cos ≥ 0.97` (`no_change` branch) | 32 |
| `cos ≥ 0.98` (arm B stop) | 49 |

These are counts of *distinct trigrams*, not character lengths; an ordinary paragraph
exceeds all three by an order of magnitude.

**Feature-only impossibility.** If `feature(x) = feature(y)`, no deterministic observer
factoring through `feature` can separate `x` from `y` (`Pilot.feature_collision`,
`Pilot.cannot_recover`). RBG is not purely set-valued — `change_type` has raw-length
branches — but it reaches them only when `cos < 0.97`, so equal nonempty sets always
yield `no_change`. Two executed witnesses: nine constant texts `abcabc` versus `abc`
repeated `2, 4, …, 512` times (lengths 6 → 1536), and a 51-symbol seed (`a = 49`) versus
its repetitions `2, 4, …, 256` — in both, every returned trace row is identical, with
`B = 1`, `C = 2` (`equilibrium_d_r`).

**Relation to hr_027.** The paper's flagship failure (26B, iteration 6 ≈ 50 copies,
`sim ≈ 0.996`, `d̂_R ≈ 0.006`, `type = no_change`, governor stops *on* the collapse) is
not an exact-set-equality instance (separators add a few grams) but is exactly the
Proposition B regime: with `a` in the hundreds, a handful of boundary grams cannot move
the cosine off 1. The blindness the paper reported qualitatively is here bounded.

## 4. Result 3 — termination: nothing new

`T1.lean` (`theorem2`, `prop1`) already proves well-founded descent and exhibits a
step-local guard that oscillates. The live `check_m_guard` enforces *serialization*
(no second open generation), not strict decrease of any potential; so "M guard plus
strict decrease ⇒ termination" would need an assumption the code does not implement.
The candidate is withdrawn, not proved. (T1's introductory comment says "N+1 steps"
while its theorem excludes N+1 visited states; we rely on the statement and leave the
comment untouched.)

## 5. Implications and recommendations

1. **RBG paper (DOI 10.5281/zenodo.22031367), §2 and §5.** "Saturation ≥ 0.70" should
   be read as "three consecutive identical non-rewrite change types". The ablation's
   conclusion — saturation is both the savings engine and the main quality-cost source —
   now has a mechanistic reading: it is the *earliest-firing* signal, firing after just
   three same-type steps. A clarification in the companion repository is warranted;
   whether to cut a Zenodo v1.1 is the owner's call (no numbers change).
2. **Live secretary (RHL).** Under default settings, saturation fires only on
   axis-unanimity across the recent window. This is a legitimate but *very conservative*
   detector; the current live reading (`sat ≈ 0.19`) reflects a non-unanimous window, not
   "19% saturated". Any tuning of the 0.70 constant is a no-op; changing the window or
   the normalization is a design change and should be reviewed as such.
3. **Minimal fix for repetition blindness.** By the impossibility result, any detector
   meant to separate the constructed pairs must use a feature that varies within the
   set-equivalence class — normalized length, occurrence multiplicity, or a
   repetition ratio (`len / deduplicated-len`). This is necessary, not sufficient;
   effectiveness on natural text is unmeasured here.
4. **Next study (not started).** Freeze a count/length-sensitive fourth signal with
   pre-registered false-positive criteria (legitimate expansions, required templates),
   and evaluate on held-out chains. It must distinguish "warn/roll back" from "stop and
   return the already-degenerate iterate".

## 6. Verification ledger

| item | status |
|---|---|
| 14 source snapshots, SHA-256 pinned, no drift after runs | PASS |
| exact certificate, all 255 positive compositions, `n ≤ 8` | PASS (`verify.py`) |
| all 64 RBG change-type triples vs implementation | PASS |
| window-range corollary, envelope over all `k`, `n ≤ 25` | PASS (`envelope_windows.py`, v1.1) |
| periodic-set equalities (10,160 comparisons) | no counterexample |
| replay of 1,000 chains / 8,000 generations vs saved stops/reasons/tokens | 0 mismatches |
| Boolean-unanimity substitution, stop index + reason | 0 mismatches (numeric trace differs, as expected) |
| Lean 4.32.2 core: `repetition_stability`, `feature_collision`, `cannot_recover`, `compositions_complete`, `exact_small_unanimity`, three integer boundary theorems | compiled fresh; axioms only `propext`, `Quot.sound`; no `sorry`/`native_decide` |
| negative controls (false first-copy invariance; zero-threshold; fixed-denominator; three broken Lean mutants; missing data / proof hole / missing review) | all REJECTED as intended |
| independent reviews (`review/`): mathematical, boundary, integration | both open items CLOSED |
| v1.1 re-verification by a second session (Claude): propositions re-derived by hand, `run_all.py --finalize-only` PASS, Lean axiom log inspected, corollary machine-checked | PASS |

Not formalized: the real-logarithm ⇔ integer bridge, the square-root/monotonicity steps
for the `d̂_R` boundary, and the correspondence between the Lean periodic model and
Python string handling. These are prose proofs plus executed tests.

## 7. Scope and prior art

Multiplicity loss in set shingles is explicit in Broder (1997); Shannon-entropy
concentration under majorization is standard (Sason 2018); observed-support
normalization is established practice. What is specific to this note is the exact
consequence for *these* deployed formulas: the unanimity equivalence with its window
range, the trigram thresholds 27/32/49, the whole-policy collision family, and the
full-corpus replay. GO as a reproducible technical note; NO-GO as a novelty-led
mathematics paper. No claim is made about semantic equilibrium, output quality, or the
prevalence of natural failures beyond the two collapses already reported in the paper.
