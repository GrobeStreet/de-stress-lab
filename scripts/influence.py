#!/usr/bin/env python3
"""
Week 4-6: influence diagnostics. Which observations create the w0wa preference?

Probe 1 (loo):   leave-one-tracer-out refits of DESI+compressedCMB (the 2.4-sigma combo).
                 For each of the 7 BAO tracers: drop it, refit LCDM and w0waCDM, record dchi2.
Probe 2 (pulls): per-tracer chi2 decomposition at the full-data LCDM and w0wa best fits —
                 which data points buy the improvement.
Probe 3 (sncut): DESI+Pantheon+ with SN low-z cuts z > {0.01, 0.025, 0.05, 0.10}:
                 does the preference live in the nearby supernovae?

Usage: python3 influence.py ../data [loo|pulls|sncut]
Results merge into results/influence.json
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from scipy import optimize, linalg, integrate, stats

TRACER_NAMES = ["BGS z=0.295", "LRG1 z=0.510", "LRG2 z=0.706", "LRG3+ELG1 z=0.934",
                "ELG2 z=1.321", "QSO z=1.484", "Lya z=2.330"]

def chi2_bao_masked(om, h, w0, wa, rd, drop=None):
    """BAO chi2 with tracer index `drop` removed (0=BGS DV; 1..6 = MH tracers)."""
    grid = W.comoving_grid(om, h, w0, wa)
    c2 = 0.0
    if drop != 0:
        z, dv, s = W.BAO_DV[0]
        dm = W.DM_Mpc(z, om, h, w0, wa, grid)
        dh = W.C_KMS/(100.0*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))
        c2 += (((z*dm*dm*dh)**(1/3.)/rd - dv)/s)**2
    for j, (z, dmv, sm, dhv, sh, r) in enumerate(W.BAO_MH, start=1):
        if j == drop: continue
        dm = W.DM_Mpc(z, om, h, w0, wa, grid)/rd - dmv
        dh = W.C_KMS/(100.0*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))/rd - dhv
        det = (sm*sh)**2*(1-r*r)
        c2 += (dm*dm*sh*sh - 2*r*dm*dh*sm*sh + dh*dh*sm*sm)/det
    return c2

def fitmin(f, x0):
    best = None
    for seed in range(3):
        x = np.array(x0)*(1 + 0.02*np.random.default_rng(seed).standard_normal(len(x0)))
        r = optimize.minimize(f, x, method="Nelder-Mead",
                              options={"xatol":1e-5,"fatol":1e-6,"maxiter":4000})
        if best is None or r.fun < best.fun: best = r
    return best

def sig2dof(d):
    p = stats.chi2.sf(-d, 2)
    return float(stats.norm.isf(p/2))

def run_loo(out):
    res = {}
    def c_dcmb(x, w0, wa, drop):
        om, h, wb = x
        if not (0.2<om<0.55 and 0.55<h<0.8 and 0.019<wb<0.026): return 1e10
        rd = W.rd_model(om, h, wb)
        return chi2_bao_masked(om, h, w0, wa, rd, drop) + W.chi2_cmb3(om, h, w0, wa, wb)
    for drop in [None,0,1,2,3,4,5,6]:
        rl = fitmin(lambda x: c_dcmb(x,-1,0,drop), [0.30,0.68,0.0222])
        rw = fitmin(lambda x: c_dcmb(x[:3],x[3],x[4],drop) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                    [0.35,0.64,0.0222,-0.45,-1.7])
        d = rw.fun - rl.fun
        key = "full" if drop is None else TRACER_NAMES[drop]
        res[key] = dict(dchi2=round(d,1), sigma=round(sig2dof(d),1),
                        w0=round(rw.x[3],2), wa=round(rw.x[4],2))
        print(f"LOO {key:20s} dchi2={d:+6.1f}  sigma={sig2dof(d):.1f}  w0={rw.x[3]:+.2f} wa={rw.x[4]:+.2f}")
    out["loo_DESI_cCMB"] = res

def run_pulls(out):
    """chi2 contribution per tracer at full-data LCDM vs w0wa best fits (DESI+cCMB)."""
    def c_dcmb(x, w0, wa):
        om, h, wb = x
        if not (0.2<om<0.55 and 0.55<h<0.8 and 0.019<wb<0.026): return 1e10
        return chi2_bao_masked(om, h, w0, wa, W.rd_model(om,h,wb)) + W.chi2_cmb3(om,h,w0,wa,wb)
    rl = fitmin(lambda x: c_dcmb(x,-1,0), [0.30,0.68,0.0222])
    rw = fitmin(lambda x: c_dcmb(x[:3],x[3],x[4]) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                [0.35,0.64,0.0222,-0.45,-1.7])
    res = {}
    for label, x, w0, wa in [("LCDM", rl.x, -1, 0), ("w0wa", rw.x[:3], rw.x[3], rw.x[4])]:
        om, h, wb = x
        rd = W.rd_model(om, h, wb)
        per = {}
        for j in range(7):
            full = chi2_bao_masked(om, h, w0, wa, rd, drop=None)
            wo   = chi2_bao_masked(om, h, w0, wa, rd, drop=j)
            per[TRACER_NAMES[j]] = round(full - wo, 2)
        per["CMB3(theta*,wb,wbc)"] = round(W.chi2_cmb3(om, h, w0, wa, wb), 2)
        res[label] = per
    diff = {k: round(res["w0wa"].get(k,0)-res["LCDM"].get(k,0), 2) for k in res["LCDM"]}
    res["improvement_w0wa_minus_LCDM"] = diff
    out["pulls_DESI_cCMB"] = res
    print("chi2 improvement by component (negative = w0wa fits it better):")
    for k, v in sorted(diff.items(), key=lambda kv: kv[1]):
        print(f"   {k:22s} {v:+.2f}")

def run_sncut(out):
    raw = np.genfromtxt(f"{DATA}/pantheon_plus.dat", names=True, dtype=None, encoding=None)
    n = len(raw); C = np.loadtxt(f"{DATA}/pantheon_plus_statsys.cov", skiprows=1).reshape(n,n)
    res = {}
    for zcut in (0.01, 0.025, 0.05, 0.10):
        m = (raw["zHD"]>zcut)&(raw["IS_CALIBRATOR"]==0); i = np.where(m)[0]
        zhd, zhel, mb = raw["zHD"][i], raw["zHEL"][i], raw["m_b_corr"][i]
        cho = linalg.cho_factor(C[np.ix_(i,i)]); ones = np.ones(len(i))
        e = ones @ linalg.cho_solve(cho, ones)
        def chi2_sn(om, h, w0, wa):
            g = W.comoving_grid(om, h, w0, wa)
            dl = (1+zhel)*np.interp(zhd, W.ZGRID, g)
            r = mb - 5*np.log10(dl)
            cr = linalg.cho_solve(cho, r)
            return r @ cr - (ones @ cr)**2/e
        def c_dsn(x, w0, wa):
            om, hrd, h = x
            if not (0.1<om<0.6 and 80<hrd<120 and 0.5<h<0.9): return 1e10
            return W.chi2_bao(om, h, w0, wa, hrd/h) + chi2_sn(om, h, w0, wa)
        rl = fitmin(lambda x: c_dsn(x,-1,0), [0.31,101,0.7])
        rw = fitmin(lambda x: c_dsn(x[:3],x[3],x[4]) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                    [0.30,101,0.7,-0.89,-0.2])
        d = rw.fun - rl.fun
        res[f"z>{zcut}"] = dict(n_sne=int(len(i)), dchi2=round(d,1), sigma=round(sig2dof(d),1),
                                w0=round(rw.x[3],3), wa=round(rw.x[4],2), Om=round(rw.x[0],3))
        print(f"SN cut z>{zcut:<5}  N={len(i):4d}  dchi2={d:+6.1f}  sigma={sig2dof(d):.1f}  "
              f"w0={rw.x[3]:+.3f}  wa={rw.x[4]:+.2f}")
    out["sncut_DESI_PantheonPlus"] = res

if __name__ == "__main__":
    DATA = sys.argv[1] if len(sys.argv)>1 else "../data"
    mode = sys.argv[2] if len(sys.argv)>2 else "all"
    path = f"{DATA}/../results/influence.json"
    out = json.load(open(path)) if os.path.exists(path) else {}
    if mode in ("loo","all"):   run_loo(out)
    if mode in ("pulls","all"): run_pulls(out)
    if mode in ("sncut","all"): run_sncut(out)
    json.dump(out, open(path,"w"), indent=1)
    print("saved ->", path)
