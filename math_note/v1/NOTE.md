# Finite-window saturation and repetition blindness in RHL/RBG

Local mathematical implementation note — 2026-09-19. Exploratory, not submitted or externally peer reviewed. Prepared for Taiko Toeda with Codex assistance. The contributions claimed here are source-specific characterization, reproducible diagnostics, and a partially formalized mathematical core. Mathematical priority is not claimed.

## 1. Outcome and scope

Two useful results survive the pilot:

1. At their current default windows, the RBG/RHL saturation thresholds select **unanimous windows**, not a graded range of dominant-category frequencies. A general sharp entropy envelope explains this, and an exact integer certificate establishes the short-window corollary.
2. Set-valued n-gram features stabilize after finitely many copies of a word. The amount of newly observed information at a concatenation boundary is bounded while repeated length is unbounded. RBG's branch ordering causes this loss to propagate to its change classifier and, for an explicit family, the complete offline stopping trace.

All 1,000 complete source trajectories (8,000 generations) were replayed with no stop/reason/token discrepancy against their saved results. Replacing the numerical saturation score by a Boolean unanimity score preserves all stopping choices and reasons in this corpus. It does **not** preserve the intermediate numerical saturation trace, which can contain 0.081704... in the original.

These results do not prove semantic equilibrium, output quality, live-model causal effects, or termination of the running secretary. Existing T1 already covers well-founded descent; no duplicate claim of novelty is made.

## 2. Source contract

`sources/manifest.json` records the exact original path, byte length, SHA-256, and same-name comparison to the local public checkout for 14 captured files. Calculations use these first-write snapshots. Relevant definitions:

- `sources/analyze.py`, `trigrams`, `cosine`, `novelty`, `change_type`, `saturation`, `compute_stops`: whitespace-stripped Unicode code points, trigram sets, cosine on set indicators, observed-support entropy, last-3 window, threshold 0.70, eight-iteration cap.
- `sources/detectors.py`, `saturation_score`: last 8 proposal axes, minimum 5 observations, observed-support normalization, threshold 0.70. The score acts as one component of the RHL injection/recovery policy; it is not the full `assess()` action.
- `sources/guard.py`, `check_m_guard`: rejects opening a generation while another remains unsealed. It calculates no semantic descent measure.
- `sources/T1.lean`: existing well-founded descent theorem and step-local oscillator counterexample, recompiled here.

For RBG, a normalized string shorter than 3 yields the singleton set `{s}`; the empty string yields `{''}`. Standard factor sets used in the mathematics below differ on short strings. Their interface is asserted only where normalized length is at least the gram order. `compute_stops` expects at least nine strings and uses indices 0..8. It computes a retrospective full trace even after its recorded stop.

## 3. Proposition E: sharp finite-window entropy envelope

Let n observations occupy exactly k observed categories, with positive integer counts c_1,...,c_k and sum n. Define

\[
S(c)=1-\frac{H(c/n)}{\log k},\qquad H(c/n)=-\sum_i\frac{c_i}{n}\log\frac{c_i}{n},\quad k\ge2,
\]

and set S=1 for k=1, as the code does. For fixed n>=k>=2,

\[
\max_c S(c)=1-\frac{\log n-\frac{n-k+1}{n}\log(n-k+1)}{\log k}.
\]

The maximizing histograms are permutations of `(n-k+1,1,...,1)`.

**Proof.** Since H=log n−(1/n)sum c_i log c_i, minimizing H maximizes the latter sum. If a>=b>=2 are two cell counts, replacing them by a+1,b−1 strictly increases that sum: x log x has strictly increasing derivative. Repeat until only one cell exceeds one. This preserves positivity, support and total, and ends at the displayed histogram. Substitution gives the formula. The all-one case k=n is included. This is a standard convexity/majorization argument, not a new general entropy theorem. ∎

### Exact certificate at 0.70

For k>=2, all logarithms have positive arguments and log k>0. Algebra and monotonicity of exp give

\[
S(c)\ge\frac7{10}\iff n^{10n}\le k^{3n}\prod_i c_i^{10c_i}.
\]

