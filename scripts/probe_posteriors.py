#!/usr/bin/env python3
"""
H-X test runner: per-probe w0wa posteriors (P2 = Pantheon+ + cCMB + BBN,
P3 = DES5Y + cCMB + BBN), emcee under DESI official priors. See HYPOTHESIS-cross-probe.md.
Usage: venv/bin/python probe_posteriors.py ../data [pantheon|des5y]
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from fit_des5y import load_des
import emcee

DATA = sys.argv[1]; PROBE = sys.argv[2]

if PROBE == "pantheon":
    chi2_sn = W.sn_factory(DATA)
else:
    zhd, zhel, mu, icov, ids = load_des(DATA)
    ones = np.ones(len(zhd))
    e_cache = None
    def chi2_sn(om, h, w0, wa):
        g = W.comoving_grid(om, h, w0, wa)
        dl = (1+zhel)*np.interp(zhd, W.ZGRID, g)
        r = mu - 5*np.log10(dl)
        b = ones @ icov @ r
        return r @ icov @ r - b*b/(ones @ icov @ ones)

def logp(x):
    om, h, wb, w0, wa = x
    if not (0.15 < om < 0.6 and 0.45 < h < 0.95 and 0.015 < wb < 0.03): return -np.inf
    if not (-3 < w0 < 1 and -3 < wa < 2 and (w0 + wa) < 0): return -np.inf
    try:
        c = chi2_sn(om, h, w0, wa) + W.chi2_cmb3(om, h, w0, wa, wb)
        c += ((wb - W.BBN[0]) / W.BBN[1])**2
        return -0.5*c
    except Exception:
        return -np.inf

rng = np.random.default_rng(7)
x0 = np.array([0.33, 0.66, 0.0222, -0.75, -0.8])
p0 = x0 + np.array([0.01, 0.01, 0.0004, 0.12, 0.3]) * rng.standard_normal((32, 5))
sam = emcee.EnsembleSampler(32, 5, logp)
sam.run_mcmc(p0, 2000, progress=False)
ch = sam.get_chain(discard=500, flat=True)

def zcross(w0, wa):
    # w(z) = -1  =>  z/(1+z) = -(1+w0)/wa
    with np.errstate(all="ignore"):
        f = -(1+w0)/wa
        z = f/(1-f)
        z[(f <= 0) | (f >= 1)] = np.nan
        return z

zx = zcross(ch[:,3], ch[:,4])
res = {
  "probe": PROBE,
  "w0": dict(zip(("lo68","med","hi68"), [round(float(v),3) for v in np.percentile(ch[:,3],[16,50,84])])),
  "wa": dict(zip(("lo68","med","hi68"), [round(float(v),3) for v in np.percentile(ch[:,4],[16,50,84])])),
  "w0_wa_mean": [round(float(ch[:,3].mean()),4), round(float(ch[:,4].mean()),4)],
  "w0_wa_cov": [[round(float(v),5) for v in row] for row in np.cov(ch[:,3], ch[:,4])],
  "zcross_frac_defined": round(float(np.mean(np.isfinite(zx))),3),
  "zcross_68": [round(float(v),3) for v in np.nanpercentile(zx,[16,50,84])] if np.isfinite(zx).any() else None,
  "acc": round(float(np.mean(sam.acceptance_fraction)),2), "n": len(ch),
}
path = f"{DATA}/../results/probe_posteriors.json"
out = json.load(open(path)) if os.path.exists(path) else {}
out[PROBE] = res
json.dump(out, open(path, "w"), indent=1)
np.savez_compressed(f"{DATA}/../results/chain_{PROBE}.npz", chain=ch[::10])
print("DONE", PROBE, res["w0"], res["wa"], "zx68:", res["zcross_68"])
