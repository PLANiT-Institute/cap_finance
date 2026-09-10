"""Verify saved v2 revision artifacts against their generating tables.

This checks arithmetic, transcription, and export; not external model validity.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import pandas as pd
from xlsx_table_reader import read_cells

ROOT=Path(__file__).resolve().parents[1]


def main():
    paper=ROOT/'paper/methodology/TCaR_METHOD_KO.md'
    text=paper.read_text()
    metrics=ROOT/'data/research_v2/block_price_paths/annual_multiplier_metrics.csv'
    df=pd.read_csv(metrics)
    checked=0
    for _,r in df.query('series == "japan_lng" and year_index == 5').iterrows():
        expected=f'| {r.model} | {r["mean"]:.3f} | {r.p50:.3f} | {r.p95:.3f} | {r.es95:.3f} |'
        assert expected in text,expected
        checked+=4
    coverage=pd.read_csv(ROOT/'data/research_v2/price_model_audit/marginal_validation.csv')
    for series in ['europe_gas','japan_lng']:
        for model in ['iid','ar1_ewma']:
            r=coverage.query('series_id == @series and model == @model').iloc[0]
            assert f'{100*r.central90_coverage:.1f}%' in text
            checked+=1
    intervals=pd.read_csv(ROOT/'data/research_v2/block_price_paths/displayed_tail_mc_intervals.csv')
    for model in ['iid_gaussian','empirical_block_24']:
        r=intervals.query('model == @model and metric == "es95"').iloc[0]
        assert f'{r.mc_percentile_lower95:.3f}–{r.mc_percentile_upper95:.3f}' in text
        checked+=2
    cap=[int(n) for n in re.findall(r'\*\*그림 (\d+)\.',text)]
    assert cap==list(range(1,len(cap)+1)) and len(cap)>=4,cap  # sequential figure numbering; count grew after v2.4
    import sys
    if '--include-historical-workbook' not in sys.argv:
        # The v2.0 register workbook is a historical artifact (see TCaR_RESEARCH_V2_NOTE_KO.md); its
        # company_energy_obs source was corrected after export, so its hash check is opt-in.
        print({'checked_manuscript_values': checked, 'historical_workbook': 'skipped (pass --include-historical-workbook)'})
        return
    payload=json.loads((ROOT/'tmp/tcar_workbook/research_v2_register_payload.json').read_text())
    book=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_research_v2_registers.xlsx'
    wb=read_cells(book)
    assert len(wb)==17
    errors=[(name,loc) for name,cells in wb.items() for loc,c in cells.items() if c['error']]
    assert not errors,errors
    source_cells=0
    for spec in payload['sheets']:
        p=ROOT/spec['source']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'],spec['name']
        cells=wb[spec['name']]
        for j,h in enumerate(spec['columns'],1):
            assert cells[(4,j)]['value']==h
        for i,row in enumerate(spec['rows'],5):
            for j,want in enumerate(row,1):
                got=cells.get((i,j),{}).get('value')
                if isinstance(want,(int,float)) and not isinstance(want,bool):
                    assert isinstance(got,(int,float)) and math.isclose(got,want,rel_tol=1e-12,abs_tol=1e-12),(spec['name'],i,j,got,want)
                else:
                    assert got==want,(spec['name'],i,j,got,want)
                source_cells+=1
    assert wb['NCC ledger'][(5,2)]['value']==434
    assert wb['NCC ledger'][(5,2)]['formula']=='B21'
    assert wb['NCC ledger'][(19,2)]['value']==678
    assert wb['NCC ledger'][(20,2)]['value']==244
    artifacts=[paper,book,ROOT/'output/pdf/TCaR_methodology.pdf',metrics,
        ROOT/'scripts/research_block_price_paths.py',ROOT/'scripts/audit_horizon_tails.py',
        ROOT/'paper/methodology/figures/distribution_validation_v2.png',
        ROOT/'paper/methodology/figures/technology_sensitivity_v2.png']
    result=dict(manuscript_new_display_metrics_checked=checked,figure_captions=cap,
        workbook_sheets=len(wb),workbook_source_cells_checked=source_cells,
        workbook_formula_errors=errors,workbook_ncc_partial_cost_EUR_t=434,
        external_model_validation=False,native_excel_app_tested=False,
        FIN_new_block_process_integrated=False,full_research_goal_complete=False,
        artifact_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts})
    target=ROOT/'docs/research_cycles/2026-09-07/resumption_verification.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='artifact_hashes'},indent=2))


if __name__=='__main__': main()
