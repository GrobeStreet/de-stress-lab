#!/usr/bin/env python3
"""
Direct, empirically calibrated test of time variation in the CPL model.

The existing headline comparison asks whether w0waCDM improves on LambdaCDM
with two extra parameters.  That is not the direct test of time variation.
Here the null is constant-w CDM and the alternative adds only wa:

    T = chi2_min(wCDM) - chi2_min(w0waCDM).

The observed statistic is calibrated with parametric mocks generated at the
observed best-fit constant-w model.  Both fits use the DESI compressed-CMB
likelihood and the DESI prior domain

    -3 < w0 < 1, -3 < wa < 2, w0 + wa < 0.

The nonlinear early-matter condition is enforced by a smooth transformation,
so every optimizer iterate remains inside the allowed domain.

Usage:
  python3 scripts/time_variation_mocks.py --mocks 5000 --workers 8
  python3 scripts/time_variation_mocks.py --mocks 20 --workers 1 --fresh \
      --output /tmp/time-variation-smoke.json
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
from scipy import optimize, special, stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import max_influence_mocks as M


SEED_START = 40_000
W0_BOUNDS = (-2.999999, -0.000001)
WA_BOUNDS = (-2.999999, 1.999999)
Q_BOUNDS = (-14.0, 14.0)
BASE_LOWER = np.asarray(M.LCDM_BOUNDS[0], dtype=float)
BASE_UPPER = np.asarray(M.LCDM_BOUNDS[1], dtype=float)
CONSTANT_LOWER = np.concatenate([BASE_LOWER, [W0_BOUNDS[0]]])
CONSTANT_UPPER = np.concatenate([BASE_UPPER, [W0_BOUNDS[1]]])
EVOLVING_LOWER = np.concatenate([BASE_LOWER, [W0_BOUNDS[0], Q_BOUNDS[0]]])
EVOLVING_UPPER = np.concatenate([BASE_UPPER, [0.999999, Q_BOUNDS[1]]])


def wa_from_coordinate(w0: float, coordinate: float) -> float:
    """Map an unconstrained coordinate into the official wa/early-matter domain."""
    upper = min(WA_BOUNDS[1], -float(w0) - 1e-9)
    fraction = float(special.expit(coordinate))
    return float(WA_BOUNDS[0] + fraction * (upper - WA_BOUNDS[0]))


def coordinate_from_wa(w0: float, wa: float) -> float:
    """Inverse of wa_from_coordinate, clipped away from infinite endpoints."""
    upper = min(WA_BOUNDS[1], -float(w0) - 1e-9)
    fraction = (float(wa) - WA_BOUNDS[0]) / (upper - WA_BOUNDS[0])
    fraction = float(np.clip(fraction, 1e-7, 1.0 - 1e-7))
    return float(special.logit(fraction))


def _constant_residuals(
    parameters: np.ndarray, dataset, drop: int | None = None
) -> np.ndarray:
    return M.residuals_dataset(
        parameters[:3], float(parameters[3]), 0.0, dataset, drop
    )


def _evolving_residuals(
    parameters: np.ndarray, dataset, drop: int | None = None
) -> np.ndarray:
    w0 = float(parameters[3])
    wa = wa_from_coordinate(w0, float(parameters[4]))
    return M.residuals_dataset(parameters[:3], w0, wa, dataset, drop)


def fit_constant_w(
    dataset, start: np.ndarray | None = None, drop: int | None = None
):
    start = np.asarray(
        start if start is not None else [0.30, 0.68, 0.0222, -1.0], dtype=float
    )
    return optimize.least_squares(
        lambda values: _constant_residuals(values, dataset, drop),
        start,
        bounds=(CONSTANT_LOWER, CONSTANT_UPPER),
        xtol=1e-10,
        ftol=1e-10,
        gtol=1e-10,
        max_nfev=1200,
    )


def fit_evolving_w(dataset, constant_fit=None, drop: int | None = None):
    if constant_fit is None:
        constant_fit = fit_constant_w(dataset, drop=drop)
    constant = np.asarray(constant_fit.x, dtype=float)
    starts = [
        np.concatenate(
            [constant[:4], [coordinate_from_wa(float(constant[3]), 0.0)]]
        ),
        np.array(
            [
                0.35,
                0.64,
                0.0222,
                -0.45,
                coordinate_from_wa(-0.45, -1.7),
            ]
        ),
    ]
    candidates = [
        optimize.least_squares(
            lambda values: _evolving_residuals(values, dataset, drop),
            start,
            bounds=(EVOLVING_LOWER, EVOLVING_UPPER),
            xtol=1e-10,
            ftol=1e-10,
            gtol=1e-10,
            max_nfev=1600,
        )
        for start in starts
    ]
    return min(candidates, key=lambda result: float(result.fun @ result.fun))


def _fit_summary(result, model: str) -> dict:
    chi2 = float(result.fun @ result.fun)
    values = np.asarray(result.x, dtype=float)
    parameters = {
        "Omega_m": float(values[0]),
        "h": float(values[1]),
        "omega_b": float(values[2]),
        "w0": float(values[3]),
        "wa": 0.0,
    }
    transformed_coordinate = None
    if model == "w0waCDM":
        transformed_coordinate = float(values[4])
        parameters["wa"] = wa_from_coordinate(float(values[3]), transformed_coordinate)
    margin = min(
        parameters["w0"] - (-3.0),
        1.0 - parameters["w0"],
        parameters["wa"] - (-3.0),
        2.0 - parameters["wa"],
        -(parameters["w0"] + parameters["wa"]),
    )
    return {
        "model": model,
        "chi2": chi2,
        "parameters": parameters,
        "transformed_wa_coordinate": transformed_coordinate,
        "minimum_prior_margin": float(margin),
        "near_prior_boundary": bool(
            margin < 1e-4
            or (
                transformed_coordinate is not None
                and abs(transformed_coordinate) > Q_BOUNDS[1] - 0.1
            )
        ),
        "converged": bool(result.success),
        "optimizer_status": int(result.status),
        "optimizer_message": str(result.message),
        "n_function_evaluations": int(result.nfev),
    }


def analyze_dataset(dataset, drop: int | None = None) -> dict:
    constant_fit = fit_constant_w(dataset, drop=drop)
    evolving_fit = fit_evolving_w(dataset, constant_fit, drop=drop)
    constant = _fit_summary(constant_fit, "wCDM")
    evolving = _fit_summary(evolving_fit, "w0waCDM")
    statistic = max(0.0, constant["chi2"] - evolving["chi2"])
    return {
        "test_statistic": float(statistic),
        "constant_w": constant,
        "evolving_w": evolving,
        "converged": bool(constant["converged"] and evolving["converged"]),
        "near_prior_boundary": bool(
            constant["near_prior_boundary"] or evolving["near_prior_boundary"]
        ),
        "dropped_tracer_index": drop,
        "dropped_tracer": M.TRACER_NAMES[drop] if drop is not None else None,
    }


def _predictions(parameters: dict) -> tuple[float, list[tuple[float, float]], np.ndarray]:
    om = float(parameters["Omega_m"])
    h = float(parameters["h"])
    wb = float(parameters["omega_b"])
    w0 = float(parameters["w0"])
    wa = 0.0
    rd = M.W.rd_model(om, h, wb)
    grid = M.W.comoving_grid(om, h, w0, wa)
    z, _, _ = M.W.BAO_DV[0]
    dm = M.W.DM_Mpc(z, om, h, w0, wa, grid)
    dh = M.W.C_KMS / (100.0 * h * np.sqrt(M.W.Ez2_late(z, om, h, w0, wa)))
    dv = (z * dm * dm * dh) ** (1.0 / 3.0) / rd
    mh = []
    for z, _, _, _, _, _ in M.W.BAO_MH:
        dm = M.W.DM_Mpc(z, om, h, w0, wa, grid) / rd
        dh = (
            M.W.C_KMS
            / (100.0 * h * np.sqrt(M.W.Ez2_late(z, om, h, w0, wa)))
            / rd
        )
        mh.append((float(dm), float(dh)))
    cmb = np.array(
        [
            M.W.theta_star(om, h, w0, wa, wb),
            wb,
            om * h * h - M.W.OMEGA_NU_MASSIVE_H2,
        ]
    )
    return float(dv), mh, cmb


def make_mock(seed: int, truth: dict):
    rng = np.random.default_rng(seed)
    prediction_dv, prediction_mh, prediction_cmb = _predictions(truth)
    bao_dv = prediction_dv + rng.standard_normal() * M.W.BAO_DV[0][2]
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
    seed, truth, drop = task
    result = analyze_dataset(make_mock(seed, truth), drop=drop)
    result["seed"] = int(seed)
    return result


def clopper_pearson(successes: int, trials: int, alpha: float = 0.05) -> list[float]:
    return M.clopper_pearson(successes, trials, alpha)


def summarize(observed: dict, records: list[dict]) -> dict:
    threshold = float(observed["test_statistic"])
    statistics = np.asarray([record["test_statistic"] for record in records])
    exceedances = int(np.count_nonzero(statistics >= threshold))
    n = len(records)
    wilks_p = float(stats.chi2.sf(threshold, 1))
    return {
        "n_mocks": n,
        "observed_threshold": threshold,
        "exceedances_ge_observed": exceedances,
        "empirical_tail_probability": float(exceedances / n) if n else math.nan,
        "plus_one_tail_probability": (
            float((exceedances + 1) / (n + 1)) if n else math.nan
        ),
        "clopper_pearson_95": clopper_pearson(exceedances, n),
        "wilks_chi2_1_tail_probability": wilks_p,
        "wilks_two_sided_gaussian_sigma": float(stats.norm.isf(wilks_p / 2.0)),
        "empirical_two_sided_gaussian_sigma": (
            float(stats.norm.isf((exceedances / n) / 2.0))
            if n and exceedances
            else math.inf
        ),
        "test_statistic_quantiles": {
            str(q): float(np.quantile(statistics, q)) if n else math.nan
            for q in (0.5, 0.68, 0.9, 0.95, 0.99, 0.995)
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


def parse_args():
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mocks", type=int, default=5000)
    parser.add_argument(
        "--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1)
    )
    parser.add_argument("--chunk-size", type=int, default=25)
    parser.add_argument(
        "--drop-index",
        type=int,
        choices=range(7),
        help="Optional DESI tracer index to omit in both the observed and mock fits.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project / "results" / "time_variation_mocks.json",
    )
    parser.add_argument("--fresh", action="store_true")
    return parser.parse_args()


def _payload(observed, truth, records, drop):
    return {
        "schema_version": 1,
        "analysis": "direct constant-w versus CPL time-variation likelihood-ratio calibration",
        "statistic": "T=chi2_min(wCDM)-chi2_min(w0waCDM)",
        "null": "parametric mocks at the observed best-fit constant-w model",
        "prior_domain": {
            "w0": [-3.0, 1.0],
            "wa": [-3.0, 2.0],
            "early_matter_condition": "w0+wa<0",
        },
        "seed_start": SEED_START,
        "dropped_tracer_index": drop,
        "dropped_tracer": M.TRACER_NAMES[drop] if drop is not None else None,
        "truth": truth,
        "observed": observed,
        "summary": summarize(observed, records),
        "mocks": records,
    }


def main():
    args = parse_args()
    if args.mocks <= 0 or args.workers <= 0 or args.chunk_size <= 0:
        raise SystemExit("--mocks, --workers, and --chunk-size must be positive")
    started = time.monotonic()
    observed = analyze_dataset(M.observed_data(), drop=args.drop_index)
    truth = observed["constant_w"]["parameters"]
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
        f"observed T={observed['test_statistic']:.4f}; "
        f"wCDM w={truth['w0']:.4f}; existing={len(by_seed)}, missing={len(missing)}"
    )
    for offset in range(0, len(missing), args.chunk_size):
        seeds = missing[offset : offset + args.chunk_size]
        tasks = [(seed, truth, args.drop_index) for seed in seeds]
        if args.workers == 1:
            completed = [analyze_task(task) for task in tasks]
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                completed = list(executor.map(analyze_task, tasks))
        by_seed.update({record["seed"]: record for record in completed})
        records = [by_seed[seed] for seed in target_seeds if seed in by_seed]
        payload = _payload(observed, truth, records, args.drop_index)
        atomic_json_dump(payload, args.output)
        summary = payload["summary"]
        print(
            f"{len(records):5d}/{args.mocks}: "
            f"k={summary['exceedances_ge_observed']} "
            f"p={summary['empirical_tail_probability']:.5f} "
            f"boundary={summary['near_prior_boundary_records']} "
            f"elapsed={time.monotonic() - started:.1f}s",
            flush=True,
        )
    records = [by_seed[seed] for seed in target_seeds if seed in by_seed]
    payload = _payload(observed, truth, records, args.drop_index)
    atomic_json_dump(payload, args.output)
    print(json.dumps(payload["summary"], indent=2))
    print(f"saved -> {args.output}")


if __name__ == "__main__":
    main()
