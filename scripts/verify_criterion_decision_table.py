"""Reconcile the 4.6 decision table with the frozen criterion_choices audit rows."""
from pathlib import Path
import hashlib, json, re
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'paper/methodology/TCaR_METHOD_KO.md'
CHOICES = ROOT / 'docs/research_cycles/2026-09-05/robustness_verified/criterion_choices.csv'


def main():
    text = PAPER.read_text()
    d = pd.read_csv(CHOICES).query("variant == 'baseline' and support == 'none'")
    rows = 0
    labels = {'LOTTE': 'LOTTE', 'MCI': 'MCI', 'NSC': 'NSC', 'POSCO': 'POSCO'}
    for (cid, sc), g in d.groupby(['company_id', 'scenario']):
        cells = []
        for crit in ['mean', 'tcar', 'es_alpha']:
            r = g[g.criterion == crit].iloc[0]
            sched = r.selected_plan_id.split('.')[0]
            cells.append(f'{sched} · {r.ppa_share:.2f}/{int(r.epc)}')
        line = f'| {labels[cid]} · {sc} | ' + ' | '.join(cells) + ' |'
        assert line in text, line
        rows += 1
    assert rows == 8
    mean_rows = d[d.criterion == 'mean']
    assert (mean_rows.ppa_share == 0).all() and (mean_rows.epc == 0).all()
    risk_rows = d[d.criterion != 'mean']
    assert (risk_rows.ppa_share >= 0.75).all()
    sched = d.assign(s=d.selected_plan_id.str.split('.').str[0]).groupby(['company_id', 'scenario']).s.nunique()
    assert set(sched[sched > 1].index) == {('LOTTE', 'NZ15'), ('MCI', 'B20'), ('MCI', 'NZ15')}
    for s in ['평균 최소 기준은 여덟 사례 모두에서 PPA 0·EPC 0을 고른다', '위험 기준은 여덟 사례 모두에서 PPA 0.75–1.00을 고른다',
              '세 사례(LOTTE NZ15, MCI B20, MCI NZ15)에서 다르다']:
        assert s in text, s
    # carbon-variant companion table (same plan, support none)
    c = pd.read_csv(ROOT / 'docs/research_cycles/2026-09-05/robustness_verified/candidate_statistics.csv')
    carbon_rows = 0
    for r in d[d.criterion == 'mean'].itertuples():
        pick = lambda v: c[(c.variant == v) & (c.company_id == r.company_id) & (c.scenario == r.scenario) & (c.plan_id == r.selected_plan_id) & (c.support == 'none')].iloc[0]
        b, z, h = pick('baseline'), pick('carbon_price_zero'), pick('carbon_price_half')
        assert abs(b.tcar - z.tcar) < 1e-9 and abs(b.tcar - h.tcar) < 1e-9
        line = f"| {r.company_id} · {r.scenario} | {b['mean']:,.2f} | {h['mean']:,.2f} | {z['mean']:,.2f} | {z.p50:,.2f} | {b.tcar:,.2f} | {z.es_alpha:,.2f} |"
        assert line in text, line
        carbon_rows += 1
    assert carbon_rows == 8
    version = re.search(r'연구 원고 (v[\d.]+)', text).group(1).replace('.', '')
    report = dict(table_rows=8, mean_criterion_all_uncontracted=True, risk_criterion_all_contracted=True,
                  schedule_changes=3, carbon_variant_rows=8, tcar_translation_invariant=True, sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                             for p in [Path(__file__), CHOICES, PAPER]})
    out = ROOT / f'docs/research_cycles/2026-09-08-hourly/criterion_decision_table_{version}_verification.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print({k: v for k, v in report.items() if k != 'sha256'})


if __name__ == '__main__':
    main()
