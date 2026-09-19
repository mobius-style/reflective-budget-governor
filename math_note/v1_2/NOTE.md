# A sharp finite-count envelope for observed-support normalized entropy

2026-09-19 · v1.2 · Codex extension of the original pilot and **Claude's v1.1**.

## Result and purpose

The saturation score used in the examined RHL/RBG implementations is one minus Shannon entropy divided by the logarithm of the number of observed categories. Its largest possible value on a non-unanimous window of size n is attained uniquely, up to permutation, by the two-category histogram (n−1,1). This holds for every integer n≥2, not just the windows previously enumerated. Consequently, the minimum window permitting a mixed pattern to meet or exceed a chosen saturation threshold is determined exactly by binary entropy.

This is a general mathematical characterization with an implementation-specific use. We supply a complete analytic proof, exact rational-threshold computation and finite Lean certificates. The universal real-analysis proof is **not Lean-formalized**. Independent AI adversarial review is recorded, but does not constitute external peer review. Priority as a new mathematical theorem is not claimed.

## Definitions and theorem

Let c=(c₁,…,cₖ) be positive integer counts, ∑cᵢ=n, n≥2, and 2≤k≤n. With natural logarithms, define

H(c)=−∑ᵢ(cᵢ/n) log(cᵢ/n),  S(c)=1−H(c)/log k.

Here k is the **observed support**, excluding zero-count categories. Separately, the implementation assigns S=1 when k=1. For 0<p<1, let h(p)=−p log p−(1−p) log(1−p).

**Theorem.** Every such non-unanimous histogram satisfies

S(c) ≤ M(n) := 1−h(1/n)/log 2.

Equality holds exactly at permutations of (n−1,1).

### Proof

For fixed k, strict convexity of t log t shows that transferring one unit from b to a when a≥b≥2 strictly increases a log a+b log b, hence decreases entropy. Repeating this integer operation reaches a permutation of (n−k+1,1,…,1). Every other histogram admits such a transfer. Thus these are precisely the fixed-k minimizers of entropy, with normalized value

Fₙ(k)=[n log n−(n+1−k)log(n+1−k)]/[n log k].

The fixed-support entropy formula is known; see Beisel and Moreteau (1997), equation (5). The remaining step is to compare it across supports.

Extend k to real x∈(1,n], put r=n+1−x and A=n log n−r log r. Then

Fₙ′(x)=D(x)/[n x(log x)²],

D(x)=x log x(log r+1)−A(x).

Direct differentiation gives

D′(x)=log x · B(x),  B(x)=log r+1−x/r,

B′(x)=−2/r−x/r²<0.

Although Fₙ is only needed on (1,n], D and B extend continuously to [1,n]. Their endpoint values are

D(1)=D(n)=0,

B(1)=log n+1−1/n>0,  B(n)=1−n<0.

Therefore B has exactly one zero x₀∈(1,n). D strictly increases on (1,x₀), then strictly decreases on (x₀,n). Its endpoint zeros imply D(x)>0 throughout (1,n). Hence Fₙ is strictly increasing on (1,n], and the smallest available normalized entropy is uniquely at k=2. Combining this with the fixed-k equality characterization proves the theorem. For n=2 the only available support is already k=2. ∎

## Exact threshold/window rule

M(2)=0, M(n) increases strictly in n, and M(n)→1. Fix 0<τ<1. There is a unique pτ∈(0,1/2) with

h(pτ)=(1−τ)log 2.

The smallest window admitting **at least one** non-unanimous histogram with S≥τ is

n*(τ)=ceil(1/pτ).

Indeed, h is strictly increasing on (0,1/2), and the binary histogram attains M(n). Thus such a witness exists iff n≥n*(τ). With the k=1 convention, S≥τ is equivalent to unanimity exactly for 2≤n<n*(τ).

This is an inverse-binary-entropy characterization, not an elementary closed form. It does not say that every mixed window fires above n*. For strict S>τ, the integer boundary is floor(1/pτ)+1. At the excluded endpoints τ=0 gives n*=2, whereas τ=1 admits no finite mixed witness.

For rational τ=p/q, 0≤p≤q, the fixed-k extremal histogram fires iff the following **integer** inequality holds:

n^(qn) ≤ k^((q−p)n) (n−k+1)^(q(n−k+1)).

This follows by rearranging Fₙ(k)≤1−p/q and exponentiating. In particular, the binary specialization certifies the adjacent integers returned by `envelope.py`; no floating-point logarithm decides the boundary. Resource caps return an explicit failure rather than an uncertified answer.

At τ=7/10 the exact comparisons are

18^180 > 17^170 · 2^54,

19^190 < 18^180 · 2^57.

Therefore **n*(0.70)=19 for all window lengths**, with witness (18,1). The illustrative scores are M(18)≈0.690456571 and M(19)≈0.702527751. The previous finite observation is now a consequence of the universal bound plus two integer certificates.

As ε=1−τ↓0, h(1/n)=(log n+1)/n+O(n⁻²), yielding

n*(τ) ∼ log(1/ε)/(ε log 2).

To see the inversion, the continuous solution N=1/pτ satisfies ε log 2=(log N+1+o(1))/N, hence log N∼log(1/ε); rounding contributes less than one. This asymptotic is a scaling law, not a substitute for exact finite design.

## Implementation implications and corrections to v1.1

