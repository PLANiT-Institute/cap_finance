"""Recheck stored NCC draws, cash timing and manuscript cells without new MC."""
from pathlib import Path
import hashlib,json,sys,re
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.risk_metrics import loss_summary


def main():
    out=ROOT/'data/research_v2/ncc_reference_cash';m=json.loads((out/'manifest.json').read_text())
    for p,sha in (m['input_sha256']|m['artifact_sha256']).items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha,p
    df=pd.read_csv(out/'conditional_metrics.csv');cash=pd.read_csv(out/'annual_cash.csv')
    draws=np.load(out/'incremental_cost_draws.npz');checks=0
    for r in df.query('block==12 and seed==20260913').itertuples():
        metric=loss_summary(draws[r.condition_id],.95)
        for source,target in [('mean','mean'),('p50','p50'),('q_alpha','q95'),('tcar','tcar95'),('es_alpha','es95')]:
            np.testing.assert_allclose(metric[source],getattr(r,target),rtol=1e-12,atol=1e-9);checks+=1
        g=cash[cash.condition_id==r.condition_id]
        b=g[g['case']=='conventional'].sort_values('year');e=g[g['case']=='electric'].sort_values('year')
        np.testing.assert_array_equal(b.output_t,e.output_t)
        np.testing.assert_array_equal(b.naphtha_t,e.naphtha_t)
        for frame, recovered_heat in [(b, (.841-.431)*r.recovery), (e, .542*r.recovery)]:
            boiler_capital = max(.492-recovered_heat, 0)*72.1*(115/.303)*1000
            expected_initial = 994490000.+boiler_capital
            np.testing.assert_allclose(frame.capex_EUR.iloc[:3], expected_initial/3, rtol=1e-12, atol=1e-7)
            np.testing.assert_allclose(frame.capex_EUR.iloc[:3].sum(), expected_initial, rtol=1e-12, atol=1e-7)
        # The only plant renewal inside the horizon is2050 for20-year electric life.
        if r.electric_life==20:assert e[e.year==2050].capex_EUR.iloc[0]>=994490000.
        else:assert not e.capex_EUR.iloc[3:].any()
    # Every saved path changes by the same amount under deterministic lifetime changes.
    spread=[]
    for recovery in [.8,1.]:
        a=draws[f'r{recovery}_life20_psi1.0_none'];b=draws[f'r{recovery}_life30_psi1.0_none']
        spread.append(float(np.ptp(a-b)));assert spread[-1]<1e-8
    paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
    cells=[[x.strip() for x in line.strip('|').split('|')] for line in paper.splitlines() if line.startswith('|')]
    printed=0
    for r in df.query('block==12 and seed==20260913 and recovery==1 and maintenance_scale==1').itertuples():
        expected=[f'{r.electric_life}년','없음' if r.terminal=='none' else '직선 대용치',f'{r.mean:.3f}',f'{r.es95:.3f}',f'{r.tcar95:.3f}']
        assert expected in cells;printed+=3
    report=dict(saved_metrics_checked=checks,new_manuscript_cells_checked=printed,
        pathwise_constant_shift_max_spread=max(spread),conditions=len(df),annual_rows=len(cash),
        company_full_cost=False,frontier_optimized=False,
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
    version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
    target=ROOT/f'docs/research_cycles/2026-09-07-hourly/ncc_cash_{version}_verification.json'
    target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'}))


if __name__=='__main__':main()
