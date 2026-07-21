#!/usr/bin/env python3
"""
Week 2-4: w0waCDM fits with a compressed CMB likelihood.

All data inputs extracted from primary sources (see README provenance table):
- BAO: DESI DR2 summary values (arXiv:2503.14738v2 table)
- SN: Pantheon+ official release (full STAT+SYS covariance)
- CMB compressed: Gaussian in (theta*, omega_b, omega_bc),
  mu = (0.01041, 0.02223, 0.14208),
  C = 1e-9 * [[0.006621,0.12444,-1.1929],[0.12444,21.344,-94.001],[-1.1929,-94.001,1488.4]]
  (DR2 paper eqs. 35-36, CamSpec-based, late-time-marginalized)
- BBN prior: omega_b = 0.02218 +/- 0.00055 (DR2 paper eq. 14)
- theta* prior: 100*theta* = 1.04110 +/- 0.00053 (DR2 paper eq. 16)

VALIDATION GATES (must pass before any w0wa result is interpreted):
  G1: integral rd reproduces the paper's own fitting formula
      rd = 147.05 (wb/0.02236)^-0.13 (wbc/0.1432)^-0.23 Mpc  to <0.3%
  G2: LCDM DESI+BBN+theta* reproduces published Om = 0.2967+/-0.0045, H0 = 68.45+/-0.47

Early-universe pieces (z*, zdrag fitting formulas: Hu & Sugiyama 1996 / Eisenstein & Hu 1998)
are implemented from standard literature and are VALIDATED by gates G1/G2 rather than trusted.
Massive-neutrino treatment: Neff=3.044 massless in radiation for early integrals; 0.06 eV
counted in Omega_m at late times (standard approximation; documented simplification).
"""
import numpy as np
from scipy import integrate, optimize, linalg
import json, sys

C_KMS = 299792.458
OMEGA_GAMMA_H2 = 2.4729e-5          # T_CMB = 2.7255 K
NEFF = 3.044
OMEGA_R_H2 = OMEGA_GAMMA_H2 * (1 + 7.0/8.0 * (4.0/11.0)**(4.0/3.0) * NEFF)
OMEGA_NU_MASSIVE_H2 = 0.06 / 93.14  # counted in late-time Omega_m

# ---------------- early universe ----------------
def z_star(wb, wm):   # Hu & Sugiyama 1996
    g1 = 0.0783 * wb**-0.238 / (1 + 39.5 * wb**0.763)
    g2 = 0.560 / (1 + 21.1 * wb**1.81)
    return 1048 * (1 + 0.00124 * wb**-0.738) * (1 + g1 * wm**g2)

def z_drag(wb, wm):   # Eisenstein & Hu 1998
    b1 = 0.313 * wm**-0.419 * (1 + 0.607 * wm**0.674)
    b2 = 0.238 * wm**0.223
    return 1291 * wm**0.251 / (1 + 0.659 * wm**0.828) * (1 + b1 * wb**b2)

def sound_horizon(z_end, wb, wm):
    """Comoving sound horizon (Mpc) at z_end, integrating a(z) from 0 to 1/(1+z_end)."""
    def integrand(a):
        R = 3.0 * wb / (4.0 * OMEGA_GAMMA_H2) * a
        cs = C_KMS / np.sqrt(3.0 * (1 + R))
        H = 100.0 * np.sqrt(OMEGA_R_H2 + wm * a) / a**2   # early: rad + matter only
        return cs / (a * a * H) * a * a                     # dz = -da/a^2 ; ds = cs dz / H
    a_end = 1.0 / (1 + z_end)
    val, _ = integrate.quad(lambda a: (C_KMS / np.sqrt(3.0 * (1 + 3.0*wb/(4.0*OMEGA_GAMMA_H2)*a)))
                            / (a**2 * 100.0 * np.sqrt((OMEGA_R_H2 + wm*a)/a**4)),
                            1e-8, a_end, limit=200)
    return val

def rd_paper_formula(wb, wbc):
    return 147.05 * (wb/0.02236)**-0.13 * (wbc/0.1432)**-0.23

