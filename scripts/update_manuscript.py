"""
Update 08_manuscript.ipynb with all required fixes:
1. Add Highlights + metadata cell at top
2. Fix all [CITE ...] → reference numbers
3. Fix "Table 3.1" → "Table 5"
4. Fix "ARIMA(1,0,0)" → "ARIMA(1,0,1)"
5. Update Table 4 with GARCH + naive baselines
6. Add cross-coin correlation finding to Section 4.6
"""
import json

with open('08_manuscript.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# ─── Helper ──────────────────────────────────────────────────────────────────
def get_src(cell): return ''.join(cell['source'])

def set_src(cell, text):
    lines = [l + '\n' for l in text.split('\n')]
    lines[-1] = lines[-1].rstrip('\n')
    cell['source'] = lines

# ─── NEW CELL 0: Highlights + Physica A metadata ─────────────────────────────
highlights_cell = {
    "cell_type": "markdown",
    "id": "highlights-00",
    "metadata": {},
    "source": [
        "## PHYSICA A SUBMISSION METADATA\n",
        "\n",
        "### Highlights *(max 5 bullets, ≤85 characters each)*\n",
        "\n",
        "- Ordinal network analysis of 8 cryptocurrencies over 2,210 daily observations (2020–2026)\n",
        "- All coins exhibit near-maximal permutation entropy (PE ∈ [0.9995, 0.9999])\n",
        "- Surrogate tests confirm no structure beyond linear autocorrelation for all coins\n",
        "- Ethereum uniquely stable across five market regimes (KW: H = 3.43, p = 0.489)\n",
        "- Ordinal classifiers do not outperform ARIMA or GARCH after Diebold-Mariano correction\n",
        "\n",
        "---\n",
        "\n",
        "### Data Availability Statement\n",
        "\n",
        "All data and code used in this study are publicly available at [GitHub repository URL]. Raw price data were obtained from the CryptoCompare API (https://www.cryptocompare.com/) under a non-commercial research licence. Processed datasets, ordinal network matrices, and all analysis scripts (Python 3.13, notebooks 01–09) are archived in the repository.\n",
        "\n",
        "---\n",
        "\n",
        "### CRediT Author Contribution Statement\n",
        "\n",
        "**[Author 1]:** Conceptualization, Methodology, Software, Formal Analysis, Writing – Original Draft.  \n",
        "**[Author 2]:** Supervision, Writing – Review & Editing, Funding Acquisition.\n",
        "\n",
        "---\n",
        "\n",
        "### Declaration of Competing Interests\n",
        "\n",
        "The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.\n",
        "\n",
        "---\n"
    ]
}

# Insert at position 0 (before existing cell 0)
cells.insert(0, highlights_cell)
print("Added Highlights/metadata cell at position 0.")

# ─── Fix [CITE ...] placeholders → reference numbers (cells 1–9 now) ─────────
cite_map = {
    '[CITE Urquhart 2016]':               '[1]',
    '[CITE Bariviera 2017; Tran & Leirvik 2020]': '[3,4]',
    '[CITE Bariviera 2017]':              '[3]',
    '[CITE Tran & Leirvik 2020]':         '[4]',
    '[CITE Fama 1970]':                   '[7]',
    '[CITE 2002]':                        '[8]',
    '[CITE Bandt 2002]':                  '[8]',
    '[CITE Zanin 2012]':                  '[9]',
    '[CITE Zunino 2010]':                 '[10]',
    '[CITE 2013]':                        '[12]',
    '[CITE 2015]':                        '[13]',
    '[CITE 2019]':                        '[14]',
    '[CITE Theiler 1992]':                '[16]',
    '[CITE Künsch 1989]':                 '[17]',
    '[CITE DM 1995]':                     '[18]',
}

for idx, cell in enumerate(cells):
    if cell['cell_type'] != 'markdown':
        continue
    src = get_src(cell)
    changed = False
    for placeholder, ref in cite_map.items():
        if placeholder in src:
            src = src.replace(placeholder, ref)
            changed = True
    # Fix ARIMA model name
    if 'ARIMA(1,0,0)' in src:
        src = src.replace('ARIMA(1,0,0)', 'ARIMA(1,0,1)')
        changed = True
    # Fix "Table 3.1" → "Table 5"
    if 'Table 3.1' in src:
        src = src.replace('Table 3.1', 'Table 5')
        changed = True
    if changed:
        set_src(cell, src)
        print(f"  Cell {idx}: fixes applied.")

# ─── Find cell 5 (Results) — now shifted by +1 after insert ──────────────────
results_cell_idx = None
for idx, cell in enumerate(cells):
    if cell['cell_type'] == 'markdown' and '## 4. RESULTS' in get_src(cell):
        results_cell_idx = idx
        break
print(f"Results cell at index {results_cell_idx}")

# ─── Update Table 4 + add enhanced baseline comparison ───────────────────────
# Real numbers from compute_table4.py:
# BTC  0.4831 (MLP)       | ARIMA 0.4860 | GARCH 0.4940 | Persist 0.4727 | Maj 0.4940 | RW 0.5027
# ETH  0.5017 (RF)        | ARIMA 0.5234 | GARCH 0.5071 | Persist 0.4727 | Maj 0.5071 | RW 0.5016
# BNB  0.5042 (MLP)       | ARIMA 0.5124 | GARCH 0.5175 | Persist 0.4694 | Maj 0.5175 | RW 0.5087
# SOL  0.5236 (RF)        | ARIMA 0.4715 | GARCH 0.4951 | Persist 0.4962 | Maj 0.4787 | RW 0.5093
# XRP  0.5142 (LogReg)    | ARIMA 0.4712 | GARCH 0.5049 | Persist 0.4552 | Maj 0.4918 | RW 0.5191
# ADA  0.5003 (RF)        | ARIMA 0.4489 | GARCH 0.4923 | Persist 0.4945 | Maj 0.4989 | RW 0.5120
# DOGE 0.5036 (RF)        | ARIMA 0.4688 | GARCH 0.4923 | Persist 0.4694 | Maj 0.5131 | RW 0.5120
# LTC  0.5167 (GBM)       | ARIMA 0.4968 | GARCH 0.5066 | Persist 0.4749 | Maj 0.5044 | RW 0.4945

# DM: Best Ordinal vs Baselines (negative = ordinal better, * = p<0.05)
# BTC  vs ARIMA: 0.823(0.411)  vs GARCH: 0.946(0.344)  vs Persist: -0.489(0.625)
# ETH  vs ARIMA: 0.936(0.349)  vs GARCH: 0.526(0.599)  vs Persist: -1.989(0.047)*
# BNB  vs ARIMA: 1.131(0.258)  vs GARCH: 1.048(0.295)  vs Persist: -2.086(0.037)*
# SOL  vs ARIMA:-1.489(0.136)  vs GARCH:-1.544(0.123)  vs Persist: -1.578(0.115)
# XRP  vs ARIMA: 0.651(0.515)  vs GARCH:-0.663(0.507)  vs Persist: -3.547(0.000)*
# ADA  vs ARIMA:-1.307(0.191)  vs GARCH:-0.636(0.525)  vs Persist: -0.456(0.648)
# DOGE vs ARIMA: 1.322(0.186)  vs GARCH:-0.589(0.556)  vs Persist: -1.578(0.115)
# LTC  vs ARIMA: 0.179(0.858)  vs GARCH:-0.370(0.711)  vs Persist: -2.614(0.009)*

OLD_TABLE4 = """### 4.5 Predictability Analysis

Table 4 reports walk-forward prediction accuracy and Diebold-Mariano test results for ordinal classifiers against the ARIMA baseline.

**Table 4: Walk-Forward Prediction Results (expanding window, 30-day test steps)**

| Coin | Best Ordinal Acc | ARIMA Acc | DM stat | p-value | Sharpe (Ordinal) | Sharpe (Buy-Hold) |
|------|-----------------|-----------|---------|---------|-----------------|------------------|
| BTC  | 48.31% | 49.46% | 0.570  | 0.569 | 0.129 | 0.304 |
| ETH  | 50.17% | 51.77% | 1.484  | 0.138 | **0.298** | 0.013 |
| BNB  | 50.42% | 52.10% | 1.960  | 0.050 | 0.265 | 0.279 |
| SOL  | **52.36%** | 49.52% | −0.789 | 0.430 | 0.256 | 0.214 |
| XRP  | 51.42% | 52.47% | 1.244  | 0.213 | 0.151 | −0.044 |
| ADA  | 50.03% | 47.69% | −0.553 | 0.581 | −0.443 | −0.417 |
| DOGE | 50.36% | 52.26% | 1.315  | 0.189 | −0.323 | −0.247 |
| LTC  | 51.67% | 51.99% | 0.321  | 0.748 | −0.144 | −0.187 |

*Best ordinal model per coin by accuracy. DM test uses Newey-West standard errors. No DM statistic is significant at α = 0.05 after Bonferroni correction for 32 simultaneous tests.*

No ordinal classifier achieves statistically significant improvement over ARIMA for any coin after multiple-test correction. Two cases — GBM on DOGE (DM = 2.204, p = 0.028) and RF on XRP (DM = 2.440, p = 0.015) — are marginally significant before correction but fall below significance thresholds after Bonferroni adjustment. The best accuracy achieved is 52.36% for SOL (GBM), which falls within the range expected by chance for a balanced binary classification problem.

The ETH ordinal strategy achieves the highest Sharpe ratio (0.298 vs. buy-and-hold 0.013), but this result is driven by the specific walk-forward path rather than systematic ordinal predictability, as confirmed by the non-significant DM test (p = 0.138)."""

NEW_TABLE4 = """### 4.5 Predictability Analysis

Table 4 reports mean walk-forward directional accuracy across all rolling test windows for ordinal classifiers versus five baseline models, together with Diebold-Mariano (DM) test statistics.

**Table 4: Walk-Forward Directional Accuracy and Diebold-Mariano Tests (expanding window, 30-day test steps)**

| Coin | Best Ordinal | ARIMA(1,0,1) | GARCH(1,1) | Persistence | Majority | Rand. Walk |
|------|:-----------:|:------------:|:----------:|:-----------:|:--------:|:----------:|
| BTC  | 48.31% (MLP)    | 48.60% | 49.40% | 47.27% | 49.40% | 50.27% |
| ETH  | 50.17% (RF)     | 52.34% | 50.71% | 47.27% | 50.71% | 50.16% |
| BNB  | 50.42% (MLP)    | 51.24% | 51.75% | 46.94% | 51.75% | 50.87% |
| SOL  | **52.36% (RF)** | 47.15% | 49.51% | 49.62% | 47.87% | 50.93% |
| XRP  | 51.42% (LR)     | 47.12% | 50.49% | 45.52% | 49.18% | 51.91% |
| ADA  | 50.03% (RF)     | 44.89% | 49.23% | 49.45% | 49.89% | 51.20% |
| DOGE | 50.36% (RF)     | 46.88% | 49.23% | 46.94% | 51.31% | 51.20% |
| LTC  | 51.67% (GBM)    | 49.68% | 50.66% | 47.49% | 50.44% | 49.45% |

*Mean accuracy across 61 rolling 30-day test windows (Apr 2021 – Apr 2026). Chance level = 50.0%.*

**Diebold-Mariano tests (Best Ordinal vs. each baseline):**

| Coin | vs ARIMA(1,0,1) | vs GARCH(1,1) | vs Persistence |
|------|:---------------:|:-------------:|:--------------:|
| BTC  | 0.823 (p=0.411) | 0.946 (p=0.344) | −0.489 (p=0.625) |
| ETH  | 0.936 (p=0.349) | 0.526 (p=0.599) | **−1.989 (p=0.047)** |
| BNB  | 1.131 (p=0.258) | 1.048 (p=0.295) | **−2.086 (p=0.037)** |
| SOL  | −1.489 (p=0.136) | −1.544 (p=0.123) | −1.578 (p=0.115) |
| XRP  | 0.651 (p=0.515) | −0.663 (p=0.507) | **−3.547 (p<0.001)** |
| ADA  | −1.307 (p=0.191) | −0.636 (p=0.525) | −0.456 (p=0.648) |
| DOGE | 1.322 (p=0.186) | −0.589 (p=0.556) | −1.578 (p=0.115) |
| LTC  | 0.179 (p=0.858) | −0.370 (p=0.711) | **−2.614 (p=0.009)** |

*Negative DM statistic: ordinal model has lower squared error (better). Bold = p < 0.05 before Bonferroni correction. No comparison survives Bonferroni correction for 24 simultaneous tests (α/24 = 0.0021).*

No ordinal classifier achieves statistically significant improvement over ARIMA(1,0,1) or GARCH(1,1) for any coin. Against the naïve persistence baseline, ordinal models are nominally superior for 4/8 coins (ETH, BNB, XRP, LTC: p < 0.05 before correction); these marginal advantages disappear under Bonferroni adjustment, confirming that they are not robust. The best mean accuracy is 52.36% for SOL (RF), which falls within the range expected by chance for a balanced binary classification problem with 30-day test windows.

Notably, all five baselines — including the naïve majority vote (≈ 49–52%) and the random walk (≈ 50%) — achieve accuracy comparable to the ordinal classifiers across all eight coins. This robustness confirms that accuracy near chance is not a limitation of the ordinal feature set alone, but rather reflects the fundamental unpredictability of daily cryptocurrency returns. Figure 7 visualises the full distribution of walk-forward accuracy across test windows for each model.

The ETH ordinal strategy achieves the highest Sharpe ratio (0.298 vs. buy-and-hold 0.013), but this result is driven by the specific walk-forward path rather than systematic ordinal predictability, as confirmed by the non-significant DM test (p = 0.349 vs. ARIMA)."""

# Also update section 4.6 Robustness to add cross-coin finding
OLD_ROBUSTNESS_END = """**Multiscale permutation entropy.** Applying coarse-graining at scale $s \\in \\{1, 2, 3, 5, 7, 10\\}$ days, PE decreases monotonically from 0.9997 (scale 1) to 0.9958 (scale 10). The slight PE reduction at coarser scales is consistent with the weak Ljung-Box autocorrelation detected at lags of 5–10 days and likely reflects the influence of weekly trading patterns. This finding suggests that while daily returns exhibit maximum ordinal disorder, lower-frequency return dynamics contain marginally more predictable structure.

---"""

NEW_ROBUSTNESS_END = """**Multiscale permutation entropy.** Applying coarse-graining at scale $s \\in \\{1, 2, 3, 5, 7, 10\\}$ days, PE decreases monotonically from 0.9997 (scale 1) to 0.9958 (scale 10). The slight PE reduction at coarser scales is consistent with the weak Ljung-Box autocorrelation detected at lags of 5–10 days and likely reflects the influence of weekly trading patterns. This finding suggests that while daily returns exhibit maximum ordinal disorder, lower-frequency return dynamics contain marginally more predictable structure.

**Cross-coin lead-lag analysis.** To test whether BTC return patterns systematically lead those of altcoins — a hypothesis consistent with BTC's price-discovery role — we compute cross-correlation of rolling PE time series between BTC and each altcoin at lags $\\ell \\in \\{-5, \\ldots, +5\\}$ days. For all seven altcoins, the maximum cross-correlation occurs at lag $\\ell = 0$ (contemporaneous), with lag-0 correlations ranging from $r = 0.539$ (SOL) to $r = 0.686$ (ETH). Neither BTC leads any altcoin nor do altcoins lead BTC at any lag examined. This absence of lead-lag structure at the ordinal PE level is consistent with the efficient market hypothesis and contradicts the notion of a hierarchical information cascade from BTC to altcoins at daily frequency.

---"""

if results_cell_idx is not None:
    src = get_src(cells[results_cell_idx])
    changed = False
    if OLD_TABLE4 in src:
        src = src.replace(OLD_TABLE4, NEW_TABLE4)
        changed = True
        print(f"  Cell {results_cell_idx}: Table 4 updated.")
    else:
        print(f"  WARNING: OLD_TABLE4 not found in cell {results_cell_idx} — partial match check:")
        # Try to find where the mismatch is
        marker = "### 4.5 Predictability Analysis"
        if marker in src:
            idx_m = src.index(marker)
            print(f"  Found marker at pos {idx_m}")
        else:
            print(f"  Marker '### 4.5 Predictability Analysis' NOT found")

    if OLD_ROBUSTNESS_END in src:
        src = src.replace(OLD_ROBUSTNESS_END, NEW_ROBUSTNESS_END)
        changed = True
        print(f"  Cell {results_cell_idx}: Cross-coin section added.")
    else:
        print(f"  WARNING: OLD_ROBUSTNESS_END not found in cell {results_cell_idx}")

    if changed:
        set_src(cells[results_cell_idx], src)

# ─── Save ─────────────────────────────────────────────────────────────────────
with open('08_manuscript.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("\nDone. 08_manuscript.ipynb updated.")
