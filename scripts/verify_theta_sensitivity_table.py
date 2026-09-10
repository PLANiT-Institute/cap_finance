"""Reconcile the 6.8 specification-sensitivity table with theta_case_comparison.csv."""
from pathlib import Path
import hashlib, json, re
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'paper/methodology/TCaR_METHOD_KO.md'
CSV = ROOT / 'data/research_v2/technology_packages/theta_case_comparison.csv'


def fmt_range(lo, hi, pct=False):
    if pct:
        f = lambda v: f'{v:+.1f}'.replace('-', '−')
        return f'{f(lo)}~{f(hi)}%'
    f = lambda v: f'{v:+,.0f}'.replace('-', '−')
    return f'{f(lo)}~{f(hi)}'


def main():
    text = PAPER.read_text()
    d = pd.read_csv(CSV)
    rows = [l for l in text.splitlines() if l.startswith('| 철강 전력') or l.startswith('| 석화 전력') or l.startswith('| 수소연료')]
    assert len(rows) >= 4, rows
    checked = []
    for case, label in [('steel_vogl_hot', '철강 전력 1.119'), ('steel_vogl_cold', '철강 전력 1.278'),
                        ('ncc_linde3', '석화 전력 3.25'), ('ncc_layritz', '석화 전력 6.99')]:
        g = d[(d.case == case) & (d.d_mean != 0)]
        if g.empty:
            cases = sorted(d.case.unique()); raise AssertionError((case, cases))
        line = next(l for l in rows if l.startswith(f'| {label} |'))
        cells = [c.strip() for c in line.strip('|').split('|')]
        assert cells[2] == fmt_range(g.d_mean.min(), g.d_mean.max()), (label, cells[2], fmt_range(g.d_mean.min(), g.d_mean.max()))
        assert cells[3] == fmt_range(g.d_tcar_pct.min(), g.d_tcar_pct.max(), pct=True), (label, cells[3])
        affected = sorted(set(zip(g.company, g.scenario)))
        changed = sorted(set(zip(g[g.plan_changed].company, g[g.plan_changed].scenario)))
        checked.append(dict(case=case, affected=[' '.join(a) for a in affected], plan_changed=[' '.join(c) for c in changed],
                            d_mean=[round(g.d_mean.min(), 2), round(g.d_mean.max(), 2)],
                            d_tcar_pct=[round(g.d_tcar_pct.min(), 2), round(g.d_tcar_pct.max(), 2)]))
    bf = d[d.case == 'base_fin']
    assert len(bf) == 8
    for _, r in bf.iterrows():
        line = f"| {r.company} · {r.scenario} | {r.selected_plan} | {r['mean']:,.2f} | {r.tcar:,.2f} |"
        assert line in text, line
    version = re.search(r'연구 원고 (v[\d.]+)', text).group(1).replace('.', '')
    report = dict(rows_checked=len(checked), base_fin_rows=8, cases=checked,
                  sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), CSV, PAPER]})
    (ROOT / f'docs/research_cycles/2026-09-08-hourly/theta_table_{version}_verification.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(checked, ensure_ascii=False))


if __name__ == '__main__':
    main()
