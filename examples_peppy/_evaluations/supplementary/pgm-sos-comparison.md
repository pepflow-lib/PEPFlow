# Paired PGM comparison

All five preregistered pairs are retained. Differences are without supplied SOS minus with supplied SOS. Consumed cost is distinct from successful workflow completion time.

| Pair | With SOS | Without SOS | Consumed seconds difference | Tokens difference |
| --- | --- | --- | --- | --- |
| pgm_r01 | PASS | PASS | 790.5044140000005 | 3043661 |
| pgm_r02 | PASS | NOT_EVALUATED | 389.64248099999986 | 649416 |
| pgm_r03 | PASS | PASS | -603.482739 | -4414145 |
| pgm_r04 | PASS | PASS | 28.88326700000016 | 1494511 |
| pgm_r05 | PASS | PASS | 158.17090199999984 | 730559 |

## Block costs and visits

Each cell lists supplied-SOS / no-supplied-SOS observations. Unreached blocks are not fast successful completions. Null differences indicate unavailable comparable measurements.

| Pair | Block | Gates | Seconds | Seconds difference | Tokens difference | Visits |
| --- | --- | --- | --- | --- | --- | --- |
| pgm_r01 | B1 | PASS (reached=True) / PASS (reached=True) | 470.774844 / 508.97275 | 38.197906000000046 | 197708 | 1 / 1 |
| pgm_r01 | B2 | PASS (reached=True) / PASS (reached=True) | 733.7708230000001 / 761.5917919999999 | 27.820968999999877 | 184856 | 2 / 2 |
| pgm_r01 | B3 | PASS (reached=True) / PASS (reached=True) | 1029.1385930000001 / 1120.725131 | 91.58653799999979 | -1283125 | 3 / 4 |
| pgm_r01 | B4 | PASS (reached=True) / PASS (reached=True) | 593.4522790000001 / 615.055264 | 21.602984999999876 | -359404 | 2 / 3 |
| pgm_r01 | B5 | PASS (reached=True) / PASS (reached=True) | 872.298012 / 1483.594028 | 611.296016 | 4303626 | 1 / 2 |
| pgm_r02 | B1 | PASS (reached=True) / NOT_EVALUATED (reached=True) | 358.439878 / 405.69756 | 47.25768199999999 | 383280 | 1 / 1 |
| pgm_r02 | B2 | PASS (reached=True) / NOT_EVALUATED (reached=True) | 735.784615 / 641.244825 | -94.53979000000004 | 90140 | 2 / 2 |
| pgm_r02 | B3 | PASS (reached=True) / NOT_EVALUATED (reached=True) | 694.450834 / 631.904838 | -62.545995999999946 | -724571 | 4 / 2 |
| pgm_r02 | B4 | PASS (reached=True) / NOT_EVALUATED (reached=True) | 669.632241 / 392.319525 | -277.312716 | -2025892 | 3 / 1 |
| pgm_r02 | B5 | PASS (reached=True) / NOT_EVALUATED (reached=True) | 715.889472 / 1492.672773 | 776.783301 | 2926459 | 1 / 1 |
| pgm_r03 | B1 | PASS (reached=True) / PASS (reached=True) | 454.138352 / 371.310289 | -82.82806299999999 | -511243 | 1 / 1 |
| pgm_r03 | B2 | PASS (reached=True) / PASS (reached=True) | 770.2361960000001 / 507.829347 | -262.4068490000001 | -2335840 | 2 / 2 |
| pgm_r03 | B3 | PASS (reached=True) / PASS (reached=True) | 742.7022039999999 / 514.112819 | -228.589385 | -1854566 | 3 / 2 |
| pgm_r03 | B4 | PASS (reached=True) / PASS (reached=True) | 688.782188 / 451.132878 | -237.64931 | -2557264 | 2 / 1 |
| pgm_r03 | B5 | PASS (reached=True) / PASS (reached=True) | 925.513284 / 1133.504152 | 207.99086799999998 | 2844768 | 1 / 1 |
| pgm_r04 | B1 | PASS (reached=True) / PASS (reached=True) | 438.033381 / 439.591025 | 1.557643999999982 | 245684 | 1 / 1 |
| pgm_r04 | B2 | PASS (reached=True) / PASS (reached=True) | 832.92336 / 636.972895 | -195.950465 | -647596 | 3 / 2 |
| pgm_r04 | B3 | PASS (reached=True) / PASS (reached=True) | 729.3181910000001 / 544.424285 | -184.89390600000002 | -1035279 | 4 / 2 |
| pgm_r04 | B4 | PASS (reached=True) / PASS (reached=True) | 586.101906 / 506.147542 | -79.954364 | -628710 | 3 / 1 |
| pgm_r04 | B5 | PASS (reached=True) / PASS (reached=True) | 647.236614 / 1135.360972 | 488.1243579999999 | 3560412 | 1 / 1 |
| pgm_r05 | B1 | PASS (reached=True) / PASS (reached=True) | 333.775604 / 415.772453 | 81.996849 | 491900 | 1 / 1 |
| pgm_r05 | B2 | PASS (reached=True) / PASS (reached=True) | 732.726139 / 609.208714 | -123.517425 | 568183 | 2 / 2 |
| pgm_r05 | B3 | PASS (reached=True) / PASS (reached=True) | 878.384831 / 578.6091729999999 | -299.775658 | -913087 | 3 / 2 |
| pgm_r05 | B4 | PASS (reached=True) / PASS (reached=True) | 526.142411 / 437.336041 | -88.80637000000002 | -180705 | 2 / 1 |
| pgm_r05 | B5 | PASS (reached=True) / PASS (reached=True) | 1211.535627 / 1799.809133 | 588.273506 | 764268 | 1 / 1 |

pgm_with_sos: 5 mathematical PASS, 0 mathematical FAIL, 0 NOT_EVALUATED across 5 attempts. All costs remain recorded; incomplete delivery and historical access findings are separate.


pgm_without_sos: 4 mathematical PASS, 0 mathematical FAIL, 1 NOT_EVALUATED across 5 attempts. All costs remain recorded; incomplete delivery and historical access findings are separate.

Review costs, observed input/cached-input/output/reasoning components, reachability, and conditional successful-completion differences are recorded per pair in details.json. These five pairs support descriptive comparison, not a general reliability or speedup claim.
Completed-workflow comparison includes 4/5 pairs meeting both-side eligibility, mathematical PASS, completed status and workflow requirements.
