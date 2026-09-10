"""Publication figures from saved diagnostics; no data re-estimation."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'paper/methodology/figures'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
models=['iid_gaussian','empirical_block_1','empirical_block_6','empirical_block_12','empirical_block_24']
labels=['Gaussian iid','Block 1m','Block 6m','Block 12m','Block 24m']
df = pd.read_csv(ROOT/'data/research_v2/block_price_paths/annual_multiplier_metrics.csv')
marg = pd.read_csv(ROOT/'data/research_v2/price_model_audit/marginal_validation.csv')
fig, ax = plt.subplots(1,2,figsize=(12,4.8))
series=['brent','thermal_coal_au','henry_hub','europe_gas','japan_lng','iron_ore']
names=['Brent','Coal (AU)','Gas (US)','Gas (EU)','LNG (Japan)','Iron ore']
x=np.arange(6)
for model,offset,color,label in [('iid',-.18,'#9eabb5','IID Gaussian'),('ar1_ewma',.18,'#236b8e','AR(1) + EWMA')]:
    y=marg.query('model == @model').set_index('series_id').loc[series,'central90_coverage']*100
    ax[0].bar(x+offset,y,width=.36,color=color,label=label)
ax[0].axhline(90,color='#a84e39',ls='--',lw=1)
ax[0].set_xticks(x,names,rotation=25,ha='right')
ax[0].set_ylim(0,103); ax[0].set_ylabel('Observed coverage of nominal 90% interval (%)')
ax[0].set_title('A. Better forecasts still miss crisis tails',loc='left',fontweight='bold')
ax[0].legend(frameon=False,loc='lower left')
lng=df.query('series == "japan_lng" and year_index == 5').set_index('model').loc[models]
x=np.arange(5)
ax[1].vlines(x,lng.p50,lng.p95,color='#236b8e',lw=4,label='P50 to P95')
ax[1].scatter(x,lng.es95,color='#a84e39',marker='D',s=38,label='ES95',zorder=3)
ax[1].axhline(1,color='#7c858c',ls='--',lw=1,label='Exact expected multiplier = 1')
ax[1].set_xticks(x,labels,rotation=25,ha='right')
ax[1].set_ylabel('Year-5 annual average LNG price multiplier')
ax[1].set_title('B. Equal means, different upper tails',loc='left',fontweight='bold')
ax[1].legend(frameon=False,fontsize=9,loc='upper left')
fig.subplots_adjust(bottom=.28,wspace=.28,top=.90)
fig.text(.06,.035,'A: 72 retrospective months (2020-2025); candidate design informed by full-sample inspection.\nB: 10,000 paths per method, 60 months; historical joint blocks, no estimated block-length probabilities.\nSource: World Bank monthly benchmarks, 2010-2025. These are benchmark diagnostics, not company TCaR.',fontsize=8,color='#555e66')
fig.savefig(OUT/'distribution_validation_v2.png',dpi=200)
plt.close(fig)

df=pd.read_csv(ROOT/'data/research_v2/technology_packages/theta_case_comparison.csv')
cases=['steel_vogl_hot','steel_vogl_cold','ncc_linde3','ncc_layritz']
colors=['#236b8e','#7eb3c5','#b96b39','#e0ad73']
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
for panel,sector,companies,keep in [(ax[0],'Steel',['POSCO','NSC'],cases[:2]),(ax[1],'Petrochemicals',['LOTTE','MCI'],cases[2:])]:
    groups=[(c,s) for c in companies for s in ['B20','NZ15']]
    for i,case in enumerate(keep):
        sub=df.query('case == @case').set_index(['company','scenario'])
        vals=[sub.loc[g,'d_tcar_pct'] for g in groups]
        panel.bar(np.arange(4)+(i-.5)*.34,vals,width=.34,color=colors[cases.index(case)],label=case.replace('steel_vogl_','Residual ').replace('ncc_','').replace('_',' '))
    panel.set_xticks(np.arange(4),[c+'\n'+s for c,s in groups])
    panel.axhline(0,color='#74818b',lw=.7)
    panel.set_title(sector,loc='left',fontweight='bold')
    panel.set_ylabel('Change in selected-plan TCaR90 (%)')
    panel.legend(frameon=False,fontsize=9)
fig.subplots_adjust(bottom=.25,wspace=.25)
fig.text(.06,.035,'Paired sensitivity runs: four frontier grid points, 4,000 common paths; same accounting settings.\nAlternative specifications are conditional boundary experiments, not validated engineering bounds or corrected firm estimates.',fontsize=8,color='#555e66')
fig.savefig(OUT/'technology_sensitivity_v2.png',dpi=200)
plt.close(fig)
print('Saved two research validation figures')
