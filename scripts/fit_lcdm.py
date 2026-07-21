#!/usr/bin/env python3
"""
Dark-Energy Stress Lab — Week 1: flat-LCDM reproduction runs.

Run 1: DESI DR2 BAO alone -> reproduce Om = 0.2975 +/- 0.0086, h*rd = 101.54 +/- 0.73 Mpc
       (targets: DESI DR2 BAO paper, arXiv:2503.14738v2, extracted from paper text 2026-07-19)
Run 2: Pantheon+ SNe alone (z>0.01, no calibrators, full STAT+SYS cov)
       -> target Om = 0.334 +/- 0.018 (Brout et al. 2022, arXiv:2202.04077) [target from lit, to re-verify]

BAO data: DR2 Table (arXiv:2503.14738v2), 7 tracers. DM/DH with r(M,H) correlation;
BGS uses DV only. Simplification vs official: Gaussian likelihood on published values
(this IS what the official 'bao' compressed likelihood does); radiation neglected in E(z)
(effect << errors at z<=2.33; documented caveat).
"""
import numpy as np
from scipy import integrate, optimize, linalg

C_KMS = 299792.458

# ---------- DESI DR2 BAO data (arXiv:2503.14738v2, summary table) ----------
# tracer: (zeff, DV/rd, sig)  or (zeff, DM/rd, sig, DH/rd, sig, r_MH)
BAO_DV = [("BGS", 0.295, 7.942, 0.075)]
BAO_MH = [
    ("LRG1",      0.510, 13.588, 0.167, 21.863, 0.425, -0.459),
    ("LRG2",      0.706, 17.351, 0.177, 19.455, 0.330, -0.404),
    ("LRG3+ELG1", 0.934, 21.576, 0.152, 17.641, 0.193, -0.416),
    ("ELG2",      1.321, 27.601, 0.318, 14.176, 0.221, -0.434),
    ("QSO",       1.484, 30.512, 0.760, 12.817, 0.516, -0.500),
    ("Lya",       2.330, 38.988, 0.531,  8.632, 0.101, -0.431),
]

def E(z, om):
    return np.sqrt(om * (1 + z) ** 3 + (1 - om))

def DM_over_rd(z, om, A):   # A = c / (H0 * rd)
    integ, _ = integrate.quad(lambda x: 1.0 / E(x, om), 0, z)
    return A * integ

def DH_over_rd(z, om, A):
    return A / E(z, om)

def DV_over_rd(z, om, A):
    dm, dh = DM_over_rd(z, om, A), DH_over_rd(z, om, A)
    return (z * dm * dm * dh) ** (1.0 / 3.0)

def chi2_bao(theta):
    om, A = theta
    if not (0.05 < om < 0.7 and 10 < A < 60):
        return 1e10
    c2 = 0.0
    for _, z, dv, s in BAO_DV:
        c2 += ((DV_over_rd(z, om, A) - dv) / s) ** 2
    for _, z, dm, sm, dh, sh, r in BAO_MH:
        rm = DM_over_rd(z, om, A) - dm
        rh = DH_over_rd(z, om, A) - dh
        det = (sm * sh) ** 2 * (1 - r * r)
        c2 += (rm * rm * sh * sh - 2 * r * rm * rh * sm * sh + rh * rh * sm * sm) / det
    return c2

# ---------- Pantheon+ SN likelihood ----------
def load_sn(data_dir):
    raw = np.genfromtxt(f"{data_dir}/pantheon_plus.dat", names=True, dtype=None, encoding=None)
    n = len(raw)
    cov_flat = np.loadtxt(f"{data_dir}/pantheon_plus_statsys.cov", skiprows=1)
    C = cov_flat.reshape(n, n)
    mask = (raw["zHD"] > 0.01) & (raw["IS_CALIBRATOR"] == 0)
    idx = np.where(mask)[0]
    return raw["zHD"][idx], raw["zHEL"][idx], raw["m_b_corr"][idx], C[np.ix_(idx, idx)], len(idx)

