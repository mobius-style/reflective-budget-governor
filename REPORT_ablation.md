# RBG N500 — Ablation: saturation disabled

## Model 12b (saturation OFF)
- early stops: 185/500, reduction vs A: 10.8%
- quality vs A (win/tie/loss): 7/452/41
- loss rate: 8.2% [Wilson CI 6.1%,10.9%]

## Model 26b (saturation OFF)
- early stops: 206/500, reduction vs A: 12.0%
- quality vs A (win/tie/loss): 8/433/59
- loss rate: 11.8% [Wilson CI 9.3%,14.9%]

## Metric note (2026-08-20)

Reductions above are aggregate token ratios (sum tok_C / sum tok_A).
The paper's §5 table uses task-level mean reductions for consistency
with the registered headline metric: saturation-OFF task-mean
reduction = 10.0% (12B) / 11.5% (26B). Both are computable from
stops_nosat.json; the quality tallies are identical under either metric.
