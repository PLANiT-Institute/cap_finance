"""Plot a conditional index-exposure diagnostic, not an available hedge menu."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,font_manager
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'data/research_v2/scenario_joint_bridge'
    d=pd.read_csv(folder/'conditional_risk_metrics.csv')
    meta=json.loads((folder/'manifest.json').read_text())
    p=pd.read_csv(folder/'procurement_central_assumptions.csv')
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
        'font.size':10,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})
    colors={'CPS':'#b66438','STEPS':'#246b8a','NZE':'#41866d'}
    fig,ax=plt.subplots(1,2,figsize=(12,5.6))
    for s,color in colors.items():
        q=p[(p.scenario==s)&(p.commodity=='electricity')&(p.beta_base==.5)]
        ax[0].plot(q.year,q.central_price/1500,marker='o',color=color,label=s)
        r=d[(d.scenario==s)&(d.shock_model=='empirical_block_12')]
        ax[1].plot(r.power_base_indexed_share*100,r.tcar/1000,marker='o',color=color,label=s)
    ax[0].set(title='시나리오를 조달가격으로 연결',xlabel='연도',
        ylabel='가정한 전력 중심가격 (2024 EUR/MWh)',xticks=[2027,2029,2031])
    ax[0].text(.04,.08,'P =100×(0.5 +0.5×LNG 시나리오 비율)',
               transform=ax[0].transAxes,fontsize=9)
    b=meta['exact_cancellation_beta_base']*100
    ax[1].axvline(b,color='#777',ls=':',lw=1)
    ax[1].annotate('약36%: 공통 지수 노출이\n수식상 상쇄되는 진단점',xy=(b,0),
        xytext=(6,1.22),fontsize=9,arrowprops={'arrowstyle':'->','color':'#666'})
    ax[1].set(title='같은 공동 충격, 다른 순비용 노출',xlabel='기준가격에서 전력비의 LNG 연동 비중 (%)',
        ylabel='부분 증분비용 TCaR95 (조 원, 2024 실질)',xticks=[0,b,50,100],
        xticklabels=['0','36','50','100'],ylim=(-.1,2.8))
    for a in ax:
        a.grid(axis='y',alpha=.18)
        a.legend(frameon=False,fontsize=9)
    fig.subplots_adjust(left=.08,right=.97,top=.88,bottom=.29,wspace=.3)
    fig.text(.08,.08,'IEA 중심경로 + 동일한 World Bank 12개월 블록 충격, 1만 경로, 2027–2031년 부분 NCC 실험\n'
        '전력·나프타·메탄 가격 연동과 환산율은 가정. 부생메탄 전량 판매. CAPEX·탄소·기타 비용은 제외.\n'
        '36%는 가정 아래의 상쇄 검증값이며 실제 이용 가능한 계약이나 최적 조달 비중이 아님.',
        fontsize=9,color='#555',linespacing=1.55)
    out=ROOT/'paper/methodology/figures/scenario_joint_price_bridge.png'
    fig.savefig(out,dpi=200)
    plt.close(fig)
    print(out)


if __name__=='__main__':main()