The inspected artifacts are pinned snapshots; this edition makes no live detector changes. Claude's v1.1 numerical result n*=19 survives. Several stronger interpretations need narrower wording:

1. **Threshold tuning has a plateau, not universal ineffectiveness.** At fixed n, every τ∈(M(n),1] produces the same unanimity predicate. At n=8, M(8)≈0.456435557; lowering τ below that boundary can admit mixed patterns without changing the formula or window length. A reported score such as 0.19 is not “19% saturated,” but the continuous score still carries variation among mixed patterns. The theorem concerns the thresholded predicate. For RHL histories of length 5–8, M(8) bounds all mixed scores; exact endpoints should be used instead of downward-rounded decimals.

2. **Saturation is not the earliest available RBG signal.** The source requires three change labels for saturation, while both two-consecutive equilibrium and nonadjacent recurrence can fire at iteration 2. Constant strings and alternating disjoint strings give executable witnesses respectively. The source orders equilibrium before loop before saturation. The identity “saturation stopping condition = three identical non-rewrite labels” remains useful, but cannot by itself explain the causal attribution of token savings or quality loss. The raw score also equals one for three rewrite labels; the separate rewrite guard rejects that stopping condition. Earlier empirical results are neither recomputed nor strengthened here.

3. **hr_027 is near-repetition, not an exact power of its predecessor.** Re-reading the 26B corpus at iterations 5→6 gives normalized lengths 763→38,177, so the latter cannot equal u^m. There are 589 old trigrams, five added, zero removed. The pure-power theorem's b≤2 bound therefore does not apply directly to this event. The more general nested-set identity does: cosine=√(589/594)≈0.995782352, novelty=5/594≈0.008417508, and d̂_R≈0.005897592. These reproduce the actual low-distance signal without asserting literal repetition. This is a retrospective single-case calculation, not a new efficacy evaluation.

4. **A distinguishing observation is necessary; exactly a fourth signal is not.** A feature-map collision cannot be distinguished by functions of that map alone. Repair requires information varying within the relevant equivalence class. That may be incorporated into an existing signal or a new one. Which choice improves behavior remains unmeasured.

## Prior work, contribution and limits

Beisel and Moreteau, “A simple formula for calculating the lower limit of Shannon’s diversity index,” Ecological Modelling 99 (1997), 289–292, DOI [10.1016/S0304-3800(97)01954-6](https://doi.org/10.1016/S0304-3800(97)01954-6), already give the same fixed-support minimum for integer counts and discuss its effect on normalized evenness. The [author-hosted original](https://www.jnbeisel.net/uploads/5/4/4/2/54425847/ecomod_1997_beisel_%26_moreteau_shannon_index.pdf), section 2, equation (5), was inspected. Their formula is explicitly attributed here, not claimed as a discovery. Beisel et al. (2003), [“A Comparative Analysis of Evenness Index Sensitivity”](https://www.jnbeisel.net/uploads/5/4/4/2/54425847/irh_2003_beisel_et_al_evenness.pdf), section 2.2, also treats this finite-count normalization issue.

Our extension supplies a self-contained comparison over all supports, the sharp binary extremizer and equality cases, a threshold/window inversion, and reproducible exact design certificates tied to this detector. The limited narrative search did not establish whether the cross-support theorem has previously appeared elsewhere. It supports a reusable technical note; it does not support a priority claim or a verdict of pure-mathematical novelty. Mathematical correctness, usefulness, and publication originality are separate questions.

Integrality is essential: real counts (0.1,9.9) with nominal total 10 give S≈0.9192, above the integer envelope M(10)≈0.5310. A fixed alphabet denominator is a different problem. Empty windows and implementation warmup need separate handling. The most significant remaining review risks are (a) overstating the scope of Lean and (b) silently changing integrality, observed support, or ≥ into >.

## Evidence and reproduction

Run `python3 verify.py` from this directory (Python with SymPy; pinned Lean path in the script). Run `python3 envelope.py 0.70` for a design certificate; the calculator itself uses only the Python standard library. `results/verification.json` includes the threshold table, every support at n=2…25, source witnesses, symbolic identities, and negative controls.

- Universal envelope, equality, threshold inversion, asymptotic: analytic proofs above, independently adversarially reviewed in `review/general_envelope.md`.
- Finite entropy checks: independent enumeration of 81,120 non-unanimous integer partitions through n=35, floating tolerance 10⁻¹²; corroboration only.
- Exact computation: all 300 (n,k) pairs at n=2…25, plus adjacent rational-threshold certificates; floating crosschecks are a separate diagnostic.
- Lean 4.32.2: the Boolean conjunction covering all 153 fixed-support envelope inequalities for n=2…18 and the exact binary 18/19 inequalities. All three declarations compile without axioms. Two deliberately false variants fail compilation. The analytic log bridge and universal theorem remain outside Lean.
- Original artifacts: all nine pinned input hashes are rechecked. No new model generation, production alteration, or external publication.

Research gates: G1 exploratory derivation and retrospective audit, not a confirmatory experiment; G2 deductive mathematics / exact finite checks / single-case source evidence distinguished, no external peer review; G3 statistical inference not applicable; G4 no subjective measurement; G5 no new LLM performance claim; G6 primary-literature comparison, explicit scope counterexamples, independently reviewed proof and calibrated negative controls. Empirical evidence labels are not used as substitutes for mathematical proof.
