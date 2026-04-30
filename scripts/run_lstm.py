"""Walk-forward LSTM + Transformer baseline evaluation."""
import pickle
import numpy as np
import pandas as pd
import scipy.stats as stats
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from itertools import permutations

print('PyTorch:', torch.__version__)
torch.manual_seed(42)
np.random.seed(42)

COINS        = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'LTC']
TRAIN_WINDOW = 365
TEST_WINDOW  = 30
STEP         = 30
SEQ_LEN      = 20
N_PATTERNS   = 6
EMBED_DIM    = 8
LSTM_HIDDEN  = 32
LSTM_LAYERS  = 2
ATTN_HEADS   = 2
EPOCHS       = 3
BATCH_SIZE   = 32
LR           = 1e-3

# ── Data ──────────────────────────────────────────────────────────────────────
with open('data/ordinal_patterns.pkl', 'rb') as f:
    op_dict = pickle.load(f)

all_perms   = list(permutations(range(3)))
perm_to_idx = {p: i for i, p in enumerate(all_perms)}

def encode_patterns(pl):
    return np.array([perm_to_idx.get(tuple(int(x) for x in p), 0) for p in pl], dtype=np.int64)

log_ret = pd.read_csv('data/preprocessed_log_returns.csv', index_col=0, parse_dates=True)

def direction_label(a):  return (np.asarray(a) > 0).astype(int)
def accuracy_score(yt, yp): return float(np.mean(np.asarray(yt) == np.asarray(yp)))
def f1_score(yt, yp):
    yt, yp = np.asarray(yt), np.asarray(yp)
    tp = np.sum((yp==1) & (yt==1)); fp = np.sum((yp==1) & (yt==0)); fn = np.sum((yp==0) & (yt==1))
    d = 2*tp + fp + fn
    return float(2*tp / d) if d > 0 else 0.0

print('Coins in op_dict:', list(op_dict.keys()))
print('log_ret shape:', log_ret.shape)

# ── Models ────────────────────────────────────────────────────────────────────
class LSTMClassifier(nn.Module):
    def __init__(self, n, e, h, l):
        super().__init__()
        self.embed = nn.Embedding(n, e)
        self.lstm  = nn.LSTM(e, h, l, batch_first=True, dropout=0.2 if l > 1 else 0.0)
        self.fc    = nn.Linear(h, 1)
    def forward(self, x):
        e = self.embed(x)
        _, (h, _) = self.lstm(e)
        return self.fc(h[-1]).squeeze(1)


class TransformerClassifier(nn.Module):
    def __init__(self, n, e, nh, sl):
        super().__init__()
        self.embed = nn.Embedding(n, e)
        self.pos   = nn.Embedding(sl, e)
        el = nn.TransformerEncoderLayer(d_model=e, nhead=nh, dim_feedforward=e*4,
                                        dropout=0.1, batch_first=True, norm_first=True)
        self.tr = nn.TransformerEncoder(el, num_layers=1)
        self.fc = nn.Linear(e, 1)
    def forward(self, x):
        B, T = x.shape
        pos  = torch.arange(T).unsqueeze(0).expand(B, T)
        e    = self.embed(x) + self.pos(pos)
        out  = self.tr(e)
        return self.fc(out[:, -1, :]).squeeze(1)


def train_model(model, X, y):
    model.train()
    opt  = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    crit = nn.BCEWithLogitsLoss()
    ds   = TensorDataset(torch.tensor(X, dtype=torch.long), torch.tensor(y, dtype=torch.float))
    dl   = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True)
    for _ in range(EPOCHS):
        for xb, yb in dl:
            opt.zero_grad()
            loss = crit(model(xb), yb)
            loss.backward()
            opt.step()
    return model


def predict_model(model, X):
    model.eval()
    with torch.no_grad():
        return (torch.sigmoid(model(torch.tensor(X, dtype=torch.long))) >= 0.5).numpy().astype(int)


def make_sequences(pat, lbl, sl):
    X, y = [], []
    for i in range(sl, len(pat)):
        X.append(pat[i-sl:i]); y.append(lbl[i])
    return np.array(X, dtype=np.int64), np.array(y, dtype=np.int64)


