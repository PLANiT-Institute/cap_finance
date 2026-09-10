"""Plot reported financial-stock scope; never label it as procurement or TCaR."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/research_v2/company_fx_scope'
font=ROOT/'tmp/pdfs/methodology/Heading.ttf';font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':10,'axes.unicode_minus':False})
d=pd.read_csv(OUT/'stock_scope_diagnostic.csv').query('year == 2024')
fig,ax=plt.subplots(figsize=(7.5,4.8),layout='constrained')
for shift,scope,color,label in [(-.19,'KRW','#267e86','원화 기능 부문'),(.19,'TOTAL','#a6b4c2','공시 전체 합계')]:
 vals=[d.query('instrument_currency==@ccy and functional_scope==@scope').net_KRW_million.iloc[0]/1000 for ccy in ['USD','EUR','MYR']]
 ax.bar([i+shift for i in range(3)],vals,width=.34,color=color,label=label)
 for i,v in enumerate(vals):ax.text(i+shift,v+(3 if v>=0 else -3),f'{v:.2f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=10)
ax.axhline(0,color='#354653',lw=.8)
ax.set(xticks=range(3),xticklabels=['USD 표시','EUR 표시','MYR 표시'],ylabel='금융자산 - 금융부채 (십억원)',ylim=(-90,185),title='같은 표시 통화도 기능통화 범위에 따라 순잔액이 달라진다')
ax.legend(frameon=False,loc='upper left',fontsize=9);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.supxlabel('롯데케미칼 연결 2024년 말 공시 · 원화 환산 잔액\n연간 원료 구매액·기업 TCaR·단일 환율쌍의 민감도가 아님',fontsize=9)
fig.savefig(OUT/'functional_currency_scope.png',dpi=180);plt.close(fig)
