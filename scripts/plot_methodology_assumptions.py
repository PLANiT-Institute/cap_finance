"""Readable assumption figures and declaration-only linear comparator register."""
from pathlib import Path
import hashlib
import json
import sys
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,font_manager
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap.disclosed_path import linear_disclosed_path
FIG=ROOT/'paper/methodology/figures'
OUT=ROOT/'data/research_v2/disclosed_linear_reference'
SOURCES={
 'POSCO':'https://sustainability.posco.com/S91/S91F10/eng/cmspage.do?mmcd=1750728562003749',
 'NSC':'https://www.nipponsteel.com/en/carbon-neutral/zerocarbon.html',
 'LOTTE':'https://www.lottechem.com/en/media/news/545/view.do',
 'MCI':'https://jp.mitsuichemicals.com/en/sustainability/mci_sustainability/circular_economy/carbon_neutrality/index.htm'}


def save(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=200)
    fig.savefig(FIG/(name+'.pdf'))
    plt.close(fig)


def main():
    FIG.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
        'font.size':10,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})
    blue='#246b8a';orange='#b66438';green='#41866d'
    p=ROOT/'data/research_v2/iea_2025_scenarios/annual_reference_curves.csv'
    prices=pd.read_csv(p)
    fig,ax=plt.subplots(1,3,figsize=(12,4.5))
    for a,(commodity,region,title,unit) in zip(ax,[('crude_oil','IEA_import_average','원유: IEA 수입평균','2024 USD / barrel'),
        ('natural_gas','Japan','일본 LNG: 재기화 전 통관가격','2024 USD / million Btu'),
        ('steam_coal','Japan','일본 발전용 석탄','2024 USD / tonne')]):
        for scenario,color in zip(('CPS','STEPS','NZE'),(orange,blue,green)):
            d=prices[(prices.commodity==commodity)&(prices.region==region)&(prices.scenario==scenario)]
            a.plot(d.year,d.value,color=color,lw=2,label=scenario)
            n=d[d.status=='source_node'];a.scatter(n.year,n.value,color=color,s=28,zorder=3)
        a.set(title=title,ylabel=unit,xlim=(2023,2051));a.grid(axis='y',alpha=.18)
        a.set_xticks([2024,2035,2050])
    ax[0].legend(frameon=False,fontsize=9)
    fig.subplots_adjust(bottom=.25,wspace=.36,top=.88)
    fig.text(.07,.055,'점: IEA 2025 표 2.3의 원문 값   |   선: 연구자가 적용한 선형보간\n시나리오별 발생확률은 부여하지 않음. 나프타·산업용 전력·원료탄 가격에는 별도 매핑이 필요함.',fontsize=9,color='#555')
    save(fig,'assumptions_scenario_prices')

    vp=ROOT/'data/research_v2/steel_cost_reference/vogl_main_text_package.json'
    rp=ROOT/'data/research_v2/steel_cost_reference/radloff_source_package.json'
    npth=ROOT/'data/research_v2/technology_packages/reference_process_packages.json'
    v=json.loads(vp.read_text());r=json.loads(rp.read_text());n=json.loads(npth.read_text())
    flows={x['package_id']:{f['flow_id']:f['quantity'] for f in x['flows']} for x in n['packages']}
    steel=[v['electricity_MWh_t'],sum(f['input'] for f in r['source_flow_rows'] if f['flow']=='Power')/1000]
    ncc=[flows['LAYRITZ2021_NCC_BASE']['electricity'],flows['LAYRITZ2021_NCC_ELECTRIC']['electricity']]
    fig,ax=plt.subplots(1,2,figsize=(10,4.7))
    for a,values,labels,title,unit in [(ax[0],steel,['DRI–EAF\nVogl 2018','DR–용융로–BOF\nRadloff 2023'],'철강: 현장 수전해 포함','MWh / t 액체강'),
        (ax[1],ncc,['기존 NCC','전기화 NCC'],'석유화학: 구매 전력','MWh / t 에틸렌')]:
        bars=a.bar(labels,values,color=[blue,orange],width=.55)
        a.bar_label(bars,labels=[f'{x:.3f}' for x in values],padding=4)
        a.set(title=title,ylabel=unit,ylim=(0,max(values)*1.3));a.grid(axis='y',alpha=.15)
    fig.subplots_adjust(bottom=.29,wspace=.35,top=.89)
    fig.text(.09,.05,'철강의 두 막대는 서로 다른 공정 사양이며 불확실성의 최소·최대가 아님.\nNCC는 Layritz 2021 공정 패키지. 내부 메탄·수소와 구매 전력을 중복 청구하지 않음.\n원료·자본·부생제품을 포함한 전체 비용은 별도 원장으로 계산.',fontsize=9,color='#555')
    save(fig,'assumptions_process_electricity')

    paths=[];declarations=[]
    for company,url in SOURCES.items():
        declarations.append(dict(company_id=company,target_year=2050,target='carbon_neutrality',source_url=url,
            checked_date='2026-09-07',target_year_verified=True,absolute_baseline_assumed=False,
            scope_harmonized_to_case=False,disclosed_path_eligible=True))
        paths.append(linear_disclosed_path(company_id=company,base_year=2025,target_year=2050,
            base_emissions=100.,years=np.arange(2025,2051),declaration_source=url,
            baseline_source='Illustration: analyst normalizes2025 to100, not a company-reported baseline',
            scope='Declaration endpoint only; company-to-case scope reconciliation pending',
            accounting_basis='normalized_declaration_index',unit='2025=100'))
    pd.DataFrame(declarations).to_csv(OUT/'declarations.csv',index=False)
    pd.concat(paths).to_csv(OUT/'normalized_linear_paths.csv',index=False)
    fig,ax=plt.subplots(1,2,figsize=(10.5,4.6))
    d=paths[0]
    ax[0].plot(d.year,d.emissions,color=blue,lw=2.5,label='선언 기반 선형 기준경로')
    ax[0].scatter([2025,2050],[100,0],color=[orange,green],s=50,zorder=3)
    ax[0].annotate('연구 정규화: 100',(2025,100),xytext=(2027,99),fontsize=9)
    ax[0].annotate('공시 목표: 2050 탄소중립',(2050,0),xytext=(2033,15),fontsize=9)
    ax[0].set(title='DISCLOSED PLAN의 선형 근사',ylabel='기준연도 배출지수 (2025=100)',ylim=(-5,112))
    h=np.arange(0,26);weights=1.05**-h
    ax[1].plot(h,weights,color=blue,lw=2.5)
    ax[1].scatter([0,10,25],weights[[0,10,25]],color=blue,s=35)
    for k in (0,10,25):ax[1].annotate(f'{weights[k]:.2f}',(k,weights[k]),xytext=(0,9),textcoords='offset points',ha='center',fontsize=9)
    ax[1].set(title='할인율 가정: 연 5%',xlabel='평가 시작 후 경과연수',ylabel='미래 비용 1의 현재가치',ylim=(0,1.18))
    for a in ax:a.grid(axis='y',alpha=.18)
    fig.subplots_adjust(bottom=.28,wspace=.32,top=.87)
    fig.text(.08,.045,'왼쪽: 네 기업의 2050 선언을 이용한 공통 정규화 예시. 2025=100과 중간 직선은 연구 가정.\n오른쪽: 현재 연구 사례의 할인율 가정이며 실증 추정치가 아님.\n선형 배출경로의 비용·TCaR는 기술·투자 일정을 모형으로 구성한 뒤 평가.',fontsize=9,color='#555')
    save(fig,'assumptions_disclosed_discount')
    inputs=[p,vp,rp,npth,Path(__file__),ROOT/'src/cap/disclosed_path.py']
    (OUT/'manifest.json').write_text(json.dumps(dict(declarations=4,normalized_path_rows=104,
        source_scope='Target years confirmed on primary company webpages; no full inventory harmonization claimed',
        comparator_policy='Declaration alone permits a linear disclosed emissions path; costs require model completion',
        figures=['assumptions_scenario_prices','assumptions_process_electricity','assumptions_disclosed_discount'],
        inputs=[dict(path=str(x.relative_to(ROOT)),sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in inputs]),indent=2)+'\n')
    print('Saved3assumption figures (PNG/PDF),4declarations and104normalized annual path rows.')


if __name__=='__main__':main()
