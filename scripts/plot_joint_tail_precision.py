"""Separate conditional Monte Carlo intervals from alternative price models."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,font_manager
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'data/research_v2/joint_tail_precision'
    d=pd.read_csv(folder/'conditional_bootstrap_intervals.csv')
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
        'font.size':10,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})
    names=['iid_gaussian','empirical_block_1','empirical_block_6','empirical_block_12','empirical_block_24']
    labels=['독립 정규','블록 1개월','블록 6개월','블록 12개월','블록 24개월']
    fig,ax=plt.subplots(1,2,figsize=(11.5,5.5))
    for a,h,c in zip(ax,(5,24),('#246b8a','#b66438')):
        x=d[d.horizon_years==h].set_index('model').loc[names]
        y=x.tcar95.to_numpy()/1000
        low=x.tcar95_low.to_numpy()/1000;hi=x.tcar95_high.to_numpy()/1000
        a.errorbar(np.arange(5),y,yerr=np.vstack([y-low,hi-y]),fmt='o',color=c,
                   capsize=5,markersize=6,elinewidth=1.5)
        a.set(title=f'{2027}–{2026+h}년 ({h}년)',ylabel='부분 증분비용 TCaR95 (조 원, 2024 실질)',
              xticks=np.arange(5),xticklabels=labels,xlim=(-.5,4.5))
        a.tick_params(axis='x',labelsize=9)
        a.grid(axis='y',alpha=.18)
        for i,v in enumerate(y):
            a.annotate(f'{v:.3f}',(i,hi[i]),xytext=(0,8),textcoords='offset points',
                       ha='center',fontsize=9,color=c)
        a.set_ylim(max(0,min(low)-(max(hi)-min(low))*.2),max(hi)+(max(hi)-min(low))*.27)
    fig.suptitle('모형 선택의 차이와 몬테카를로 표본오차',y=.96,fontsize=14)
    fig.subplots_adjust(left=.075,right=.98,top=.82,bottom=.3,wspace=.27)
    fig.text(.075,.07,'STEPS 조건, 전력 기준 LNG 연동 50%, 부생메탄 전량 판매를 가정한 부분 NCC 실험\n'
        '점: 1만 경로의 TCaR95   |   오차막대: 전체 비용 경로를 200회 재표집한 조건부 95% 구간\n'
        '구간은 MC 표본오차만 포함. 기술·계약·분포 추정의 불확실성이나 실제 미래의 95% 보장구간이 아님.',
        fontsize=9,color='#555',linespacing=1.55)
    path=ROOT/'paper/methodology/figures/joint_tail_precision.png'
    fig.savefig(path,dpi=200)
    plt.close(fig)
    print(path)


if __name__=='__main__':main()
