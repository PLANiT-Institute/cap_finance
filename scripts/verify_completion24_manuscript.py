"""Verify v2.29 source transcription, preservation and two axiomatic failures.

Uses finite exact-distribution examples, not new Monte Carlo runs.
"""
from pathlib import Path
from fractions import Fraction as F
import csv, hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'paper/methodology/TCaR_METHOD_KO.md'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))

def main():
    text=PAPER.read_text();old=(ROOT/'tmp/research_completion24/TCaR_METHOD_KO.md').read_text()
    old_rows=[l for l in old.splitlines() if l.startswith('|')]
    for l in old_rows: assert l in text,l
    equations=lambda t:re.findall(r'\\\[.*?\\\]',t,re.S)
    assert equations(text)==equations(old)
    figs=lambda t:re.findall(r'!\[[^\]]*\]\(([^)]+)\)',t)
    assert figs(text)[:len(figs(old))]==figs(old)
    for f in figs(text): assert (PAPER.parent/f).exists(),f
    assert re.findall(r'\*\*그림 (\d+)\.',text)==list(map(str,range(1,25)))
    assert re.findall(r'\*\*표 (\d+)\.',text)==list(map(str,range(1,23)))
    assert re.findall(r'\*\*표 C(\d+)\.',text)==list(map(str,range(1,7)))
    refs=text.split('## 참고문헌 및 재현 자료')[1]
    assert re.findall(r'^(\d+)\. ',refs,re.M)==list(map(str,range(1,63)))
    a=text.split('### C.9 ')[1].split('### C.10 ')[0]
    b=text.split('### C.10 ')[1].split('## 참고문헌')[0]
    plant=read('data/research_v2/langhorst_plant_reference/scenario_physical_ledger.csv')
    checked=[]
    for i,label in [(0,'기존 BF–BOF'),(1,'H₂–DRI–EAF'),(2,'압연 수소·전기화 포함'),(7,'에너지·재료 효율 개선 모두 적용')]:
        r=plant[i]
        vals=[float(r['electricity_demand_before_CHP_GWh_y'])/1000,float(r['onsite_hydrogen_kt_y']),float(r['liquid_steel_kt_y'])]
        line='| '+label+' | '+' | '.join(f'{v:,.3f}' for v in vals)+' |'
        assert line in a,line;checked+=vals
    for key in ['source_gross_subsystem_energy_GWh_y','internal_COG_to_rolling_GWh_y','carrier_inputs_excluding_internal_COG_GWh_y','export_slabs_kt_y']:
        v=float(plant[0][key]);assert f'{v:,.3f}' in a;checked.append(v)
    delta=float(plant[1]['natural_gas_input_GWh_y'])-float(plant[0]['natural_gas_input_GWh_y'])
    assert f'{delta:.3f}' in a;checked.append(delta)
    for key in ['source_steelmaking_emissions_per_t_slab','derived_steelmaking_emissions_per_t_liquid_steel']:
        v=float(plant[1][key]);assert f'{v:.6f}' in a;checked.append(v)
    specs=read('data/research_v2/dea_electrolyser_reference/specification_comparison.csv')
    for r in specs:
        for key in ['Langhorst_source_kWh_per_kg_H2','DEA_AEC100_reference_kWh_per_kg_H2','Langhorst_electrolysis_MWh_per_t_DRI','DEA_electrolysis_MWh_per_t_DRI','substitution_change_percent']:
            v=float(r[key]);assert f'{v:.3f}' in b;checked.append(v)
    diag=read('data/research_v2/dea_electrolyser_reference/interval_identification.csv')[1]
    for key in ['source_central','source_lower','source_upper','assumed_equal_tail_lognormal_median']:
        v=float(diag[key]);assert f'{v:,.3f}' in b;checked.append(v)
    pct=abs(float(diag['median_vs_source_central_percent']))
    assert f'{pct:.3f}%' in b;checked.append(pct)
    # Definition F^-1(p)=inf{z:F(z)>=p}; 100 equiprobable states.
    def q(x,p):return sorted(x)[int(p*len(x))-1]
    def gap(x):return q(x,F(9,10))-q(x,F(1,2))
    x=[F(100)]*6+[F(0)]*94
    y=[F(0)]*6+[F(100)]*6+[F(0)]*88
    total=[v+w for v,w in zip(x,y)]
    assert gap(x)==gap(y)==0 and gap(total)==100
    examples=[]
    for amount in [F(1),F(100),F(10000)]:
        z=[F(0)]*95+[amount]*5
        mean=sum(z)/100;es=sum(sorted(z)[90:])/10
        assert len(set(z))==2 and gap(z)==0 and mean==amount/20 and es==amount/2
        examples.append(dict(M=float(amount),TCaR=float(gap(z)),mean=float(mean),ES90=float(es)))
    assert '일반화 편차측도 공리와 같으며' not in text
    for required in ['엄격한 양성 조건(D4)','준가법성(D3)','두 지침이 확률 사용을 금지한다는 뜻은 아니다','최신판을 기존 논문의 정확한 원자료로 간주하지 않는다','전망 중 낙관적인 효율값을 기업이 자유롭게 고르게 하면']:
        assert required in text,required
    book=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
    assert sha(book)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
    report=dict(version='v2.29',new_printed_values_checked=len(checked),existing_table_rows_preserved=len(old_rows),
                old_figures_preserved=len(figs(old)),figures=len(figs(text)),numbered_equations=len(equations(text)),
                references=62,source_D3_counterexample={'X':0,'Y':0,'sum':100},source_D4_counterexamples=examples,
                integrated_Excel_v6_unchanged=True,new_MC_runs=0,corporate_calibration=False,
                source_author_manuscript_sha256=sha(ROOT/'tmp/research_completion24/generalized_deviations_author.pdf'),
                manuscript_sha256=sha(PAPER),PDF_sha256=sha(ROOT/'output/pdf/TCaR_methodology.pdf'),all_passed=True)
    (ROOT/'docs/research_cycles/2026-09-07-hourly/completion_24_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
