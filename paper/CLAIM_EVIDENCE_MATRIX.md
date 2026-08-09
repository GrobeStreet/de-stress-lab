# Scientific manuscript claim-to-evidence matrix

Status: reconciled on 2026-08-09. Run `python3 scripts/audit_manuscript_claims.py` before distributing any manuscript build.

| Manuscript claim | Canonical evidence | Audit status |
|---|---|---|
| Global DESI+cCMB CPL improvement is Δχ² = −8.4575 (displayed −8.5). | `results/max_influence_mocks.json`; `RESULTS_MANIFEST.json` | Machine-checked |
| LRG2 is the selected maximum-influence tracer, M = 4.1249. | `results/max_influence_mocks.json` | Machine-checked |
| Selected-null tail is 78/5,000, p = 0.0156. | `results/max_influence_mocks.json` | Machine-checked |
| Conditional localization is 34/70, p = 0.486. | `results/max_influence_mocks.json` | Machine-checked |
| Direct CPL time-variation statistic is 7.8506; 30/5,000, p = 0.0060. | `results/time_variation_mocks.json` | Machine-checked |
| Without LRG2 the direct statistic is 3.4263; 349/5,000, p = 0.0698. | `results/time_variation_no_lrg2_mocks.json` | Machine-checked |
| Held-out LRG2 joint p = 0.0408; D_V p = 0.0204; D_M/D_H p = 0.3744. | `results/lrg2_posterior_predictive.json` | Machine-checked |
| CAMB gives Δχ² = −8.28 and −4.14 with/without LRG2. | `results/camb_check.json` | Machine-checked |
| PR3-native full-CMB variant gives −10.35 and −3.76 with/without LRG2. | `results/lensing_leg_summary.json` | Machine-checked |
| DES5Y baseline is Δχ² = −7.3; the free low-z offset branch is −0.4 and D = +0.0375 mag under ΛCDM. | `results/des5y.json` | Machine-checked |
| Human clean-room verification is not complete. | `cleanroom/README.md`; `cleanroom/VERIFIER_WORKSHEET.md`; `RESULTS_MANIFEST.json` | Explicit caveat retained |
| This is a compressed-likelihood implementation, not a raw-data reanalysis. | `whitepaper.md`; versioned likelihood inputs and download records | Explicit scope retained |

## Reconciliation decision

The July 2026 DDM expansion was excluded from the scientific submission build because its cited `DDM_FRONTIER_GATE.md`, `cleanroom/run_ddm_gate.sh`, result JSONs, and CLASS patch were absent from the public repository and its numbers were absent from `RESULTS_MANIFEST.json`. The historical commit remains in Git. Those claims can return only after the full evidence chain is versioned, hashed, documented, and independently rerunnable.

## Open gates

- Independent human execution of the flagship and frontier clean-room protocols.
- Native-likelihood reconstruction of LRG2 or an explicit journal-scope limitation.
- Author-controlled confirmation of final name, affiliation wording, ORCID choice, and preprint license.
