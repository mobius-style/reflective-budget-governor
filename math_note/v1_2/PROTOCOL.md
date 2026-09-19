# General envelope extension — 2026-09-19

Parent v1.0 was the earlier Codex pilot. v1.1 is Claude's revision, explicitly corrected by the user. This v1.2 is Codex's mathematical extension and audit; originals remain unchanged.

## Definition of done
1. Resolve the all-n, all-support binary-extremizer conjecture by a complete proof or counterexample; derive the threshold/window design rule if it survives.
2. Deliver a deterministic exact rational-threshold calculator with endpoint certificates, finite Lean checks, calibrated negative controls, and an independent adversarial review; distinguish the analytic proof from its formalized portion.
3. Compare primary literature, check strengthened v1.1 implementation interpretations against source data, preserve original artifacts, and leave a self-contained Japanese entry point.

## Boundary and evidence contract
New files only under v1_2; no publication, model inference, live RHL changes, or amendments of Claude's files. Counts are positive integers with observed support k>=2 and total n>=2. Threshold domain is 0<tau<1 unless endpoint cases are separately stated. Real logarithms/natural units for mathematics; rational threshold decisions by arbitrary-precision integers. Exact proof and finite tests are distinct. Existing source corpus remains retrospective. No statistical or quality conclusion.

G1 exploratory work; G2 mathematical proof/exact computation/source audit separately labeled; G3/G4 no population or subjective measurement; G5 no new performance study; G6 online primary-literature comparison, counterexamples to over-broad claims, independent review and negative controls.

## Conjecture and rejection condition
For every n>=2 the maximum mixed-window score 1-H/log(k) occurs at k=2 with counts (n-1,1). Reject on any valid histogram exceeding this binary score, any flaw in the proposed support-monotonicity proof, or a mismatched derivative/end condition. Finite search alone cannot discharge the universal statement.

## Proposed proof route (before full checks)
At fixed k, the envelope follows from concentration of counts. Extend its normalized minimum entropy to x in (1,n]: F_n(x)=[n log n-(n+1-x)log(n+1-x)]/[n log x]. Derivative sign reduces to a function D with endpoints zero and one turning point. Prove F strictly increasing, then optimize at k=2. Compute the smallest effective n for general tau using monotonic binary entropy and exact rational endpoint certificates.

## Scope of follow-up claims
Audit 'saturation fires earliest' (code permits d_R and loop at iteration2, saturation at3), exact-power applicability to hr_027, and tunability below the unanimity plateau. Any correction is recorded in this edition, not silently changed in v1.1. The representational impossibility demands a distinguishing observation; it does not logically demand exactly a fourth signal.
