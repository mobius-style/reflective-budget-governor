# Independent envelope review — checkpoint

Scope: mathematical refutation of all-n normalized observed-support entropy envelope, derivative proof, equality cases and threshold inversion. Original bundle/runtime read-only. Read research methodology ch00 and ch03. DoD: check algebra independently; attempt counterexamples and boundary mutants; save exact finite and prose-proof findings separately. No Lean certification or novelty claim implied.

Refutation condition: any positive integer histogram with sum n>=2, support k>=2, whose S=1-H/log(k) exceeds the binary (n-1,1) score, or a non-permutation equality case. Theory task; empirical/statistical gates G1/G3/G4/G5 are inapplicable to deductive proof; finite checks are exploratory corroboration. G2: unreviewed mathematical deduction. G6 online prior-art work delegated to parent; this file is no novelty verdict.

## Verdict

PASS for the stated **positive integer histogram** theorem and the proposed derivative argument. No mathematical blocker found. This is an independent derivation/review, not journal peer review and not Lean verification. Claude's v1.1 contribution remains attributed to Claude. No novelty verdict is made.

## Full proof checked independently

Let n>=2 be an integer. For positive integer counts c_1,...,c_k summing to n and k>=2, put H=log(n)-sum(c_i log(c_i))/n and S=1-H/log(k). Logs may have any common base >1.

For fixed k, strict convexity of t log t shows that if two counts a>=b>=2 exist, replacing (a,b) by (a+1,b-1) strictly increases sum(c_i log c_i), and so strictly decreases H. Iteration terminates because counts are integers and the sum is fixed. It reaches a permutation of (n-k+1,1,...,1). Conversely, only those permutations minimize H. This includes k=n, when the all-ones histogram is the sole possibility.

Therefore the fixed-k minimum normalized entropy equals

F_n(k)=[n log n-(n+1-k)log(n+1-k)]/[n log k].

Extend k to real x in (1,n], define r=n+1-x and A=n log n-r log r. Then A'=log r+1 and

F_n'(x) = D(x)/[n x (log x)^2],
D(x)=x log x(log r+1)-A(x).

Direct differentiation yields

D'(x)=log x B(x),
B(x)=log r+1-x/r,
B'(x)=-2/r-x/r^2<0.

All expressions for D are defined on [1,n]; F is only needed on (1,n]. Endpoint values are

D(1)=0, D(n)=0,
B(1)=log n+1-1/n>0,
B(n)=1-n<0.

Continuity and strict decrease of B give exactly one zero x0 in (1,n). Since log x>0, D increases strictly on (1,x0) and decreases strictly on (x0,n). Its two endpoint zeros force D(x)>0 throughout (1,n). Thus F_n is strictly increasing on (1,n], and its minimum over integer k=2,...,n is uniquely at k=2. The case n=2 simply has only k=2 and is included.

Consequently

max S = 1-h(1/n)/log 2,
h(p)=-p log p-(1-p)log(1-p),

with equality exactly for permutations of (n-1,1). There is no additional equality at k>2.

## Exact threshold inversion

For 0<tau<1, let q_tau be the **unique** q in (0,1/2) satisfying h(q)=(1-tau)log 2. Here h inverse means the lower increasing branch on [0,1/2], not an elementary inverse formula.

Then a non-unanimous histogram can meet S>=tau if and only if

n >= n*(tau) = ceil(1/q_tau).

This follows because h is strictly increasing on (0,1/2), 1/n decreases with n, and the binary histogram attains the bound. The ceiling must respect exact equality; a numerical inverse near an integer boundary requires a certified final integer inequality. With the convention S=1 at support k=1, S>=tau is equivalent to unanimity precisely for 2<=n<n*(tau). At n=n*(tau), a non-unanimous witness exists. If the detector uses strict S>tau instead, the integer boundary becomes floor(1/q_tau)+1. This is a substantive inequality-direction caveat.

Endpoint thresholds are outside the stated formula: tau=0 gives n*=2; tau=1 has no finite non-unanimous witness.

For tau=7/10, two exact integer comparisons give

18^180 > 17^170 * 2^54,
19^190 < 18^180 * 2^57.

These imply S_binary(18)<7/10<S_binary(19), without trusting floating logs. The all-n monotonic bound therefore proves n*(7/10)=19. Illustrative decimal scores are 0.6904565708496755 and 0.7025277510807109.

## Asymptotic consequence (prose deduction only)

Set delta=1-tau. Since h(1/n)=(log n+1)/n+O(n^-2), as tau tends to 1 from below,

n*(tau) ~ log(1/delta)/(delta log 2).

Ceiling contributes at most 1 and does not alter the equivalence. This is a scaling law, not an accurate finite-threshold replacement. It gives a further general design consequence: raising a threshold toward one requires windows diverging faster than 1/(1-tau) before any non-unanimous pattern can trigger.

## Refutation attempts and concrete scope failures

1. Independently enumerated 81,120 non-unanimous integer partitions for n=2,...,35. Comparing scores at floating tolerance 1e-12 found zero bound violations and zero extra equality cases. This finite floating check corroborates but does not prove the universal theorem.
2. Exact integer n=18 and n=19 certificates both passed. The known-broken mutant 'unanimity equivalence holds through n=19 at tau=.7' was rejected by the second certificate.
3. Integrality is essential: positive real counts (0.1,9.9) total n=10 but have S approximately .9192068641, exceeding the integer n=10 envelope approximately .5310044064. Thus this is a finite count lattice result, not a bound for arbitrary probability vectors merely assigned a nominal n.
4. Observed support k is essential. Replacing it with a fixed alphabet size changes the optimization and unanimity threshold conclusions; zero-count bins must not enter k in this theorem.
5. k=1 requires a declared convention because H/log(k)=0/0. The theorem itself only addresses k>=2, avoiding that singularity.

Most painful remaining review issues: (i) the proof could be described as fully Lean-certified when it currently is prose; (ii) the application could silently change observed support, positive integer counts, or >= into >. These must be explicit in the note. Novelty and implementation usefulness require the parent's separate source/literature audit.

## Verification levels

- Universal all-n envelope, uniqueness, threshold inversion, asymptotic: independently reviewed prose proofs.
- n=18/19 thresholds: exact arbitrary-precision integer checks in refute_envelope.py and refute_envelope.json.
- n=2..35 search: finite floating corroboration, not exact entropy certificate or universal proof.
- Lean: **none performed by this reviewer**. Parent must scope any Lean claim to the declarations actually compiled.

Research gates: G1 theory/refutation scope recorded before this check; no empirical confirmatory study claimed. G2 deductive result with independent AI review, not statistical evidence or peer-reviewed novelty. G3/G4/G5 not applicable (no samples, judges, or new LLM evaluation). G6 counterexample attempts and two risks above supplied; online prior-art status remains the parent's responsibility.