# CALIBRATED SURROGATE (audit-corrected docs): TWO separate empirical constants are used.
# _RD_CAL (~0.9768, a 2.32% correction) pins the rd integral to the paper's CAMB-calibrated
# formula at its pivot. _RS_CAL (~1.00125) separately anchors theta* to the paper's CMB-alone
# LCDM column. G1 tests rd SCALING after pivot normalization; G2 is a partially circular
# integration test (its anchor is related to the published CMB values). This module is a
# calibrated surrogate, NOT an independent early-universe prediction — CLASS/CAMB required
# for proof-grade claims (see camb_check.py; anchor +/-1sigma moves dchi2 by ~-6.1..-11.1).
# NOTE: DESI's baseline CPL analysis imposes early matter domination (w0+wa<0); our best fits
# satisfy it, but posterior sampling must impose it explicitly.
_RD_CAL = None
def rd_cal():
    global _RD_CAL
    if _RD_CAL is None:
        _RD_CAL = rd_paper_formula(0.02236, 0.1432) / sound_horizon(z_drag(0.02236, 0.1432), 0.02236, 0.1432)
    return _RD_CAL

# ---------------- late universe ----------------
ZGRID = np.linspace(0, 3.0, 3000)

def Ez2_late(z, om, h, w0, wa):
    wr = OMEGA_R_H2 / h**2
    ode = 1.0 - om - wr
    fde = (1+z)**(3*(1+w0+wa)) * np.exp(-3*wa*z/(1+z))
    return wr*(1+z)**4 + om*(1+z)**3 + ode*fde

def comoving_grid(om, h, w0, wa):
    ez = np.sqrt(Ez2_late(ZGRID, om, h, w0, wa))
    return integrate.cumulative_trapezoid(1.0/ez, ZGRID, initial=0)  # in units c/H0

def DM_Mpc(z, om, h, w0, wa, grid=None):
    g = grid if grid is not None else comoving_grid(om, h, w0, wa)
    dc = np.interp(z, ZGRID, g)
    return dc * C_KMS / (100.0*h)

def DM_to_zstar(zs, om, h, w0, wa):
    """Comoving distance to z* : late grid to z=3 + integral 3..z* with rad+matter+DE."""
    g = comoving_grid(om, h, w0, wa)
    dc3 = g[-1]
    val, _ = integrate.quad(lambda z: 1.0/np.sqrt(Ez2_late(z, om, h, w0, wa)), 3.0, zs, limit=200)
    return (dc3 + val) * C_KMS / (100.0*h)

# ---------------- likelihood pieces ----------------
BAO_DV = [(0.295, 7.942, 0.075)]
BAO_MH = [(0.510,13.588,0.167,21.863,0.425,-0.459),(0.706,17.351,0.177,19.455,0.330,-0.404),
          (0.934,21.576,0.152,17.641,0.193,-0.416),(1.321,27.601,0.318,14.176,0.221,-0.434),
          (1.484,30.512,0.760,12.817,0.516,-0.500),(2.330,38.988,0.531,8.632,0.101,-0.431)]

def chi2_bao(om, h, w0, wa, rd):
    grid = comoving_grid(om, h, w0, wa)
    c2 = 0.0
    for z, dv, s in BAO_DV:
        dm = DM_Mpc(z, om, h, w0, wa, grid); dh = C_KMS/(100.0*h*np.sqrt(Ez2_late(z,om,h,w0,wa)))
        c2 += (((z*dm*dm*dh)**(1/3.)/rd - dv)/s)**2
    for z, dmv, sm, dhv, sh, r in BAO_MH:
        dm = DM_Mpc(z, om, h, w0, wa, grid)/rd - dmv
        dh = C_KMS/(100.0*h*np.sqrt(Ez2_late(z,om,h,w0,wa)))/rd - dhv
        det = (sm*sh)**2*(1-r*r)
        c2 += (dm*dm*sh*sh - 2*r*dm*dh*sm*sh + dh*dh*sm*sm)/det
    return c2

CMB_MU = np.array([0.01041, 0.02223, 0.14208])
CMB_COV = 1e-9*np.array([[0.006621,0.12444,-1.1929],[0.12444,21.344,-94.001],[-1.1929,-94.001,1488.4]])
CMB_ICOV = np.linalg.inv(CMB_COV)

def _theta_star_raw(om, h, w0, wa, wb):
    wbc = om*h*h - OMEGA_NU_MASSIVE_H2   # baryons+CDM (DESI convention)
    zs = z_star(wb, wbc)
    rstar = sound_horizon(zs, wb, wbc)
    return rstar / DM_to_zstar(zs, om, h, w0, wa)

# r* anchor: the paper's own CMB-alone LCDM column (Om=0.3169, H0=67.14) must map the
# compressed-prior means (theta*=0.0104110 at wb=0.02223, wbc=0.14208) onto themselves.
# One constant; theta* SCALING with parameters remains a genuine prediction tested by G2.
_RS_CAL = None
def rs_cal():
    global _RS_CAL
    if _RS_CAL is None:
        h_anchor = 0.6714                     # paper CMB column H0=67.14
        om_anchor = (0.14208 + OMEGA_NU_MASSIVE_H2) / h_anchor**2
        _RS_CAL = 0.0104110 / _theta_star_raw(om_anchor, h_anchor, -1, 0, 0.02223)
    return _RS_CAL

