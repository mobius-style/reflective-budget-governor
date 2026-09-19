# Independent final artifact review

Date: 2026-09-19. Reviewer: envelope_refuter, independent agent. Verdict: **PASS; no concrete blocker found**. Original bundle, implementation and runtime were not modified. New reviewer evidence is `final_checks.json`.

## Artifacts actually inspected

Read NOTE.md, LITERATURE.md, envelope.py, verify.py, lean/Envelope.lean, results/verification.json; compared source implications against pinned sources/analyze.py. Re-executed input hash verification and pure-function source audit, several exact calculator cases/cap boundaries, invalid CLI requests, and the actual Lean file. Theorem algebra and equality cases were previously independently derived in general_envelope.md.

## Mathematics

The fixed-k transfer argument, support-monotonicity derivative proof and unique binary equality characterization are correct. Endpoint n=2 is covered. Positive integer counts, observed support, and the separate unanimity convention are explicit. The inverse-binary-entropy branch and ceiling formula are correct for >=, and the separate strict inequality formula is correct. The asymptotic inversion follows from the displayed expansion. The note does not claim an elementary inverse formula or a universal Lean proof.

The integer inequality in envelope_fires follows from n log n-r log r <= n(1-p/q)log k after multiplication by q; its direction and exponents are correct. n*=19 at .7 follows from the universal result and exact adjacent checks.

## Calculator and resource behavior

Independent exact outputs: tau=1/100 ->3; 1/3 ->6; 7/10 ->19; 9/10 ->78. For every case, setting max_n to the returned n succeeds, while max_n=n-1 fails explicitly. Invalid CLI values 0, 1, -1, 2, junk, and a very high-denominator near-one decimal were rejected with code 2. The latter rejects under the integer-arithmetic budget rather than allocating enormous powers.

Power bit-length upper bounds are conservative and checked before exponentiation. Doubling/bisection decisions are exact and the adjacent certificate is rechecked. A conservative resource failure is permissible even when a tighter search might fit; no uncertified numeric answer is returned. Float calculations appear only in display_scores. No runtime inference or network path was invoked by this review.

## Verification scope and source implications

All nine input hashes reverified. The independently rerun pure-function audit reproduces equilibrium at iteration 2 for constant strings and loop at iteration 2 for alternating strings. The pinned source explicitly permits saturation only after three change labels and checks equilibrium then loop then saturation. Thus removing the earlier 'earliest signal' causal interpretation is warranted.

The hr_027 reread reproduces raw lengths 899/45152, normalized lengths 763/38177, old trigram count 589, added 5, removed 0. The second normalized length is not a multiple of the first, excluding a literal power. Novelty against the complete seed-plus-previous history is also exactly 5/594, matching the note's computation. The b<=2 pure-power result cannot directly certify this event. The revised nested-set argument and retrospective single-case qualification are correct.

Lean 4.32.2 was actually rerun: all_153_small_envelopes, binary_18_below, and binary_19_above each report no axioms. The list bounds genuinely enumerate n=2..18 and k=2..n, totaling 153. This certifies finite integer facts; the logarithmic bridge and universal analytic proof remain prose, as disclosed. The stored verifier's 45,675 floating crosschecks and symbolic identities are characterized correctly as diagnostic checks rather than universal proofs.

## Prior work and attribution

Claude's v1.1 is correctly attributed. LITERATURE.md explicitly identifies the fixed-support minimum as prior art, supplies primary links, and avoids a priority claim. This reviewer did not independently reopen those external PDFs in this final pass; source coverage is the parent's recorded literature audit, not an independent full bibliography review.

## Nonblocking wording improvements

1. Introductory 'exceed a chosen saturation threshold' is colloquial where the operational rule is >=; 'meet or exceed' would remove ambiguity.
2. The quoted identity 'saturation = three identical non-rewrite labels' should preferably read 'saturation stopping condition = ...'. In pinned code, saturation(types) itself equals 1 for three rewrites too, and the separate dominant-type guard suppresses stopping. Subsequent surrounding text is enough to reconstruct the intended claim, so this is precision rather than a mathematical blocker.

No speculative expansion is required for acceptance. New generality is real, while mathematical priority and behavior improvement are unestablished and correctly left unclaimed.
