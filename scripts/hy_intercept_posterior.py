#!/usr/bin/env python3
"""H-Y test: DES5Y + cCMB + BBN posterior with the low-z intercept D marginalized
alongside the global offset M. Registered in HYPOTHESIS-cross-probe.md before running.
Does the SN crossing preference (zx ~ 0.30) survive its leading systematic explanation?"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from fit_des5y import load_des
import emcee

DATA = sys.argv[1] if len(sys.argv) > 1 else "../data"
zhd, zhel, mu, icov, ids = load_des(DATA)
lowz = (ids != 10).astype(float)
T = np.column_stack([np.ones(len(zhd)), lowz])
A = T.T @ icov @ T

def chi2_sn_marg(om, h, w0, wa):
    g = W.comoving_grid(om, h, w0, wa)
    dl = (1+zhel)*np.interp(zhd, W.ZGRID, g)
    r = mu - 5*np.log10(dl)
    b = T.T @ icov @ r
    return r @ icov @ r - b @ np.linalg.solve(A, b)

def logp(x):
    om, h, wb, w0, wa = x
    if not (0.15<om<0.6 and 0.45<h<0.95 and 0.015<wb<0.03): return -np.inf
    if not (-3<w0<1 and -3<wa<2 and (w0+wa)<0): return -np.inf
    try:
        c = chi2_sn_marg(om,h,w0,wa) + W.chi2_cmb3(om,h,w0,wa,wb) + ((wb-W.BBN[0])/W.BBN[1])**2
        return -0.5*c
    except Exception:
        return -np.inf

rng = np.random.default_rng(23)
p0 = np.array([0.32,0.66,0.0222,-0.85,-0.5]) + np.array([0.01,0.008,0.0004,0.12,0.3])*rng.standard_normal((32,5))
sam = emcee.EnsembleSampler(32, 5, logp)
sam.run_mcmc(p0, 2000, progress=False)
ch = sam.get_chain(discard=500, flat=True)
w0, wa = ch[:,3], ch[:,4]
f = -(1+w0)/wa; z = f/(1-f); z[(f<=0)|(f>=1)] = np.nan
res = {"probe":"des5y_WITH_intercept_marg",
 "w0": dict(zip(("lo68","med","hi68"),[round(float(v),3) for v in np.percentile(w0,[16,50,84])])),
 "wa": dict(zip(("lo68","med","hi68"),[round(float(v),3) for v in np.percentile(wa,[16,50,84])])),
 "zcross_frac_defined": round(float(np.mean(np.isfinite(z))),3),
 "zcross_68":[round(float(v),3) for v in np.nanpercentile(z,[16,50,84])] if np.isfinite(z).any() else None,
 "wa_68_includes_0": bool(np.percentile(wa,16) < 0 < np.percentile(wa,84)),
 "acc": round(float(np.mean(sam.acceptance_fraction)),2)}
path = f"{DATA}/../results/probe_posteriors.json"
out = json.load(open(path)); out["des5y_WITH_intercept_marg"] = res
json.dump(out, open(path,"w"), indent=1)
print("DONE HY:", res["w0"], res["wa"], "zx68:", res["zcross_68"],
      "defined:", res["zcross_frac_defined"], "wa_68_incl_0:", res["wa_68_includes_0"])