Specifically, multiply H<=(3/10)log k by 10n and exponentiate. The right comparison is over integers; no floating logarithm enters its decision. `verify.py` enumerates all 255 ordered positive compositions with 1<=n<=8. `Pilot.compositions_complete` proves the Lean generator includes every positive histogram; `Pilot.exact_small_unanimity` establishes that its exact predicate is true iff k=1 for this domain. The real-logarithm algebraic bridge is proved above in prose, not formalized in Lean core.

| n | Largest mixed-window S (approx.) | Attaining histogram |
|---:|---:|---|
| 3 | 0.081704166 | (2,1) |
| 5 | 0.278071905 | (4,1) |
| 6 | 0.349977578 | (5,1) |
| 7 | 0.408327221 | (6,1) |
| 8 | 0.456435557 | (7,1) |

Therefore, at the implemented threshold:

- **RBG score breach:** exactly three identical most recent labels, with at least three labels available. Actual saturation-triggered stopping additionally excludes `rewrite`, and can be preempted by the earlier equilibrium or loop branches.
- **RHL score breach, default window:** exactly one observed axis among the most recent min(total,8) proposals, with at least five proposals. Loop state and prior lens injection can still change `assess()` independently.

More generally, in exact arithmetic every threshold in `(0.0817041659...,1]` produces the same RBG score-breach predicate, and every threshold in `(0.4564355568...,1]` produces the same default RHL predicate. Here the endpoints denote the exact entropy expressions, not rounded decimal cutoffs. Raising 0.70 to 0.90 cannot make these components more selective. This gives a concrete design interpretation of the inherited constant without proposing an untested replacement.

**Boundary failures.** With 19 observations, `(18,1)` has S≈0.702527751, so extending this corollary to arbitrary windows is false. Exact envelope evaluation confirms 19 is the first n admitting a mixed breach. Fixed-alphabet normalization also changes the conclusion: `(7,1)` divided by log 8 instead of log 2 has S≈0.818811852. Finally, a general maximum-frequency iff rule is false even at threshold .70: `(910,89,1)` and `(910,45,45)` have the same n=1000, k=3 and maximum count 910, but S≈0.719617139 and 0.667834528 respectively. The original proposed candidate is thus repaired by a count-domain envelope, not accepted as stated.

## 4. Proposition R: eventual n-gram-set stabilization

Let u be a nonempty word of length L, q>=1 a gram order, and G_q(v) the set of contiguous factors of length q in v. Put

\[
m_0=\left\lceil\frac{q+L-1}{L}\right\rceil.
\]

Then G_q(u^m)=G_q(u^{m_0}) for every m>=m_0.

**Proof.** An occurrence in the periodic word uuu... is determined by its start position modulo L. A prefix of length mL contains all L start phases as soon as mL>=q+L−1: the last needed start is L−1 and its exclusive endpoint is L−1+q. Every later start produces the same word as its phase representative. Thus all subsequent finite repetitions have exactly the same set of factors. ∎

**Sharp uniform copy bound.** When the alphabet has at least L symbols, take all L symbols of u distinct. Each start phase has a different first symbol. One fewer copy than m_0 has fewer than L feasible starts and misses a phase (for q=1 the minimal positive count is simply one). A smaller word-specific bound can hold when u has a shorter primitive period or different phases produce the same gram.

For trigrams, L>=2 needs at most two copies, while L=1 needs three. The false first-copy claim is refuted by `G_3(abc)={abc}` versus `G_3(abcabc)={abc,bca,cab}`. Whitespace deletion commutes with concatenation, so the theorem applies to RBG after normalizing u, provided the normalized word is nonempty and the stable strings have length >=3.

`Pilot.repetition_stability` formalizes the arbitrary-word, arbitrary-period, arbitrary-order proof as finite windows in a periodic sequence. Its periodic-window definition is the mathematical model; the connection to Python slicing/Unicode whitespace normalization remains a specified and tested interface, not verified Python compilation.

## 5. Proposition B: bounded boundary change, unbounded length

Let L>=q and a=|G_q(u)|>=1. For every m>=2,

\[
G_q(u^m)=G_q(u)\cup B,\qquad b=|B|\le q-1,
\]

