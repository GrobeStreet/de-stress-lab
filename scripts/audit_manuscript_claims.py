#!/usr/bin/env python3
"""Fail closed when canonical manuscript claims drift from released evidence."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    return json.loads((ROOT / name).read_text())


def close(actual: float, expected: float, tolerance: float = 5e-5) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance)


def require(condition: bool, label: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        print(f"FAIL  {label}")
        failures.append(label)


def main() -> int:
    manuscript_path = ROOT / "whitepaper.md"
    manuscript = manuscript_path.read_text()
    manifest = load("RESULTS_MANIFEST.json")
    influence = load("results/max_influence_mocks.json")
    direct = load("results/time_variation_mocks.json")
    direct_no_lrg2 = load("results/time_variation_no_lrg2_mocks.json")
    held_out = load("results/lrg2_posterior_predictive.json")
    camb = load("results/camb_check.json")
    lensing = load("results/lensing_leg_summary.json")
    des5y = load("results/des5y.json")
    failures: list[str] = []

    digest = hashlib.sha256(manuscript_path.read_bytes()).hexdigest()
    require(
        digest == manifest["sha256"]["whitepaper.md"],
        "canonical Markdown hash matches RESULTS_MANIFEST.json",
        failures,
    )
    require(
        "run_ddm_gate.sh" not in manuscript and "dynamical-dark-matter gate" not in manuscript,
        "unversioned DDM gate claims are excluded",
        failures,
    )
    require(
        close(influence["observed"]["dchi2_full"], -8.457489554940723, 1e-12),
        "global compressed-likelihood statistic",
        failures,
    )
    require(
        influence["observed"]["selected_tracer"] == "LRG2 z=0.706"
        and close(influence["observed"]["max_influence"], 4.124942514489671, 1e-12),
        "selected tracer and maximum influence",
        failures,
    )
    summary = influence["summary"]
    require(
        summary["n_mocks"] == 5000
        and summary["exceedances_ge_observed"] == 78
        and close(summary["empirical_tail_probability"], 0.0156, 1e-12),
        "unconditional selected-null calibration",
        failures,
    )
    conditional = summary["conditional_on_global_preference_as_strong_or_stronger"]
    require(
        conditional["n_mocks"] == 70
        and conditional["exceedances_ge_observed"] == 34
        and close(conditional["empirical_tail_probability"], 34 / 70, 1e-12),
        "conditional localization calibration",
        failures,
    )
    require(
        close(direct["observed"]["test_statistic"], 7.85059006555734, 1e-12)
        and direct["summary"]["exceedances_ge_observed"] == 30
        and close(direct["summary"]["empirical_tail_probability"], 0.006, 1e-12),
        "direct CPL time-variation calibration",
        failures,
    )
    require(
        close(direct_no_lrg2["observed"]["test_statistic"], 3.4263244079039517, 1e-12)
        and direct_no_lrg2["summary"]["exceedances_ge_observed"] == 349
        and close(direct_no_lrg2["summary"]["empirical_tail_probability"], 0.0698, 1e-12),
        "direct time-variation calibration without LRG2",
        failures,
    )
    require(
        held_out["summary"]["joint_chi2"]["exceedances_ge_observed"] == 204
        and close(held_out["summary"]["joint_chi2"]["empirical_tail_probability"], 0.0408, 1e-12)
        and close(held_out["summary"]["absolute_dv_z"]["empirical_tail_probability"], 0.0204, 1e-12)
        and close(held_out["summary"]["absolute_ap_z"]["empirical_tail_probability"], 0.3744, 1e-12),
        "held-out LRG2 joint, isotropic, and shape diagnostics",
        failures,
    )
    require(
        close(camb["w0wa"]["chi2"] - camb["lcdm"]["chi2"], -8.28, 1e-9)
        and close(camb["w0wa_noLRG2"]["chi2"] - camb["lcdm_noLRG2"]["chi2"], -4.14, 1e-9),
        "full-Boltzmann verification",
        failures,
    )
    require(
        close(lensing["with_lrg2"]["dchi2"], -10.35, 1e-12)
        and close(lensing["without_lrg2"]["dchi2"], -3.76, 1e-12),
        "full-CMB lensing variant",
        failures,
    )
    require(
        close(des5y["A_DESI_DES5Y"]["dchi2"], -7.3, 1e-12)
        and close(des5y["B_intercept_test"]["dchi2"], -0.4, 1e-12)
        and close(des5y["B_intercept_test"]["D_lowz_mag_at_LCDM"], 0.0375, 1e-12),
        "DES5Y baseline and low-redshift-offset sensitivity",
        failures,
    )
    require(
        all(token in manuscript for token in ("not a raw-data reanalysis", "not independent scientific peer review", "clean-room human rerun remains")),
        "scope and independence caveats retained",
        failures,
    )
    require(
        all(token in manuscript for token in ("p = 0.0156", "p_cond = 0.486", "p = 0.0060", "p = 0.0698", "p = 0.0408")),
        "headline displayed values occur in the manuscript",
        failures,
    )

    if failures:
        print(f"\n{len(failures)} manuscript audit check(s) failed.")
        return 1
    print("\nAll canonical manuscript claim checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
