"""Scientific figure for the explicitly conditional partial NCC experiment."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
d=pd.read_csv(ROOT/'data/research_v2/ncc_joint_ledger/conditional_risk_metrics.csv')
fig,ax=plt.subplots(1,2,figsize=(12,4.9),gridspec_kw=dict(width_ratios=[1.15,1]))
colors=['#355C7D','#C76A42','#38857B']
models=['iid_gaussian','empirical_block_12','empirical_block_24']
labels=['IID Gaussian','12-month blocks','24-month blocks']
for model,label,color in zip(models,labels,colors):
    s=d[(d.model==model)&(d.sale_fraction==1)&(d.pairing=='same_path')].sort_values('power_indexed_share')
    ax[0].plot(s.power_indexed_share,s.tcar/1000,'o-',label=label,color=color,lw=2,ms=5)
ax[0].axvline(244/678,color='#777',linestyle=':',lw=1)
ax[0].text(244/678+.015,2.1,'Exact cancellation\nunder assumed mapping',fontsize=9,color='#555')
ax[0].set(xlabel='Electricity price share linked to the common gas index',
          ylabel='Partial NPV TCaR95 (trillion KRW)',title='A  Cost risk depends on the net exposure')
ax[0].legend(frameon=False,fontsize=9,loc='upper left')
for i,(model,label) in enumerate(zip(models,labels)):
    s=d[(d.model==model)&(d.sale_fraction==1)&(d.power_indexed_share==.5)].set_index('pairing')
    for shift,pair,c in [(-.18,'same_path','#38857B'),(.18,'permuted_netback_paths','#C76A42')]:
        v=s.loc[pair,'tcar']/1000
        ax[1].bar(i+shift,v,width=.32,color=c,label=('Same price paths' if pair=='same_path' else 'Netback paths permuted') if i==0 else None)
        ax[1].text(i+shift,v+.025,f'{v:.2f}',ha='center',fontsize=9)
ax[1].set(xticks=range(3),xticklabels=['IID\nGaussian','12-month\nblocks','24-month\nblocks'],
          ylabel='Partial NPV TCaR95 (trillion KRW)',title='B  Same marginals and mean; different tail')
ax[1].legend(frameon=False,fontsize=9,loc='upper left')
ax[1].set_ylim(0,2.85)
for a in ax:
    a.spines[['top','right']].set_visible(False)
    a.grid(axis='y',alpha=.18)
    a.set_axisbelow(True)
fig.suptitle('NCC incremental electricity and methane netback: a conditional accounting experiment',fontsize=13,y=.99)
fig.text(.5,.02,'Full sale of freed methane; 1 Mt ethylene/year for 5 years; fixed FX; 5% discount rate.\n'
         'Assumed LNG-index mapping, not observed company contracts. Capital, steam, carbon and other changes excluded.',
         ha='center',fontsize=9,color='#555')
fig.tight_layout(rect=(0,.11,1,.94))
out=ROOT/'paper/methodology/figures/ncc_joint_ledger_experiment.png'
fig.savefig(out,dpi=180,bbox_inches='tight')
print(out)
