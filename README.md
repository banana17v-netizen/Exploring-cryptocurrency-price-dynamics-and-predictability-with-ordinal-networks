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
4. **Predictability is near chance** — Walk-forward accuracy: 48–53% across all models (ordinal classifiers, ARIMA, GARCH, naïve, LSTM, Transformer). No model significantly outperforms any other after Bonferroni-corrected Diebold-Mariano testing (40 simultaneous tests, α/40 = 0.00125). Best single accuracy: 53.01% for SOL (LSTM).

---

## Repository structure

```
.
├── data.ipynb                      # Data download from CryptoCompare API
├── 01_preprocessing.ipynb          # Log-return computation, stationarity tests
├── 02_ordinal_network.ipynb        # Ordinal pattern encoding & network construction
├── 03_network_metrics.ipynb        # PE, spectral gap, bootstrap CIs, surrogate tests
├── 04_predictability.ipynb         # Walk-forward prediction (LogReg, RF, GBM, MLP)
├── 05_evaluation.ipynb             # ARIMA(1,0,1) baseline & DM tests
├── 06_advanced_analysis.ipynb      # Rolling PE, regime analysis, robustness checks
├── 07_enhanced_baseline.ipynb      # Extended baselines: GARCH(1,1), Persistence,
│                                   #   Majority Vote, Random Walk
├── 08_lstm_transformer.ipynb       # LSTM & Transformer walk-forward results
├── 09_paper_outline.ipynb          # Paper outline and section planning
├── 10_manuscript.ipynb             # Full manuscript draft (Physica A format)
├── scripts/
│   └── run_lstm.py                 # Standalone LSTM/Transformer walk-forward script
├── data/
│   ├── preprocessed_log_returns.csv       # Daily log-returns (8 coins × 2,210 days)
│   ├── ordinal_patterns.pkl               # Encoded ordinal patterns per coin
│   ├── transition_matrices.pkl            # Ordinal transition matrices per coin
│   ├── walkforward_results.csv            # 1,920 rows: ordinal classifier results
│   ├── baseline_results.csv               # ARIMA(1,0,1) walk-forward results
│   ├── enhanced_baseline_results.csv      # 1,952 rows: GARCH + naïve baselines
│   ├── dl_baseline_results.csv            # 976 rows: LSTM + Transformer results
│   ├── dl_dm_results.csv                  # DM tests for LSTM/Transformer
│   ├── surrogate_test_results.csv         # PE z-scores and p-values
│   ├── regime_kruskal_wallis.csv          # KW test results per coin
│   ├── network_metrics_static.csv         # PE, spectral gap, forbidden patterns
│   ├── crosscoin_correlation.csv          # Cross-coin PE lead-lag analysis
│   ├── diebold_mariano_results.csv        # Full DM test table
│   ├── fig_*.png                          # All manuscript figures (35+)
│   └── ...
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
| torch | 2.11.0+cpu | LSTM & Transformer models |
| networkx | 3.6.1 | Network analysis |
| matplotlib | 3.10.9 | Figures |

---

## Reproducing the analysis

Run notebooks in order:

```bash
jupyter lab
```

1. **`data.ipynb`** — download price data (requires free CryptoCompare API key)
2. **`01` → `07`** — preprocessing, ordinal network analysis, PE, surrogate tests, regime tests, walk-forward, GARCH/naïve baselines
3. **`08_lstm_transformer.ipynb`** — view LSTM/Transformer results (pre-computed)
4. **`10_manuscript.ipynb`** — full manuscript (view only)

To re-run the LSTM/Transformer walk-forward experiments from scratch (~40 min on CPU):

```bash
python scripts/run_lstm.py
```

This regenerates `data/dl_baseline_results.csv`, `data/dl_dm_results.csv`, and `data/fig_dl_comparison.png`.

> **Note:** All intermediate outputs are already saved in `data/`, so notebooks `01`–`09` can be read without re-running.

---

## Data sources

Daily closing prices obtained from the [CryptoCompare API](https://www.cryptocompare.com/) (non-commercial research licence). The balanced panel covers **April 10, 2020 – April 29, 2026** with no missing values.

---

## Citation

If you use this code or data, please cite:

```
[Author(s)]. (2026). Exploring cryptocurrency price dynamics and predictability 
with ordinal networks. Physica A: Statistical Mechanics and its Applications.
[DOI pending]
```

---

## License

This project is released under the [MIT License](LICENSE).
