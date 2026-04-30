# Exploring Cryptocurrency Price Dynamics and Predictability with Ordinal Networks

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Companion code for the manuscript *"Exploring Cryptocurrency Price Dynamics and Predictability with Ordinal Networks"* (submitted to *Physica A: Statistical Mechanics and its Applications*).

---

## Overview

This repository applies **ordinal network analysis** — combining permutation entropy (PE), ordinal transition matrices, and spectral gap analysis — to characterize price dynamics and return predictability for eight major cryptocurrencies over a six-year period (April 2020 – April 2026, 2,210 daily observations).

**Cryptocurrencies studied:** BTC, ETH, BNB, SOL, XRP, ADA, DOGE, LTC

### Key findings

1. **Near-maximal ordinal entropy across all coins** — PE ∈ [0.9995, 0.9999] with no forbidden ordinal patterns, consistent with weak-form market efficiency at the daily scale.
2. **No nonlinear structure detectable** — Surrogate tests (500 IAAFT surrogates per coin) yield z-scores ∈ [−1.14, +0.24]; all p > 0.05. Daily returns are statistically indistinguishable from phase-randomized processes.
3. **Regime-dependent efficiency** — 7/8 coins show significant PE variation across five market regimes (Kruskal-Wallis, p < 0.001); ETH is the sole exception (H = 3.43, p = 0.489), exhibiting regime-invariant efficiency.
4. **Predictability is near chance** — Walk-forward accuracy: 48–52% across all models. No ordinal classifier significantly outperforms ARIMA(1,0,1), GARCH(1,1), or naïve baselines after Diebold-Mariano testing with Bonferroni correction (24 tests, α/24 = 0.0021). Best accuracy: 52.36% for SOL (Random Forest).

---

## Repository structure

```
.
├── data.ipynb                      # Data download from CryptoCompare API
├── 01_ordinal_network.ipynb        # Ordinal pattern encoding & network construction
├── 02_permutation_entropy.ipynb    # PE computation, bootstrap CIs
├── 03_surrogate_test.ipynb         # IAAFT surrogate significance tests
├── 04_time_varying_pe.ipynb        # Rolling PE analysis
├── 05_regime_analysis.ipynb        # Kruskal-Wallis & Mann-Whitney regime tests
├── 06_walkforward.ipynb            # Walk-forward prediction (LogReg, RF, GBM, MLP)
├── 07_baseline.ipynb               # ARIMA(1,0,1) baseline
├── 08_manuscript.ipynb             # Full manuscript draft (Physica A format)
├── 09_enhanced_baseline.ipynb      # Extended baselines: GARCH(1,1), Persistence,
│                                   #   Majority Vote, Random Walk
├── data/
│   ├── crypto_prices.csv           # Raw daily closing prices (8 coins × 2,210 days)
│   ├── walkforward_results.csv     # Walk-forward accuracy by model/coin/window
│   ├── enhanced_baseline_results.csv  # 1,952 rows: 8 coins × 4 baselines × 61 windows
│   ├── enhanced_final_comparison.csv  # Summary comparison table
│   ├── surrogate_test_results.csv  # PE z-scores and p-values
│   ├── regime_kruskal_wallis.csv   # KW test results per coin
│   ├── network_metrics_static.csv  # PE, spectral gap, forbidden patterns
│   ├── crosscoin_correlation.csv   # Cross-coin PE lead-lag analysis
│   ├── fig_*.png                   # All manuscript figures (30+)
│   └── ...
├── scripts/                        # Utility scripts for manuscript preparation
├── requirements.txt                # Pinned Python dependencies
└── README.md
```

---

## Setup

### Requirements

- Python 3.13  
- pip

### Installation

```bash
git clone https://github.com/banana17v-netizen/Exploring-cryptocurrency-price-dynamics-and-predictability-with-ordinal-networks.git
cd Exploring-cryptocurrency-price-dynamics-and-predictability-with-ordinal-networks

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Key dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | 2.4.4 | Numerical computation |
| pandas | 3.0.2 | Data handling |
| scipy | 1.17.1 | Statistical tests |
| statsmodels | 0.14.6 | ARIMA models |
| arch | 8.0.0 | GARCH models |
| scikit-learn | 1.8.0 | ML classifiers |
| networkx | 3.6.1 | Network analysis |
| matplotlib | 3.10.9 | Figures |

---

## Reproducing the analysis

Run notebooks in order:

```bash
jupyter lab
```

1. **`data.ipynb`** — download price data (requires free CryptoCompare API key)
2. **`01` → `07`** — ordinal network analysis, PE, surrogate tests, regime tests, walk-forward
3. **`09_enhanced_baseline.ipynb`** — GARCH and naïve baseline comparisons
4. **`08_manuscript.ipynb`** — full manuscript (view only)

> **Note:** All intermediate outputs are already saved in `data/` and `data/*.png`, so notebooks `01`–`08` can be read without re-running.

---

## Data sources

Daily closing prices obtained from the [CryptoCompare API](https://www.cryptocompare.com/) (non-commercial research licence). The balanced panel covers **April 10, 2020 – April 29, 2026** with no missing values.

---

## Citation

If you use this code or data, please cite:

```
[Author(s)]. (2025). Exploring cryptocurrency price dynamics and predictability 
with ordinal networks. Physica A: Statistical Mechanics and its Applications.
[DOI pending]
```

---

## License

This project is released under the [NEU License](LICENSE).
