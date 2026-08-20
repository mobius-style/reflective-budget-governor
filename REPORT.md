# RBG Pilot — REPORT (machine-generated)

- N tasks: 12
- Tokens A(fixed-cap)=73311  B(single)=54407  C(governor)=52369
- Reduction vs A: B=25.8%  C=28.6%
- Quality vs A (win/tie/loss): B=0/8/4  C=0/9/3
- C non-inferiority (win+tie >= 50%): True
- C beats B (reduction or quality): True
- C stop reasons: {'hard_cap': 7, 'equilibrium_d_r': 3, 'saturation': 2}
- Mean stop iter: B=6.67  C=6.58

## Pre-registered verdict: **WIN**
(criteria: C reduction >=15% AND C non-inferior AND C beats B)

## Per-task

| task | stopB | stopC | C reason | tokA | tokC | B_vs_A | C_vs_A |
|---|---|---|---|---|---|---|---|
| t01_product | 7 | 8 | hard_cap | 4836 | 4836 | loss | tie |
| t02_apology | 4 | 5 | equilibrium_d_r | 8084 | 4699 | tie | loss |
| t03_blog | 8 | 3 | saturation | 4513 | 1314 | tie | loss |
| t04_abstract | 8 | 8 | hard_cap | 4090 | 4090 | tie | tie |
| t05_minutes | 6 | 7 | equilibrium_d_r | 3061 | 2641 | tie | tie |
| t06_job | 5 | 3 | saturation | 15835 | 3875 | loss | loss |
| t07_press | 8 | 8 | hard_cap | 2460 | 2460 | tie | tie |
| t08_api | 8 | 8 | hard_cap | 7331 | 7331 | tie | tie |
| t09_speech | 6 | 5 | equilibrium_d_r | 4781 | 2803 | tie | tie |
| t10_review | 7 | 8 | hard_cap | 4189 | 4189 | loss | tie |
| t11_notice | 5 | 8 | hard_cap | 7883 | 7883 | loss | tie |
| t12_grant | 8 | 8 | hard_cap | 6248 | 6248 | tie | tie |
