# Final integration review — 2026-09-19

Reviewed current NOTE.md, LITERATURE.md, PROTOCOL.md, verify.py, lean/Pilot.lean, source manifest and persisted results. Original sources unchanged. Only this review file is written by this integration pass.

## Verdict

The note accurately represents a local reproducible mathematical implementation pilot, with two concrete completion conditions below. It does not claim mathematical priority, full end-to-end formal verification, improved model quality, or causal effectiveness. No additional mathematical blocker was found. All numerical corpus and exhaustive-check claims reviewed match the persisted artifacts and a fresh independent read-only execution.

## Concrete unresolved items at review time

1. **MEDIUM — make the previous-state assumption explicit.** NOTE.md §5, line 107 currently says “For the actual weights, the ideal RBG distance obeys” after assuming only that seen history includes G_q(u). The displayed cosine is specifically between seed A and repeated set A union B. History inclusion bounds novelty, but does not constrain an arbitrary immediate predecessor. Amend to require immediately previous set G_q(u) for the displayed distance bound (or state a sufficient cosine bound). The following actual first-transition witness already satisfies this assumption. This is a local wording gap, not a failure of the intended lemma. Parent has announced the amendment; completion must be checked against the edited file.

2. **EVIDENCE PENDING — new Lean build and negative controls.** NOTE.md lines 23 and 170 assert current successful recompilation and reference results/lean.log and results/lean_checks.json. Both files were absent at review completion. Existing lean/Pilot.olean was older than current Pilot.lean; it cannot establish compilation of the current source. Earlier attempt logs exist but are not substitutes for the promised current-source success and invalid-mutant results. Parent is generating those results. Do not declare the Lean verification part complete until logs, toolchain identity, clean current-source compilation, T1 compilation, and rejection controls are persisted and checked. This is not classified as mathematical failure or a reason to expand scope.

No other unresolved severity finding.

## Verification performed

- Independently recomputed SHA-256 for every one of 14 captured source artifacts AND their original live paths; all match sources/manifest.json.
- Read persisted results/entropy.json, repetition.json, replay.json, verification.json. Counts, approximate values, threshold boundaries, histogram distributions, saturation reason counts, and hr_027 details agree with NOTE.md.
- Independently executed verify.py in a fresh Python process with only its `dump` sink replaced by an in-memory collector. This executes the exact same assertion paths without rewriting results. Current execution finished successfully and its newly generated in-memory verification status is PASS: 255 ordered positive compositions, 64 label triples, 10,160 repetition equalities, 1,000 real chains/8,000 generation rows, 14 source files with no drift. The script prints the pre-existing final JSON from disk; this review additionally asserted the newly collected in-memory PASS object, so the old printed timestamp is not used as fresh-run evidence.
- Read current Lean definitions and theorem statements. `repetition_stability` is a universal theorem about finite windows of a periodic Nat-indexed sequence. `compositions_complete` bridges the generator to every positive list of the specified sum. `exact_small_unanimity` is universal over all positive lists summing 1..8. The boundary theorems certify integer endpoint comparisons. The note correctly leaves logarithm/square-root algebra, monotonicity, and Python/normalization correspondence as prose/tested interfaces.
- No `sorry`, `admit`, added axioms or native_decide proof is present in the read Pilot.lean source. Its introductory comment merely names these prohibited constructs; text matching comments must not be mistaken for proof usage. Compilation/axiom output remains the pending item above.

## Scope and consistency assessment

PROTOCOL accurately calls the work exploratory and the checkpoint not preregistration. Its deferred quality/noise/contraction claims are not smuggled into the result. Replay on already available data establishes implementation consistency rather than held-out empirical confirmation. The note explicitly distinguishes saved stop/reason/token agreement from equality of numerical traces under Boolean saturation substitution.

The current mathematical proofs cover their stated domains. The sharp entropy envelope is fixed observed support, not fixed alphabet size; the counterexamples explain that difference. RHL's minimum history and default window are stated. The repetition theorem supplies a finite copy threshold rather than incorrect first-copy invariance. Full-policy collision accounts for raw length branch precedence, eight-step cap, and retrospective trace generation. Equal-set floating computations and exact-real mathematics are distinguished. No live runtime behavior or model quality is inferred from the synthetic witnesses.

LITERATURE is bounded and explicitly declines priority. It identifies established set-shingle multiplicity loss and Schur-concavity rather than asserting that the cited works contain the precise implementation corollaries. This integration pass did not independently reopen the web sources or verify search-history claims; it reviews the persisted comparison and its conservative use. Therefore it is internal mathematical/integration review, not independent bibliographic replication.

The original T1 overlap and live M-guard mismatch are handled correctly. The local theorem is not repackaged as new, the serialization check is not a descending-rank guarantee, and the existing T1 step/state comment discrepancy is preserved as a limitation rather than silently edited.

## Final release condition

After the explicit previous-set clause is present and the promised current Lean evidence exists and passes, GO for delivery as this scoped local pilot. No basis for a novelty-led mathematical publication, general semantic equilibrium guarantee, or detector effectiveness claim is established. No original source edits or further model generation are required for this completion.

## Resolution after rereading current files — 2026-09-19

Both original completion items are now CLOSED on persisted evidence:

1. NOTE.md line 107 explicitly states: “When the immediately preceding set is G_q(u) and the seen history contains it, the actual weights give the following ideal RBG distance bound”. This supplies exactly the missing assumption and agrees with the executable first-transition witness.
2. results/lean.log and results/lean_checks.json now exist. The recorded toolchain is Lean 4.32.2, commit f3b06c705e6c85f5314019d5d3baab0fec5b580c. The current run_all.py compiles into a newly created temporary directory rather than reusing the stale workspace .olean. Checks report Pilot returncode 0, fresh artifact 412,480 bytes, SHA-256 f44d0cd3758c2962e0f48e50022f72d6a39614af383d5d4423b0510cff026cc1; T1 returncode 0 and fresh artifact 146,456 bytes. Clean axiom output lists only propext and Quot.sound where needed, with no added axioms or forbidden proof commands.

The three persisted mutant logs were also read, rather than accepting only their summary names. Coverage weakening fails an omega proof (and downstream type check); a changed entropy threshold is refuted by decide; removal of the increment branch leaves the completeness proof with an impossible goal. The errors are mathematical/proof failures, not missing-tool or file-open errors. Expected sorryAx appearing in these FAILED mutant logs is not present in the successful original proof log.

**Updated verdict: GO for delivery as the scoped local mathematical implementation pilot. No unresolved mathematical or scientific-claim finding remains.** This does not confer novelty, full Python verification, quality improvement, or causal effectiveness.

### Separate orchestration observation

The run_all.py version read during resolution records review-file existence as flags but does not yet reject a missing review before writing status PASS. This does not invalidate the actual current review artifacts (all three exist), but is a future acceptance-check weakness. Parent has identified it and is adding a gate and known-missing-review negative control in a finalization path that reuses the already verified outputs. Verify that finalization reports the review control rejected before claiming the acceptance runner itself is complete. Recording a source SHA for Pilot.lean in reusable Lean checks is additionally recommended to bind future finalization to the compiled source. This observation requires no repeat of the corpus computation or mathematical work.
