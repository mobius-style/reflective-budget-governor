# Independent adversarial mathematical review — 2026-09-19

Scope: read-only source inspection and pure-function probes of the supplied four files. No original files modified; no model/network calls. Research methodology ch00 and ch03 read. This is an internal, unreviewed, exploratory verification report, not a novelty claim or empirical model-performance result.

Acceptance: distinguish mathematical proof, exact finite computation, and synthetic executable replay. Reject any unsupported universal statement, implementation substitution, or attribution of known local results as new.

## Verdict

Corrected claims (1) and (2) withstand attack under the stated domains. Claim (3) is valid as a feature-indistinguishability result for the specified offline `compute_stops` implementation, with domain/numerical qualifications below. Claim (4) is directly supported by inspected source, but this review alone does not establish current Lean compilation. No unresolved mathematical blocker found in the corrected forms; original Claude proposals 1, 2, 5 cannot be accepted unchanged.

## Findings by severity

### MAJOR if omitted: observable score is not the whole governor

RBG saturation uses the last three labels, only after three labels exist. Its `.7` breach is equivalent to equality of those three labels. But `compute_stops` excludes `rewrite` dominance and gives consecutive d_r priority over loop, and loop priority over saturation. Therefore this is not an iff statement about C stopping or its recorded reason.

RHL `saturation_score()` with default window 8 and at least 5 proposals breaches `.7` iff the observed axes all coincide. `assess()` can nevertheless inject/keep/brake on a loop-score breach, and depends on prior injection state. The theorem concerns the saturation component only. Explicit custom windows can exceed 8 and invalidate the corollary: binary counts (19,1) yield S > .7.

### MAJOR if omitted: real M guard is not semantic descent

Inspected `addons/secretary/evolution/kernel/guard.py::check_m_guard` rejects a new generation when the ledger has unsealed generations. It accepts a completed `no_change_fixation` as a terminal transition. It neither calculates a semantic potential nor establishes a well-founded decreasing rank. Do not derive global termination of the live secretary from this function.

Existing `docs/theory_series_2026-08/lean/T1.lean::theorem2` states well-founded descent implies no infinite run. `prop1` supplies a Bool oscillator satisfying step-local semantic separation forever. Consequently those are existing portfolio results, not fresh discoveries of this pilot. Source inspection is confirmed; compilation must be separately verified. Minor source-documentation caveat: introductory comment says “no guarded run of N+1 steps,” whereas actual theorem1 forbids N+1 visited states (N steps); the detailed theorem comment is correct.

### MEDIUM: string and sequence domains matter

`trigrams` removes all whitespace via `''.join(s.split())`, then emits contiguous character/code-point triples, with singleton fallback `{s}` for length below 3. In particular `trigrams('') == {''}`, a NONEMPTY set. Mathematical n-gram definitions normally give an empty set for short strings; do not silently equate definitions outside the stable-length domain.

`compute_stops` assumes at least 9 strings, indexes only the first 9, and short sequences raise IndexError. Its theorem must fix `MAX_ITERS=8` and this input domain. It computes all 8 trace rows even after reporting an early stop; do not describe that trace as execution of a live stopped model.

Exact set equality overrides raw length checks in `change_type` because cosine >= .97 is tested first. Thus even raw growth caused solely by whitespace is invisible to this classifier. This does not imply that the entire analysis/report/judging pipeline ignores length: token accounting and judge inputs use information beyond these sets.

### LOW: floating-point scope

Finite mathematical set cosine of an equal nonempty set is exactly one. Python uses sqrt and floating-point division; distinguish that ideal statement from implementation numerics. Trace identity under equal feature sets is structural (identical operands), whereas universal exact `d_r == 0` at all representable cardinalities is an unnecessary stronger claim. B=1, C=2 are verified in the attached practical witnesses and follow in exact arithmetic. Thresholds have ample margins for ordinary feasible strings.

## Correct statements and proof checks

### 1. Finite-window saturation envelope

For n >= k >= 2 and positive integer counts c_i summing to n, define

S = 1 - H(c/n)/log k.

Then its maximum at fixed n,k is

Smax(n,k) = 1 - [log n - ((n-k+1)/n) log(n-k+1)]/log k,

