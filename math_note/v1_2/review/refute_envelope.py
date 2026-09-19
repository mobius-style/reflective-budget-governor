import json, math
from pathlib import Path

def partitions(n, lower=1):
    if n == 0:
        yield ()
    for first in range(lower, n + 1):
        for rest in partitions(n - first, first):
            yield (first,) + rest

def score(parts):
    n, k = sum(parts), len(parts)
    return 1 - (math.log(n) - sum(a * math.log(a) for a in parts)/n)/math.log(k)

count = 0
violations = []
nonunique = []
for n in range(2, 36):
    binary = score((1, n-1))
    for p in partitions(n):
        if len(p) < 2:
            continue
        count += 1
        s = score(p)
        if s > binary + 1e-12:
            violations.append([n, p, s, binary])
        if abs(s-binary) < 1e-12 and p != (1,n-1):
            nonunique.append([n,p])

# Exact integer certificates, not floating logarithm comparisons.
cert18 = 18**180 > 17**170 * 2**54
cert19 = 19**190 < 18**180 * 2**57
# Known-broken nearby claim: all n<=19 only unanimity at tau .7.
negative_control = cert19
# Real-valued frequencies fail a universal integer-window bound.
real_counterexample_score = score((0.1, 9.9))
result = {
    'partition_range':[2,35], 'histograms_checked':count,
    'floating_comparison_tolerance':1e-12,
    'violations':violations, 'extra_equality_cases':nonunique,
    'exact_certificate_n18_below_0_7':cert18,
    'exact_certificate_n19_above_0_7':cert19,
    'negative_control_n19_unanimity_claim_rejected':negative_control,
    'scores_n18_n19':[score((1,17)),score((1,18))],
    'noninteger_boundary_counterexample':{
        'counts':[0.1,9.9],'sum':10,'score':real_counterexample_score,
        'integer_n10_max':score((1,9))},
    'status':'PASS' if not violations and not nonunique and cert18 and cert19 else 'FAIL',
    'scope':'Independent finite floating corroboration plus two exact integer threshold certificates; not a proof of the all-n theorem.'
}
Path(__file__).with_name('refute_envelope.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
