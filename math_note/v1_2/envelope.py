#!/usr/bin/env python3
"""Exact window threshold design for observed-support normalized entropy.

The universal mathematical reduction to k=2 is proved in NOTE.md, not here.
All decisions use integer arithmetic; floats are display-only.
"""
import argparse
from fractions import Fraction
import json
import math


def envelope_fires(n, k, tau, max_bits=8_000_000):
    """Whether the extremal positive integer histogram at (n,k) meets S>=tau."""
    if type(n) is not int or type(k) is not int or not 2 <= k <= n:
        raise ValueError("require integers 2 <= k <= n")
    if not isinstance(tau, Fraction) or not 0 <= tau <= 1:
        raise ValueError("tau must be a Fraction in [0,1]")
    p, q = tau.numerator, tau.denominator
    r = n - k + 1
    # Upper bounds on bit length, checked before allocating large powers.
    bound = max(q*n*n.bit_length(), (q-p)*n*k.bit_length()+q*r*r.bit_length())
    if bound > max_bits:
        raise ValueError(f"exact arithmetic budget exceeded ({bound} > {max_bits} bits)")
    return n**(q*n) <= k**((q-p)*n) * r**(q*r)


def minimum_window(tau, max_n=100_000, max_bits=8_000_000):
    if not isinstance(tau, Fraction) or not 0 < tau < 1:
        raise ValueError("require a rational threshold strictly between 0 and 1")
    if type(max_n) is not int or max_n < 2:
        raise ValueError("max_n must be an integer >=2")
    def fires(n):
        return envelope_fires(n, 2, tau, max_bits)
    lo, hi = 2, 2
    while not fires(hi):
        lo = hi
        if hi == max_n:
            raise ValueError("minimum window exceeds max_n; no result certified")
        hi = min(2*hi, max_n)
    while hi-lo > 1:
        mid = (lo+hi)//2
        if fires(mid):
            hi = mid
        else:
            lo = mid
    assert not fires(hi-1) and fires(hi)
    return hi


def binary_score(n):
    p = 1/n
    return 1-(-p*math.log(p)-(1-p)*math.log1p(-p))/math.log(2)


def certificate(tau, **limits):
    n = minimum_window(tau, **limits)
    p, q = tau.numerator, tau.denominator
    return {"threshold":str(tau), "n_star":n,
            "previous_fires":envelope_fires(n-1,2,tau,limits.get("max_bits",8_000_000)),
            "first_fires":envelope_fires(n,2,tau,limits.get("max_bits",8_000_000)),
            "witness":[n-1,1], "display_scores":[binary_score(n-1),binary_score(n)],
            "exact_rule":f"n^({q}*n) <= 2^({q-p}*n)*(n-1)^({q}*(n-1))",
            "scope":"positive integer counts; observed support; S >= threshold"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("threshold", help="exact decimal or rational, e.g. 0.70 or 7/10")
    parser.add_argument("--max-n",type=int,default=100_000)
    parser.add_argument("--max-bits",type=int,default=8_000_000)
    args = parser.parse_args()
    try:
        result = certificate(Fraction(args.threshold),max_n=args.max_n,max_bits=args.max_bits)
    except (ValueError,ZeroDivisionError) as exc:
        parser.error(str(exc))
    print(json.dumps(result,indent=2))
