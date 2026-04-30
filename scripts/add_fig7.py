import json

with open('08_manuscript.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

c = nb['cells']
s9 = ''.join(c[9]['source'])

NEEDLE = 'fig_multiscale_pe.png`.'
FIG7 = (
    '\n\n**Figure 7.** Distribution of walk-forward directional accuracy across all 61 test windows '
    'for each model and coin. Each panel shows a box-and-whisker plot with individual window accuracy '
    'as jittered points; the dashed line marks the 50%% chance level. The overlap across all models '
    '(ordinal, ARIMA, GARCH, naive baselines) confirms that no approach achieves systematic outperformance. '
    'Source: `fig_model_comparison.png`.'
)

print('NEEDLE found:', NEEDLE in s9)
print('Repr around needle:', repr(s9[s9.find(NEEDLE)-5:s9.find(NEEDLE)+len(NEEDLE)+5]))

s9_new = s9.replace(NEEDLE, NEEDLE + FIG7)
print('Figure 7 in result:', 'Figure 7' in s9_new)

lines = s9_new.split('\n')
c[9]['source'] = [l + '\n' for l in lines[:-1]] + [lines[-1]]

with open('08_manuscript.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print('Saved.')
