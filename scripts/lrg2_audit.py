#!/usr/bin/env python3
"""
Gate 1 (public-data version): the LRG2 audit.

The z~0.7 BAO measurement across three analyses:
  eBOSS DR16 (z=0.698): DM/rd=17.646+/-0.302, DH/rd=19.770+/-0.469, r=-0.239
      [official cobaya bao_data release of SDSS DR16 LRG consensus]
  DESI DR1  (z=0.706): DM/rd=16.85+/-0.32,  DH/rd=20.08+/-0.60,  r=-0.420  [arXiv:2404.03002 Table]
  DESI DR2  (z=0.706): DM/rd=17.351+/-0.177, DH/rd=19.455+/-0.330, r=-0.404 [arXiv:2503.14738]

Tests (DESI+cCMB frame):
  T1: sigma-distance of each z~0.7 measurement from the LCDM best-fit prediction.
  T2: SWAP test — replace DR2 LRG2 with the INDEPENDENT eBOSS point; refit LCDM & w0wa.
  T3: SWAP with DESI DR1 LRG2 (not independent — same instrument, subset sky — but shows
      the DR1->DR2 evolution's effect on the preference).
CAVEATS: eBOSS/DESI footprints partially overlap (not fully independent); zeff differs
(0.698 vs 0.706 — model evaluated at each point's own zeff); eBOSS value is the BAO+FS
consensus (fs8 row dropped, DM/DH block used).
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from scipy import optimize, stats

POINTS = {
 "eBOSS_DR16": dict(z=0.698, dm=17.645955, sm=0.302, dh=19.769664, sh=0.469, r=-0.239),
 "DESI_DR1":   dict(z=0.706, dm=16.85,     sm=0.32,  dh=20.08,     sh=0.60,  r=-0.420),
 "DESI_DR2":   dict(z=0.706, dm=17.351,    sm=0.177, dh=19.455,    sh=0.330, r=-0.404),
}

def sig2(dd): return float(stats.norm.isf(stats.chi2.sf(-dd, 2)/2))

def chi2_point(p, om, h, w0, wa, rd):
    grid = W.comoving_grid(om, h, w0, wa)
    dmm = W.DM_Mpc(p["z"], om, h, w0, wa, grid)/rd - p["dm"]
    dhm = W.C_KMS/(100*h*np.sqrt(W.Ez2_late(p["z"], om, h, w0, wa)))/rd - p["dh"]
    det = (p["sm"]*p["sh"])**2*(1-p["r"]**2)
    return (dmm*dmm*p["sh"]**2 - 2*p["r"]*dmm*dhm*p["sm"]*p["sh"] + dhm*dhm*p["sm"]**2)/det

def chi2_swap(x, w0, wa, sub):
    """DESI+cCMB with the LRG2 slot (index 1 of BAO_MH) replaced by `sub` (or dropped if None)."""
    om, h, wb = x
    if not (0.2<om<0.55 and 0.5<h<0.85 and 0.019<wb<0.026): return 1e10
    rd = W.rd_model(om, h, wb)
    grid = W.comoving_grid(om, h, w0, wa)
    z, dv, s = W.BAO_DV[0]
    dm = W.DM_Mpc(z, om, h, w0, wa, grid)
    dh = W.C_KMS/(100*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))
    c2 = (((z*dm*dm*dh)**(1/3.)/rd - dv)/s)**2
    for j,(z, dmv, sm, dhv, sh, rho) in enumerate(W.BAO_MH):
        if j == 1: continue
        rm = W.DM_Mpc(z, om, h, w0, wa, grid)/rd - dmv
        rh = W.C_KMS/(100*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))/rd - dhv
        det = (sm*sh)**2*(1-rho*rho)
        c2 += (rm*rm*sh*sh - 2*rho*rm*rh*sm*sh + rh*rh*sm*sm)/det
    if sub is not None:
        c2 += chi2_point(sub, om, h, w0, wa, rd)
    return c2 + W.chi2_cmb3(om, h, w0, wa, wb)

def fitpair(sub):
    rl = optimize.minimize(lambda x: chi2_swap(x,-1,0,sub), [0.298,0.684,0.0222],
                           method="Nelder-Mead", options={"xatol":1e-5,"fatol":1e-6,"maxiter":3000})
    rw = optimize.minimize(lambda x: chi2_swap(x[:3],x[3],x[4],sub) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                           [0.35,0.64,0.0222,-0.45,-1.7],
                           method="Nelder-Mead", options={"xatol":1e-5,"fatol":1e-6,"maxiter":4000})
    return rw.fun - rl.fun, rw.x

if __name__ == "__main__":
    DATA = sys.argv[1] if len(sys.argv)>1 else "../data"
    out = {}
    # T1: tension of each z~0.7 point vs LCDM best fit of the FULL DESI+cCMB combo
    om0, h0, wb0 = 0.2976, 0.6837, 0.02223
    rd0 = W.rd_model(om0, h0, wb0)
    print("T1: distance from LCDM best-fit prediction (DESI+cCMB frame):")
    t1 = {}
    for name, p in POINTS.items():
        c2 = chi2_point(p, om0, h0, -1, 0, rd0)
        gs = float(stats.norm.isf(stats.chi2.sf(c2, 2)/2))
        grid = W.comoving_grid(om0, h0, -1, 0)
        dm_pred = W.DM_Mpc(p["z"], om0, h0, -1, 0, grid)/rd0
        dh_pred = W.C_KMS/(100*h0*np.sqrt(W.Ez2_late(p["z"], om0, h0, -1, 0)))/rd0
        zm = (p["dm"]-dm_pred)/p["sm"]; zh = (p["dh"]-dh_pred)/p["sh"]
        t1[name] = dict(joint_chi2=round(c2,2), joint_sigma=round(gs,2),
                        zscore_DM=round(zm,2), zscore_DH=round(zh,2))
        print(f"  {name:11s} joint {gs:.2f}sig  (DM {zm:+.2f}sig, DH {zh:+.2f}sig)")
    out["T1_tension_vs_LCDM"] = t1

    # T2/T3: swap tests
    print("T2/T3: DESI+cCMB with the z~0.7 slot filled by:")
    t2 = {}
    for label, sub in [("DESI_DR2 (baseline)", POINTS["DESI_DR2"]),
                       ("eBOSS_DR16 (independent)", POINTS["eBOSS_DR16"]),
                       ("DESI_DR1", POINTS["DESI_DR1"]),
                       ("none (dropped)", None)]:
        d, xw = fitpair(sub)
        t2[label] = dict(dchi2=round(d,1), sigma=round(sig2(d),1),
                         w0=round(xw[3],2), wa=round(xw[4],2))
        print(f"  {label:26s} dchi2={d:+6.1f}  sigma={sig2(d):.1f}  w0={xw[3]:+.2f} wa={xw[4]:+.2f}")
    out["T2_T3_swap"] = t2

    json.dump(out, open(f"{DATA}/../results/lrg2_audit.json","w"), indent=1)
    print("saved -> results/lrg2_audit.json")
