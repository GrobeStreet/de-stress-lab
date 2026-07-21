# Data provenance — download commands
All inputs are official public releases. Run from the `data/` directory. Nothing in this
repo's analysis uses any value not obtainable from these sources (see README provenance rules).

```bash
# Pantheon+ (official release: distances + full STAT+SYS covariance)
curl -sL -o pantheon_plus.dat "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES.dat"
curl -sL -o pantheon_plus_statsys.cov "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES_STAT%2BSYS.cov"

# DES-SN5YR, 2025 Dovekie release (Hubble diagram + inverse covariance)
curl -sL -o des_dovekie_hd.csv "https://raw.githubusercontent.com/des-science/DES-SN5YR/main/4_DISTANCES_COVMAT/DES-Dovekie_HD.csv"
curl -sL -o des_statsys.npz "https://raw.githubusercontent.com/des-science/DES-SN5YR/main/4_DISTANCES_COVMAT/STAT%2BSYS.npz"

# eBOSS DR16 LRG consensus (official SDSS values via cobaya bao_data)
curl -sL -O "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/sdss_DR16_BAOplus_LRG_FSBAO_DMDHfs8.dat"
curl -sL -O "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/sdss_DR16_BAOplus_LRG_FSBAO_DMDHfs8_covtot.txt"

# DESI DR2/DR1 BAO values + compressed-CMB prior: machine-extracted from the papers' arXiv HTML
curl -sL -o desi_dr2.html "https://arxiv.org/html/2503.14738v2"
curl -sL -o desi_dr1.html "https://arxiv.org/html/2404.03002v3"
# Extraction snippets are documented in the scripts and session record; the hardcoded values
# in scripts/fit_w0wa.py carry per-value provenance comments and can be re-verified against
# these files.
```

Planck 2018 native likelihood data (for lensing-leg/) installs via:
`cobaya-install planck_2018_lowl.TT planck_2018_lowl.EE planck_2018_highl_plik.TTTEEE_lite_native planck_2018_lensing.native --packages-path ../cobaya_packages`
