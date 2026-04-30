"""
Final manuscript fixes:
1. Fill in GitHub URL
2. Remove draft note from References
3. Update Abstract to mention GARCH
4. Fix Conclusion to mention GARCH
5. Add Figure 7 caption
"""
import json, re

GITHUB_URL = "https://github.com/banana17v-netizen/Exploring-cryptocurrency-price-dynamics-and-predictability-with-ordinal-networks"

with open('08_manuscript.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

def fix_cell(cell, fixes):
    src = ''.join(cell['source'])
    for old, new in fixes:
        if old in src:
            src = src.replace(old, new)
            print(f'  Fixed: {old[:60]}...')
    lines = src.split('\n')
    cell['source'] = [l + '\n' for l in lines[:-1]] + [lines[-1]]

# ── Cell 0: Data Availability ─────────────────────────────────────────────
fix_cell(cells[0], [
    ('[GitHub repository URL]', GITHUB_URL),
])

# ── Cell 2 (TITLE PAGE): Abstract ─────────────────────────────────────────
fix_cell(cells[2], [
    (
        'with no model significantly outperforming ARIMA after Diebold-Mariano testing.',
        'with no model significantly outperforming ARIMA(1,0,1) or GARCH(1,1) after Diebold-Mariano testing with Bonferroni correction.'
    ),
])

# ── Cell 7 (Conclusion) ────────────────────────────────────────────────────
fix_cell(cells[7], [
    (
        'ordinal-based classifiers achieve accuracy statistically indistinguishable from the ARIMA baseline for all eight coins after Diebold-Mariano testing and multiple-test correction.',
        'ordinal-based classifiers achieve accuracy statistically indistinguishable from ARIMA(1,0,1), GARCH(1,1), and na\u00efve baselines for all eight coins after Diebold-Mariano testing with Bonferroni correction.'
    ),
])

# ── Cell 8 (References): remove draft note ────────────────────────────────
fix_cell(cells[8], [
    (
        '*[Fill in full citations using journal style. Required references:]*\n\n**Market efficiency',
        '**Market efficiency'
    ),
])

# ── Cell 8 (References): add Figure 7 caption ─────────────────────────────
FIG7 = (
    "\n\n**Figure 7.** Distribution of walk-forward directional accuracy across all 61 test windows "
    "for each model and coin. Each panel shows a box-and-whisker plot with individual window accuracy "
    "as jittered points; the dashed line marks the 50% chance level. The overlap across all models "
    "(ordinal, ARIMA, GARCH, na\u00efve baselines) confirms that no approach achieves systematic outperformance. "
    "Source: `fig_model_comparison.png`."
)
src8 = ''.join(cells[8]['source'])
if 'fig_multiscale_pe.png`.' in src8 and 'Figure 7' not in src8:
    src8 = src8.replace('fig_multiscale_pe.png`.', 'fig_multiscale_pe.png`.' + FIG7)
    lines = src8.split('\n')
    cells[8]['source'] = [l + '\n' for l in lines[:-1]] + [lines[-1]]
    print('  Added Figure 7 caption.')

with open('08_manuscript.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print('\nDone.')
