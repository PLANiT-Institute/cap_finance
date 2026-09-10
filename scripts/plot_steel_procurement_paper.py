"""Typeset two panels from the saved procurement audit; no new simulation."""
from pathlib import Path
import hashlib,json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/research_v2/steel_procurement_tail'
paths=[source/'conditional_risk.csv',source/'tail_allocation.csv']
r=pd.read_csv(paths[0]);a=pd.read_csv(paths[1])
font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
                     'font.size':10,'axes.unicode_minus':False})
fig,ax=plt.subplots(2,1,figsize=(7,6.4),layout='constrained')
for seed,color in [(20260923,'#236997'),(20260924,'#b35a26')]:
    q=r[(r.seed==seed)&(r.pairing=='joint')].sort_values('beta')
    ax[0].plot(q.beta,q.es_alpha,marker='o',color=color,label=f'표본 {seed-20260922}: ES95')
    ax[0].plot(q.beta,q['mean'],ls=':',color=color)
ax[0].set(title='A. 같은 기대가격에서 원료 연동 가정의 영향',
          xlabel='철광석 지수 연동 비중 β (미추정 가정)',ylabel='비용 NPV (백만 원문 EUR)',xticks=[0,.5,1])
ax[0].legend(fontsize=9,loc='upper left');ax[0].grid(axis='y',alpha=.15)
view=a[(a.seed==20260923)&(a.pairing=='joint')]
bottom=np.zeros(3)
for comp,color,label in [('electricity','#236997','전력'),('pellets','#59a398','펠릿')]:
    value=view[view.component==comp].sort_values('beta').excess_ES_contribution.to_numpy()
    ax[1].bar(np.arange(3),value,bottom=bottom,color=color,label=label,width=.5)
    bottom+=value
ax[1].set(title='B. 총비용의 같은 꼬리 경로에서 배분 (표본 1)',
          xticks=np.arange(3),xticklabels=['0','0.5','1'],xlabel='철광석 지수 연동 비중 β',
          ylabel='ES95 - 평균 (백만 원문 EUR)')
ax[1].legend(fontsize=9);ax[1].grid(axis='y',alpha=.15);ax[1].set_axisbelow(True)
fig.supxlabel('점선은 표본 평균. 동일 물량의 가정 비교이며 계약 선택·효율경계가 아님.',fontsize=9)
out=ROOT/'paper/methodology/figures/steel_procurement_tail_paper.png'
fig.savefig(out,dpi=220);plt.close(fig)
record={'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'new_MC':False}
(ROOT/'tmp/research_completion21/figure_provenance.json').write_text(json.dumps(record,indent=2)+'\n')
print(out)
