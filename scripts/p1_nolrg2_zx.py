#!/usr/bin/env python3
"""Registered H-X follow-up: P1 (DESI BAO + cCMB) posterior WITHOUT LRG2 — does the
BAO leg's tight z× = 0.49 preference dissolve when the influential point is removed?
Registered in HYPOTHESIS-cross-probe.md before running."""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
import emcee

DATA = sys.argv[1] if len(sys.argv) > 1 else "../data"

def chi2_bao_nolrg2(om, h, w0, wa, rd):
    grid = W.comoving_grid(om, h, w0, wa)
    z, dv, s = W.BAO_DV[0]
    dm = W.DM_Mpc(z, om, h, w0, wa, grid)
    dh = W.C_KMS/(100*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))
    c2 = (((z*dm*dm*dh)**(1/3.)/rd - dv)/s)**2
    for j,(z, dmv, sm, dhv, sh, r) in enumerate(W.BAO_MH):
        if j == 1: continue
        a = W.DM_Mpc(z, om, h, w0, wa, grid)/rd - dmv
        b = W.C_KMS/(100*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))/rd - dhv
        det = (sm*sh)**2*(1-r*r)
        c2 += (a*a*sh*sh - 2*r*a*b*sm*sh + b*b*sm*sm)/det
    return c2

def logp(x):
    om, h, wb, w0, wa = x
    if not (0.15<om<0.6 and 0.45<h<0.95 and 0.015<wb<0.03): return -np.inf
    if not (-3<w0<1 and -3<wa<2 and (w0+wa)<0): return -np.inf
    try:
        return -0.5*(chi2_bao_nolrg2(om,h,w0,wa,W.rd_model(om,h,wb)) + W.chi2_cmb3(om,h,w0,wa,wb))
    except Exception:
        return -np.inf

rng = np.random.default_rng(11)
p0 = np.array([0.33,0.65,0.0222,-0.6,-1.1]) + np.array([0.01,0.008,0.0004,0.12,0.3])*rng.standard_normal((32,5))
sam = emcee.EnsembleSampler(32, 5, logp)
sam.run_mcmc(p0, 2000, progress=False)
ch = sam.get_chain(discard=500, flat=True)
w0, wa = ch[:,3], ch[:,4]
f = -(1+w0)/wa; z = f/(1-f); z[(f<=0)|(f>=1)] = np.nan
res = {"probe":"desi_bao_ccmb_NOLRG2",
 "w0": dict(zip(("lo68","med","hi68"),[round(float(v),3) for v in np.percentile(w0,[16,50,84])])),
 "wa": dict(zip(("lo68","med","hi68"),[round(float(v),3) for v in np.percentile(wa,[16,50,84])])),
 "w0_wa_mean":[round(float(w0.mean()),4), round(float(wa.mean()),4)],
 "w0_wa_cov":[[round(float(v),5) for v in r] for r in np.cov(w0,wa)],
 "zcross_frac_defined": round(float(np.mean(np.isfinite(z))),3),
 "zcross_68":[round(float(v),3) for v in np.nanpercentile(z,[16,50,84])] if np.isfinite(z).any() else None,
 "acc": round(float(np.mean(sam.acceptance_fraction)),2)}
path = f"{DATA}/../results/probe_posteriors.json"
out = json.load(open(path)); out["desi_bao_ccmb_NOLRG2"] = res
json.dump(out, open(path,"w"), indent=1)
print("DONE noLRG2:", res["w0"], res["wa"], "zx68:", res["zcross_68"], "defined:", res["zcross_frac_defined"])