# ── Walk-forward ──────────────────────────────────────────────────────────────
def walk_forward_dl(coin_name):
    r        = log_ret[coin_name].dropna()
    y_all    = direction_label(r.values)
    patterns = encode_patterns(op_dict[coin_name])
    PAT_OFFSET = 2
    n = len(r)
    results = []
    for i_start in range(TRAIN_WINDOW, n - TEST_WINDOW + 1, STEP):
        i_end   = i_start + TEST_WINDOW
        test_y  = y_all[i_start:i_end]
        if len(test_y) == 0:
            continue
        row_base = dict(coin=coin_name,
                        date_start=str(r.index[i_start]),
                        date_end=str(r.index[i_end - 1]),
                        n_test=len(test_y),
                        target='target_direction')
        train_end_p = i_start - PAT_OFFSET
        test_end_p  = i_end   - PAT_OFFSET
        if train_end_p < SEQ_LEN + 1 or test_end_p > len(patterns):
            continue
        train_pat = patterns[:train_end_p]
        train_lbl = y_all[PAT_OFFSET:i_start]
        test_pat  = patterns[train_end_p:test_end_p]
        test_lbl  = y_all[i_start:i_end][:len(test_pat)]
        if len(test_pat) == 0:
            continue
        X_tr, y_tr = make_sequences(train_pat, train_lbl, SEQ_LEN)
        X_te, _    = make_sequences(
            np.concatenate([train_pat[-SEQ_LEN:], test_pat]),
            np.concatenate([train_lbl[-SEQ_LEN:], test_lbl]),
            SEQ_LEN
        )
        y_te = test_lbl[:len(X_te)]
        if len(X_tr) < BATCH_SIZE or len(X_te) == 0:
            continue
        torch.manual_seed(i_start)
        lstm    = train_model(LSTMClassifier(N_PATTERNS, EMBED_DIM, LSTM_HIDDEN, LSTM_LAYERS), X_tr, y_tr)
        p_lstm  = predict_model(lstm, X_te)
        results.append({**row_base, 'model': 'LSTM',
                         'acc': accuracy_score(y_te, p_lstm), 'f1': f1_score(y_te, p_lstm)})
        torch.manual_seed(i_start)
        tfm   = train_model(TransformerClassifier(N_PATTERNS, EMBED_DIM, ATTN_HEADS, SEQ_LEN), X_tr, y_tr)
        p_tfm = predict_model(tfm, X_te)
        results.append({**row_base, 'model': 'Transformer',
                         'acc': accuracy_score(y_te, p_tfm), 'f1': f1_score(y_te, p_tfm)})
    return results


print('=== STARTING WALK-FORWARD LOOP ===', flush=True)
all_dl = []
for coin in COINS:
    print(f'{coin}...', end=' ', flush=True)
    try:
        res = walk_forward_dl(coin)
    except Exception as ex:
        print(f'ERROR: {ex}', flush=True)
        import traceback; traceback.print_exc()
        res = []
    all_dl.extend(res)
    nw = len([r for r in res if r['model'] == 'LSTM'])
    print(f'{nw}w', end='  ', flush=True)
    # Save incrementally after each coin
    if all_dl:
        pd.DataFrame(all_dl).to_csv('data/dl_baseline_results.csv', index=False)

df_dl = pd.DataFrame(all_dl)
df_dl.to_csv('data/dl_baseline_results.csv', index=False)
print(f'\n\nSaved {len(df_dl)} rows → data/dl_baseline_results.csv')
print('\nMean accuracy by coin and model:')
print(df_dl.groupby(['coin', 'model'])['acc'].mean().unstack().round(4).to_string())

# ── DM test ───────────────────────────────────────────────────────────────────
wf = pd.read_csv('data/walkforward_results.csv')

def dm_test_windows(e1, e2):
    d = np.asarray(e1)**2 - np.asarray(e2)**2
    n = len(d)
    if n < 6: return np.nan, np.nan
    d_mean = d.mean()
    g0 = np.var(d, ddof=1)
    g1 = np.cov(d[1:], d[:-1])[0, 1] if n > 2 else 0.0
    nw_var = g0 + 2*g1
    if nw_var <= 0: return 0.0, 1.0
    dm = d_mean / np.sqrt(abs(nw_var) / n)
    p  = float(2 * (1 - stats.norm.cdf(abs(dm))))
    return round(float(dm), 3), round(p, 4)

dm_rows = []
for coin in COINS:
    ord_sub    = wf[wf['coin'] == coin]
    best_model = ord_sub.groupby('model')['acc'].mean().idxmax()
    ord_err    = 1 - ord_sub[ord_sub['model'] == best_model]['acc'].values
    for bl_name in ['LSTM', 'Transformer']:
        bl_err = 1 - df_dl[(df_dl['coin']==coin) & (df_dl['model']==bl_name)]['acc'].values
        n_min  = min(len(ord_err), len(bl_err))
        if n_min < 6: continue
        dm_s, dm_p = dm_test_windows(ord_err[:n_min], bl_err[:n_min])
        dm_rows.append({'coin': coin, 'ordinal_model': best_model,
                         'baseline': bl_name, 'DM_stat': dm_s,
                         'p_value': dm_p,
                         'significant_p05': dm_p < 0.05 if dm_p == dm_p else False})

dm_df = pd.DataFrame(dm_rows)
dm_df.to_csv('data/dl_dm_results.csv', index=False)
print('\n=== DM Test Results ===')
print(dm_df.to_string(index=False))
n_tests = len(dm_df)
alpha_bonf = 0.05 / n_tests if n_tests > 0 else 0.05
n_sig_b = (dm_df['p_value'] < alpha_bonf).sum()
print(f'\nSignificant after Bonferroni (α={alpha_bonf:.4f}): {n_sig_b}/{n_tests}')

