"""Scientific figure from the audited source physical ledger; no cost simulation."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/langhorst_plant_reference'
x=pd.read_csv(OUT/'scenario_physical_ledger.csv')
font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':10,'axes.unicode_minus':False})
labels=['기존 BF–BOF','H₂–DRI–EAF','압연 수소·전기화','수전해 효율 개선','산소 연소','주조·압연 수율 개선','EAF 철 수율 개선','모든 개선 결합']
fig,axs=plt.subplots(2,1,figsize=(9,8.8),gridspec_kw={'height_ratios':[1.5,1]},layout='constrained')
a=axs[0]; vals=x.electricity_demand_before_CHP_GWh_y/1000
colors=['#9babb8','#6b859b','#b77b3e']+['#43928b']*5
a.barh(labels,vals,color=colors,height=.65);a.invert_yaxis();a.set_xlim(0,5.4);a.set_ylim(8.9,-.6)
for i,v in enumerate(vals):a.text(v+.055,i,f'{v:.3f}',va='center')
a.set(title='A. 같은 최종 제품을 공급할 때 필요한 전력',xlabel='전력 수요 (TWh/년, 수전해 포함·자가발전 차감 전)')
a.text(.99,.035,'후판 513 kt/년 + 외부 공급 슬래브 403.271 kt/년\n효율 개선 5개 조건은 압연 수소·전기화 조건에 적용',ha='right',va='bottom',transform=a.transAxes,fontsize=9)
a=axs[1]; q=x.iloc[:2];whole=q.natural_gas_input_GWh_y.to_numpy();up=q.steelmaking_natural_gas_GWh_y.to_numpy();roll=q.rolling_natural_gas_GWh_y.to_numpy()
# Component inputs retain separate source locators in selected_native_cells.json.
a.bar([0,1],up,label='제철·제강 천연가스',color='#45677f',width=.45)
a.bar([0,1],roll,bottom=up,label='압연 천연가스',color='#d5a465',width=.45)
for i,v in enumerate(whole):a.text(i,v+7,f'{v:.1f}',ha='center')
a.set(xticks=[0,1],xticklabels=labels[:2],ylim=(0,500),xlim=(-.6,2.3),ylabel='천연가스 투입 (GWh/년)',title='B. 압연 가스 증가와 제철소 전체의 순증가는 다르다')
a.text(1.38,260,'압연: +148.5 GWh/년\n전체: +50.7 GWh/년\n\n내부 COG 감소를\n압연 천연가스가 대체',fontsize=10,va='center')
a.legend(frameon=False,loc='upper right',fontsize=9)
for a in axs:
 a.spines[['top','right']].set_visible(False);a.grid(axis='x' if a==axs[0] else 'y',alpha=.12);a.set_axisbelow(True)
fig.savefig(OUT/'plant_energy_boundary.png',dpi=180)
plt.close(fig)
print(OUT/'plant_energy_boundary.png')
