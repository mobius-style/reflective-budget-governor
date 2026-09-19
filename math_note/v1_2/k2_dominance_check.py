#!/usr/bin/env python3
"""Numeric corroboration (not proof) of Theorem 1's cross-support step and of
Corollary 2's monotonicity: for every n in 2..400 the fixed-support minimum
normalized entropy F_n(k) is strictly smallest at k=2 (so S is maximized at
(n-1,1)); and M(n)=1-h(1/n)/log 2 is strictly increasing for n in 2..2000.
Portable: Python standard library only. Writes results/k2_dominance.json."""
import json, math

def Fmin(n, k):
    r = n - k + 1
    return (n*math.log(n) - r*math.log(r)) / (n*math.log(k))

def M(n):
    p = 1/n
    return 1 - (-p*math.log(p) - (1-p)*math.log1p(-p)) / math.log(2)

violations = [(n, k) for n in range(3, 401) for k in range(3, n+1)
              if Fmin(n, k) <= Fmin(n, 2) + 1e-12]
mono_ok = all(M(n+1) > M(n) for n in range(2, 2000))
out = {"k2_dominance_n_range": [3, 400], "k2_violations": violations,
       "M_strictly_increasing_n_range": [2, 2000], "M_monotone": mono_ok,
       "status": "PASS" if (not violations and mono_ok) else "FAIL",
       "note": "floating corroboration at 1e-12 slack; the universal proof is in NOTE.md"}
json.dump(out, open("results/k2_dominance.json", "w"), indent=1)
print(out["status"], "violations:", len(violations), "M monotone:", mono_ok)
