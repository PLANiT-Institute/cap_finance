"""Publication figures for verified finite research candidates and fixed-menu stresses."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'paper/methodology/figures';OUT.mkdir(parents=True,exist_ok=True)
A=ROOT/'docs/research_cycles/2026-09-05/robustness_verified'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
p=pd.read_csv(ROOT/'tmp/research_case_expanded/run/e5/frontier_points.csv')
fig,axes=plt.subplots(2,2,figsize=(9.3,7.1),layout='constrained')
for ax,co in zip(axes.flat,['LOTTE','MCI','NSC','POSCO']):
    g=p[(p.company_id==co)&(p.scenario=='NZ15')]
    feasible=g[g.decision_eligible];front=feasible[feasible.on_mean_tcar_frontier]
    ax.scatter(g['mean'],g.tcar,s=14,c='#c5ced6',label='Evaluated candidates')
    ax.scatter(front['mean'],front.tcar,s=27,c='#21658c',label='Mean–TCaR nondominated')
    chosen=feasible.sort_values(['mean','es_alpha','plan_id']).iloc[0]
    ax.scatter(chosen['mean'],chosen.tcar,s=90,marker='*',c='#cf703c',edgecolors='white',linewidth=.4,label='Minimum sampled mean')
    ax.set_title(f'{co} | NZ15',loc='left',fontweight='bold');ax.set_xlabel('Mean incremental NPV (KRW billion)');ax.set_ylabel('TCaR90 (KRW billion)')
    ax.xaxis.set_major_locator(MaxNLocator(4));ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:,.0f}'));ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:,.0f}'));ax.grid(alpha=.15)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,frameon=False)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'finite_frontiers.{ext}',dpi=220)
plt.close(fig)
labels={'independent_seed_1':'Independent seed 1','independent_seed_2':'Independent seed 2','initial_forecast_uncertainty':'Uncertain initial forecast','ou_10yr':'Log OU, 10-year half-life','h2_vol_half':'Hydrogen volatility ×0.5','h2_vol_1_5':'Hydrogen volatility ×1.5','capex_vol_double':'CAPEX volatility ×2','correlation_0_5':'Factor correlation 0.5','h2_price_0_7':'Hydrogen price ×0.7','h2_price_1_3':'Hydrogen price ×1.3','carbon_price_half':'Carbon price ×0.5','carbon_price_zero':'Carbon price zero','no_capital_renewals':'No capital renewals','terminal_straight_line':'Straight-line terminal proxy','discount_3_5pct':'Discount rate 3.5%','discount_6_5pct':'Discount rate 6.5%'}
s=pd.read_csv(A/'selection_changes.csv').set_index('variant').loc[list(labels)]
fig,ax=plt.subplots(figsize=(7.4,6.5),layout='constrained');matrix=s[['mean','tcar','es_alpha']].to_numpy()
im=ax.imshow(matrix,cmap='Blues',vmin=0,vmax=8,aspect='auto')
ax.set_xticks(range(3),['Minimum mean','Minimum TCaR90','Minimum ES90']);ax.set_yticks(range(len(s)),[labels[k] for k in s.index]);ax.tick_params(length=0)
for i in range(len(s)):
    for j in range(3):ax.text(j,i,str(matrix[i,j]),ha='center',va='center',color='white' if matrix[i,j]>=5 else '#17324d',fontweight='bold')
ax.set_title('Changed selections out of eight company–scenario cases',loc='left',pad=14,fontweight='bold')
fig.colorbar(im,ax=ax,shrink=.7,label='Number of changed candidate IDs',ticks=range(9))
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'selection_stability.{ext}',dpi=220)
plt.close(fig)
(OUT/'manifest.json').write_text(json.dumps({'scope':'Finite evaluated menu; no interpolated attainable plans; structural scenarios are assumptions','source_sha256':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [ROOT/'tmp/research_case_expanded/run/e5/frontier_points.csv',A/'selection_changes.csv']}},indent=2)+'\n')
print(OUT)
