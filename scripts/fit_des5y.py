#!/usr/bin/env python3
"""
Week 6: DES5Y leg + the Efstathiou intercept test.

Data: DES-SN5YR repo, 2025 'Dovekie' recalibrated release (DES-Dovekie_HD.csv, N=1820;
STAT+SYS.npz stores the INVERSE covariance, upper-triangular packed — convention taken
from the repo's own DES-Dovekie-SN_Likelihood.py). PROVENANCE CAVEAT: the DR2 paper's
published Delta-chi2 = -13.6 (3.3 sigma) used the 2024 DES-SN5YR release; differences
here may partly reflect the Dovekie recalibration itself. Reported as found.

Tests:
  A. DESI + DES5Y: LCDM vs w0waCDM (published ladder row: -13.6, 3.3 sigma)
  B. Efstathiou intercept test: free magnitude offset D applied to the low-z external
     subsample (zHD < 0.1 proxy; the external low-z sample dominates there), marginalized
     analytically together with the global offset M. How much preference survives?
  C. Low-z cut sweep on DES5Y (as done for Pantheon+).
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from scipy import optimize, stats

def load_des(data_dir):
    zhd, zhel, mu, ids = [], [], [], []
    for line in open(f"{data_dir}/des_dovekie_hd.csv"):
        if not line.startswith("SN:"): continue
        p = line.split()
        ids.append(int(p[2])); zhd.append(float(p[3])); zhel.append(float(p[4])); mu.append(float(p[5]))
    zhd, zhel, mu, ids = map(np.array, (zhd, zhel, mu, ids))
    d = np.load(f"{data_dir}/des_statsys.npz")
    n = int(d["nsn"][0])
    icov = np.zeros((n, n))
    icov[np.triu_indices(n)] = d["cov"]
    il = np.tril_indices(n, -1)
    icov[il] = icov.T[il]
    assert len(zhd) == n, (len(zhd), n)
    return zhd, zhel, mu, icov, ids

def sig2dof(dd):
    return float(stats.norm.isf(stats.chi2.sf(-dd, 2) / 2))

def fitmin(f, x0):
    best = None
    for seed in range(3):
        x = np.array(x0)*(1 + 0.02*np.random.default_rng(seed).standard_normal(len(x0)))
        r = optimize.minimize(f, x, method="Nelder-Mead",
                              options={"xatol":1e-5,"fatol":1e-6,"maxiter":4000})
        if best is None or r.fun < best.fun: best = r
    return best

if __name__ == "__main__":
    DATA = sys.argv[1] if len(sys.argv) > 1 else "../data"
    zhd, zhel, mu, icov, ids = load_des(DATA)
    n = len(zhd)
    lowz = ids != 10   # external (non-DES) low-z sample, identified by IDSURVEY
    print(f"DES5Y (Dovekie): N={n}, external low-z sample (IDSURVEY!=10) N={lowz.sum()}, zmax={zhd[lowz].max():.3f}")

    ones = np.ones(n)
    def chi2_des_nuis(om, h, w0, wa, templates):
        """chi2 with analytic marginalization over linear nuisances (columns of T)."""
        g = W.comoving_grid(om, h, w0, wa)
        dl = (1+zhel)*np.interp(zhd, W.ZGRID, g)          # units c/H0; normalization -> M
        r = mu - 5*np.log10(dl)
        T = np.column_stack(templates)
        A = T.T @ icov @ T
        b = T.T @ icov @ r
        return r @ icov @ r - b @ np.linalg.solve(A, b)

    def combo(x, w0, wa, templates):
        om, hrd, h = x
        if not (0.1<om<0.6 and 80<hrd<120 and 0.5<h<0.9): return 1e10
        return W.chi2_bao(om, h, w0, wa, hrd/h) + chi2_des_nuis(om, h, w0, wa, templates)

    out = {}
    # ---- A: baseline (M only) ----
    Tm = [ones]
    rl = fitmin(lambda x: combo(x,-1,0,Tm), [0.31,101,0.7])
    rw = fitmin(lambda x: combo(x[:3],x[3],x[4],Tm) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                [0.32,100,0.7,-0.75,-0.8])
    dA = rw.fun - rl.fun
    out["A_DESI_DES5Y"] = dict(dchi2=round(dA,1), sigma=round(sig2dof(dA),1),
                               w0=round(rw.x[3],3), wa=round(rw.x[4],2), Om=round(rw.x[0],3),
                               published="dchi2=-13.6, 3.3sigma (2024 release; ours is Dovekie)")
    print(f"A  DESI+DES5Y:            dchi2={dA:+6.1f}  sigma={sig2dof(dA):.1f}  "
          f"w0={rw.x[3]:+.3f} wa={rw.x[4]:+.2f} Om={rw.x[0]:.3f}   (pub: -13.6, 3.3sig)")

    # ---- B: Efstathiou intercept (M + low-z offset D) ----
    Td = [ones, lowz.astype(float)]
    rl2 = fitmin(lambda x: combo(x,-1,0,Td), [0.31,101,0.7])
    rw2 = fitmin(lambda x: combo(x[:3],x[3],x[4],Td) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                 [0.32,100,0.7,-0.75,-0.8])
    dB = rw2.fun - rl2.fun
    # recover best-fit offset D at the w0wa solution
    om,hrd,h = rw2.x[:3]; g = W.comoving_grid(om,h,rw2.x[3],rw2.x[4])
    r = mu - 5*np.log10((1+zhel)*np.interp(zhd, W.ZGRID, g))
    T = np.column_stack(Td); A = T.T@icov@T; bb = T.T@icov@r
    coef = np.linalg.solve(A,bb); Dfit_w = coef[1]
    # and at the LCDM solution
    om,hrd,h = rl2.x; g = W.comoving_grid(om,h,-1,0)
    r = mu - 5*np.log10((1+zhel)*np.interp(zhd, W.ZGRID, g))
    bb = T.T@icov@r; coefL = np.linalg.solve(A,bb); Dfit_l = coefL[1]
    out["B_intercept_test"] = dict(dchi2=round(dB,1), sigma=round(sig2dof(dB),1),
                                   w0=round(rw2.x[3],3), wa=round(rw2.x[4],2),
                                   D_lowz_mag_at_w0wa=round(float(Dfit_w),4),
                                   D_lowz_mag_at_LCDM=round(float(Dfit_l),4),
                                   note="free magnitude offset on external (IDSURVEY!=10) low-z sample, analytically marginalized")
    print(f"B  +low-z intercept D:    dchi2={dB:+6.1f}  sigma={sig2dof(dB):.1f}  "
          f"w0={rw2.x[3]:+.3f} wa={rw2.x[4]:+.2f}   D(LCDM)={Dfit_l:+.4f} mag  D(w0wa)={Dfit_w:+.4f} mag")

    # ---- C: low-z cut sweep ----
    res = {}
    for zc in (0.0, 0.025, 0.05, 0.10):
        m = zhd > zc
        idx = np.where(m)[0]
        ic = icov[np.ix_(idx,idx)]   # NOTE: subsetting an inverse covariance is approximate
        # proper way: invert, subset, re-invert. N=1820 invert ~ fine once.
        pass
    C = np.linalg.inv(icov)
    for zc in (0.0, 0.025, 0.05, 0.10):
        idx = np.where(zhd > zc)[0]
        ic = np.linalg.inv(C[np.ix_(idx,idx)])
        o1 = np.ones(len(idx))
        def chi2_cut(om, h, w0, wa):
            g = W.comoving_grid(om, h, w0, wa)
            dl = (1+zhel[idx])*np.interp(zhd[idx], W.ZGRID, g)
            r = mu[idx] - 5*np.log10(dl)
            b = o1 @ ic @ r
            return r @ ic @ r - b*b/(o1 @ ic @ o1)
        def cc(x, w0, wa):
            om, hrd, h = x
            if not (0.1<om<0.6 and 80<hrd<120 and 0.5<h<0.9): return 1e10
            return W.chi2_bao(om, h, w0, wa, hrd/h) + chi2_cut(om, h, w0, wa)
        rl3 = fitmin(lambda x: cc(x,-1,0), [0.31,101,0.7])
        rw3 = fitmin(lambda x: cc(x[:3],x[3],x[4]) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                     [0.32,100,0.7,-0.75,-0.8])
        d3 = rw3.fun - rl3.fun
        res[f"z>{zc}"] = dict(n=len(idx), dchi2=round(d3,1), sigma=round(sig2dof(d3),1),
                              w0=round(rw3.x[3],3), wa=round(rw3.x[4],2))
        print(f"C  cut z>{zc:<6} N={len(idx):4d}  dchi2={d3:+6.1f}  sigma={sig2dof(d3):.1f}  "
              f"w0={rw3.x[3]:+.3f}  wa={rw3.x[4]:+.2f}")
    out["C_lowz_cut_sweep"] = res

    json.dump(out, open(f"{DATA}/../results/des5y.json","w"), indent=1)
    print("saved -> results/des5y.json")
