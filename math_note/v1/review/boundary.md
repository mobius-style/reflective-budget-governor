# Independent addendum: first-copy boundary dilution

Date: 2026-09-19. Status: internal mathematical derivation plus exact integer checks and synthetic source-function execution; no novelty claim, model-performance inference, or publication approval. Same source/manual scope and research gates as independent_math.md.

## Verdict

The proposed bound and constants are correct. Moreover, all three cardinality constants are sharp as worst-case guarantees even for realizable strings over a sufficiently large alphabet; explicit distinct-character witnesses below establish this. Do not strengthen this into minimal thresholds for each individual word, because many words have b<2.

## Corrected statement with boundaries

Let u be a nonempty whitespace-normalized word, L=|u| >= q >=1, A=G_q(u), a=|A|>=1. Let B=G_q(u^2)\A and b=|B|. For every m>=2,

G_q(u^m)=A union B, with b<=q-1.

Proof: every factor in two copies either lies within one copy (in A) or starts at one of the q-1 crossing positions. Since L>=q, a q-gram can cross only one boundary. All possible phases already fit in two copies, so later copies add none. The stabilization extension L>=q-1 is also true, but L=q-1 makes A empty; the subsequent a>=1 cosine formulas cannot be applied there. Retain L>=q for the full combined lemma.

For any previous feature history whose union contains A, novelty <=b/(a+b), and

cosine(A,A union B)=sqrt(a/(a+b)).

The cosine here is specifically against the previous set A. A history containing A does not imply that an arbitrary immediately preceding set has this cosine. Thus the dR upper bound additionally requires previous feature set A (as at the first doubling), or another explicit cosine lower bound.

At that first doubling, the RBG ideal-arithmetic dR is bounded above by

.6(1-sqrt(a/(a+q-1))) + .4(q-1)/(a+q-1),

because both terms increase monotonically with b>=0. With history consisting only of the seed A, novelty equals b/(a+b), so the b-specific formula is an equality. q=1 gives b=0, cosine=1, novelty=dR=0, as expected.

## Exact trigram threshold checks

For q=3, worst-case b=2. The following are exact rational/integer comparisons, not floating-point threshold arguments:

- dR<=1/20 iff sqrt(a/(a+2)) >= (11a+38)/(12(a+2)), equivalent to 144a(a+2)>=(11a+38)^2, or 23a^2-548a-1444>=0. At a=26 it equals -144; at a=27 it equals 527. The dR expression is decreasing in positive a; therefore 27 is the least positive integer sufficient for the worst case.
- cosine>=97/100 iff 10000a>=9409(a+2), i.e. 591a>=18818. Least integer a=32.
- cosine>=98/100 iff 10000a>=9604(a+2), i.e. 396a>=19208. Least integer a=49.

A word of a+2 distinct non-whitespace characters has exactly a internal trigrams and exactly two new crossing trigrams. This realizes b=2 for every a>=1 over a sufficiently large alphabet. The executable witnesses use consecutive CJK code points beginning U+4E00; these are distinct ordinary non-whitespace characters. Thus the near-threshold failures are realizable, not merely feasible abstract cardinalities.

## Full stop-trace identity

For literal repetitions x0=u and xi=u^mi with all mi>=2 (i=1..8), the feature sequence is fixed: A,T,T,...,T where T=A union B. Initial raw growth is always at least twofold, so if the first similarity is below .97 the first type is always `expand`; otherwise it is `no_change`. Every subsequent change type is `no_change` because its sets coincide. Consequently all returned trace rows and stop decisions are identical across exponent schedules under the stated arithmetic conditions; this extends beyond the a>=49 corollary.

When a>=49, first similarity clears .98, hence B=1; first dR clears .05 and second dR is zero, hence C=2 with reason equilibrium_d_r. The family permits arbitrarily large finite repetitions as mathematical inputs; no infinite object is processed and no finite-memory implementation is claimed to support unlimited length.

If arbitrary whitespace is inserted or removed independently at each step, features still agree, but the raw initial length relation may differ when a<32. Therefore use literal raw repetitions for the general full-trace theorem, or a>=32 so the initial no_change branch suppresses raw length. Do not infer arbitrary raw-text trace invariance solely from normalized powers in the below-.97 case.

Floating implementation caveat remains: exact arithmetic proves the constants, while executable finite probes establish current Python behavior for the provided sizes. Whole-pipeline judging/token outputs are not included in stop-trace identity.

## Independent execution

boundary_probe.py extracts only source pure functions and checks a in {26,27,31,32,48,49}, each using distinct-character u. For every case it verifies a internal grams, two added grams, and exact full-dictionary equality between fixed two-copy tails and doubling tails. All six pass.

Actual Python results agree with exact comparisons. a=26: B=2,C=2,reason loop (first dR=.05039696 fails epsilon). a=27: B=2,C=2,reason equilibrium_d_r. a=48: B=2; a=49: B=1. This also demonstrates why C stop index alone cannot establish that the epsilon condition fired: its reason must be inspected.

Artifacts: boundary_probe.py and boundary_probe.json. Originals unchanged, no network/model calls.
