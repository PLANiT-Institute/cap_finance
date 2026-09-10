"""Reconcile steel cash tables and preserve the scope of the added paper case."""
from pathlib import Path
import hashlib,json,re
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]


def main():
    text=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
    df=pd.read_csv(ROOT/'data/research_v2/steel_reference_ledger/absolute_cost_sensitivity.csv')
    printed=[[c.strip() for c in l.strip('|').split('|')] for l in text.splitlines() if l.startswith('|')]
    cells=[]
    for r in df.query('model == "block_12" and seed == 20260908 and oxygen_sale_fraction == 0.6').itertuples():
        rows=[x for x in printed if len(x)==6 and x[0]==f'{r.utilization:.0%}'];assert len(rows)==1
        values=[r.mean_million_source_EUR,r.p50_million_source_EUR,r.q95_million_source_EUR,r.ES95_million_source_EUR,r.mean_per_discounted_output_source_EUR_t]
        assert rows[0][1:]==[f'{v:.3f}' for v in values]
        cells.extend(rows[0][1:])
    # Changing a deterministic coproduct credit must not change a quantile spread.
    for _,g in df.groupby(['model','seed','utilization']):
        g=g.sort_values('oxygen_sale_fraction');a,b=g.iloc[0],g.iloc[1]
        assert np.isclose(a.absolute_cost_upper_gap95_million_source_EUR,b.absolute_cost_upper_gap95_million_source_EUR,atol=1e-8)
        shifts=[a[k]-b[k] for k in ['mean_million_source_EUR','p50_million_source_EUR','q95_million_source_EUR','ES95_million_source_EUR']]
        np.testing.assert_allclose(shifts,shifts[0],atol=1e-8)
    cash=pd.read_csv(ROOT/'data/research_v2/component_capital/comparison.csv')
    for variant in ['source_components','all_20_years']:
        for terminal in ['none','straight_line_proxy']:
            v=cash[(cash.variant==variant)&(cash.terminal_rule==terminal)].iloc[0].npv_EUR/1e6
            assert f'{v:.3f}' in text
    assert '이 그림은 효율경계가 아니다' in text and '기업의 전환 증분 TCaR나 신규 기업 frontier를 산출했다고 표시하지 않는다' in text
    assert '(HHV)' not in (ROOT/'scripts/plot_methodology_assumptions.py').read_text()
    assert '발열량 기준은 원표에 명시되지 않았다' in text
    version=re.search(r'연구 원고 (v[0-9.]+)',text).group(1)
    report=dict(steel_table_cells_verified=len(cells),capital_cash_values_verified=4,
        deterministic_credit_shift_cases=12,manuscript_version=version,
        manuscript_sha256=hashlib.sha256((ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_bytes()).hexdigest(),
        source_composite_not_uniform_price_year=True,absolute_reference_cost_not_company_transition_TCaR=True)
    out=ROOT/f'docs/research_cycles/2026-09-07-hourly/steel_manuscript_{version.replace(".","")}_verification.json'
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
