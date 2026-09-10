"""Source-checked context figure and an explicit finite-frontier explanation."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,font_manager

ROOT=Path(__file__).resolve().parents[1]


class Rows(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.row=[];self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        if tag in ('td','th'):self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        if tag=='tr' and self.row:self.rows.append(self.row)


def read_rows(path):
    parser=Rows();parser.feed(path.read_bytes().decode('utf-8',errors='replace'));return parser.rows


def frontier(points):
    """Independent record-by-record comparison; keep coincident coordinates."""
    return np.array([not any(all(b<=a) and any(b<a) for b in points) for a in points])


def main():
    out=ROOT/'data/research_v2/frontier_industry_context';out.mkdir(parents=True,exist_ok=True)
    raw=ROOT/'tmp/pdfs/industry_context'
    rows=read_rows(raw/'worldsteel_2025.html')
    steel=[]
    for country,expected in [('Japan',[84.,73.8,26.2]),('South Korea',[63.6,72.3,27.7])]:
        matches=[r for r in rows if r[0]==country and len(r)==6 and r[1:4]==[f'{x:.1f}' for x in expected]]
        assert len(matches)==1,(country,matches)
        steel.append(dict(country=country,year=2024,production_mt=float(matches[0][1]),
            oxygen_percent=float(matches[0][2]),electric_percent=float(matches[0][3]),
            source_url='https://worldsteel.org/data/world-steel-in-figures/world-steel-in-figures-2025/',
            source_table='Crude steel production by process 2024',scope='national crude steel; not company input'))
    jp=read_rows(raw/'jpca_production.html')
    eth=[r for r in jp if 'Ethylene' in r]
    assert len(eth)==1
    assert eth[0][-1]=='4,989'
    numeric={'steel':steel,'japan_ethylene_2024':{'value':4989,'unit':'thousand metric tonnes',
        'source_url':'https://www.jpca.or.jp/english/06stats/production.htm','source_table':'Ethylene row,2024 column',
        'scope':'national production; not nameplate capacity'}}
    naphtha=read_rows(raw/'jpca_naphtha.html')
    middle_east=[r for r in naphtha if r[0]=='計' and r[-2:]==['(15,122)','(73.6)']]
    korea=[r for r in naphtha if '韓国' in r and r[-2:]==['2,509','12.2']]
    assert len(middle_east)==len(korea)==1
    numeric['japan_naphtha_import_shares_2024']={'middle_east_percent':73.6,'korea_percent':12.2,
        'source_url':'https://www.jpca.or.jp/statistics/annual/nafusa.html',
        'source_table':'ナフサの国別輸入推移,2024 columns',
        'denominator':'imported naphtha volume; excludes domestic production'}
    (out/'verified_context_observations.json').write_text(json.dumps(numeric,indent=2)+'\n')

    sources=[ROOT/'tmp/research_case_expanded/run/e5/frontier_points.csv',
             ROOT/'data/research_v2/contract_menu_audit/unhedged_frontier_points.csv']
    audit=[]
    for file in sources:
        data=pd.read_csv(file)
        for keys,g in data.groupby(['company_id','scenario','support']):
            g=g[g.budget_ok & ~g.is_disclosed]
            for risk,flag in [('tcar','on_mean_tcar_frontier'),('es_alpha','on_mean_es_frontier')]:
                actual=frontier(g[['mean',risk]].to_numpy())
                assert np.array_equal(actual,g[flag].to_numpy()),(file,keys,risk)
                audit.append(dict(menu='legacy_contracts' if file==sources[0] else 'unhedged',
                    company=keys[0],scenario=keys[1],support=keys[2],risk=risk,
                    candidates=len(g),nondominated=int(actual.sum()),engine_flags_match=True))
    (out/'frontier_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    data=pd.read_csv(sources[0]);g=data[(data.company_id=='LOTTE')&(data.scenario=='NZ15')&(data.support=='none')]
    assert len(g)==60 and g.budget_ok.all()
    f=frontier(g[['mean','es_alpha']].to_numpy());assert f.sum()==5
    g.assign(verified_mean_es_frontier=f).to_csv(out/'plotted_candidates.csv',index=False)

    font=ROOT/'tmp/pdfs/methodology/Heading.ttf';font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
        'font.size':10,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})
    figs=ROOT/'paper/methodology/figures'
    fig,ax=plt.subplots(figsize=(8.5,3.7))
    for i,r in enumerate(steel):
        ax.barh(i,r['oxygen_percent'],color='#344f6b',height=.48)
        ax.barh(i,r['electric_percent'],left=r['oxygen_percent'],color='#4a9b91',height=.48)
        ax.text(r['oxygen_percent']/2,i,f"산소제강 {r['oxygen_percent']}%",ha='center',va='center',color='white')
        ax.text(r['oxygen_percent']+r['electric_percent']/2,i,f"전기제강 {r['electric_percent']}%",ha='center',va='center',color='white',fontsize=9)
    ax.set(yticks=[0,1],yticklabels=['일본 | 84.0 Mt','한국 | 63.6 Mt'],xlim=(0,100),xlabel='2024년 국가 조강 생산 비중 (%)',title='두 나라 모두 산소제강 비중이 70% 이상')
    ax.invert_yaxis();ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
    fig.subplots_adjust(left=.2,right=.97,top=.82,bottom=.27)
    fig.text(.2,.065,'출처: worldsteel, World Steel in Figures 2025의2024년 공정별 표\n국가 통계이며 사례 기업의 공정 비중·스크랩 투입률이 아님.',fontsize=9,color='#555')
    fig.savefig(figs/'industry_steel_context.png',dpi=200);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11.4,5.3))
    toy=np.array([[10,30],[12,25],[16,22],[14,29]],float);good=frontier(toy)
    assert good.tolist()==[True,True,True,False]
    a=axes[0];a.scatter(toy[good,0],toy[good,1],s=65,color='#247b82',label='비지배 계획')
    a.scatter(toy[~good,0],toy[~good,1],s=65,color='#b9c2ca',label='지배되는 계획')
    for label,(x,y) in zip('ABCD',toy):a.annotate(label,(x,y),xytext=(7,5),textcoords='offset points')
    a.annotate('B는 D보다 두 축 모두 낮음',xy=(12,25),xytext=(10.3,23.2),
        fontsize=9,arrowprops={'arrowstyle':'->','color':'#666'})
    a.set(title='정의: 설명용 가상 계획',xlabel='평균비용 (가상 단위)',ylabel='ES (가상 단위)',xlim=(9,17.3),ylim=(20.5,32.3))
    a.legend(frameon=False,fontsize=9,loc='upper right')
    a=axes[1];a.scatter(g['mean']/1000,g.es_alpha/1000,c='#c9d1d7',s=23,label='평가 후보60개')
    u=(g.ppa_share==0)&(g.epc==0);assert u.sum()==6
    a.scatter(g.loc[u,'mean']/1000,g.loc[u,'es_alpha']/1000,s=70,facecolors='none',edgecolors='#b77747',linewidths=1.2,label='무계약6개')
    a.scatter(g.loc[f,'mean']/1000,g.loc[f,'es_alpha']/1000,c='#247b82',s=40,label='평균–ES 비지배5개')
    a.set(title='조건부 사례: LOTTE · NZ15',xlabel='평균 증분비용 (조 원)',ylabel='ES90 증분비용 (조 원)')
    a.legend(frameon=False,fontsize=9,loc='upper right')
    for a in axes:a.grid(alpha=.15)
    fig.subplots_adjust(left=.07,right=.97,top=.88,bottom=.29,wspace=.3)
    fig.text(.07,.065,'오른쪽: 기존6개 기술 일정 ×10개 이상화된 PPA/EPC 조합,1만 공동 경로,2027–2050년\n'
        '같은 누적 감축예산과 고정 생산 조건. 선형 연간 선언 경로를 충족한 결과가 아님.\n'
        '점 사이의 선분은 추가 실행 계획이 아니므로 그리지 않음. 실제 기업의 계약 최적성으로 해석하지 않음.',
        fontsize=9,color='#555',linespacing=1.5)
    fig.savefig(figs/'frontier_explained.png',dpi=200);plt.close(fig)
    inputs=sources+[raw/'worldsteel_2025.html',raw/'jpca_production.html',raw/'jpca_naphtha.html',Path(__file__),
        ROOT/'paper/methodology/FRONTIER_AND_INDUSTRY_CONTEXT_KO.md']
    (out/'manifest.json').write_text(json.dumps({'scope':'Context source cells and finite-menu frontier explanation; no new corporate MC run',
        'comparisons_verified':len(audit),'plotted_points':len(g),'plotted_frontier_points':int(f.sum()),
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}},indent=2)+'\n')
    print(f'{len(audit)} frontier groups/axes verified;2context rows andJPCA cell verified;2figures generated')


if __name__=='__main__':main()
