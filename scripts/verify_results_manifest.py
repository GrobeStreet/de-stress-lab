#!/usr/bin/env python3
"""Verify canonical result hashes and flagship fields in RESULTS_MANIFEST.json."""

import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
manifest = json.load(open(PROJECT / "RESULTS_MANIFEST.json"))
errors = []

for relative, expected in manifest["sha256"].items():
    path = PROJECT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        errors.append(f"hash mismatch: {relative}: expected {expected}, got {actual}")

result = json.load(open(PROJECT / "results" / "max_influence_mocks.json"))
canonical = manifest["canonical_results"]["selection_calibrated_maximum_influence"]
checks = {
    "observed_selected_tracer": result["observed"]["selected_tracer"],
    "observed_max_influence": result["observed"]["max_influence"],
    "observed_dchi2_without_selected_tracer": result["observed"]["dchi2_deleted"][2],
    "n_mocks": result["summary"]["n_mocks"],
}
for key, actual in checks.items():
    if canonical[key] != actual:
        errors.append(f"field mismatch: {key}: manifest {canonical[key]!r}, result {actual!r}")

frontier_checks = []
time_variation = json.load(open(PROJECT / "results" / "time_variation_mocks.json"))
frontier_checks.extend(
    [
        (
            "direct_time_variation_full.observed_test_statistic",
            manifest["canonical_results"]["direct_time_variation_full"][
                "observed_test_statistic"
            ],
            time_variation["observed"]["test_statistic"],
        ),
        (
            "direct_time_variation_full.exceedances",
            manifest["canonical_results"]["direct_time_variation_full"][
                "exceedances"
            ],
            time_variation["summary"]["exceedances_ge_observed"],
        ),
    ]
)
time_variation_no_lrg2 = json.load(
    open(PROJECT / "results" / "time_variation_no_lrg2_mocks.json")
)
frontier_checks.extend(
    [
        (
            "direct_time_variation_without_lrg2.observed_test_statistic",
            manifest["canonical_results"]["direct_time_variation_without_lrg2"][
                "observed_test_statistic"
            ],
            time_variation_no_lrg2["observed"]["test_statistic"],
        ),
        (
            "direct_time_variation_without_lrg2.exceedances",
            manifest["canonical_results"]["direct_time_variation_without_lrg2"][
                "exceedances"
            ],
            time_variation_no_lrg2["summary"]["exceedances_ge_observed"],
        ),
    ]
)
lrg2 = json.load(open(PROJECT / "results" / "lrg2_posterior_predictive.json"))
frontier_checks.extend(
    [
        (
            "held_out_lrg2_prediction.joint_chi2",
            manifest["canonical_results"]["held_out_lrg2_prediction"]["joint_chi2"],
            lrg2["observed"]["chi2"],
        ),
        (
            "held_out_lrg2_prediction.joint_exceedances",
            manifest["canonical_results"]["held_out_lrg2_prediction"][
                "joint_exceedances"
            ],
            lrg2["summary"]["joint_chi2"]["exceedances_ge_observed"],
        ),
    ]
)
for key, expected, actual in frontier_checks:
    if expected != actual:
        errors.append(f"field mismatch: {key}: manifest {expected!r}, result {actual!r}")

if errors:
    raise SystemExit("\n".join(errors))
print(
    f"PASS: {len(manifest['sha256'])} hashes, {len(checks)} flagship fields, "
    f"and {len(frontier_checks)} frontier fields verified"
)
