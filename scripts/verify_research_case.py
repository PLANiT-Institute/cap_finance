"""Revalue every saved research candidate and audit its executable quantities."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C
from cap.e1_constraints import COMPANY_REGION
from cap.e2_milp import _prep_company
from cap.e3_prices import load_shocks
from cap.e4_revalue import _central_px
from cap.e5_metrics import _empty_plan
from cap.plancost import build_profile,simulate_cost,support_params
from cap.schemas import load_input


def independent_stats(values,alpha=.9):
    ordered=np.sort(values);mass=(1-alpha)*len(ordered)
    whole=int(np.floor(mass));fraction=mass-whole
    total=ordered[-whole:].sum() if whole else 0.
    if fraction:total+=fraction*ordered[-whole-1]
    median,upper=np.quantile(values,[.5,alpha])
    return dict(mean=float(np.mean(values)),p50=float(median),p90=float(upper),
                tcar=float(upper-median),es_alpha=float(total/mass))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--compare-current-code',action='store_true',
                    help='Explicit regression comparison: permit recorded src/cap code changes, never changed inputs')
    args=ap.parse_args();cfg=C.load(args.config);run=Path(cfg.out_dir)
    manifest=json.loads((run/'run_manifest.json').read_text())
    assert manifest['status']=='completed'
    changed_code = []
    for name,expected in manifest['source_sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected and args.compare_current_code and path.resolve().is_relative_to((ROOT/'src/cap').resolve()):
            changed_code.append(dict(path=str(path.relative_to(ROOT)),saved_sha256=expected,current_sha256=actual))
        else:
            assert actual==expected, f'Stale source/input: {path}'
    args.out.mkdir(parents=True,exist_ok=True)
    idx=pd.read_csv(run/'e2/plan_index.csv')
    assert idx.primal_feasible.all() and not idx.is_disclosed.any()
    assert set(idx.budget_mode)=={'cumulative_hard'}
    assert set(idx.solution_status)<= {'Optimal Solution Found','Solution Found'}
    fac,tech,cal=_prep_company(cfg,C.data_dir(cfg))
    prices=pd.read_csv(run/'e1/price_paths_central.csv');shocks=load_shocks(cfg)
    years=np.arange(cfg.years.start,cfg.years.end+1)
    central={k:np.ones((1,len(years))) for k in shocks}
    budgets=pd.read_csv(run/'e1/constraints.csv')
    points=pd.read_csv(run/'e5/frontier_points.csv')
    d5=load_input(C.data_dir(cfg),'D5_policy_support')
    ledger,checks,rows=[],[],[];profiles={}
    for (company,scenario),g in idx.groupby(['company_id','scenario']):
        px=_central_px(prices,COMPANY_REGION[company],scenario,years,cfg,cal)
        budget=budgets[(budgets.company_id==company)&(budgets.scenario==scenario)].set_index('year').company_budget_tco2.reindex(years).to_numpy()
        baseline=build_profile(_empty_plan(company),fac,tech,px,years,cfg)
        for r in g.itertuples():
            plan=pd.read_csv(run/'e2/plans'/f'plan_{r.plan_id}.csv')
            adopted=plan.dropna(subset=['tech_id'])
            assert adopted.facility_id.is_unique
            for a in adopted.itertuples():
                assert a.adopt_year>=years[0] and a.op_year<=years[-1]
                assert a.tech_id!='retire'  # fixed-output portfolio convention for this research case
                tk=tech.set_index('tech_id').loc[a.tech_id]
                assert a.op_year==a.adopt_year+tk.build_years
                assert a.adopt_year>=tk.avail_year
                assert tk.applies_to_unit==fac.loc[a.facility_id,'unit_type']
            p=build_profile(plan,fac,tech,px,years,cfg)
            profiles[r.plan_id]=p
            np.testing.assert_allclose(p.capex_k,sum(p.capex_by_tech.values(),np.zeros(len(years)))+p.maintenance_capex_k,atol=1e-5)
            assert not p.terminal_value_k.any()
            assert p.emissions.sum()<=budget.sum()+max(1.,budget.sum())*1e-6
            np.testing.assert_allclose(p.emissions.sum(),r.cum_emis_tco2,atol=1e-3,rtol=1e-10)
            central_cost=simulate_cost(p,px,central,support_params(d5,'none',years),cfg)[0]
            np.testing.assert_allclose(central_cost,r.npv_cost_bnkrw,atol=1e-6,rtol=0)
            checks.append(dict(company_id=company,scenario=scenario,plan_id=r.plan_id,
                cumulative_emissions=float(p.emissions.sum()),cumulative_budget=float(budget.sum()),
                annual_budget_compliant=bool(np.all(p.emissions<=budget+1e-3)),
                annual_excess_tco2=float(np.maximum(p.emissions-budget,0).sum()),
                central_cost_reconciliation_error=float(central_cost-r.npv_cost_bnkrw)))
            for i,year in enumerate(years):
                ledger.append(dict(company_id=company,scenario=scenario,plan_id=r.plan_id,year=int(year),
                    plan_gross_capex_k=p.capex_k[i],baseline_gross_capex_k=baseline.capex_k[i],
                    incremental_gross_capex_k=p.capex_k[i]-baseline.capex_k[i],
                    noncash_writeoff_k=p.noncash_writeoff_k[i],maintenance_capex_k=p.maintenance_capex_k[i],
                    plan_scope1_tco2=p.emissions[i],baseline_scope1_tco2=baseline.emissions[i]))
        pg=points[(points.company_id==company)&(points.scenario==scenario)]
        for support,sg in pg.groupby('support'):
            sp=support_params(d5,support,years)
            base=simulate_cost(baseline,px,shocks,sp,cfg)
            from dataclasses import replace
            losses={}
            for r in sg.itertuples():
                p=replace(profiles[r.base_plan_id],ppa=r.ppa_share,epc=r.epc,ccfd=r.ccfd)
                loss=simulate_cost(p,px,shocks,sp,cfg)-base
                losses[r.plan_id]=loss
                stats=independent_stats(loss)
                errors={key:stats[key]-getattr(r,key) for key in stats}
                assert max(abs(v) for v in errors.values())<1e-6,(r.plan_id,errors)
                rows.append(dict(company_id=company,scenario=scenario,support=support,plan_id=r.plan_id,
                                 **stats,maximum_statistic_error=max(abs(v) for v in errors.values())))
            for r in sg.itertuples():
                if r.sampled_statewise_dominated:
                    alternative=losses[r.sampled_dominance_witness]
                    assert np.all(alternative<=losses[r.plan_id]+1e-9)
                    assert np.any(alternative<losses[r.plan_id]-1e-9)
    metrics=pd.read_csv(run/'e5/metrics_company.csv')
    for r in metrics.itertuples():
        group=points[(points.company_id==r.company_id)&(points.scenario==r.scenario)&(points.support==r.support)]
        best=group[group.decision_eligible].sort_values(['mean','es_alpha','plan_id']).iloc[0]
        assert best.plan_id==r.selected_plan_id
    gap=pd.read_csv(run/'e5/gap.csv');assert gap.empty
    funding=pd.read_csv(run/'e5/affordability.csv')
    assert funding[funding.company_id!='POSCO'].capex_peak_to_ebitda.isna().all()
    assert funding.netdebt_to_ebitda_post.isna().all()
    assert funding[funding.company_id=='POSCO'].ebitda_ref_bnkrw.eq(4230).all()
    pd.DataFrame(checks).to_csv(args.out/'plan_feasibility_and_cost.csv',index=False)
    pd.DataFrame(ledger).to_csv(args.out/'paired_annual_capital_and_emissions.csv',index=False)
    pd.DataFrame(rows).to_csv(args.out/'independent_candidate_risk.csv',index=False)
    report=dict(comparison_with_current_code=args.compare_current_code,changed_code=changed_code,
        current_cap_source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted((ROOT/'src/cap').glob('*.py'))},
        schedule_count=len(idx),evaluated_candidate_count=len(points),price_paths=shocks['elec'].shape[0],
        independent_risk_cells=len(rows)*5,annual_ledger_rows=len(ledger),
        annual_budget_compliant_schedules=sum(r['annual_budget_compliant'] for r in checks),
        cumulative_budget_compliant_schedules=len(checks),sampled_dominated_candidates=int(points.sampled_statewise_dominated.sum()),
        selected_mean_cost_plans_verified=len(metrics),validated_disclosed_comparators=0,
        maximum_central_cost_error_bnkrw=max(abs(r['central_cost_reconciliation_error']) for r in checks),
        maximum_risk_statistic_error_bnkrw=max(r['maximum_statistic_error'] for r in rows),
        run_manifest_sha256=hashlib.sha256((run/'run_manifest.json').read_bytes()).hexdigest(),
        implementation_and_conditional_results_verified=True,
        company_coverage_or_heat_balance_or_all_price_deflators_verified=False,
        caveat='These checks verify the declared conditional model; they do not turn estimated inputs into measurements')
    (args.out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
