#!/usr/bin/env python3
"""
Out-of-sample posterior-predictive diagnostic for DESI LRG2.

LambdaCDM is fit to DESI+cCMB after removing LRG2.  The held-out
(D_M/r_d, D_H/r_d) vector is then compared with the prediction after adding
both its published measurement covariance and a Laplace propagation of the
three fitted cosmological parameters.

The optional parametric bootstrap repeats the exclusion, fit, prediction,
and score under the fitted LambdaCDM null.  This is a targeted diagnostic:
the separate maximum-influence analysis is still required to account for
having selected LRG2 after inspecting all seven tracers.

Usage:
  python3 scripts/lrg2_posterior_predictive.py --mocks 5000 --workers 8
  python3 scripts/lrg2_posterior_predictive.py --mocks 20 --workers 1 \
      --fresh --output /tmp/lrg2-predictive-smoke.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import optimize, stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import max_influence_mocks as M


LRG2_INDEX = 2
LRG2_MH_INDEX = 1
SEED_START = 60_000


def measurement_covariance() -> np.ndarray:
    _, _, sigma_dm, _, sigma_dh, correlation = M.W.BAO_MH[LRG2_MH_INDEX]
    return np.array(
        [
            [sigma_dm**2, correlation * sigma_dm * sigma_dh],
            [correlation * sigma_dm * sigma_dh, sigma_dh**2],
        ]
    )


def fit_without_lrg2(dataset):
    result = optimize.least_squares(
        lambda values: M.residuals_dataset(
            values, -1.0, 0.0, dataset, LRG2_INDEX
        ),
        M.LCDM_START,
        bounds=M.LCDM_BOUNDS,
        xtol=1e-11,
        ftol=1e-11,
        gtol=1e-11,
        max_nfev=1200,
    )
    fisher = result.jac.T @ result.jac
    if np.linalg.matrix_rank(fisher) < fisher.shape[0]:
        raise RuntimeError("No-LRG2 parameter Fisher matrix is rank deficient")
    parameter_covariance = np.linalg.inv(fisher)
    return result, parameter_covariance


def predict_lrg2(parameters: np.ndarray) -> np.ndarray:
    om, h, wb = map(float, parameters)
    rd = M.W.rd_model(om, h, wb)
    grid = M.W.comoving_grid(om, h, -1.0, 0.0)
    z = M.W.BAO_MH[LRG2_MH_INDEX][0]
    dm = M.W.DM_Mpc(z, om, h, -1.0, 0.0, grid) / rd
    dh = (
        M.W.C_KMS
        / (100.0 * h * np.sqrt(M.W.Ez2_late(z, om, h, -1.0, 0.0)))
        / rd
    )
    return np.array([float(dm), float(dh)])


def prediction_jacobian(parameters: np.ndarray) -> np.ndarray:
    parameters = np.asarray(parameters, dtype=float)
    steps = np.array([1e-5, 1e-5, 1e-6])
    columns = []
    for index, step in enumerate(steps):
        shift = np.zeros_like(parameters)
        shift[index] = step
        columns.append(
            (predict_lrg2(parameters + shift) - predict_lrg2(parameters - shift))
            / (2.0 * step)
        )
    return np.column_stack(columns)


def _ratio_gradient(vector: np.ndarray) -> np.ndarray:
    dm, dh = map(float, vector)
    return np.array([1.0 / dh, -dm / dh**2])


def _volume_distance(vector: np.ndarray) -> float:
    redshift = float(M.W.BAO_MH[LRG2_MH_INDEX][0])
    dm, dh = map(float, vector)
    return float((redshift * dm * dm * dh) ** (1.0 / 3.0))


def _volume_distance_gradient(vector: np.ndarray) -> np.ndarray:
    dm, dh = map(float, vector)
    distance = _volume_distance(vector)
    return np.array([2.0 * distance / (3.0 * dm), distance / (3.0 * dh)])


def analyze_dataset(dataset) -> dict:
    fit, parameter_covariance = fit_without_lrg2(dataset)
    prediction = predict_lrg2(fit.x)
    jacobian = prediction_jacobian(fit.x)
    prediction_covariance = jacobian @ parameter_covariance @ jacobian.T
    observed = np.asarray(dataset[1][LRG2_MH_INDEX], dtype=float)
    data_covariance = measurement_covariance()
    total_covariance = data_covariance + prediction_covariance
    residual = observed - prediction
    statistic = float(residual @ np.linalg.solve(total_covariance, residual))
    p_value = float(stats.chi2.sf(statistic, 2))
    component_z = residual / np.sqrt(np.diag(total_covariance))

    observed_ratio = float(observed[0] / observed[1])
    predicted_ratio = float(prediction[0] / prediction[1])
    ratio_variance = float(
        _ratio_gradient(observed) @ data_covariance @ _ratio_gradient(observed)
        + _ratio_gradient(prediction)
        @ prediction_covariance
        @ _ratio_gradient(prediction)
    )
    ratio_z = float((observed_ratio - predicted_ratio) / np.sqrt(ratio_variance))
    observed_volume_distance = _volume_distance(observed)
    predicted_volume_distance = _volume_distance(prediction)
    volume_distance_variance = float(
        _volume_distance_gradient(observed)
        @ data_covariance
        @ _volume_distance_gradient(observed)
        + _volume_distance_gradient(prediction)
        @ prediction_covariance
        @ _volume_distance_gradient(prediction)
    )
    volume_distance_z = float(
        (observed_volume_distance - predicted_volume_distance)
        / np.sqrt(volume_distance_variance)
    )

    lower = np.asarray(M.LCDM_BOUNDS[0])
    upper = np.asarray(M.LCDM_BOUNDS[1])
    prior_margin = float(np.min(np.minimum(fit.x - lower, upper - fit.x)))
    return {
        "chi2": statistic,
        "degrees_of_freedom": 2,
        "analytic_chi2_tail_probability": p_value,
        "two_sided_gaussian_equivalent": float(stats.norm.isf(p_value / 2.0)),
        "fit_without_lrg2": {
            "parameters": {
                "Omega_m": float(fit.x[0]),
                "h": float(fit.x[1]),
                "omega_b": float(fit.x[2]),
            },
            "chi2": float(fit.fun @ fit.fun),
            "parameter_covariance_laplace": parameter_covariance.tolist(),
            "fisher_condition_number": float(
                np.linalg.cond(fit.jac.T @ fit.jac)
            ),
            "minimum_prior_margin": prior_margin,
            "near_prior_boundary": bool(prior_margin < 1e-4),
            "converged": bool(fit.success),
            "optimizer_message": str(fit.message),
        },
        "lrg2": {
            "observed": observed.tolist(),
            "prediction": prediction.tolist(),
            "residual": residual.tolist(),
            "component_z_using_marginal_total_errors": component_z.tolist(),
            "measurement_covariance": data_covariance.tolist(),
            "prediction_covariance_laplace": prediction_covariance.tolist(),
            "total_covariance": total_covariance.tolist(),
        },
        "alcock_paczynski_ratio": {
            "definition": "F_AP=(D_M/r_d)/(D_H/r_d)=D_M/D_H",
            "observed": observed_ratio,
            "prediction": predicted_ratio,
            "standard_deviation_delta_method": float(np.sqrt(ratio_variance)),
            "z_score": ratio_z,
            "two_sided_gaussian_p_value": float(2.0 * stats.norm.sf(abs(ratio_z))),
        },
        "isotropic_volume_distance": {
            "definition": "D_V/r_d=[z(D_M/r_d)^2(D_H/r_d)]^(1/3)",
            "observed": observed_volume_distance,
            "prediction": predicted_volume_distance,
            "standard_deviation_delta_method": float(
                np.sqrt(volume_distance_variance)
            ),
            "z_score": volume_distance_z,
            "two_sided_gaussian_p_value": float(
                2.0 * stats.norm.sf(abs(volume_distance_z))
            ),
        },
        "converged": bool(fit.success),
        "near_prior_boundary": bool(prior_margin < 1e-4),
    }


def _predictions(parameters: dict):
    om = float(parameters["Omega_m"])
    h = float(parameters["h"])
    wb = float(parameters["omega_b"])
    rd = M.W.rd_model(om, h, wb)
    grid = M.W.comoving_grid(om, h, -1.0, 0.0)
    z, _, sigma_dv = M.W.BAO_DV[0]
    dm = M.W.DM_Mpc(z, om, h, -1.0, 0.0, grid)
    dh = M.W.C_KMS / (100.0 * h * np.sqrt(M.W.Ez2_late(z, om, h, -1.0, 0.0)))
    dv = (z * dm * dm * dh) ** (1.0 / 3.0) / rd
    mh = []
    for z, _, _, _, _, _ in M.W.BAO_MH:
        dm = M.W.DM_Mpc(z, om, h, -1.0, 0.0, grid) / rd
        dh = (
            M.W.C_KMS
            / (100.0 * h * np.sqrt(M.W.Ez2_late(z, om, h, -1.0, 0.0)))
            / rd
        )
        mh.append((float(dm), float(dh)))
    cmb = np.array(
        [
            M.W.theta_star(om, h, -1.0, 0.0, wb),
            wb,
            om * h * h - M.W.OMEGA_NU_MASSIVE_H2,
        ]
    )
    return float(dv), float(sigma_dv), mh, cmb


def make_mock(seed: int, truth: dict):
    rng = np.random.default_rng(seed)
    prediction_dv, sigma_dv, prediction_mh, prediction_cmb = _predictions(truth)
    bao_dv = prediction_dv + sigma_dv * rng.standard_normal()
    mh = []
    for (dm_prediction, dh_prediction), (_, _, sm, _, sh, rho) in zip(
        prediction_mh, M.W.BAO_MH
    ):
        covariance = np.array(
            [[sm * sm, rho * sm * sh], [rho * sm * sh, sh * sh]]
        )
        noise = np.linalg.cholesky(covariance) @ rng.standard_normal(2)
        mh.append(
            (float(dm_prediction + noise[0]), float(dh_prediction + noise[1]))
        )
    cmb = prediction_cmb + M.CMB_CHOL @ rng.standard_normal(3)
    return float(bao_dv), mh, cmb


def analyze_task(task):
    seed, truth = task
    result = analyze_dataset(make_mock(seed, truth))
    return {
        "seed": int(seed),
        "chi2": result["chi2"],
        "ap_z_score": result["alcock_paczynski_ratio"]["z_score"],
        "dv_z_score": result["isotropic_volume_distance"]["z_score"],
        "converged": result["converged"],
        "near_prior_boundary": result["near_prior_boundary"],
    }


def summarize(observed: dict, records: list[dict]) -> dict:
    statistics = np.asarray([record["chi2"] for record in records])
    threshold = float(observed["chi2"])
    exceedances = int(np.count_nonzero(statistics >= threshold))
    n = len(records)
    ap_threshold = abs(float(observed["alcock_paczynski_ratio"]["z_score"]))
    ap_exceedances = int(
        np.count_nonzero(
            np.abs(np.asarray([record["ap_z_score"] for record in records]))
            >= ap_threshold
        )
    )
    dv_threshold = abs(float(observed["isotropic_volume_distance"]["z_score"]))
    dv_exceedances = int(
        np.count_nonzero(
            np.abs(np.asarray([record["dv_z_score"] for record in records]))
            >= dv_threshold
        )
    )
    return {
        "n_mocks": n,
        "joint_chi2": {
            "observed_threshold": threshold,
            "exceedances_ge_observed": exceedances,
            "empirical_tail_probability": (
                float(exceedances / n) if n else math.nan
            ),
            "plus_one_tail_probability": (
                float((exceedances + 1) / (n + 1)) if n else math.nan
            ),
            "clopper_pearson_95": M.clopper_pearson(exceedances, n),
            "empirical_two_sided_gaussian_sigma": (
                float(stats.norm.isf((exceedances / n) / 2.0))
                if n and exceedances
                else math.inf
            ),
        },
        "absolute_ap_z": {
            "observed_threshold": ap_threshold,
            "exceedances_ge_observed": ap_exceedances,
            "empirical_tail_probability": (
                float(ap_exceedances / n) if n else math.nan
            ),
            "plus_one_tail_probability": (
                float((ap_exceedances + 1) / (n + 1)) if n else math.nan
            ),
            "clopper_pearson_95": M.clopper_pearson(ap_exceedances, n),
        },
        "absolute_dv_z": {
            "observed_threshold": dv_threshold,
            "exceedances_ge_observed": dv_exceedances,
            "empirical_tail_probability": (
                float(dv_exceedances / n) if n else math.nan
            ),
            "plus_one_tail_probability": (
                float((dv_exceedances + 1) / (n + 1)) if n else math.nan
            ),
            "clopper_pearson_95": M.clopper_pearson(dv_exceedances, n),
        },
        "failed_optimizer_records": int(
            sum(not record["converged"] for record in records)
        ),
        "near_prior_boundary_records": int(
            sum(record["near_prior_boundary"] for record in records)
        ),
    }


def atomic_json_dump(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
        os.chmod(path, 0o644)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _payload(observed, truth, records):
    return {
        "schema_version": 1,
        "analysis": "held-out LRG2 posterior-predictive diagnostic",
        "method": (
            "Fit LambdaCDM to DESI+cCMB without LRG2; add Laplace-propagated "
            "parameter covariance to the published LRG2 measurement covariance"
        ),
        "scope": (
            "Targeted out-of-sample diagnostic. It does not replace the separate "
            "selection-calibrated maximum-influence test."
        ),
        "seed_start": SEED_START,
        "truth": truth,
        "observed": observed,
        "summary": summarize(observed, records),
        "mocks": records,
    }


def parse_args():
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mocks", type=int, default=5000)
    parser.add_argument(
        "--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1)
    )
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument(
        "--output",
        type=Path,
        default=project / "results" / "lrg2_posterior_predictive.json",
    )
    parser.add_argument("--fresh", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.mocks <= 0 or args.workers <= 0 or args.chunk_size <= 0:
        raise SystemExit("--mocks, --workers, and --chunk-size must be positive")
    started = time.monotonic()
    observed = analyze_dataset(M.observed_data())
    truth = observed["fit_without_lrg2"]["parameters"]
    payload = {}
    if args.output.exists() and not args.fresh:
        payload = json.load(open(args.output))
        if payload.get("truth") != truth:
            raise SystemExit("Existing output was generated under a different null truth; use --fresh")
    existing = payload.get("mocks", [])
    by_seed = {int(record["seed"]): record for record in existing}
    target_seeds = list(range(SEED_START, SEED_START + args.mocks))
    missing = [seed for seed in target_seeds if seed not in by_seed]
    print(
        f"observed chi2={observed['chi2']:.4f}, "
        f"AP z={observed['alcock_paczynski_ratio']['z_score']:.3f}, "
        f"DV z={observed['isotropic_volume_distance']['z_score']:.3f}; "
        f"existing={len(by_seed)}, missing={len(missing)}"
    )
    for offset in range(0, len(missing), args.chunk_size):
        seeds = missing[offset : offset + args.chunk_size]
        tasks = [(seed, truth) for seed in seeds]
        if args.workers == 1:
            completed = [analyze_task(task) for task in tasks]
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                completed = list(executor.map(analyze_task, tasks))
        by_seed.update({record["seed"]: record for record in completed})
        records = [by_seed[seed] for seed in target_seeds if seed in by_seed]
        payload = _payload(observed, truth, records)
        atomic_json_dump(payload, args.output)
        joint = payload["summary"]["joint_chi2"]
        print(
            f"{len(records):5d}/{args.mocks}: "
            f"k={joint['exceedances_ge_observed']} "
            f"p={joint['empirical_tail_probability']:.4f} "
            f"elapsed={time.monotonic() - started:.1f}s",
            flush=True,
        )
    records = [by_seed[seed] for seed in target_seeds if seed in by_seed]
    payload = _payload(observed, truth, records)
    atomic_json_dump(payload, args.output)
    print(json.dumps(payload["summary"], indent=2))
    print(f"saved -> {args.output}")


if __name__ == "__main__":
    main()
