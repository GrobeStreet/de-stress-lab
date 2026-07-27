# Frontier review of “Advancing Research to Frontier Standards”

## Status

Reviewed against the frozen numerical results at analysis commit
`28894e7ad3ae874506f6adf0059546a9b008c8f3`.

The supplied DOCX is a broad literature synthesis, not an independent replication
or a new dataset. It is useful for identifying future tests, but it cannot add
evidentiary weight to the stress-lab results by itself.

## Recommendation matrix

| DOCX theme or claim | Comparison with this project | Canonical treatment |
|---|---|---|
| LRG2 is highly influential | Supported by leave-one-out, full-CAMB, full-CMB, direct time-variation, and held-out tests | Retain, with the conditional selection calibration |
| The anomaly is specifically radial | Too strong. D_H has greater model leverage, but the held-out AP ratio is ordinary; the residual is mainly an isotropic distance-scale shift | Correct the distinction throughout |
| Fiber assignment or multiplet clustering caused LRG2 | Not tested by the compressed likelihood | Treat as a candidate mechanism requiring catalog-level and official-likelihood tests |
| The supernova offset proves calibration error | Not supported. The nuisance offset establishes degeneracy and loss of identifiability, not cause | Retain as a sensitivity/degeneracy result only |
| Constant w fits poorly, therefore time variation is established | Previously indirect | Superseded by the calibrated wCDM-versus-CPL test: 2.75σ full, 1.81σ without LRG2 |
| Gaussian-process reconstructions confirm the crossing | External and method-dependent; not reproduced here | Use only as a future robustness test with mock-calibrated coverage |
| Early dark energy resolves the Hubble tension | Outside this project’s late-time likelihood and not tested here | Exclude from the evidentiary conclusions |
| Interacting/decaying dark matter explains the result | A speculative theory class, not a finding from these data | Require joint background, growth, lensing, and Bayesian-evidence tests before discussion as an explanation |
| Modified gravity or future singularities follow | Not constrained by this analysis | Exclude from the canonical findings |

## Frontier gates adopted

1. Reconstruct the native LRG2 likelihood and its covariance orientation from
   official products.
2. Test survey splits and nuisance templates capable of isolating fiber assignment,
   reconstruction, redshift failures, observing conditions, and window-function
   effects.
3. Repeat flexible or nonparametric expansion reconstructions inside null mocks to
   calibrate feature selection and coverage.
4. Compute Bayesian evidence or predictive scores for ΛCDM, wCDM, CPL, and flexible
   alternatives under documented prior sensitivity.
5. Test the favored background histories against RSD, `fσ8`, weak lensing, and CMB
   lensing.
6. Replace the single supernova intercept with a hierarchical, survey-aware
   calibration and population model.
7. Obtain a human clean-room rerun before promoting the work beyond an independent
   computational stress test.

## Bottom line

The DOCX broadens the research agenda but does not strengthen the discovery claim.
Its most valuable effect is to sharpen the boundary between what this project has
measured and what remains speculative.
