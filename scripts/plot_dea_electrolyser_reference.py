"""Static assumption figure; source intervals are not an adopted distribution."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/dea_electrolyser_reference'
font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
                    'font.size':10,'axes.unicode_minus':False})
x=pd.read_csv(OUT/'specification_comparison.csv')
y=pd.read_csv(OUT/'interval_identification.csv')
publication='--publication' in sys.argv
fig,axs=plt.subplots(2,1,figsize=(6.8,8.3),layout='constrained') if publication else plt.subplots(1,2,figsize=(12,5.7),layout='constrained')
a=axs[0]
for shift,col,color,label in [(-.17,'Langhorst_source_kWh_per_kg_H2','#9aabba','Langhorst 저자 모형'),
                             (.17,'DEA_AEC100_reference_kWh_per_kg_H2','#247f80','DEA 2026.08 · AEC 100 MW')]:
    a.bar([i+shift for i in range(2)],x[col],width=.30,color=color,label=label)
    for i,v in enumerate(x[col]): a.text(i+shift,v+.6,f'{v:.2f}',ha='center',fontsize=10)
a.set(xticks=[0,1],xticklabels=['2025 사양','2050 사양'],ylim=(0,70),
      ylabel='수전해 전력소비 (kWh/kg H₂)',title='A. 사양 선택에 따른 전력수요')
a.legend(frameon=False,loc='upper right',fontsize=9)
a.text(.02,.05,'58 kg H₂/t DRI로 고정하면 전력 차이:\n2025 -0.103 / 2050 +0.252 MWh/t DRI',
       transform=a.transAxes,fontsize=9,va='bottom',bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
a=axs[1]
for i,r in y.iterrows():
    a.errorbar(i,r.source_central,yerr=[[r.source_central-r.source_lower],[r.source_upper-r.source_central]],
               fmt='o',color='#247f80',capsize=6,ms=7,label='원문 중심값·구간' if i==0 else None)
    a.scatter(i+.10,r.assumed_equal_tail_lognormal_median,marker='D',s=65,facecolors='none',edgecolors='#b57631',
              label='추가 가정으로 도출한 중앙값' if i==0 else None)
    a.text(i+.15,r.source_central+40,f'중심값 {r.source_central:,.0f}',fontsize=9)
    a.text(i+.15,r.assumed_equal_tail_lognormal_median-90,f'도출값 {r.assumed_equal_tail_lognormal_median:,.0f}',fontsize=9)
a.set(xticks=[0,1],xticklabels=['2025 사양','2050 사양'],xlim=(-.45,1.95),ylim=(0,2500),
      ylabel='투자비 (2025 EUR/kW 전력입력)',title='B. 구간만으로 중심·분포가 모두 정해지지 않는다')
a.legend(frameon=False,loc='upper right',fontsize=9)
a.text(.02,.04,'마름모: 구간을 5·95% 분위수로 놓은 로그정규 가정\n실제 분포로 채택하거나 MC에 넣지 않음',transform=a.transAxes,fontsize=9)
for a in axs:
    a.spines[['top','right']].set_visible(False)
    a.grid(axis='y',alpha=.15);a.set_axisbelow(True)
fig.suptitle('기술 사양과 확률분포를 분리해 기록하는 이유',fontsize=13 if publication else 15)
target=ROOT/'paper/methodology/figures/electrolyser_assumptions_publication.png' if publication else OUT/'electrolyser_assumptions.png'
fig.savefig(target,dpi=180)
plt.close(fig)
print(target)
