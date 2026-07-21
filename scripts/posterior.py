#!/usr/bin/env python3
"""
Gate 3: posterior sampling + DIC for DESI+cCMB, under DESI's OFFICIAL priors
(extracted verbatim from arXiv:2503.14738: w0 ~ U[-3,1], wa ~ U[-3,2], w0+wa<0).

Sampler: emcee over the CAMB-validated surrogate likelihood (exact-physics check
showed dchi2 agreement to ~0.03 sigma). Models: LCDM (om,h,wb) and w0waCDM (+w0,wa).
Outputs: marginalized means/68% CIs, w0-wa contour percentiles, DIC per model,
Delta-DIC (published target for this data combo: -4.4), boundary-mass diagnostics.

Run: venv/bin/python posterior.py ../data
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
import emcee

DATA = sys.argv[1] if len(sys.argv) > 1 else "../data"

def loglike(om, h, wb, w0, wa):
    rd = W.rd_model(om, h, wb)
    return -0.5*(W.chi2_bao(om, h, w0, wa, rd) + W.chi2_cmb3(om, h, w0, wa, wb))

def logp_lcdm(x):
    om, h, wb = x
    if not (0.15 < om < 0.6 and 0.45 < h < 0.95 and 0.015 < wb < 0.03): return -np.inf
    try: return loglike(om, h, wb, -1.0, 0.0)
    except Exception: return -np.inf

def logp_w0wa(x):
    om, h, wb, w0, wa = x
    if not (0.15 < om < 0.6 and 0.45 < h < 0.95 and 0.015 < wb < 0.03): return -np.inf
    if not (-3 < w0 < 1 and -3 < wa < 2 and (w0 + wa) < 0): return -np.inf   # DESI official
    try: return loglike(om, h, wb, w0, wa)
    except Exception: return -np.inf

def run(logp, x0, scales, nwalk, nstep, burn, seed):
    rng = np.random.default_rng(seed)
    ndim = len(x0)
    p0 = x0 + scales * rng.standard_normal((nwalk, ndim))
    sam = emcee.EnsembleSampler(nwalk, ndim, logp)
    sam.run_mcmc(p0, nstep, progress=False)
    chain = sam.get_chain(discard=burn, flat=True)
    logs = sam.get_log_prob(discard=burn, flat=True)
    return chain, logs, float(np.mean(sam.acceptance_fraction))

def summarize(chain, logs, names):
    out = {}
    for i, nm in enumerate(names):
        lo, med, hi = np.percentile(chain[:, i], [16, 50, 84])
        out[nm] = dict(median=round(float(med), 4), lo68=round(float(lo), 4), hi68=round(float(hi), 4))
    # DIC = 2*mean(D) - D(at posterior-mean params); D = -2 logL
    D = -2.0 * logs
    Dbar = float(np.mean(D))
    xbar = np.mean(chain, axis=0)
    return out, Dbar, xbar

if __name__ == "__main__":
    res = {}
    # LCDM
    ch, lg, acc = run(logp_lcdm, np.array([0.2976, 0.6837, 0.02223]),
                      np.array([0.006, 0.006, 0.0004]), 24, 1600, 400, 1)
    s, Dbar, xbar = summarize(ch, lg, ["Om", "h", "wb"])
    Dhat = -2.0 * logp_lcdm(xbar)
    dic_l = 2*Dbar - Dhat
    res["LCDM"] = dict(params=s, DIC=round(dic_l, 2), acc=round(acc, 2), n=len(ch))
    print("LCDM   ", {k: v["median"] for k, v in s.items()}, "DIC=%.2f acc=%.2f" % (dic_l, acc))

    # w0wa
    ch, lg, acc = run(logp_w0wa, np.array([0.35, 0.64, 0.02223, -0.45, -1.6]),
                      np.array([0.01, 0.008, 0.0004, 0.1, 0.25]), 32, 2200, 600, 2)
    s, Dbar, xbar = summarize(ch, lg, ["Om", "h", "wb", "w0", "wa"])
    Dhat = -2.0 * logp_w0wa(xbar)
    dic_w = 2*Dbar - Dhat
    # boundary mass + contour data
    bmass = float(np.mean(ch[:, 3] + ch[:, 4] > -0.05))
    lam_mass = float(np.mean((ch[:, 3] < -0.95) & (ch[:, 3] > -1.05)))
    w0wa_cov = np.cov(ch[:, 3], ch[:, 4]).tolist()
    res["w0wa"] = dict(params=s, DIC=round(dic_w, 2), acc=round(acc, 2), n=len(ch),
                       near_prior_boundary_frac=round(bmass, 3),
                       w0_wa_cov=[[round(v, 4) for v in row] for row in w0wa_cov])
    res["Delta_DIC"] = round(dic_w - dic_l, 2)
    res["published_Delta_DIC_target"] = -4.4
    # save thinned chain for contours
    np.savez_compressed(f"{DATA}/../results/w0wa_chain.npz", chain=ch[::10], logp=lg[::10])
    print("w0wa   ", {k: v["median"] for k, v in s.items()}, "DIC=%.2f acc=%.2f" % (dic_w, acc))
    print("Delta-DIC = %.2f  (published target -4.4)" % (dic_w - dic_l))
    json.dump(res, open(f"{DATA}/../results/posterior.json", "w"), indent=1)
    print("DONE")
