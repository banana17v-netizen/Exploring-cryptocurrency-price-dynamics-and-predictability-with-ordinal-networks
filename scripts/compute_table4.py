import numpy as np, pandas as pd, scipy.stats as stats, warnings
warnings.filterwarnings('ignore')

COINS = ['BTC','ETH','BNB','SOL','XRP','ADA','DOGE','LTC']

df_new = pd.read_csv('data/enhanced_baseline_results.csv')
wf     = pd.read_csv('data/walkforward_results.csv')
bl     = pd.read_csv('data/baseline_results.csv')
fe     = pd.read_csv('data/final_evaluation.csv')

ordinal_best = (wf.groupby(['coin','model'])['acc'].mean().reset_index()
                  .sort_values('acc', ascending=False)
                  .groupby('coin').first().reset_index()
                  .rename(columns={'acc':'acc_ord','model':'best_model'}))

arima_acc = bl.groupby('coin')['acc'].mean().reset_index().rename(columns={'acc':'acc_ARIMA'})

print('=== TABLE 4: Walk-Forward Accuracy ===')
print(f"{'Coin':<6} {'BestOrdinal':>12} {'BestModel':<20} {'ARIMA':>8} {'GARCH11':>8} {'Persist':>8} {'Majority':>9} {'RandWalk':>9}")
for coin in COINS:
    row = ordinal_best[ordinal_best['coin']==coin].iloc[0]
    arima = arima_acc[arima_acc['coin']==coin]['acc_ARIMA'].values[0]
    garch = df_new[(df_new['coin']==coin)&(df_new['model']=='GARCH11_directional')]['acc'].mean()
    pers  = df_new[(df_new['coin']==coin)&(df_new['model']=='Naive_Persistence')]['acc'].mean()
    maj   = df_new[(df_new['coin']==coin)&(df_new['model']=='Naive_Majority')]['acc'].mean()
    rw    = df_new[(df_new['coin']==coin)&(df_new['model']=='Random_Walk')]['acc'].mean()
    print(f"{coin:<6} {row['acc_ord']:>12.4f} {row['best_model']:<20} {arima:>8.4f} {garch:>8.4f} {pers:>8.4f} {maj:>9.4f} {rw:>9.4f}")

def dm_test(e1, e2):
    d = np.asarray(e1)**2 - np.asarray(e2)**2
    n = len(d)
    if n < 6: return float('nan'), float('nan')
    dm = d.mean() / (np.std(d, ddof=1) / np.sqrt(n))
    return round(float(dm), 3), round(float(2*(1 - stats.norm.cdf(abs(dm)))), 4)

print()
print('=== DM TEST: Best Ordinal vs. Baselines ===')
print(f"{'Coin':<6}  vs_ARIMA(stat/p)        vs_GARCH(stat/p)       vs_Persist(stat/p)")
for coin in COINS:
    best_m = ordinal_best[ordinal_best['coin']==coin]['best_model'].values[0]
    ord_e = 1 - wf[(wf['coin']==coin) & (wf['model']==best_m)]['acc'].values
    ar_e  = 1 - bl[bl['coin']==coin]['acc'].values
    ga_e  = 1 - df_new[(df_new['coin']==coin) & (df_new['model']=='GARCH11_directional')]['acc'].values
    pe_e  = 1 - df_new[(df_new['coin']==coin) & (df_new['model']=='Naive_Persistence')]['acc'].values

    n1 = min(len(ord_e), len(ar_e));  dm_ar = dm_test(ord_e[:n1], ar_e[:n1])
    n2 = min(len(ord_e), len(ga_e));  dm_ga = dm_test(ord_e[:n2], ga_e[:n2])
    n3 = min(len(ord_e), len(pe_e));  dm_pe = dm_test(ord_e[:n3], pe_e[:n3])

    s_ar = '*' if dm_ar[1] < 0.05 else ' '
    s_ga = '*' if dm_ga[1] < 0.05 else ' '
    s_pe = '*' if dm_pe[1] < 0.05 else ' '
    print(f"{coin:<6}  {dm_ar[0]:>6.3f}/p={dm_ar[1]:.3f}{s_ar}        {dm_ga[0]:>6.3f}/p={dm_ga[1]:.3f}{s_ga}       {dm_pe[0]:>6.3f}/p={dm_pe[1]:.3f}{s_pe}")

# Save enhanced comparison CSV
new_bl_wide = (df_new.groupby(['coin','model'])['acc'].mean().unstack().reset_index())
new_bl_wide.columns.name = None
rename = {
    'GARCH11_directional': 'acc_GARCH11',
    'Naive_Majority': 'acc_Naive_Majority',
    'Naive_Persistence': 'acc_Naive_Persistence',
    'Random_Walk': 'acc_Random_Walk'
}
new_bl_wide = new_bl_wide.rename(columns=rename)

summary = (ordinal_best.rename(columns={'acc_ord':'acc_best_ordinal'})
           .merge(arima_acc, on='coin')
           .merge(new_bl_wide, on='coin')
           .merge(fe[['coin','DM_vs_ARIMA','DM_pval','DM_sig','sharpe_strategy','sharpe_buyhold','max_drawdown_strategy']], on='coin'))
summary.to_csv('data/enhanced_final_comparison.csv', index=False)
print()
print('Saved data/enhanced_final_comparison.csv')
