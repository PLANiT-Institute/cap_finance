"""Scientific diagnostics from the audited monthly benchmark panel; no forecast."""
from pathlib import Path
from statistics import NormalDist
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/research_v2/price_history'
OUT=ROOT/'output/research_v2/figures'
KEYS=['brent','thermal_coal_au','henry_hub','europe_gas','japan_lng','iron_ore']
LABELS=['Brent oil','Australian thermal coal','US gas','European gas','Japan LNG imports','Iron ore']
COLORS=['#176B87','#B06E28','#8263A8','#338D75','#D34E5E','#666C76']


def read(name):
    with (DATA/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    price={}
    for r in read('native_monthly_prices.csv'):
        if '2010M01'<=r['period']<='2025M12':price.setdefault(r['period'],{})[r['series_id']]=float(r['value'])
    dates=sorted(price);levels=np.array([[price[d][k] for k in KEYS] for d in dates])
    returns=np.diff(np.log(levels),axis=0);assert len(returns)==191
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'axes.titleweight':'bold'})
    fig,axs=plt.subplots(2,2,figsize=(13.4,9.1),gridspec_kw={'hspace':.44,'wspace':.30})
    for i in [0,1,3,4]:
        axs[0,0].plot(np.arange(len(dates)),levels[:,i]/levels[0,i]*100,color=COLORS[i],label=LABELS[i],lw=1.8)
    axs[0,0].set(yscale='log',ylabel='Price index (Jan 2010 = 100; log scale)',
                 title='A  Prices move together, but not identically')
    axs[0,0].set_xticks(np.arange(0,192,36),[dates[i][:4] for i in range(0,192,36)])
    axs[0,0].legend(fontsize=8,ncol=2,loc='upper left',frameon=False)
    axs[0,0].grid(axis='y',alpha=.15)
    z=(returns-returns.mean(axis=0))/returns.std(axis=0,ddof=1)
    qs=(np.arange(1,len(z)+1)-.5)/len(z)
    normal=np.array([NormalDist().inv_cdf(q) for q in qs])
    axs[0,1].plot([-3,3],[-3,3],color='#999999',ls='--',lw=1,label='Gaussian reference')
    for i in [0,1,3,4]:axs[0,1].plot(normal,np.sort(z[:,i]),'.',ms=3.2,color=COLORS[i],alpha=.72)
    axs[0,1].set(xlabel='Gaussian quantiles',ylabel='Standardized monthly log changes',
                 title='B  A Gaussian fit misses parts of the tails')
    axs[0,1].text(.03,.95,'191 monthly changes; extreme quantiles are imprecise',
                    transform=axs[0,1].transAxes,va='top',fontsize=8,color='#555555')
    corr=np.corrcoef(returns,rowvar=False)
    im=axs[1,0].imshow(corr,vmin=-1,vmax=1,cmap='BrBG')
    short=['Brent','Coal','US gas','EU gas','Japan LNG','Iron ore']
    axs[1,0].set_xticks(range(6),short,rotation=35,ha='right');axs[1,0].set_yticks(range(6),short)
    for i in range(6):
        for j in range(6):axs[1,0].text(j,i,f'{corr[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(corr[i,j])>.65 else '#222222')
    axs[1,0].set_title('C  Cross-price dependence belongs in the model',pad=12)
    fig.colorbar(im,ax=axs[1,0],fraction=.042,pad=.025,label='Monthly log-change correlation')
    acf=np.array([[np.corrcoef(returns[:-1,i],returns[1:,i])[0,1],
                   np.corrcoef(returns[:-1,i]**2,returns[1:,i]**2)[0,1]] for i in range(6)])
    y=np.arange(6)
    axs[1,1].barh(y-.16,acf[:,0],height=.29,color='#176B87',label='Log change')
    axs[1,1].barh(y+.16,acf[:,1],height=.29,color='#D1A35E',label='Squared log change')
    axs[1,1].set_yticks(y,short);axs[1,1].invert_yaxis();axs[1,1].axvline(0,color='#888888',lw=.7)
    axs[1,1].set(xlabel='Lag-one sample autocorrelation',title='D  Time dependence also matters')
    axs[1,1].legend(fontsize=8,frameon=False,loc='lower right');axs[1,1].grid(axis='x',alpha=.15)
    fig.suptitle('Evidence for joint price shocks — before choosing a cost-tail model',
                 x=.07,y=.98,ha='left',fontsize=17,fontweight='bold')
    fig.text(.07,.925,'World Bank monthly nominal benchmarks, 2010–2025 | Descriptive diagnostics; not GCAM forecast errors',fontsize=10,color='#555555')
    fig.subplots_adjust(top=.865,bottom=.135,left=.09,right=.965)
    fig.text(.07,.045,'Scope: thermal coal is not coking coal; LNG imports are not company contracts. European gas and coal definitions change within the period.\nNo electricity, hydrogen or carbon-allowance calibration is implied. Source: World Bank Pink Sheet, downloaded 5 Sep 2026; frozen source hash in manifest.',fontsize=8,color='#555555',linespacing=1.5)
    path=OUT/'price_shock_evidence.png';fig.savefig(path,dpi=180,facecolor='white');plt.close(fig)
    print(path)


if __name__=='__main__':main()
