#!/usr/bin/env python3
"""
Null-mock test: empirical false-positive distribution of the w0wa preference.

Generate LCDM pseudo-data at the LCDM best fit of DESI+cCMB (Om=0.298, H0=68.4, wb=0.0222):
BAO 13-vector drawn from the published per-tracer (co)variances; CMB 3-vector from the
published compressed covariance. For each mock: fit LCDM and w0waCDM (same optimizer
settings as the real analysis), record dchi2. Accumulates across invocations.

Usage: python3 null_mocks.py ../data <n_mocks> <seed_offset>
Answers: how often does a pure-LCDM universe produce dchi2 <= -8.46 in THIS pipeline?
(Wilks 2-dof expectation: P(dchi2<=-8.46) = 1.45e-2... actually chi2.sf(8.46,2)=0.0146.)
"""
import numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_w0wa as W
from scipy import optimize

DATA = sys.argv[1]; NM = int(sys.argv[2]); OFF = int(sys.argv[3])
path = f"{DATA}/../results/null_mocks.json"
store = json.load(open(path)) if os.path.exists(path) else {"dchi2": []}

# truth: LCDM best fit of real DESI+cCMB
OM0, H0_, WB0 = 0.2976, 0.6837, 0.02223
rd0 = W.rd_model(OM0, H0_, WB0)
grid0 = W.comoving_grid(OM0, H0_, -1, 0)

# model predictions at truth
pred_dv = []
z, dv, s = W.BAO_DV[0]
dm = W.DM_Mpc(z, OM0, H0_, -1, 0, grid0)
dh = W.C_KMS/(100*H0_*np.sqrt(W.Ez2_late(z, OM0, H0_, -1, 0)))
pred_dv = (z*dm*dm*dh)**(1/3.)/rd0
pred_mh = []
for z, dmv, sm, dhv, sh, rho in W.BAO_MH:
    dmp = W.DM_Mpc(z, OM0, H0_, -1, 0, grid0)/rd0
    dhp = W.C_KMS/(100*H0_*np.sqrt(W.Ez2_late(z, OM0, H0_, -1, 0)))/rd0
    pred_mh.append((dmp, dhp))
th0 = W.theta_star(OM0, H0_, -1, 0, WB0)
wbc0 = OM0*H0_*H0_ - W.OMEGA_NU_MASSIVE_H2
cmb_pred = np.array([th0, WB0, wbc0])
CMB_CHOL = np.linalg.cholesky(W.CMB_COV)

def make_mock(rng):
    bao_dv = pred_dv + rng.standard_normal()*W.BAO_DV[0][2]
    mh = []
    for (dmp, dhp), (z, dmv, sm, dhv, sh, rho) in zip(pred_mh, W.BAO_MH):
        cov = np.array([[sm*sm, rho*sm*sh],[rho*sm*sh, sh*sh]])
        d = np.linalg.cholesky(cov) @ rng.standard_normal(2)
        mh.append((dmp+d[0], dhp+d[1]))
    cmb = cmb_pred + CMB_CHOL @ rng.standard_normal(3)
    return bao_dv, mh, cmb

def chi2_mock(x, w0, wa, mock):
    om, h, wb = x
    if not (0.2<om<0.55 and 0.5<h<0.85 and 0.019<wb<0.026): return 1e10
    bao_dv, mh, cmb = mock
    rd = W.rd_model(om, h, wb)
    grid = W.comoving_grid(om, h, w0, wa)
    z, _, s = W.BAO_DV[0]
    dm = W.DM_Mpc(z, om, h, w0, wa, grid)
    dh = W.C_KMS/(100*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))
    c2 = (((z*dm*dm*dh)**(1/3.)/rd - bao_dv)/s)**2
    for (dmo, dho), (z, dmv, sm, dhv, sh, rho) in zip(mh, W.BAO_MH):
        rm = W.DM_Mpc(z, om, h, w0, wa, grid)/rd - dmo
        rh = W.C_KMS/(100*h*np.sqrt(W.Ez2_late(z, om, h, w0, wa)))/rd - dho
        det = (sm*sh)**2*(1-rho*rho)
        c2 += (rm*rm*sh*sh - 2*rho*rm*rh*sm*sh + rh*rh*sm*sm)/det
    v = np.array([W.theta_star(om, h, w0, wa, wb), wb, om*h*h - W.OMEGA_NU_MASSIVE_H2]) - cmb
    return c2 + v @ W.CMB_ICOV @ v

opts = {"xatol":2e-5,"fatol":2e-5,"maxiter":1500}
for i in range(NM):
    rng = np.random.default_rng(10_000 + OFF + i)
    mock = make_mock(rng)
    rl = optimize.minimize(lambda x: chi2_mock(x,-1,0,mock), [OM0,H0_,WB0],
                           method="Nelder-Mead", options=opts)
    rw = optimize.minimize(lambda x: chi2_mock(x[:3],x[3],x[4],mock) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
                           [OM0+0.05, H0_-0.04, WB0, -0.5, -1.5],
                           method="Nelder-Mead", options=opts)
    store["dchi2"].append(round(min(0.0, rw.fun - rl.fun), 2))

d = np.array(store["dchi2"])
json.dump(store, open(path, "w"))
print(f"mocks total: {len(d)} | median dchi2 {np.median(d):.2f} | P(<=-4.74)={np.mean(d<=-4.74):.3f} "
      f"| P(<=-8.46)={np.mean(d<=-8.46):.3f} | min {d.min():.2f}")
