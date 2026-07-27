#!/usr/bin/env python3
"""
Selection-calibrated maximum leave-one-tracer-out influence test.

For the observed DESI+cCMB data and for every LambdaCDM mock:

  1. Fit LambdaCDM and w0waCDM to all seven BAO tracers plus cCMB.
  2. Repeat both fits after deleting each of the seven tracers in turn.
  3. Define tracer influence as

         I_j = DeltaChi2(-j) - DeltaChi2(full),

     where DeltaChi2 = Chi2(w0waCDM) - Chi2(LambdaCDM). Positive I_j means
     deleting tracer j weakens the preference for w0waCDM.
  4. Select M = max_j I_j inside each mock.

The empirical tail P(M_mock >= M_observed | LambdaCDM) therefore accounts for
having searched all seven tracers before naming the most influential one.

The mocks use the same Gaussian published-summary likelihood and LambdaCDM
truth as scripts/null_mocks.py. Results are deterministic by seed, resumable,
and written atomically after every chunk.

Usage:
  python3 scripts/max_influence_mocks.py --mocks 5000 --workers 8
  python3 scripts/max_influence_mocks.py --mocks 20 --workers 1 --output /tmp/test.json
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
import fit_w0wa as W


TRACER_NAMES = [
    "BGS z=0.295",
    "LRG1 z=0.510",
    "LRG2 z=0.706",
    "LRG3+ELG1 z=0.934",
    "ELG2 z=1.321",
    "QSO z=1.484",
    "Lya z=2.330",
]

SEED_START = 10_000
TRUTH = {"Omega_m": 0.2976, "h": 0.6837, "omega_b": 0.02223}
LCDM_START = np.array([TRUTH["Omega_m"], TRUTH["h"], TRUTH["omega_b"]])
W0WA_START = np.array([TRUTH["Omega_m"] + 0.05, TRUTH["h"] - 0.04, TRUTH["omega_b"], -0.5, -1.5])
OPT_OPTIONS = {"xatol": 2e-5, "fatol": 2e-5, "maxiter": 1800}
LCDM_BOUNDS = ([0.200001, 0.500001, 0.019001], [0.549999, 0.849999, 0.025999])
W0WA_BOUNDS = (
    [0.200001, 0.500001, 0.019001, -2.999999, -4.999999],
    [0.549999, 0.849999, 0.025999, 0.999999, 2.999999],
)


def _truth_predictions():
    om, h, wb = TRUTH["Omega_m"], TRUTH["h"], TRUTH["omega_b"]
    rd = W.rd_model(om, h, wb)
    grid = W.comoving_grid(om, h, -1.0, 0.0)
    z, _, _ = W.BAO_DV[0]
    dm = W.DM_Mpc(z, om, h, -1.0, 0.0, grid)
    dh = W.C_KMS / (100.0 * h * np.sqrt(W.Ez2_late(z, om, h, -1.0, 0.0)))
    pred_dv = (z * dm * dm * dh) ** (1.0 / 3.0) / rd
    pred_mh = []
    for z, _, _, _, _, _ in W.BAO_MH:
        dm = W.DM_Mpc(z, om, h, -1.0, 0.0, grid) / rd
        dh = W.C_KMS / (100.0 * h * np.sqrt(W.Ez2_late(z, om, h, -1.0, 0.0))) / rd
        pred_mh.append((dm, dh))
    theta = W.theta_star(om, h, -1.0, 0.0, wb)
    cmb = np.array([theta, wb, om * h * h - W.OMEGA_NU_MASSIVE_H2])
    return pred_dv, pred_mh, cmb


PRED_DV, PRED_MH, CMB_PRED = _truth_predictions()
CMB_CHOL = np.linalg.cholesky(W.CMB_COV)


def make_mock(seed: int):
    rng = np.random.default_rng(seed)
    bao_dv = PRED_DV + rng.standard_normal() * W.BAO_DV[0][2]
    mh = []
    for (dm_pred, dh_pred), (_, _, sm, _, sh, rho) in zip(PRED_MH, W.BAO_MH):
        covariance = np.array([[sm * sm, rho * sm * sh], [rho * sm * sh, sh * sh]])
        noise = np.linalg.cholesky(covariance) @ rng.standard_normal(2)
        mh.append((dm_pred + noise[0], dh_pred + noise[1]))
    cmb = CMB_PRED + CMB_CHOL @ rng.standard_normal(3)
    return float(bao_dv), mh, cmb


def observed_data():
    return (
        float(W.BAO_DV[0][1]),
        [(float(row[1]), float(row[3])) for row in W.BAO_MH],
        W.CMB_MU.copy(),
    )


def chi2_dataset(x, w0: float, wa: float, dataset, drop: int | None):
    om, h, wb = x
    if not (0.2 < om < 0.55 and 0.5 < h < 0.85 and 0.019 < wb < 0.026):
        return 1e10
    bao_dv, mh, cmb = dataset
    rd = W.rd_model(om, h, wb)
    grid = W.comoving_grid(om, h, w0, wa)
    c2 = 0.0
    if drop != 0:
        z, _, sigma = W.BAO_DV[0]
        dm = W.DM_Mpc(z, om, h, w0, wa, grid)
        dh = W.C_KMS / (100.0 * h * np.sqrt(W.Ez2_late(z, om, h, w0, wa)))
        c2 += (((z * dm * dm * dh) ** (1.0 / 3.0) / rd - bao_dv) / sigma) ** 2
    for index, ((dm_obs, dh_obs), (z, _, sm, _, sh, rho)) in enumerate(
        zip(mh, W.BAO_MH), start=1
    ):
        if drop == index:
            continue
        dm_resid = W.DM_Mpc(z, om, h, w0, wa, grid) / rd - dm_obs
        dh_resid = (
            W.C_KMS / (100.0 * h * np.sqrt(W.Ez2_late(z, om, h, w0, wa))) / rd - dh_obs
        )
        determinant = (sm * sh) ** 2 * (1.0 - rho * rho)
        c2 += (
            dm_resid * dm_resid * sh * sh
            - 2.0 * rho * dm_resid * dh_resid * sm * sh
            + dh_resid * dh_resid * sm * sm
        ) / determinant
    vector = np.array(
        [W.theta_star(om, h, w0, wa, wb), wb, om * h * h - W.OMEGA_NU_MASSIVE_H2]
    ) - cmb
    return float(c2 + vector @ W.CMB_ICOV @ vector)


def residuals_dataset(x, w0: float, wa: float, dataset, drop: int | None):
    """Whitened Gaussian residual vector; its squared norm is chi2_dataset."""
    om, h, wb = x
    bao_dv, mh, cmb = dataset
    rd = W.rd_model(om, h, wb)
    grid = W.comoving_grid(om, h, w0, wa)
    residuals = []
    if drop != 0:
        z, _, sigma = W.BAO_DV[0]
        dm = W.DM_Mpc(z, om, h, w0, wa, grid)
        dh = W.C_KMS / (100.0 * h * np.sqrt(W.Ez2_late(z, om, h, w0, wa)))
        residuals.append(((z * dm * dm * dh) ** (1.0 / 3.0) / rd - bao_dv) / sigma)
    for index, ((dm_obs, dh_obs), (z, _, sm, _, sh, rho)) in enumerate(
        zip(mh, W.BAO_MH), start=1
    ):
        if drop == index:
            continue
        raw = np.array(
            [
                W.DM_Mpc(z, om, h, w0, wa, grid) / rd - dm_obs,
                W.C_KMS / (100.0 * h * np.sqrt(W.Ez2_late(z, om, h, w0, wa))) / rd
                - dh_obs,
            ]
        )
        covariance = np.array([[sm * sm, rho * sm * sh], [rho * sm * sh, sh * sh]])
        residuals.extend(np.linalg.solve(np.linalg.cholesky(covariance), raw))
    cmb_raw = np.array(
        [W.theta_star(om, h, w0, wa, wb), wb, om * h * h - W.OMEGA_NU_MASSIVE_H2]
    ) - cmb
    residuals.extend(np.linalg.solve(CMB_CHOL, cmb_raw))
    return np.asarray(residuals)


def _fit_pair(dataset, drop, lcdm_start, w0wa_start, solver):
    if solver == "least-squares":
        lcdm = optimize.least_squares(
            lambda x: residuals_dataset(x, -1.0, 0.0, dataset, drop),
            lcdm_start,
            bounds=LCDM_BOUNDS,
            xtol=1e-10,
            ftol=1e-10,
            gtol=1e-10,
            max_nfev=1000,
        )
        wfit = optimize.least_squares(
            lambda x: residuals_dataset(x[:3], x[3], x[4], dataset, drop),
            w0wa_start,
            bounds=W0WA_BOUNDS,
            xtol=1e-10,
            ftol=1e-10,
            gtol=1e-10,
            max_nfev=1500,
        )
        lcdm.fun_value = float(np.dot(lcdm.fun, lcdm.fun))
        wfit.fun_value = float(np.dot(wfit.fun, wfit.fun))
        dchi2 = min(0.0, wfit.fun_value - lcdm.fun_value)
        return lcdm, wfit, dchi2

    lcdm = optimize.minimize(
        lambda x: chi2_dataset(x, -1.0, 0.0, dataset, drop),
        lcdm_start,
        method="Nelder-Mead",
        options=OPT_OPTIONS,
    )

    def w_objective(x):
        if not (-3.0 < x[3] < 1.0 and -5.0 < x[4] < 3.0):
            return 1e10
        return chi2_dataset(x[:3], x[3], x[4], dataset, drop)

    wfit = optimize.minimize(
        w_objective,
        w0wa_start,
        method="Nelder-Mead",
        options=OPT_OPTIONS,
    )
    dchi2 = min(0.0, float(wfit.fun - lcdm.fun))
    return lcdm, wfit, dchi2


def analyze_dataset(dataset, solver="least-squares"):
    full_lcdm, full_w, full_dchi2 = _fit_pair(
        dataset, None, LCDM_START, W0WA_START, solver
    )
    deletion_dchi2 = []
    converged = bool(full_lcdm.success and full_w.success)
    for drop in range(7):
        lcdm, wfit, dchi2 = _fit_pair(
            dataset, drop, full_lcdm.x, full_w.x, solver
        )
        deletion_dchi2.append(dchi2)
        converged = converged and bool(lcdm.success and wfit.success)
    influences = np.asarray(deletion_dchi2) - full_dchi2
    selected = int(np.argmax(influences))
    return {
        "dchi2_full": float(full_dchi2),
        "dchi2_deleted": [float(x) for x in deletion_dchi2],
        "influence": [float(x) for x in influences],
        "max_influence": float(influences[selected]),
        "selected_index": selected,
        "selected_tracer": TRACER_NAMES[selected],
        "converged": converged,
    }


def analyze_task(task):
    seed, solver = task
    result = analyze_dataset(make_mock(seed), solver)
    result["seed"] = int(seed)
    return result


def clopper_pearson(successes: int, trials: int, alpha: float = 0.05):
    if trials == 0:
        return [math.nan, math.nan]
    low = 0.0 if successes == 0 else stats.beta.ppf(alpha / 2.0, successes, trials - successes + 1)
    high = (
        1.0
        if successes == trials
        else stats.beta.ppf(1.0 - alpha / 2.0, successes + 1, trials - successes)
    )
    return [float(low), float(high)]


def summarize(observed, records):
    threshold = observed["max_influence"]
    maxima = np.array([record["max_influence"] for record in records])
    full_dchi2 = np.array([record["dchi2_full"] for record in records])
    exceedances = int(np.count_nonzero(maxima >= threshold))
    n = len(records)
    global_as_strong = full_dchi2 <= observed["dchi2_full"]
    conditional_n = int(np.count_nonzero(global_as_strong))
    conditional_exceedances = int(
        np.count_nonzero((maxima >= threshold) & global_as_strong)
    )
    frequencies = {
        name: int(sum(record["selected_index"] == index for record in records))
        for index, name in enumerate(TRACER_NAMES)
    }
    return {
        "n_mocks": n,
        "observed_threshold": threshold,
        "exceedances_ge_observed": exceedances,
        "empirical_tail_probability": float(exceedances / n) if n else math.nan,
        "plus_one_tail_probability": float((exceedances + 1) / (n + 1)) if n else math.nan,
        "clopper_pearson_95": clopper_pearson(exceedances, n),
        "global_preference_tail_check": {
            "threshold_dchi2": observed["dchi2_full"],
            "exceedances": conditional_n,
            "empirical_tail_probability": (
                float(conditional_n / n) if n else math.nan
            ),
            "clopper_pearson_95": clopper_pearson(conditional_n, n),
        },
        "conditional_on_global_preference_as_strong_or_stronger": {
            "condition": "dchi2_full_mock <= dchi2_full_observed",
            "n_mocks": conditional_n,
            "exceedances_ge_observed": conditional_exceedances,
            "empirical_tail_probability": (
                float(conditional_exceedances / conditional_n)
                if conditional_n
                else math.nan
            ),
            "clopper_pearson_95": clopper_pearson(
                conditional_exceedances, conditional_n
            ),
        },
        "max_influence_quantiles": {
            str(q): float(np.quantile(maxima, q)) if n else math.nan
            for q in (0.5, 0.68, 0.9, 0.95, 0.99)
        },
        "selected_tracer_counts": frequencies,
        "failed_optimizer_records": int(sum(not record["converged"] for record in records)),
    }


def atomic_json_dump(payload, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
    parser.add_argument("--mocks", type=int, default=5000, help="Total deterministic mocks desired.")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    parser.add_argument("--chunk-size", type=int, default=25, help="Checkpoint interval.")
    parser.add_argument(
        "--solver",
        choices=("least-squares", "nelder-mead"),
        default="least-squares",
        help="Gaussian residual least-squares is faster; Nelder-Mead reproduces the legacy pipeline.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project / "results" / "max_influence_mocks.json",
    )
    parser.add_argument("--fresh", action="store_true", help="Ignore any existing output.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.mocks <= 0 or args.workers <= 0 or args.chunk_size <= 0:
        raise SystemExit("--mocks, --workers, and --chunk-size must be positive")

    started = time.monotonic()
    observed = analyze_dataset(observed_data(), args.solver)
    payload = {}
    if args.output.exists() and not args.fresh:
        payload = json.load(open(args.output))
    records = payload.get("mocks", [])
    by_seed = {int(record["seed"]): record for record in records}
    target_seeds = list(range(SEED_START, SEED_START + args.mocks))
    missing = [seed for seed in target_seeds if seed not in by_seed]

    print(
        f"observed M={observed['max_influence']:.4f} "
        f"({observed['selected_tracer']}); existing={len(by_seed)}, missing={len(missing)}"
    )

    for offset in range(0, len(missing), args.chunk_size):
        seeds = missing[offset : offset + args.chunk_size]
        tasks = [(seed, args.solver) for seed in seeds]
        if args.workers == 1:
            completed = [analyze_task(task) for task in tasks]
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                completed = list(executor.map(analyze_task, tasks))
        by_seed.update({record["seed"]: record for record in completed})
        selected_records = [by_seed[seed] for seed in target_seeds if seed in by_seed]
        payload = {
            "schema_version": 1,
            "analysis": "selection-calibrated maximum leave-one-tracer-out influence",
            "statistic": "I_j=dchi2_deleted_j-dchi2_full; M=max_j(I_j)",
            "solver": args.solver,
            "null": "LambdaCDM parametric mocks of DESI DR2 published BAO summaries plus compressed CMB",
            "seed_start": SEED_START,
            "truth": TRUTH,
            "tracers": TRACER_NAMES,
            "observed": observed,
            "summary": summarize(observed, selected_records),
            "mocks": selected_records,
        }
        atomic_json_dump(payload, args.output)
        summary = payload["summary"]
        print(
            f"{len(selected_records):5d}/{args.mocks}: "
            f"k={summary['exceedances_ge_observed']} "
            f"p={summary['empirical_tail_probability']:.4f} "
            f"elapsed={time.monotonic() - started:.1f}s",
            flush=True,
        )

    selected_records = [by_seed[seed] for seed in target_seeds if seed in by_seed]
    payload = {
        "schema_version": 1,
        "analysis": "selection-calibrated maximum leave-one-tracer-out influence",
        "statistic": "I_j=dchi2_deleted_j-dchi2_full; M=max_j(I_j)",
        "solver": args.solver,
        "null": "LambdaCDM parametric mocks of DESI DR2 published BAO summaries plus compressed CMB",
        "seed_start": SEED_START,
        "truth": TRUTH,
        "tracers": TRACER_NAMES,
        "observed": observed,
        "summary": summarize(observed, selected_records),
        "mocks": selected_records,
    }
    atomic_json_dump(payload, args.output)
    print(json.dumps(payload["summary"], indent=2))
    print(f"saved -> {args.output}")


if __name__ == "__main__":
    main()
