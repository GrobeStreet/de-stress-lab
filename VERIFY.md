# Independent verifier wanted

`de-stress-lab` is seeking a human verifier who was not involved in developing this repository.

This is a request for **independent execution and defect reporting**, not endorsement of the cosmological interpretation.

## Fast path: install and smoke-test the released software

Start with [Issue #21](https://github.com/GrobeStreet/de-stress-lab/issues/21). It contains the exact clone/install/test commands and asks you to report operating system, Python version, tag/commit, pass/fail status, and any undocumented intervention.

## Full path: blinded scientific rerun

Follow [`cleanroom/README.md`](cleanroom/README.md) and fill in [`cleanroom/VERIFIER_WORKSHEET.md`](cleanroom/VERIFIER_WORKSHEET.md) before viewing the expected numerical results.

The full protocol includes a deterministic smoke test, the 5,000-mock maximum-influence calibration, direct time-variation calibrations with and without LRG2, held-out LRG2 diagnostics, output hashes, and explicit acceptance criteria.

## What counts

A useful verification can be as small as a clean install plus tests, or as deep as the full blinded rerun. Failures are useful evidence. Please report errors and deviations rather than silently repairing them.

Public verification requests:

- [Issue #21 — independent install / clean-room verification](https://github.com/GrobeStreet/de-stress-lab/issues/21)
- [Issue #13 — complete an independent clean-room reproduction](https://github.com/GrobeStreet/de-stress-lab/issues/13)

The project currently has no second-person human verification record.