# ── Figure ────────────────────────────────────────────────────────────────────
df_enh = pd.read_csv('data/enhanced_baseline_results.csv')
bl     = pd.read_csv('data/baseline_results.csv')

wf_best = (wf.groupby(['coin','model'])['acc'].mean()
              .reset_index()
              .sort_values('acc', ascending=False)
              .groupby('coin').first().reset_index())
wf_best['label'] = 'Best Ordinal'

arima_m = bl.groupby('coin')['acc'].mean().reset_index()
arima_m['label'] = 'ARIMA(1,0,1)'

label_map = {'GARCH11_directional': 'GARCH(1,1)',
             'Naive_Persistence':   'Persistence',
             'Naive_Majority':      'Majority',
             'Random_Walk':         'Rand. Walk',
             'LSTM':                'LSTM',
             'Transformer':         'Transformer'}
enh_m = df_enh.groupby(['coin','model'])['acc'].mean().reset_index()
enh_m['label'] = enh_m['model'].map(label_map)
dl_m  = df_dl.groupby(['coin','model'])['acc'].mean().reset_index()
dl_m['label']  = dl_m['model'].map(label_map)

plot_df = pd.concat([wf_best[['coin','acc','label']],
                     arima_m[['coin','acc','label']],
                     enh_m[['coin','acc','label']],
                     dl_m[['coin','acc','label']]])

ORDER  = ['Best Ordinal','ARIMA(1,0,1)','GARCH(1,1)',
          'Persistence','Majority','Rand. Walk','LSTM','Transformer']
COLORS = ['#1565C0','#E65100','#6A1B9A','#2E7D32','#C62828','#757575','#00838F','#AD1457']

sns.set_style('whitegrid')
fig, axes = plt.subplots(2, 4, figsize=(18, 8))
axes = axes.flatten()
for i, coin in enumerate(COINS):
    ax  = axes[i]
    sub = (plot_df[plot_df['coin'] == coin]
           .drop_duplicates('label')
           .set_index('label')['acc']
           .reindex(ORDER))
    bars = ax.bar(range(len(ORDER)), sub.values, color=COLORS, width=0.7, edgecolor='white')
    ax.axhline(0.5, color='black', linestyle='--', linewidth=1)
    ax.set_title(coin, fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels(ORDER, rotation=45, ha='right', fontsize=7)
    lo = max(0.38, float(np.nanmin(sub.values)) - 0.03)
    hi = min(0.65, float(np.nanmax(sub.values)) + 0.05)
    ax.set_ylim(lo, hi)
    if i % 4 == 0:
        ax.set_ylabel('Mean Accuracy', fontsize=9)
    for bar, val in zip(bars, sub.values):
        if not np.isnan(val):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=6)

fig.suptitle('Walk-Forward Directional Accuracy: Ordinal Network vs. All Baselines incl. LSTM & Transformer\n'
             '(Mean over rolling 30-day test windows, Apr 2021 – Apr 2026)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('data/fig_dl_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print('\nSaved → data/fig_dl_comparison.png')

# ── Summary table ─────────────────────────────────────────────────────────────
print('\n=== COMPLETE COMPARISON TABLE ===')
print(f'{"Coin":5s} | {"Best Ordinal":12s} | {"ARIMA":6s} | {"GARCH":6s} | {"Persist":8s} | {"Majority":8s} | {"Rand.Walk":9s} | {"LSTM":6s} | {"Transf.":7s}')
print('-' * 90)
for coin in COINS:
    o  = wf[wf['coin']==coin].groupby('model')['acc'].mean().max()
    a  = bl[bl['coin']==coin]['acc'].mean()
    g  = df_enh[(df_enh['coin']==coin) & (df_enh['model']=='GARCH11_directional')]['acc'].mean()
    p  = df_enh[(df_enh['coin']==coin) & (df_enh['model']=='Naive_Persistence')]['acc'].mean()
    m  = df_enh[(df_enh['coin']==coin) & (df_enh['model']=='Naive_Majority')]['acc'].mean()
    r  = df_enh[(df_enh['coin']==coin) & (df_enh['model']=='Random_Walk')]['acc'].mean()
    ls = df_dl[(df_dl['coin']==coin) & (df_dl['model']=='LSTM')]['acc'].mean()
    tf = df_dl[(df_dl['coin']==coin) & (df_dl['model']=='Transformer')]['acc'].mean()
    print(f'{coin:5s} | {o:.4f}       | {a:.4f} | {g:.4f} | {p:.4f}   | {m:.4f}   | {r:.4f}    | {ls:.4f} | {tf:.4f}')

print('\nAll models cluster near 50% -- no predictability at daily frequency.')