where B consists of new boundary-crossing grams and does not depend on m. Indeed, the single copy contains starts 0..L−q; only the remaining q−1 phases can add new grams. Consequently

\[
\operatorname{cos}(G_q(u),G_q(u^m))=\sqrt{\frac a{a+b}},\qquad
\operatorname{novelty}(u^m)\le\frac b{a+b}
\]

whenever the seen history includes G_q(u). Equality in the novelty expression holds when history consists only of that set. In contrast, |u^m|/|u|=m has no finite bound.

When the immediately preceding set is G_q(u) and the seen history contains it, the actual weights give the following ideal RBG distance bound:

\[
\widehat d_R\le\frac35\left(1-\sqrt{\frac a{a+q-1}}\right)+\frac25\frac{q-1}{a+q-1}.
\]

For q=3, sufficient worst-case cardinalities are:

| Condition | Sufficient a, with b<=2 |
|---|---:|
| distance <=0.05 | 27 |
| cosine >=0.97 (`no_change` branch) | 32 |
| cosine >=0.98 (arm B stop) | 49 |

These are the smallest integer a for the worst-case b=2 algebra. They are not length-in-characters thresholds. Cosine thresholds follow by squaring nonnegative quantities. For distance, write r=a/(a+b); the inequality is equivalent to `12 sqrt(r)+8r>=19`. Since `(19−8r)/12` is positive for 0<r<=1, squaring gives `23a²>=274ab+361b²`. Monotonicity in a and b extends each boundary check to all larger a and smaller b. Lean verifies the integer boundary comparisons; the square-root reduction and monotonicity are prose arguments.

This is stronger than the bare eventual-invariance observation: it quantifies how a **single** ordinary-length starting copy can already be arbitrarily inflated while satisfying a high similarity threshold.

## 6. Consequences for observability and the full RBG policy

**Feature-only impossibility.** If feature(x)=feature(y), every deterministic observer factoring through that feature returns the same value at x and y. It cannot recover a label that differs between x and y. `Pilot.feature_collision` and `Pilot.cannot_recover` formalize this elementary statement. Randomized observers with the same feature-conditioned law also have identical output distributions; that extension is not needed or formalized here.

**Whole-policy collision for a specified family.** RBG is not globally a function of sets alone: `change_type` also has raw length branches. But it tests cosine>=.97 **before** those branches. Thus equal nonempty sets take `no_change` even when length expands drastically. If all nine inputs share one common set and equal-set cosine passes the thresholds, the complete returned trace depends only on that set. Ideal arithmetic gives B=1, C=2 (`equilibrium_d_r`); loop also becomes true at step 2 but loses branch priority.

An executed witness compared nine constant texts `abcabc` against `abc` repeated 2,4,8,...,512 times. Their returned dictionaries, including every trace row, are exactly equal. Lengths range 6..1536 in the growing sequence.

A second executed witness starts with **one** copy of 51 distinct non-whitespace code points (49 internal trigrams, 2 new boundary trigrams), then compares fixed two-copy outputs against repetitions 2,4,...,256. Proposition B yields B=1, C=2; current Python reproduces identical complete traces. More generally, for a fixed u the set sequence `[G(u), G(u²), G(u²), ...]` is independent of the later repetition exponents, as long as all are >=2 and L>=3. When a>=49 the ideal thresholds force every transition into `no_change`.

Floating-point scope: identical set operands structurally produce identical computed scalars. Ideal equal-set cosine=1 and the algebraic threshold bounds are real-arithmetic results; executed witnesses establish current Python behavior. We do not assert a universal exact floating `d_r==0` for arbitrary infeasible set sizes. Neither token accounting nor quality judging factors only through these features.

**Necessary design consequence.** An observer intended to distinguish these pairs must use at least one feature that changes within this set-equivalence class. Adding normalized length or occurrence multiplicity can separate the constructed pairs. Sufficiency for semantic quality, ordinary expansion, or safe early stopping is not established. No live detector was changed.

## 7. Real-corpus replay and its limits

| Model tag | Complete tasks | Generation rows | Saved stop/reason/token mismatches | Boolean-substitution stop/reason mismatches |
|---|---:|---:|---:|---:|
| 12b | 500 | 4000 | 0 | 0 |
| 26b | 500 | 4000 | 0 | 0 |