def mu_model(zhd, zhel, om):
    zs = np.sort(np.unique(np.concatenate([[0], zhd])))
    integ = integrate.cumulative_trapezoid(1.0 / E(np.linspace(0, zhd.max(), 4000), om),
                                           np.linspace(0, zhd.max(), 4000), initial=0)
    grid = np.linspace(0, zhd.max(), 4000)
    dc = np.interp(zhd, grid, integ)          # comoving distance / (c/H0)
    dl = (1 + zhel) * dc                       # luminosity distance / (c/H0)
    return 5 * np.log10(dl)                    # mu up to additive const (absorbed in M marg.)

def chi2_sn_factory(data_dir):
    zhd, zhel, mb, C, n = load_sn(data_dir)
    cho = linalg.cho_factor(C)
    ones = np.ones(n)
    Cinv_1 = linalg.cho_solve(cho, ones)
    e = ones @ Cinv_1
    def chi2(om):
        if not (0.05 < om < 0.7):
            return 1e10
        r = mb - mu_model(zhd, zhel, om)
        Cinv_r = linalg.cho_solve(cho, r)
        a = r @ Cinv_r
        b = ones @ Cinv_r
        return a - b * b / e            # analytic marginalization over offset (M, H0)
    return chi2, n

def uncertainty_1d(chi2f, xbest, span):
    # scan for delta-chi2 = 1 crossings
    xs = np.linspace(xbest - span, xbest + span, 201)
    c = np.array([chi2f(x) for x in xs]); c -= c.min()
    lo = xs[c < 1][0]; hi = xs[c < 1][-1]
    return (hi - lo) / 2

if __name__ == "__main__":
    import json, sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "../data"
    out = {}

    # --- Run 1: BAO alone ---
    res = optimize.minimize(chi2_bao, x0=[0.3, 30.0], method="Nelder-Mead",
                            options={"xatol": 1e-5, "fatol": 1e-7})
    om_b, A_b = res.x
    hrd = C_KMS / A_b / 100.0  # h * rd in Mpc
    # 1D uncertainties by profiling
    prof_om = lambda om: optimize.minimize_scalar(lambda A: chi2_bao([om, A]),
                bounds=(20, 40), method="bounded").fun
    prof_A = lambda A: optimize.minimize_scalar(lambda om: chi2_bao([om, A]),
                bounds=(0.15, 0.5), method="bounded").fun
    som = uncertainty_1d(prof_om, om_b, 0.03)
    sA = uncertainty_1d(prof_A, A_b, 0.35)
    shrd = hrd * sA / A_b
    ndof = 1 + 6 * 2 - 2
    out["bao_alone"] = dict(Om=round(om_b, 4), Om_err=round(som, 4),
                            hrd_Mpc=round(hrd, 2), hrd_err=round(shrd, 2),
                            chi2_min=round(res.fun, 2), ndata=13, nparam=2,
                            target="Om=0.2975+/-0.0086, hrd=101.54+/-0.73 (arXiv:2503.14738)")
    print("BAO alone:  Om = %.4f +/- %.4f   (target 0.2975 +/- 0.0086)" % (om_b, som))
    print("            h*rd = %.2f +/- %.2f Mpc (target 101.54 +/- 0.73)" % (hrd, shrd))
    print("            chi2_min = %.2f for 13 data, 2 params" % res.fun)

    # --- Run 2: SN alone ---
    chi2_sn, nsn = chi2_sn_factory(data_dir)
    r2 = optimize.minimize_scalar(chi2_sn, bounds=(0.1, 0.6), method="bounded")
    om_s = r2.x
    som_s = uncertainty_1d(chi2_sn, om_s, 0.06)
    out["sn_alone"] = dict(Om=round(om_s, 4), Om_err=round(som_s, 4),
                           chi2_min=round(r2.fun, 2), n_sne=int(nsn),
                           cuts="zHD>0.01, IS_CALIBRATOR==0, full STAT+SYS cov, M marginalized",
                           target="Om=0.334+/-0.018 (arXiv:2202.04077) [to re-verify]")
    print("SN alone:   Om = %.4f +/- %.4f   (target 0.334 +/- 0.018), N_SN = %d, chi2 = %.1f"
          % (om_s, som_s, nsn, r2.fun))

    json.dump(out, open(f"{data_dir}/../results/lcdm_reproduction.json", "w"), indent=1)
    print("saved -> results/lcdm_reproduction.json")
