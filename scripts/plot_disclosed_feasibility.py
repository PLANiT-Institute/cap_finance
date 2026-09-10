"""Show a conditional menu diagnostic without judging corporate declarations."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, font_manager
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'data/research_v2/disclosed_feasibility'
    data=pd.read_csv(folder/'linear_paths_and_bounds.csv')
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
        'font.size':10,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(11,8),sharex=True,sharey=True)
    for ax,company in zip(axes.flat,['POSCO','NSC','LOTTE','MCI']):
        q=data[(data.company_id==company)&(data.scenario=='NZ15')]
        early=q[q.earliest_start_year==2024].sort_values('year')
        late=q[q.earliest_start_year==2027].sort_values('year')
        # The normalization denominator is constant within each company.
        base=early.floor_emissions_tco2.iloc[0]/early.floor_relative_to_baseline.iloc[0]
        ax.plot(early.year,early.emissions/base*100,color='#303d49',lw=2,label='선언 기반 선형 경로')
        ax.step(early.year,early.floor_relative_to_baseline*100,where='post',
                color='#247b82',lw=2,label='물리적 하한: 2024년부터 투자 가능')
        ax.step(late.year,late.floor_relative_to_baseline*100,where='post',
                color='#bb7846',lw=1.5,ls='--',label='물리적 하한: 2027년부터 투자 가능')
        ax.set(title=company,ylim=(-3,106),xticks=[2027,2035,2040,2050],yticks=[0,25,50,75,100])
        ax.grid(axis='y',alpha=.2)
        ax.text(.5,.85,f'2050년 잔여 하한 {early.floor_relative_to_baseline.iloc[-1]*100:.2f}%',
                transform=ax.transAxes,fontsize=9,color='#247b82')
    for ax in axes[:,0]:ax.set_ylabel('추정 기준 배출량 = 100')
    for ax in axes[1,:]:ax.set_xlabel('연도')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.945),frameon=False,ncol=1,fontsize=9)
    fig.suptitle('선형 선언 경로와 현재 기술 메뉴의 물리적 하한',y=.985,fontsize=15)
    fig.subplots_adjust(left=.09,right=.97,top=.79,bottom=.19,hspace=.27,wspace=.15)
    fig.text(.09,.035,'추정 22개 설비의 Scope 1 대리값, 2022–2024년 평균을 2024년 기준에 배치한 가정.\n'
        '생산량 고정·제거/상쇄/폐쇄 없음. 기존 NZ15 기술 가용성 사용; B20의 하한도 이 입력에서는 같음.\n'
        '각 연도에 최저 배출 기술을 자유롭게 고르는 완화된 하한이며 실행 가능한 투자 일정이 아님.\n'
        '기업 전체 선언의 실현 가능성을 판정하는 그래프가 아님. 비용·TCaR를 계산한 결과도 아님.',
        fontsize=9,color='#555',linespacing=1.5)
    out=ROOT/'paper/methodology/figures/disclosed_feasibility.png'
    fig.savefig(out,dpi=180)
    plt.close(fig)
    print(out)


if __name__=='__main__':main()
