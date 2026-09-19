# math_note — what the deployed saturation / similarity signals actually compute

Companion bundle for the note *Unanimity in Disguise: What an Observed-Support
Entropy Threshold Actually Detects at Short Windows* https://doi.org/10.5281/zenodo.22842506

- `v1/` — pilot: exact unanimity for windows n ≤ 8 (Lean), repetition
  stabilization and boundary bounds, full-corpus replay, Claude v1.1 brush-up
  with the window-range corollary (`envelope_windows.py`).
- `v1_2/` — general theorem (all-support envelope maximized at (n−1,1)),
  threshold-to-window rule `n*(τ)`, exact integer certificates
  (`envelope.py <τ>`), Lean finite certificates, adversarial refutation review.

Source snapshots hashed in `v1/sources_manifest.json` are the RBG study files
published in this repository's root (analyze.py, stops_*.json, rollouts_*.jsonl)
plus the RHL detector transcription; they are not duplicated here.

## Which scripts are portable

- **Portable (standard library, run anywhere):** `v1_2/envelope.py <τ>` (exact
  integer certificate for any rational threshold), `v1/envelope_windows.py`
  (window-range corollary), `v1_2/k2_dominance_check.py` (numeric corroboration
  of the cross-support step, n ≤ 400, and monotonicity of M(n), n ≤ 2000).
  The Lean sources compile with Lean 4.32.2 core (no Mathlib).
- **Archival (bound to the original pinned snapshot):** `v1/verify.py`,
  `v1/run_all.py` and `v1_2/verify.py` recheck SHA-256 hashes of absolute local
  paths and expect a `sources/` directory that is not duplicated here (the
  underlying data files are the RBG study files in this repository's root).
  They are published as the exact record of what was executed, with their
  outputs in `results/`; they are not expected to run unmodified elsewhere.