def theta_star(om, h, w0, wa, wb):
    return rs_cal() * _theta_star_raw(om, h, w0, wa, wb)

def chi2_cmb3(om, h, w0, wa, wb):
    wbc = om*h*h - OMEGA_NU_MASSIVE_H2
    v = np.array([theta_star(om, h, w0, wa, wb), wb, wbc]) - CMB_MU
    return v @ CMB_ICOV @ v

def rd_model(om, h, wb):
    wbc = om*h*h - OMEGA_NU_MASSIVE_H2
    return rd_cal() * sound_horizon(z_drag(wb, wbc), wb, wbc)

# SN
def sn_factory(data_dir):
    raw = np.genfromtxt(f"{data_dir}/pantheon_plus.dat", names=True, dtype=None, encoding=None)
    n = len(raw); C = np.loadtxt(f"{data_dir}/pantheon_plus_statsys.cov", skiprows=1).reshape(n,n)
    m = (raw["zHD"]>0.01)&(raw["IS_CALIBRATOR"]==0); i = np.where(m)[0]
    zhd, zhel, mb = raw["zHD"][i], raw["zHEL"][i], raw["m_b_corr"][i]
    cho = linalg.cho_factor(C[np.ix_(i,i)]); ones = np.ones(len(i))
    e = ones @ linalg.cho_solve(cho, ones)
    def chi2(om, h, w0, wa):
        g = comoving_grid(om, h, w0, wa)
        dl = (1+zhel)*np.interp(zhd, ZGRID, g)
        r = mb - 5*np.log10(dl)
        cr = linalg.cho_solve(cho, r)
        return r @ cr - (ones @ cr)**2/e
    return chi2

BBN = (0.02218, 0.00055)
THSTAR = (0.0104110, 0.0000053)

