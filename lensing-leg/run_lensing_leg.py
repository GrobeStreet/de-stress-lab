#!/usr/bin/env python3
"""
Expedition 2 runner: full-CMB (Planck 2018 native likelihoods incl. LENSING) + DESI BAO.
MAP minimizations for 4 cases: {LCDM, w0wa} x {with, without LRG2}.
Deliverable: does the ~3-sigma full-CMB preference survive LRG2 removal?

CMB stack (all clik-free native Python, auto-installed by cobaya):
  planck_2018_lowl.TT + planck_2018_lowl.EE + planck_2018_highl_plik.TTTEEE_lite_native
  + planck_2018_lensing.native
NOTE vs DESI DR2: they use Planck PR4 CamSpec + PR4/ACT lensing; we use the 2018 (PR3)
native equivalents. Expect the same qualitative lensing lift (2.4 -> ~3 sigma), not identical
numbers. Documented as the comparison caveat.

Usage: venv/bin/python run_lensing_leg.py <case>   case in: lcdm, w0wa, lcdm_nolrg2, w0wa_nolrg2
Results appended to results_lensing.json. Each case ~20-60 min (CAMB Cls per eval).
"""
import json, os, sys
_DIR = os.path.dirname(os.path.abspath(__file__))

CASE = sys.argv[1]
W0WA = CASE.startswith("w0wa")
DROP = CASE.endswith("nolrg2")

info = {
    "likelihood": {
        "planck_2018_lowl.TT": None,
        "planck_2018_lowl.EE": None,
        "planck_2018_highl_plik.TTTEEE_lite_native": None,
        "planck_2018_lensing.native": None,
        "desi_bao": {"class": "desi_bao_like.DESIDR2BAO",
                      "python_path": _DIR, "drop_lrg2": DROP},
    },
    "theory": {"camb": {"extra_args": {"num_massive_neutrinos": 1, "nnu": 3.044,
                                        "halofit_version": "mead2020",
                                        "dark_energy_model": "ppf"}}},
    "params": {
        "ombh2":  {"prior": {"min": 0.017, "max": 0.027}, "ref": 0.02236, "proposal": 0.0001},
        "omch2":  {"prior": {"min": 0.09, "max": 0.15},  "ref": 0.1202,  "proposal": 0.001},
        "H0":     {"prior": {"min": 50, "max": 80},      "ref": 67.3,    "proposal": 0.5},
        "tau":    {"prior": {"min": 0.01, "max": 0.12},  "ref": 0.055,   "proposal": 0.005},
        "ns":     {"prior": {"min": 0.9, "max": 1.05},   "ref": 0.965,   "proposal": 0.004},
        "logA":   {"prior": {"min": 2.9, "max": 3.2},    "ref": 3.045,   "proposal": 0.01,
                    "latex": r"\log(10^{10} A_\mathrm{s})", "drop": True},
        "As":     {"value": "lambda logA: 1e-10*np.exp(logA)"},
        "mnu":    0.06,
        "rdrag":  {"derived": True},
    },
    "sampler": {"minimize": {"ignore_prior": False, "override_bobyqa": {"rhoend": 0.01}}},
    "output": os.path.join(_DIR, "chains", CASE),
    "force": True,
    "packages_path": os.path.join(os.path.dirname(_DIR), "cobaya_packages"),
}
if W0WA:
    info["params"]["w"]  = {"prior": {"min": -3, "max": 1}, "ref": -0.45, "proposal": 0.05}
    info["params"]["wa"] = {"prior": {"min": -3, "max": 2}, "ref": -1.6,  "proposal": 0.1}
    # DESI early-matter condition w0+wa<0 via an external prior
    info["prior"] = {"early_matter": "lambda w, wa: 0 if (w+wa)<0 else -np.inf"}

from cobaya.run import run
upd, sampler = run(info)
res = sampler.products()
m = res["minimum"]
out_path = os.path.join(_DIR, "results_lensing.json")
out = json.load(open(out_path)) if os.path.exists(out_path) else {}
pd = {}
for k in ("H0","ombh2","omch2","tau","ns","logA","w","wa"):
    try: pd[k] = round(float(m[k]), 5)
    except Exception: pass
out[CASE] = {"chi2_total": round(2*float(m["minuslogpost"]), 3),
             "minuslogpost": float(m["minuslogpost"]),
             "params": pd}
json.dump(out, open(out_path, "w"), indent=1)
print("DONE", CASE, out[CASE])
