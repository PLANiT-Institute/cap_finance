"""Plot the cycle 1 investment audit from its saved tables."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'docs/research_cycles/2026-09-10-investment-review/cycle1'
d = pd.read_csv(p/'cost_decomposition.csv').pivot(index='component', columns='candidate', values='mean_million_EUR')
keys = ['construction', 'electric_renewal', 'incumbent_renewal_difference',
        'maintenance_difference', 'electricity_difference', 'methane_net_sales_difference']
labels = ['Construction timing', 'Electric renewal in 2050', 'Incumbent renewal',
          'Maintenance', 'Electricity purchases', 'Net methane sales']
v = (d.replace_2030-d.replace_2040).loc[keys].to_numpy()
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw={'width_ratios': [1.25, 1]})
axes[0].barh(labels, v, color=['#28576D' if x > 0 else '#278C88' for x in v])
axes[0].invert_yaxis()
axes[0].axvline(0, color='#aaa', lw=.7)
for i, x in enumerate(v):
    if x < -100:
        axes[0].text(x/2, i, f'{x:+,.0f}', va='center', ha='center', fontsize=9, color='white')
    else:
        axes[0].text(x+(45 if x >= 0 else -45), i, f'{x:+,.0f}', va='center',
                     ha='left' if x >= 0 else 'right', fontsize=9)
axes[0].set_xlim(-1600, 4000)
axes[0].set_xlabel('2030 minus 2040 mean cost (million EUR)')
axes[0].set_title('Cost difference: +2,199.10 million EUR', fontsize=11)
q = pd.read_csv(ROOT/'data/research_v2/ncc_timing_frontier/qualification.csv')
q = q[(q.grid_initial == .2) & (q.residual_per_t_naphtha == 0)]
abatement = 100*(1-q.cumulative_ratio)
axes[1].bar(q.commission_year.astype(str), abatement, color='#28576D', width=.6)
for i, x in enumerate(abatement):
    axes[1].text(i, x+1, f'{x:.2f}%', ha='center', fontsize=9)
axes[1].axhline(50, ls='--', color='#B8733D', label='Illustrative 50% requirement')
axes[1].set_ylim(0, 62)
axes[1].set_ylabel('Cumulative reduction from baseline (%)')
axes[1].set_xlabel('Electric commissioning year')
axes[1].set_title('Equal output; different abatement', fontsize=11)
axes[1].legend(loc='upper right', fontsize=8, frameon=False)
for ax in axes:
    ax.spines[['top', 'right']].set_visible(False)
fig.text(.5, .02, 'Conditional NCC reference, 2027–2050; assumed EUR2019 operating basis; grid 0.2→0, residual emissions 0.', ha='center', fontsize=8)
fig.tight_layout(rect=(0, .06, 1, 1))
for ext in ['png', 'svg']:
    fig.savefig(p/f'investment_audit.{ext}', dpi=180)
plt.close(fig)
