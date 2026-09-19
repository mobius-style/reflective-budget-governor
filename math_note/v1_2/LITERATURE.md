# Narrative prior-art check — 2026-09-19

Scope: exact normalized-entropy lower envelope for finite integer histograms, varying observed support, and detector threshold inversion. This is a targeted web/narrative comparison, not a systematic review or proof of absence. Search results were used for discovery; claims in NOTE.md use inspected primary PDFs.

Queries executed included:

- normalized Shannon entropy minimum empirical distribution support fixed sample size binary histogram
- Pielou evenness minimum sample size species richness entropy (N-S+1)
- "entropy" "log k" "n-k+1"
- "A simple formula for calculating the lower limit" Shannon author
- "Pielou" "minimum" "richness" "increases"
- "evenness" "minimum" "binary" entropy
- "normalized entropy" "minimum" "counts"
- Gosselin 2006 evenness minimum sample size Pielou lower limit
- "Pielou" "lower bound" "two"
- "minimum evenness" "richness"
- Beisel Moreteau 1997 lower limit Shannon pdf
- "S0304380097019546" pdf
- "Pielou" "lower limit" "ln"

## Closest primary source

Jean-Nicolas Beisel and Jean-Claude Moreteau (1997), *A simple formula for calculating the lower limit of Shannon’s diversity index*, Ecological Modelling 99, 289–292. DOI 10.1016/S0304-3800(97)01954-6. [Original author-hosted PDF](https://www.jnbeisel.net/uploads/5/4/4/2/54425847/ecomod_1997_beisel_%26_moreteau_shannon_index.pdf).

Section 2, equation (5), gives Hmin=log Q−(Q−S+1)log(Q−S+1)/Q for integer counts. This is exactly the fixed-k entropy expression used in the pilot. Pages 290 and 292 discuss its consequences for Pielou normalization. **Overlap: exact fixed-support formula and finite-count interpretation.** This material is prior art. The article does not state the all-support binary extremizer or the saturation-threshold inversion presented here; that observation about this article does not establish priority over the literature as a whole.

## Follow-up inspected

Beisel, Usseglio-Polatera, Bachmann and Moreteau (2003), *A Comparative Analysis of Evenness Index Sensitivity*, International Review of Hydrobiology 88(1), 3–15. [Original PDF](https://www.jnbeisel.net/uploads/5/4/4/2/54425847/irh_2003_beisel_et_al_evenness.pdf). Section 2.2 explicitly revisits finite-count minima in evenness measures. This reinforces that the normalization issue is established rather than a new general phenomenon.

Other search leads included Gosselin (2006), *An assessment of the dependence of evenness indices on species richness*, and a 2026 article *The Usefulness of Evenness*. They are not used to claim an exact match or a proof of novelty. Publisher access for the 1997 article failed, but the original PDF on the author's site was successfully inspected.

## Decision

GO for the additive technical note, sharp implementation-bound calculation, and reusable exact calculator. NO-GO for “first,” “new entropy inequality,” or a general mathematical priority claim. Generality has increased relative to Claude's finite-window extension; originality relative to all prior literature remains unestablished. Further publication positioning would require a wider specialist search/review and external assessment.
