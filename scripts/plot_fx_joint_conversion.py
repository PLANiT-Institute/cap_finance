"""FX source and exact finite-support cost diagnostic; no corporate frontier."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/research_v2/ecb_fx_reference'
font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
                    'font.size':10,'axes.unicode_minus':False})
m=pd.read_csv(OUT/'monthly_USD_basis.csv')
t=pd.to_datetime(m.period.str.replace('M','-',regex=False))
fig,axs=plt.subplots(2,1,figsize=(7.5,8.3),layout='constrained')
for key,color,label in [('KRW_per_USD','#267e86','원화 / 달러'),('JPY_per_USD','#a16c43','엔화 / 달러')]:
    axs[0].plot(t,100*m[key]/m[key].iloc[0],color=color,label=label,lw=1.7)
axs[0].set(ylabel='환율 지수 (2010년 1월 = 100)',title='A. 같은 달의 원화·엔화 환율 이력')
axs[0].legend(frameon=False,loc='upper left');axs[0].grid(alpha=.17)
axs[0].set_xlim(t.iloc[0],t.iloc[-1])
d=pd.read_csv(OUT/'exact_block_conversion_metrics.csv')
labels=[]
for i,(commodity,currency) in enumerate([(c,f) for c in ['brent','japan_lng','iron_ore'] for f in ['KRW','JPY']]):
    sub=d[(d.commodity==commodity)&(d.currency==currency)].set_index('method')
    for shift,method,color in [(-.17,'same_historical_block','#267e86'),(.17,'independent_block_pairs','#bac4cd')]:
        x=sub.loc[method,'es95'];axs[1].barh(i+shift,x,height=.29,color=color)
        axs[1].text(x+.008,i+shift,f'{x:.3f}',va='center',fontsize=9)
    labels.append({'brent':'원유','japan_lng':'일본 LNG','iron_ore':'철광석'}[commodity]+' · '+{'KRW':'원화','JPY':'엔화'}[currency])
axs[1].set(yticks=range(6),yticklabels=labels,xlim=(0,1.83),xlabel='1년 평균 구매비 배율의 ES95',
           title='B. 동일한 한계분포에서도 공동 연결에 따라 꼬리가 달라진다')
axs[1].set_ylim(6.25,-.6)
from matplotlib.patches import Patch
axs[1].legend(handles=[Patch(color='#267e86',label='같은 역사 블록'),Patch(color='#bac4cd',label='독립 블록 조합')],
              frameon=False,loc='lower right',fontsize=9)
axs[1].grid(axis='x',alpha=.17);axs[1].set_axisbelow(True)
for a in axs:a.spines[['top','right']].set_visible(False)
fig.supxlabel('ECB·World Bank 2010–2025 · 12개월 블록 전수 열거\n조건부 참조 분포이며 실질 기업비용·미래 예측·TCaR가 아님',fontsize=9)
fig.savefig(OUT/'fx_joint_conversion.png',dpi=180);plt.close(fig)