def fit(chi2f, x0, bounds):
    best = None
    for seed in range(3):
        x = np.array(x0) * (1 + 0.02*np.random.default_rng(seed).standard_normal(len(x0)))
        r = optimize.minimize(chi2f, x, method="Nelder-Mead",
                              options={"xatol":1e-5,"fatol":1e-6,"maxiter":4000})
        if best is None or r.fun < best.fun: best = r
    return best

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv)>1 else "../data"
    out = {}
    rng = np.random.default_rng(0)

    # ---- Gate G1: rd integral vs paper formula ----
    errs = []
    for wb in (0.021, 0.02236, 0.0235):
        for wbc in (0.135, 0.1432, 0.150):
            errs.append(abs(rd_cal()*sound_horizon(z_drag(wb,wbc), wb, wbc)/rd_paper_formula(wb,wbc)-1))
    g1 = max(errs)
    print(f"G1 rd scaling (pivot-calibrated) vs paper formula: max dev = {g1*100:.2f}%  ({'PASS' if g1<0.003 else 'FAIL'})")
    out["gate_G1_rd_max_dev_pct"] = round(g1*100, 3)

    # ---- Gate G2: LCDM DESI + BBN + theta* ----
    def chi2_g2(x):
        om, h, wb = x
        if not (0.2<om<0.45 and 0.55<h<0.8 and 0.019<wb<0.026): return 1e10
        rd = rd_model(om, h, wb)
        c = chi2_bao(om, h, -1, 0, rd)
        c += ((wb-BBN[0])/BBN[1])**2
        c += ((theta_star(om, h, -1, 0, wb)-THSTAR[0])/THSTAR[1])**2
        return c
    r = fit(chi2_g2, [0.30, 0.68, 0.0222], None)
    om2, h2, wb2 = r.x
    print(f"G2 LCDM DESI+BBN+theta*: Om={om2:.4f} H0={100*h2:.2f}  (target 0.2967+/-0.0045, 68.45+/-0.47)  chi2={r.fun:.2f}")
    ok2 = abs(om2-0.2967)<0.0045 and abs(100*h2-68.45)<0.47
    print(f"   {'PASS' if ok2 else 'FAIL'} (within 1 published sigma)")
    out["gate_G2"] = dict(Om=round(om2,4), H0=round(100*h2,2), chi2=round(r.fun,2), passed=bool(ok2))

    if g1 >= 0.003 or not ok2:
        print("VALIDATION FAILED — stopping before w0wa per protocol."); json.dump(out, open(f"{data_dir}/../results/w0wa.json","w"), indent=1); sys.exit(1)

    chi2_sn = sn_factory(data_dir)

    # ---- Run 1: DESI alone, LCDM vs w0wa (rd free -> use A param via rd as free scale) ----
    def c_desi(x, w0, wa):
        om, hrd = x   # hrd = h*rd in Mpc; rd enters only via h*rd for BAO-alone
        if not (0.1<om<0.6 and 80<hrd<120): return 1e10
        rd_eff = hrd/0.68  # fix h=0.68 internally; only product matters
        return chi2_bao(om, 0.68, w0, wa, rd_eff)
    rl = fit(lambda x: c_desi(x,-1,0), [0.297,101.5], None)
    rw = fit(lambda x: c_desi(x[:2], x[2], x[3]) if (-3<x[2]<1 and -5<x[3]<3) else 1e10,
             [0.35, 99, -0.5, -1.3], None)
    d1 = rw.fun - rl.fun
    out["run1_DESI_alone"] = dict(dchi2=round(d1,1), target=-4.7,
                                  w0=round(rw.x[2],2), wa=round(rw.x[3],2))
    print(f"Run1 DESI alone:      dchi2(w0wa-LCDM) = {d1:+.1f}   (target -4.7)   w0={rw.x[2]:.2f} wa={rw.x[3]:.2f}")

    # ---- Run 2: DESI + Pantheon+ ----
    def c_dsn(x, w0, wa):
        om, hrd, h = x
        if not (0.1<om<0.6 and 80<hrd<120 and 0.5<h<0.9): return 1e10
        return chi2_bao(om, h, w0, wa, hrd/h) + chi2_sn(om, h, w0, wa)
    rl2 = fit(lambda x: c_dsn(x,-1,0), [0.31,101,0.7], None)
    rw2 = fit(lambda x: c_dsn(x[:3],x[3],x[4]) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
              [0.30,101,0.7,-0.89,-0.2], None)
    d2 = rw2.fun - rl2.fun
    out["run2_DESI_SN"] = dict(dchi2=round(d2,1), target=-4.9,
                               w0=round(rw2.x[3],3), wa=round(rw2.x[4],2),
                               target_w0="-0.888+0.055-0.064", target_wa="-0.17+/-0.46",
                               Om=round(rw2.x[0],3))
    print(f"Run2 DESI+Pantheon+:  dchi2 = {d2:+.1f}   (target -4.9)   w0={rw2.x[3]:.3f} (tgt -0.888)  wa={rw2.x[4]:.2f} (tgt -0.17)  Om={rw2.x[0]:.3f}")

    # ---- Run 3: DESI + compressed CMB ----
    def c_dcmb(x, w0, wa):
        om, h, wb = x
        if not (0.2<om<0.55 and 0.55<h<0.8 and 0.019<wb<0.026): return 1e10
        rd = rd_model(om, h, wb)
        return chi2_bao(om, h, w0, wa, rd) + chi2_cmb3(om, h, w0, wa, wb)
    rl3 = fit(lambda x: c_dcmb(x,-1,0), [0.30,0.68,0.0222], None)
    rw3 = fit(lambda x: c_dcmb(x[:3],x[3],x[4]) if (-3<x[3]<1 and -5<x[4]<3) else 1e10,
              [0.35,0.64,0.0222,-0.45,-1.7], None)
    d3 = rw3.fun - rl3.fun
    out["run3_DESI_cCMB"] = dict(dchi2=round(d3,1), target=-8.0,
                                 w0=round(rw3.x[3],2), wa=round(rw3.x[4],2),
                                 target_w0="~ -0.43+/-0.21 (paper: compressed ~ full)",
                                 Om=round(rw3.x[0],3), H0=round(100*rw3.x[1],1))
    print(f"Run3 DESI+cCMB:       dchi2 = {d3:+.1f}   (target -8.0)   w0={rw3.x[3]:.2f} wa={rw3.x[4]:.2f}  Om={rw3.x[0]:.3f} H0={100*rw3.x[1]:.1f}")

    # significance conversion (2 dof)
    from scipy import stats
    for k, d in [("run1",d1),("run2",d2),("run3",d3)]:
        p = stats.chi2.sf(-d, 2); ns = stats.norm.isf(p/2)
        out[k+"_sigma"] = round(float(ns),1)
        print(f"   {k}: {ns:.1f} sigma equivalent")

    json.dump(out, open(f"{data_dir}/../results/w0wa.json","w"), indent=1)
    print("saved -> results/w0wa.json")
