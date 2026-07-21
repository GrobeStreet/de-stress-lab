#!/usr/bin/env python3
"""
Week 7: EXACT-PHYSICS CHECK (response to the cross-AI audit's theta*-surrogate critique).

Replaces the two empirically calibrated constants (rd_cal, rs_cal) with CAMB 1.6.6:
full RECFAST recombination, exact rdrag and thetastar, w0wa (PPF) background.
Late-time BAO distances still use our validated fast integrator (identical background).

Runs one fit per invocation (CAMB background calls ~0.1s each):
  python3 camb_check.py ../data lcdm         # LCDM  DESI+cCMB
  python3 camb_check.py ../data w0wa         # w0wa  DESI+cCMB
  python3 camb_check.py ../data lcdm_noLRG2  # LCDM  without LRG2
  python3 camb_check.py ../data w0wa_noLRG2  # w0wa  without LRG2
Appends to results/camb_check.json. Surrogate references: -8.46 baseline, -4.33 no-LRG2.
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from scipy import optimize
import camb

CACHE = {}
def camb_early(om, h, wb, w0, wa):
    """Exact rdrag [Mpc] and 100*theta_star from CAMB (background+recombination only)."""
    key = (round(om,6), round(h,6), round(wb,6), round(w0,5), round(wa,5))
    if key in CACHE: return CACHE[key]
    wc = om*h*h - wb - W.OMEGA_NU_MASSIVE_H2
    pars = camb.set_params(H0=100*h, ombh2=wb, omch2=wc, mnu=0.06, nnu=3.044,
                           w=w0, wa=wa, dark_energy_model='ppf', WantCls=False)
    r = camb.get_background(pars)
    d = r.get_derived_params()
    CACHE[key] = (d['rdrag'], d['thetastar'])   # thetastar is 100*theta_*
    return CACHE[key]

def chi2_bao_drop(om, h, w0, wa, rd, drop_lrg2=False):
    grid = W.comoving_grid(om, h, w0, wa)
    c2 = 0.0
    z, dv, s = W.BAO_DV[0]
    dm = W.DM_Mpc(z, om, h, w0, wa, grid)
    dh = W.C_KMS/(100.0*h*np.sqrt(W.Ez2_late(z,om,h,w0,wa)))
    c2 += (((z*dm*dm*dh)**(1/3.)/rd - dv)/s)**2
    for j,(z, dmv, sm, dhv, sh, rho) in enumerate(W.BAO_MH):
        if drop_lrg2 and j == 1: continue   # LRG2 is index 1 in BAO_MH
        dm = W.DM_Mpc(z, om, h, w0, wa, grid)/rd - dmv
        dh = W.C_KMS/(100.0*h*np.sqrt(W.Ez2_late(z,om,h,w0,wa)))/rd - dhv
        det = (sm*sh)**2*(1-rho*rho)
        c2 += (dm*dm*sh*sh - 2*rho*dm*dh*sm*sh + dh*dh*sm*sm)/det
    return c2

def chi2_total(x, w0, wa, drop_lrg2):
    om, h, wb = x
    if not (0.2<om<0.55 and 0.5<h<0.85 and 0.019<wb<0.026): return 1e10
    try:
        rd, th100 = camb_early(om, h, wb, w0, wa)
    except Exception:
        return 1e10
    wbc = om*h*h - W.OMEGA_NU_MASSIVE_H2
    v = np.array([th100/100.0, wb, wbc]) - W.CMB_MU
    return chi2_bao_drop(om, h, w0, wa, rd, drop_lrg2) + v @ W.CMB_ICOV @ v

if __name__ == "__main__":
    DATA = sys.argv[1]; MODE = sys.argv[2]
    drop = MODE.endswith("noLRG2")
    path = f"{DATA}/../results/camb_check.json"
    out = json.load(open(path)) if os.path.exists(path) else {}

    if MODE.startswith("lcdm"):
        f = lambda x: chi2_total(x, -1, 0, drop)
        x0 = [0.298, 0.684, 0.0222]
        r = optimize.minimize(f, x0, method="Nelder-Mead",
                              options={"xatol":2e-5,"fatol":2e-5,"maxiter":250})
        out[MODE] = dict(chi2=round(r.fun,2), Om=round(r.x[0],4), H0=round(100*r.x[1],2),
                         wb=round(r.x[2],5), nfev=int(r.nfev))
        print(MODE, "chi2=%.2f Om=%.4f H0=%.2f (nfev=%d)" % (r.fun, r.x[0], 100*r.x[1], r.nfev))
    else:
        f = lambda x: chi2_total(x[:3], x[3], x[4], drop) if (-3<x[3]<1 and -5<x[4]<3) else 1e10
        x0 = [0.352, 0.636, 0.0223, -0.44, -1.68] if not drop else [0.33, 0.65, 0.0223, -0.62, -1.17]
        r = optimize.minimize(f, x0, method="Nelder-Mead",
                              options={"xatol":2e-5,"fatol":2e-5,"maxiter":400})
        out[MODE] = dict(chi2=round(r.fun,2), Om=round(r.x[0],4), H0=round(100*r.x[1],2),
                         w0=round(r.x[3],3), wa=round(r.x[4],2), nfev=int(r.nfev))
        print(MODE, "chi2=%.2f Om=%.4f H0=%.2f w0=%+.3f wa=%+.2f (nfev=%d)"
              % (r.fun, r.x[0], 100*r.x[1], r.x[3], r.x[4], r.nfev))

    # surrogate-vs-CAMB diagnostic at this best fit
    om, h, wb = (out[MODE]["Om"], out[MODE]["H0"]/100, out[MODE].get("wb", 0.0222))
    w0v = out[MODE].get("w0", -1); wav = out[MODE].get("wa", 0)
    rd_c, th_c = camb_early(om, h, wb, w0v, wav)
    rd_s = W.rd_model(om, h, wb); th_s = 100*W.theta_star(om, h, w0v, wav, wb)
    out[MODE]["camb_vs_surrogate"] = dict(rd_camb=round(rd_c,2), rd_surr=round(rd_s,2),
                                          th_camb=round(th_c,5), th_surr=round(th_s,5))
    print("  rd: CAMB %.2f vs surrogate %.2f | 100theta*: CAMB %.5f vs surrogate %.5f"
          % (rd_c, rd_s, th_c, th_s))
    json.dump(out, open(path,"w"), indent=1)