attained only by permutations of (n-k+1,1,...,1). Proof: maximizing S is maximizing sum c_i log c_i. For two counts a >= b >= 2, moving one unit b->a strictly increases that sum because x log x has strictly increasing derivative. Repeat until all but one count equal 1. k=1 is a separately defined score of 1, not the formula's removable algebraic case.

For k>=2, S >= 7/10 is equivalent, over exact real logarithms and integers, to

n^(10n) <= k^(3n) * product_i c_i^(10c_i).

No floating comparison is needed. Independent code enumerated every integer partition for n=3..8 and found every mixed partition violates this inequality. Approximate maximum mixed scores: n=3 .0817042; n=5 .2780719; n=6 .3499776; n=7 .4083272; n=8 .4564356. This is an exact finite-domain result, not statistical evidence. Score calculations are illustrative approximations only.

### 2. Repetition stabilization

Let u be a nonempty finite word, L its length, and n>=1 the gram order. Define genuine length-n contiguous factor sets G_n. For m>=ceil((n+L-1)/L), G_n(u^m) is independent of m. Proof: there are at most L start phases modulo L; the bound guarantees all starts 0,...,L-1 fit in u^m, and every later start yields the same factor as its phase representative. Each factor in any larger repetition thus already occurs.

The bound is optimal uniformly over words of length L if the alphabet permits L distinct symbols: choose all symbols of u distinct. Each phase has a distinct first symbol, hence a distinct n-gram; one fewer copy provides fewer than L feasible starts and misses at least one. n=1 separately has universal minimal bound one copy. Restricted alphabets or words with shorter primitive periods may stabilize earlier.

For n=3: L>=2 needs at most 2 copies; L=1 needs 3. Whitespace normalization commutes with concatenation, so apply this to normalized u, requiring normalized length >0. Any function whose only argument is this stabilized set loses repetition multiplicity. This identifies a representation collision; it does not establish an impossibility for count-aware, length-aware, or semantic observers.

Independent finite probe checked binary words of lengths 1..7 and gram orders 1..9 (2,286 cases), comparing the bound against three additional copies, with zero counterexamples. This is a bug-finding check in addition to the proof, not its substitute.

### 3. Entire offline stop-trace collision

Fix the code's constants and 9-step input layout. Suppose every text at indices 0..8 has the same trigram set T, with T nonempty, and equal-set cosine clears .98 (which it does exactly in the real arithmetic model). Then every transition is `no_change`; novelty is zero; d_r is near zero/zero; B=1 and C=2 with reason `equilibrium_d_r`. At iteration 2 recurrence also holds, but d_r wins by code ordering. Saturation is zero at iterations 1,2, then one. All these observations depend on T, not raw repetition counts.

Independent executable witness compares `['abab']*9` with `['ab'*(2**(i+1)) for i in range(9)]`. Returned dictionaries, including all trace rows, are exactly equal in current Python. A=8, B=1, C=2. This is a synthetic offline replay and a proved structural collision under the specified features, not a measured frequency or severity claim on natural model outputs.

## Research gates and rejection conditions

G1: exploratory audit, no prospective empirical study registered. G2: unreviewed mathematical derivations, exact finite computations, source facts, and synthetic replay explicitly separated. Statistical evidence grades do not manufacture proof status. G3/G4: no population inference, p-values, human annotation, or stochastic effect estimate; not applicable. G5: no new model evaluation; training contamination not assessed and no model-performance conclusions permitted. G6: counterexamples and negative conditions are explicit; online prior-art work was outside this assigned read-only scope and must be supplied by parent before any novelty/publication claim.

Two strongest objections anticipated: (a) finite-state feature collisions and entropy extrema are standard mathematics, so contribution is implementation diagnosis unless literature proves otherwise; (b) synthetic repetition failures do not demonstrate task-quality harm or its prevalence in real outputs. Both objections stand and constrain wording.

Reject this review's conclusions if a source snapshot differs in normalization, support denominator, window, thresholds, branch order, cap, or guard function; if any exact partition violates the finite corollary; or if a valid 9-string equal-feature witness yields a different trace without a numerical-domain explanation.

## Evidence artifacts

`independent_probe.py` extracts only six pure functions via AST and runs no source main, imports no model client, and writes its own output only. `independent_probe.json` records exact finite check completion, 2,286 word cases, trace witness, empty-string behavior, and short-sequence error.
