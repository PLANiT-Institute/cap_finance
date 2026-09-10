"""Publication-size physical comparison; this figure is not a risk frontier."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/ieaghg_physical_reference'
f=ROOT/'tmp/pdfs/methodology/Heading.ttf'
font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=f).get_name(),
                     'font.size':10,'axes.unicode_minus':False})
d=pd.read_csv(OUT/'same_product_ledger.csv')
fig,axs=plt.subplots(2,1,figsize=(7.2,7.2),layout='constrained')
a=axs[0]
v=d.source_ng_GJ_y/1e6
a.bar(range(3),v,color=['#8d9ba6','#39898b','#215560'],width=.55)
for i,x in enumerate(v):a.text(i,x+.45,f'{x:.3f}',ha='center')
a.set(xticks=range(3),xticklabels=['기준 공정','포집 L1','포집 L2'],ylim=(0,26),
      ylabel='천연가스 투입 (PJ/년)',title='A. 같은 열연코일 4 Mt/년을 생산할 때')
a.text(.02,.95,'자가 전력·증기 생산용 가스의 합계',transform=a.transAxes,va='top',fontsize=9)
a=axs[1]
v=d.iloc[1:]
for shift,col,color,label in [(-.17,'captured_t_CO2_y','#9cafbc','포집량'),(.17,'avoided_t_CO2_y','#297d82','기준 공정 대비 배출 감소')]:
 values=v[col].to_numpy()/1e6
 a.bar([i+shift for i in range(2)],values,width=.31,color=color,label=label)
 for i,x in enumerate(values):a.text(i+shift,x+.07,f'{x:.3f}',ha='center',fontsize=10)
a.set(xticks=range(2),xticklabels=['포집 L1','포집 L2'],ylim=(0,7.8),ylabel='CO₂ (Mt/년)',
      title='B. 포집량과 배출 감소량의 구분')
a.legend(loc='upper left',frameon=False,fontsize=9)
fig.supxlabel('IEAGHG 2013/04 참조 · C-7 운송 포함 경계 · 영구저장 검증값 아님',fontsize=9)
for a in axs:
 a.spines[['top','right']].set_visible(False)
 a.grid(axis='y',alpha=.17);a.set_axisbelow(True)
fig.savefig(OUT/'capture_energy_emissions.png',dpi=180)
plt.close(fig)
