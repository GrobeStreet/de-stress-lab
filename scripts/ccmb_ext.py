#!/usr/bin/env python3
"""
Week 6-7 extensions.

Mode `intercept`: attach the compressed CMB to the Efstathiou test.
   DESI + cCMB + DES5Y(Dovekie): LCDM vs w0waCDM, with and without the free
   magnitude offset D on the external low-z sample.
   (Published full-CMB row: -21.0 / 4.2 sigma with the 2024 release. Our cCMB
   analog is expected lower — cCMB carried -8.5 of the full -12.5 for DESI+CMB.)

Mode `wz`: parameterization swap on the anchored combos.
   How much of the "evolving dark energy" preference depends on the CPL form?
   Families (all reduce to LCDM at w0=-1, wa=0):
     CPL : w = w0 + wa z/(1+z)        rho_DE = (1+z)^{3(1+w0+wa)} exp(-3 wa z/(1+z))
     JBP : w = w0 + wa z/(1+z)^2      rho_DE = (1+z)^{3(1+w0)} exp(+1.5 wa (z/(1+z))^2)
     LOG : w = w0 + wa ln(1+z)        rho_DE = (1+z)^{3(1+w0)} exp(+1.5 wa ln^2(1+z))
     wCDM: w = w0 (1 dof)
   Run on DESI+cCMB and DESI+cCMB+DES5Y; report dchi2 and sigma-equivalent
   (2 dof; 1 dof for wCDM).
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from fit_des5y import load_des
from scipy import optimize, stats, integrate

def make_Ez2(mode):
    def Ez2(z, om, h, w0, wa):
        wr = W.OMEGA_R_H2 / h**2
        ode = 1.0 - om - wr
        z = np.asarray(z, dtype=float)
        if mode == "CPL":
            fde = (1+z)**(3*(1+w0+wa)) * np.exp(-3*wa*z/(1+z))
        elif mode == "JBP":
            fde = (1+z)**(3*(1+w0)) * np.exp(1.5*wa*(z/(1+z))**2)
        elif mode == "LOG":
            fde = (1+z)**(3*(1+w0)) * np.exp(1.5*wa*np.log1p(z)**2)
        elif mode == "wCDM":
            fde = (1+z)**(3*(1+w0))
        else:
            raise ValueError(mode)
        return wr*(1+z)**4 + om*(1+z)**3 + ode*fde
    return Ez2

def set_mode(mode):
    W.Ez2_late = make_Ez2(mode)   # all W internals route through this

def sig(dd, dof):
    return float(stats.norm.isf(stats.chi2.sf(-dd, dof)/2))

def fitmin(f, x0):
    best = None
    for seed in range(3):
        x = np.array(x0)*(1+0.02*np.random.default_rng(seed).standard_normal(len(x0)))
        r = optimize.minimize(f, x, method="Nelder-Mead",
                              options={"xatol":1e-5,"fatol":1e-6,"maxiter":5000})
        if best is None or r.fun < best.fun: best = r
    return best

DATA = sys.argv[1] if len(sys.argv)>1 else "../data"
MODE = sys.argv[2] if len(sys.argv)>2 else "intercept"
zhd, zhel, mu, icov, ids = load_des(DATA)
lowz = (ids != 10).astype(float)
ones = np.ones(len(zhd))

def chi2_des(om, h, w0, wa, templates):
    g = W.comoving_grid(om, h, w0, wa)
    dl = (1+zhel)*np.interp(zhd, W.ZGRID, g)
    r = mu - 5*np.log10(dl)
    T = np.column_stack(templates)
    A = T.T @ icov @ T; b = T.T @ icov @ r
    return r @ icov @ r - b @ np.linalg.solve(A, b)

def combo3(x, w0, wa, templates=None):
    om, h, wb = x
    if not (0.2<om<0.55 and 0.5<h<0.85 and 0.019<wb<0.026): return 1e10
    rd = W.rd_model(om, h, wb)
    c = W.chi2_bao(om, h, w0, wa, rd) + W.chi2_cmb3(om, h, w0, wa, wb)
    if templates is not None:
        c += chi2_des(om, h, w0, wa, templates)
    return c

out_path = f"{DATA}/../results/ccmb_ext.json"
out = json.load(open(out_path)) if os.path.exists(out_path) else {}

if MODE == "intercept":
    set_mode("CPL")
    res = {}
    for label, T in [("baseline_M_only", [ones]), ("with_lowz_intercept", [ones, lowz])]:
        rl = fitmin(lambda x: combo3(x,-1,0,T), [0.31,0.67,0.0222])
        rw = fitmin(lambda x: combo3(x[:3],x[3],x[4],T) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                    [0.33,0.66,0.0222,-0.7,-1.0])
        d = rw.fun - rl.fun
        res[label] = dict(dchi2=round(d,1), sigma=round(sig(d,2),1),
                          w0=round(rw.x[3],3), wa=round(rw.x[4],2),
                          Om=round(rw.x[0],3), H0=round(100*rw.x[1],1))
        print(f"{label:22s} dchi2={d:+6.1f}  sigma={sig(d,2):.1f}  w0={rw.x[3]:+.3f} wa={rw.x[4]:+.2f}  Om={rw.x[0]:.3f} H0={100*rw.x[1]:.1f}")
        if label == "with_lowz_intercept":
            om,h,wb = rl.x
            g = W.comoving_grid(om,h,-1,0)
            r = mu - 5*np.log10((1+zhel)*np.interp(zhd, W.ZGRID, g))
            Tm = np.column_stack(T); A = Tm.T@icov@Tm; b = Tm.T@icov@r
            res[label]["D_mag_at_LCDM"] = round(float(np.linalg.solve(A,b)[1]),4)
            print(f"{'':22s} fitted low-z offset at LCDM: D = {res[label]['D_mag_at_LCDM']:+.4f} mag")
    out["intercept_DESI_cCMB_DES5Y"] = res

elif MODE == "wz":
    res = {}
    for combo_label, use_des in [("DESI+cCMB", False), ("DESI+cCMB+DES5Y", True)]:
        T = [ones] if use_des else None
        row = {}
        set_mode("CPL")
        rl = fitmin(lambda x: combo3(x,-1,0,T), [0.31,0.67,0.0222])
        for mode, dof, x0w in [("CPL",2,[-0.6,-1.4]), ("JBP",2,[-0.6,-2.0]),
                               ("LOG",2,[-0.6,-0.8]), ("wCDM",1,[-0.9,0.0])]:
            set_mode(mode)
            # LCDM chi2 is mode-independent (w0=-1, wa=0 identical in all families) -> reuse rl.fun
            if mode == "wCDM":
                rw = fitmin(lambda x: combo3(x[:3],x[3],0,T) if (-3<x[3]<1) else 1e10,
                            [0.31,0.67,0.0222]+x0w[:1])
                w0b, wab = rw.x[3], 0.0
            else:
                rw = fitmin(lambda x: combo3(x[:3],x[3],x[4],T) if (-3<x[3]<1 and -8<x[4]<5) else 1e10,
                            [0.33,0.66,0.0222]+x0w)
                w0b, wab = rw.x[3], rw.x[4]
            d = rw.fun - rl.fun
            row[mode] = dict(dchi2=round(d,1), dof=dof, sigma=round(sig(d,dof),1),
                             w0=round(w0b,3), wa=round(wab,2))
            print(f"{combo_label:18s} {mode:5s} dchi2={d:+6.1f} ({dof}dof) sigma={sig(d,dof):.1f}  w0={w0b:+.3f} wa={wab:+.2f}")
        res[combo_label] = row
    out["wz_parameterization_swap"] = res

json.dump(out, open(out_path,"w"), indent=1)
print("saved ->", out_path)
