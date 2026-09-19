# Prior-art check and novelty decision

Search date: 2026-09-19 UTC/JST. Two passes: broad antecedents before finalizing propositions, then targeted overlap after identifying the actual small-window and repetition mechanisms. This is a bounded web search, not a systematic review or an absence proof.

## Searches actually issued

Pass 1: `entropy minimum fixed maximum probability distribution Harremoes Topsoe`; `shingling set representation document resemblance Broder 1997`; `site:github.com/mobius-style reflective-budget-governor`; `"On the resemblance and containment of documents" Broder pdf`; `"entropy" "maximum probability" "tight" bounds`; `"normalized entropy" "sample size" "observed" diversity`; `Sason tight bounds Renyi entropy majorization 2018 arxiv`; `Broder resemblance containment documents research google 1997`.

Pass 2: `"entropy" "unanimity" "window"`; `"normalized entropy" "integer" "minimum"`; `"n-gram" "repetition" "set" "invariant"`; `"reflective budget governor"`. Exact-name search had weak indexing; opening the known primary repository directly succeeded. An attempted Stanford textbook PDF open failed; no claim relies on that failed fetch.

## Primary sources opened and inspected

1. Andrei Z. Broder (1997), *On the resemblance and containment of documents*, DOI 10.1109/SEQUEN.1997.666900. [Original paper PDF, hosted mirror](https://skeptric.com/resources/broder97resemblance.pdf), §2, PDF pp.2–3. It explicitly distinguishes occurrence-labelled shingles (Option A) from unique shingles (Option B). Multiplicity loss in a set representation is therefore old prior art. Our copy-count bound and current RBG branch analysis specialize that basic fact; they are not grounds for claiming a new general information-loss theorem.
2. Broder, Glassman, Manasse, Zweig (1997), *Syntactic Clustering of the Web*, SRC Technical Note 1997-015. [Original institutional PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/1997/01/src-tn-1997-015.pdf), “Defining similarity,” PDF p.4. It defines unique contiguous shingles. This is corroborating foundational context, not a paper about RBG or adaptive stopping.
3. Igal Sason (2018), *Tight Bounds on the Rényi Entropy via Majorization with Applications to Guessing and Compression*, Entropy 20(12), 896. [Full paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7512480/), Proposition 1; [author abstract](https://arxiv.org/abs/1812.03324). Shannon entropy is Schur-concave. Thus our extremal positive-integer histogram is a standard concentration/majorization argument. This paper studies different constraints, so it is not asserted to contain the exact RBG finite-window corollary.
4. Stan `posterior`, [official normalized-entropy documentation](https://mc-stan.org/posterior/reference/entropy.html). Numeric samples normalize by the number of distinct observed values, whereas factors can use declared levels. This directly supports why fixed alphabet size and observed support must not be interchanged. The normalized entropy definition is established, not invented here.
5. Toeda, *Reflective Budget Governor*, [primary repository](https://github.com/mobius-style/reflective-budget-governor). Its README routes canonical stopping definitions to `analyze.py`, and identifies the existing study. All calculations in this pilot use hashed local source snapshots and raw data, not README performance summaries. Public checkout equality is recorded separately in `sources/manifest.json`; no remote-head byte-identity claim is made.
6. Existing portfolio T1, local `sources/T1.lean`, theorem2 and prop1. Well-founded descent and the failure of a step-local guard already exist here. Recompiled in this pilot; not a new contribution.

## Decision

**GO** for a reproducible local mathematical implementation note: sharp count-domain envelope, exact .70 threshold interpretation, periodic feature collision, source correspondence and full-corpus policy replay.

**NO-GO** for advertising a newly discovered general mathematical theorem or submitting a stand-alone novelty-led mathematics paper on current evidence. No search establishes priority. The worthwhile project-specific addition is the exact characterization of what these deployed formulas can and cannot observe. RBG's original paper already reports the qualitative repetition failure; our work formalizes and bounds it.

Closest objections: (i) elementary/known mathematics; (ii) synthetic feature collisions are not quality measurements. Both are accepted scope limits, not claims to be refuted away.
