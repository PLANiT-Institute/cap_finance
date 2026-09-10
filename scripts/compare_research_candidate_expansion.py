"""Audit preservation and decision changes when a verified candidate menu expands."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--expanded', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(args.base / 'e5/frontier_points.csv')
    expanded = pd.read_csv(args.expanded / 'e5/frontier_points.csv')
    keys = ['company_id', 'scenario', 'support']
    numeric = ['p50', 'p90', 'mean', 'tcar', 'es_alpha']
    old = base.set_index('plan_id').sort_index()
    kept = expanded.set_index('plan_id').loc[old.index]
    np.testing.assert_allclose(old[numeric], kept[numeric], atol=1e-8, rtol=0)
    for key in keys:
        assert old[key].equals(kept[key])
    rows = []
    for values, group in base.groupby(keys):
        other = expanded
        for key, value in zip(keys, values):
            other = other[other[key] == value]
        for criterion in ['mean', 'tcar', 'es_alpha']:
            a = group[group.decision_eligible].sort_values([criterion, 'mean', 'plan_id']).iloc[0]
            b = other[other.decision_eligible].sort_values([criterion, 'mean', 'plan_id']).iloc[0]
            rows.append(dict(zip(keys, values), criterion=criterion,
                base_plan=a.plan_id, expanded_plan=b.plan_id,
                base_value=a[criterion], expanded_value=b[criterion],
                reduction=a[criterion]-b[criterion],
                changed=bool(a.plan_id != b.plan_id),
                base_menu_size=len(group), expanded_menu_size=len(other),
                base_eligible=int(group.decision_eligible.sum()), expanded_eligible=int(other.decision_eligible.sum())))
    comparison = pd.DataFrame(rows)
    comparison.to_csv(args.out / 'candidate_expansion_comparison.csv', index=False)
    report = dict(base_candidates=len(base), expanded_candidates=len(expanded),
        preserved_candidates=len(kept), maximum_preservation_error=float(np.abs(old[numeric].to_numpy()-kept[numeric].to_numpy()).max()),
        changed_choices=comparison.groupby('criterion').changed.sum().astype(int).to_dict(),
        source_hashes={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            args.base/'run_manifest.json', args.expanded/'run_manifest.json',
            args.base/'e5/frontier_points.csv', args.expanded/'e5/frontier_points.csv']},
        interpretation='Only this nested candidate expansion is tested; no completeness or global optimality certificate is implied.')
    (args.out / 'candidate_expansion_validation.json').write_text(json.dumps(report, indent=2)+'\n')
    metrics = pd.read_csv(args.expanded / 'e5/metrics_company.csv')
    lines = ['| 기업 | 시나리오 | 선택 후보 | P50 | 평균 | TCaR90 | ES90 |',
             '|---|---|---|---:|---:|---:|---:|']
    for r in metrics.itertuples():
        lines.append(f'| {r.company_id} | {r.scenario} | {r.selected_plan_id} | {r.p50_bnkrw:,.2f} | {r.mean_bnkrw:,.2f} | {r.tcar_bnkrw:,.2f} | {r.es_alpha_bnkrw:,.2f} |')
    (args.out / 'selected_case_table.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
