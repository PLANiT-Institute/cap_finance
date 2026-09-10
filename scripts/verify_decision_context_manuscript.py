"""Audit the explanatory procurement algebra and unchanged manuscript tables."""
from pathlib import Path
import hashlib
import itertools
import json
import re

import numpy as np
import pandas as pd

from verify_methodology_manuscript import verify as verify_legacy
from verify_joint_manuscript import verify as verify_joint

ROOT = Path(__file__).resolve().parents[1]


def main():
    paper = ROOT / 'paper/methodology/TCaR_METHOD_KO.md'
    text = paper.read_text()
    legacy, joint = verify_legacy(), verify_joint()
    # Compare each displayed simplified expression with two full purchase bills.
    rows = []
    for pf, pg, pe, h in itertools.product([1., 1000.], [1., 10., 100.],
                                          [1., 40., 200.], [0., .25, .5, .75, 1.]):
        strike = 50.
        baseline = 100 * pf + 10 * pg + 2 * pe
        transition = 100 * pf + 4 * pg + 8 * ((1-h) * pe + h * strike)
        simplified = (6-8*h) * pe - 6 * pg + 8*h*strike
        np.testing.assert_allclose(transition-baseline, simplified, atol=1e-9)
        rows.append(dict(feedstock_price=pf, gas_price=pg, power_price=pe,
                         hedge_fraction=h, baseline=baseline, transition=transition,
                         difference=transition-baseline, simplified=simplified))
    demo = pd.DataFrame(rows)
    # At 75%, different spot power prices give the same incremental cost;
    # at 100%, the incremental exposure is -2 even though the new bill is fixed.
    for (_, pg, h), group in demo.groupby(['feedstock_price', 'gas_price', 'hedge_fraction']):
        group = group.sort_values('power_price')
        slope = np.diff(group.difference) / np.diff(group.power_price)
        np.testing.assert_allclose(slope, 6-8*h, atol=1e-9)
    table_rows = [[v.strip() for v in l.strip('|').split('|')]
                  for l in text.splitlines() if l.startswith('|')]
    steel = pd.read_csv(ROOT/'data/research_v2/steel_reference_ledger/absolute_cost_sensitivity.csv')
    steel_cells = 0
    for r in steel.query('model == "block_12" and seed == 20260908 and oxygen_sale_fraction == 0.6').itertuples():
        printed = [v for v in table_rows if len(v)==6 and v[0]==f'{r.utilization:.0%}']
        expected = [f'{v:.3f}' for v in [r.mean_million_source_EUR, r.p50_million_source_EUR,
                    r.q95_million_source_EUR, r.ES95_million_source_EUR,
                    r.mean_per_discounted_output_source_EUR_t]]
        assert len(printed)==1 and printed[0][1:]==expected
        steel_cells += 5
    captions=re.findall(r'\*\*그림 (\d+)\.', text)
    assert captions==[str(i) for i in range(1,len(captions)+1)]
    assert text.count('### 1.1 이 연구')==text.count('### 3.6 원료')==1
    assert '이 가상 원장의 전력 노출을 상쇄하는 비율일 뿐 최적 계약비율은 아니다' in text
    assert '매 시점 GCAM의 시장균형을 만족한다고 주장하지 않는다' in text
    assert '100 t/년 | 100 t/년 | 0 t/년' in text
    version=re.search(r'연구 원고 (v[0-9.]+)',text).group(1)
    report = dict(manuscript_version=version, toy_ledger_cases=len(rows),
                  toy_inputs_are_hypothetical=True, corporate_results_reestimated=False,
                  prior_printed_cells_verified=len(legacy['checked_cells'])+len(joint['checked_cells'])+steel_cells,
                  numbered_equations=12, figures=len(captions),
                  primary_context_source='https://jgcri.github.io/gcam-doc/overview.html')
    out = ROOT/'docs/research_cycles/2026-09-07-hourly'
    demo.to_csv(out/'decision_context_toy_ledger.csv', index=False)
    files = [paper, ROOT/'paper/methodology/DECISION_CONTEXT_KO.md',
             ROOT/'scripts/integrate_research_v2_manuscript.py', Path(__file__),
             ROOT/'output/pdf/TCaR_methodology.pdf', out/'decision_context_toy_ledger.csv']
    report['sha256'] = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (out/f'decision_context_{version.replace(".","")}_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='sha256'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