All task IDs, iteration IDs 1..8, uniqueness and per-arm token sums were checked. Each model contributes 3,000 full length-3 windows. For 12b their histogram shapes occur 1,284 times `(3)`, 1,626 `(2,1)`, and 90 `(1,1,1)`; for 26b: 1,178, 1,681, and 141. These are exact corpus descriptions, not independent statistical samples or estimates of model behavior.

The recorded reason is saturation in 206 12b tasks and 168 26b tasks. These counts include any reason recorded at the cap; they should not automatically be called early interventions. Other branches and `rewrite` exclusion explain why unanimous-window counts are not stop counts.

For the previously named 26b `hr_027`, iteration 5 is 899 raw characters, iteration 6 is 45,152, and iteration 7 returns to 899. Recomputed C selects iteration 6 with `equilibrium_d_r`; its trace shows similarity≈.996, distance≈.006, `loop=true`, `type=no_change`. This is **not** an exact-set-equality instance of Proposition R; it is a high-similarity practical failure consistent with boundary insensitivity. No new semantic label or quality judgment was assigned.

## 8. Candidate disposition and prior art

| Original proposal | Pilot disposition |
|---|---|
| Any trigram-set similarity is invariant to verbatim repetition | False from the first copy; replace by Propositions R/B and a scoped feature-collision corollary. |
| Saturation threshold iff maximum frequency exceeds a function | False generally; retain Proposition E and exact default-window corollaries. |
| Contraction implies logarithmic stopping | Conditional standard direction; actual RBG proxy is not established as the contraction metric. Deferred, not a proved portfolio result. |
| Two consecutive epsilon events bound false equilibrium | Requires a specified dependence/noise model and definition of false equilibrium. Deferred; no independence assumption invented. |
| M guard plus strict decrease proves termination | Real decrease alone is insufficient; well-founded version already in T1. Live serialization guard is not that assumption. No new result claimed. |

Primary-literature comparisons and searches are in `LITERATURE.md`. Broder already distinguishes set shingles from occurrence-labelled shingles; Shannon entropy concentration is standard; observed-support normalization is established. The added value here is their exact consequences for these implementations. GO for a local reproducible technical note; NO-GO for claiming priority or a new deep theorem.

The existing T1 introductory comment loosely says “N+1 steps,” while the theorem's actual statement excludes N+1 visited states (N steps). This pilot relies on the theorem statement, not that comment, and leaves the original untouched.

## 9. Verification, refutation, and next experiment

`verify.py` checks all 255 small positive compositions, all 64 RBG type triples, 10,160 periodic-set equalities, sharpness witnesses, one-copy boundary cases, both complete real corpora, and source non-drift. Negative controls deliberately falsify first-copy invariance, a zero-threshold unanimity claim, and substituting a fixed support denominator. `review/independent_math.md`, `review/boundary.md` and `review/final_integration.md` contain a separate agent's attempts to construct counterexamples and reconcile the final artifacts; this is internal adversarial review, not external peer review or an independent organization’s replication.

Lean 4.32.2 compiles the periodic-window theorem, feature collision, histogram-generator completeness, and exact small-sum unanimity theorem. No `sorry`, `admit`, new axioms, or `native_decide` is used. Axiom output is recorded in `results/lean.log`; standard Lean axioms `propext` and `Quot.sound` occur in some proofs. `results/lean_checks.json` also records negative compilation controls and recompilation of the pre-existing T1.

Two objections remain accepted: the general mathematics is elementary/known, and constructed indistinguishability does not measure the prevalence or quality cost of natural failures. All empirical material is retrospective and exploratory. G1 exploratory only; G2 evidence types explicitly separated; G3/G4 not applicable without statistical/subjective inference; G5 no model-performance conclusion; G6 counterexamples, primary-source search and adversarial review supplied.

The next justified study would freeze a count/length-sensitive detector and its false-positive criteria on new held-out examples, including legitimate expansions and repeated necessary templates. It must distinguish a warning/rollback decision from stopping and returning the already-degenerated iterate. The current pilot makes no effectiveness claim for such a remedy and launches no new generation campaign.
