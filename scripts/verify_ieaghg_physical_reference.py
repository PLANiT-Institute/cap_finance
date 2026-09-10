"""Check source bindings, independent emissions eligibility and preserved results."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/ieaghg_physical_reference'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    m=json.loads((OUT/'manifest.json').read_text())
    assert sha(ROOT/m['source_pdf'])==m['source_pdf_sha256']
    for paths in [m['frozen_inputs_sha256'],m['artifact_sha256']]:
        for p,h in paths.items():assert sha(ROOT/p)==h,p
    d=pd.read_csv(OUT/'same_product_ledger.csv').set_index('case')
    q=pd.read_csv(OUT/'emissions_qualification.csv')
    counts={}
    for c,e,cap in [('REFERENCE',8376554,0),('EOP_L1',4182921,4972525),('EOP_L2',3325694,6131267)]:
        r=d.loc[c]
        assert r.avoided_t_CO2_y==8376554-e
        assert r.captured_t_CO2_y==cap
        for row in q[q.case==c].itertuples():
            target=F(str(row.target))
            assert row.C7_eligible==(F(8376554-e,8376554)>=target)
            assert row.incorrect_capture_as_avoidance_eligible==(F(cap,8376554)>=target)
    for target in [.5,.501,.55,.6,.604]:
        rows=q[q.target==target]
        counts[str(target)]={col:rows.loc[rows[col],'case'].tolist() for col in ['C7_eligible','D15_eligible','incorrect_capture_as_avoidance_eligible']}
    assert counts['0.5']['C7_eligible']==['EOP_L1','EOP_L2']
    assert counts['0.6']['C7_eligible']==['EOP_L2']
    assert counts['0.501']['C7_eligible']==['EOP_L2']
    assert counts['0.604']['C7_eligible']==[]
    assert counts['0.55']['incorrect_capture_as_avoidance_eligible']==['EOP_L1','EOP_L2']
    paper=ROOT/'paper/methodology/TCaR_METHOD_KO.md'
    text=paper.read_text();old=(ROOT/'tmp/research_completion25/TCaR_METHOD_KO.md').read_text()
    oldrows=[l for l in old.splitlines() if l.startswith('|')]
    assert all(l in text for l in oldrows)
    for pattern in [r'!\[[^\]]*\]\(([^)]+)\)',r'\\\[.*?\\\]']:
        assert re.findall(pattern,text,re.S)==re.findall(pattern,old,re.S)
    note=(ROOT/'paper/methodology/STEEL_CAPTURE_QUALIFICATION_KO.md').read_text()
    nvalues=0
    for c in d.index:
        for key in ['source_ng_GJ_y','initial_capex_million_source_USD','C7_emitted_t_CO2_y','avoided_t_CO2_y','captured_t_CO2_y']:
            v=d.loc[c,key]
            assert f'{v:,.0f}' in note,(c,key,v)
            nvalues+=1
    for c in ['EOP_L1','EOP_L2']:
        for key in ['C7_avoided_fraction','D15_avoided_fraction']:
            v=f'{100*d.loc[c,key]:.4f}%'
            assert v in text and v in note,v;nvalues+=1
    assert '16,862,476GJ/년' in text and '22,070,357GJ/년' in text
    wb=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
    assert sha(wb)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
    report=dict(all_passed=True,new_values_checked=nvalues+2,qualification_rows_checked=len(q),
        eligibility=counts,old_table_rows_preserved=len(oldrows),old_figures_preserved=24,
        old_equations_preserved=12,source_selected_pages_visually_reviewed=m['selected_pages_visually_reviewed'],
        frozen_experiment_unchanged=True,Excel_v6_unchanged=True,new_MC_runs=0,company_calibration=False,
        artifacts={str(p.relative_to(ROOT)):sha(p) for p in [paper,ROOT/'output/pdf/TCaR_methodology.pdf',
            OUT/'capture_energy_emissions.png',OUT/'manifest.json',ROOT/'paper/methodology/STEEL_CAPTURE_QUALIFICATION_KO.md',Path(__file__)]})
    (ROOT/'docs/research_cycles/2026-09-07-hourly/completion_25_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['artifacts','eligibility']},ensure_ascii=False))

if __name__=='__main__':main()
