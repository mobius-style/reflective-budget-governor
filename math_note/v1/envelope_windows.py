#!/usr/bin/env python3
"""Corollary check (v1.1): for every window length w <= 18, the observed-support
saturation score S = 1 - H/log k of ANY non-unanimous positive histogram is < 0.70,
so 'S >= 0.70' is equivalent to unanimity at those windows. Also reports the first
window admitting a non-unanimous breach (19, histogram 18:1) and, per Proposition E,
the envelope max over all k is attained at k=2 for every w in 2..25.
Exact integer certificate: S >= 7/10  <=>  n^(10n) <= k^(3n) * prod c_i^(10 c_i).
"""
import json, math, sys

def S(cs):
    n, k = sum(cs), len(cs)
    if k == 1: return 1.0
    H = -sum(c/n*math.log(c/n) for c in cs)
    return 1 - H/math.log(k)

def exact_breach(cs):
    n, k = sum(cs), len(cs)
    if k == 1: return True
    return n**(10*n) <= k**(3*n) * math.prod(c**(10*c) for c in cs)

rows, first = [], None
for n in range(2, 26):
    env = [(S([n-k+1] + [1]*(k-1)), k) for k in range(2, n+1)]
    best = max(env)
    # exact integer check of the envelope-maximizing histogram
    breach = exact_breach([n-best[1]+1] + [1]*(best[1]-1))
    rows.append({"window": n, "max_mixed_S": round(best[0], 9), "argmax_k": best[1],
                 "mixed_breach_at_0.70_exact": breach})
    if first is None and breach: first = n
unanimity_only = [r["window"] for r in rows if not r["mixed_breach_at_0.70_exact"]]
out = {"threshold": "7/10", "first_window_with_nonunanimous_breach": first,
       "unanimity_only_windows": unanimity_only, "rows": rows,
       "corollary": "for all windows 2..18, S>=0.70 iff unanimous (by Proposition E envelope + exact certificate)"}
assert first == 19 and unanimity_only == list(range(2, 19)), out
json.dump(out, open("results/envelope_windows.json", "w"), indent=1)
print("PASS: unanimity-only windows 2..18; first non-unanimous breach at", first)
