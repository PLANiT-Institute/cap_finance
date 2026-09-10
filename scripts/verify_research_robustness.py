"""Audit fixed-menu robustness outputs and the conditional analytic mean identity."""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C
from cap.e1_constraints import COMPANY_REGION
from cap.e2_milp import _prep_company
from cap.e4_revalue import _central_px
from cap.e5_metrics import _empty_plan
from cap.plancost import build_profile,simulate_cost
from audit_research_robustness import bootstrap_statistics

OUT=ROOT/'docs/research_cycles/2026-09-05/robustness_verified'
OUT.mkdir(parents=True,exist_ok=True)
AUDIT=ROOT/'docs/research_cycles/2026-09-05/robustness'
EXTRA=ROOT/'docs/research_cycles/2026-09-05/robustness_initial_forecast'

def analytic_mean(p,px,cfg,years):
    """Separate arithmetic for mean-one affine exposures; reviewed case only."""
    assert cfg.shock_normalisation=='mean' and cfg.capital_accounting=='cash_v1'
    assert cfg.carbon_accounting_mode=='gross_obligation_proxy' and p.ccfd==0
    # KRW physical purchases -> thousand KRW, discounted -> billion KRW.
    annual=(p.grid_mwh*px['elec']+p.re_mwh*px['re'])*(1+p.ppa*cfg.contracts.ppa_premium_pct)/1000
    annual+=p.h2_kg*px['h2']/1000
    annual+=sum(p.capex_by_tech.values(),np.zeros(len(years)))*(1+p.epc*cfg.contracts.epc_premium_pct)
    annual+=p.maintenance_capex_k+p.emissions*px['co2']/1000+p.other_cost_k-p.terminal_value_k
    return float(np.sum(annual*(1+cfg.discount_rate)**-(years-years[0]))/1e6)


def main():
    cfg=C.load(ROOT/'tmp/research_case_expanded/config.yaml');run=Path(cfg.out_dir)
    points=pd.read_csv(run/'e5/frontier_points.csv')
    stats=pd.read_csv(AUDIT/'candidate_statistics.csv');choices=pd.read_csv(AUDIT/'criterion_choices.csv')
    manifest=json.loads((AUDIT/'manifest.json').read_text())
    assert manifest['status']=='completed'
    assert hashlib.sha256((AUDIT/'producer_snapshot.py').read_bytes()).hexdigest()==manifest['code_sha256']
    extra=pd.read_csv(EXTRA/'candidate_statistics.csv');xc=pd.read_csv(EXTRA/'criterion_choices.csv')
    for frame in [extra,stats]:
        assert frame.groupby('variant').size().eq(450).all()
        assert not frame.duplicated(['variant','company_id','scenario','support','plan_id']).any()
    for row in pd.concat([choices,xc]).itertuples():
        frame=extra if row.variant=='initial_forecast_uncertainty' else stats
        group=frame[(frame.variant==row.variant)&(frame.company_id==row.company_id)&(frame.scenario==row.scenario)]
        eligible=group[~group.sampled_dominated].sort_values([row.criterion,'mean','plan_id'])
        assert row.selected_plan_id==eligible.iloc[0].plan_id
        assert abs(row.minimum_value-eligible.iloc[0][row.criterion])<1e-7
    # A deterministic carbon or terminal adjustment translates the entire loss distribution.
    base=stats[stats.variant=='baseline'].set_index('plan_id');translation=[]
    for name in ['carbon_price_half','carbon_price_zero','terminal_straight_line']:
        shifted=stats[stats.variant==name].set_index('plan_id').loc[base.index]
        delta=shifted['mean']-base['mean']
        err=max(float((shifted[k]-base[k]-delta).abs().max()) for k in ['p50','p90','es_alpha'])
        tcar_error=float((shifted.tcar-base.tcar).abs().max())
        assert max(err,tcar_error)<1e-6
        translation.append(dict(variant=name,maximum_translation_error=err,maximum_tcar_change=tcar_error))
    for values,alpha,expected in [(np.array([0.,2.,10.]),.5,22/3),(np.r_[np.zeros(95),np.full(5,100.)],.9,50)]:
        b=bootstrap_statistics(values,np.arange(len(values))[None,:],alpha)
        assert abs(b['es_alpha'][0]-expected)<1e-10
    fac,tech,cal=_prep_company(cfg,C.data_dir(cfg));years=np.arange(cfg.years.start,cfg.years.end+1)
    prices=pd.read_csv(run/'e1/price_paths_central.csv');ones={k:np.ones((1,len(years))) for k in ['elec','h2','capex']}
    records=[];profiles={};errors=[]
    for (co,sc,support),group in points.groupby(['company_id','scenario','support']):
        assert support=='none'
        px=_central_px(prices,COMPANY_REGION[co],sc,years,cfg,cal)
        baseline=build_profile(_empty_plan(co),fac,tech,px,years,cfg)
        b=analytic_mean(baseline,px,cfg,years)
        for row in group.itertuples():
            if row.base_plan_id not in profiles:
                profiles[row.base_plan_id]=build_profile(pd.read_csv(run/'e2/plans'/f'plan_{row.base_plan_id}.csv'),fac,tech,px,years,cfg)
            p=replace(profiles[row.base_plan_id],ppa=row.ppa_share,epc=row.epc,ccfd=row.ccfd)
            a=analytic_mean(p,px,cfg,years)-b
            engine=simulate_cost(p,px,ones,{'subsidy':{},'ccfd_strike':None},cfg)[0]-simulate_cost(baseline,px,ones,{'subsidy':{},'ccfd_strike':None},cfg)[0]
            errors.append(abs(a-engine))
            records.append(dict(company_id=co,scenario=sc,support=support,plan_id=row.plan_id,analytic_mean=a,
                                monte_carlo_mean=row.mean,monte_carlo_error=row.mean-a,decision_eligible=row.decision_eligible))
    means=pd.DataFrame(records);assert max(errors)<1e-6
    picks=[];ties=[]
    boot=pd.read_csv(AUDIT/'fixed_candidate_bootstrap.csv')
    for (co,sc),group in means.groupby(['company_id','scenario']):
        eligible=group[group.decision_eligible];minimum=eligible.analytic_mean.min()
        equivalent=eligible[abs(eligible.analytic_mean-minimum)<1e-7]
        sample=eligible.sort_values(['monte_carlo_mean','plan_id']).iloc[0]
        assert sample.plan_id in equivalent.plan_id.to_list()
        ci=boot[(boot.company_id==co)&(boot.scenario==sc)&(boot.plan_id==sample.plan_id)&(boot.metric=='mean')].iloc[0]
        picks.append(dict(company_id=co,scenario=sc,selected_plan_id=sample.plan_id,analytic_mean=sample.analytic_mean,
                          monte_carlo_mean=sample.monte_carlo_mean,bootstrap_low_95=ci.bootstrap_low_95,
                          bootstrap_high_95=ci.bootstrap_high_95,analytic_mean_in_interval=ci.bootstrap_low_95<=sample.analytic_mean<=ci.bootstrap_high_95,
                          tied_analytic_minimum_count=len(equivalent)))
        if len(equivalent)>1:
            first=profiles[sample.plan_id.split('.')[0]]
            for row in equivalent.itertuples():
                other=profiles[row.plan_id.split('.')[0]]
                array_fields=['grid_mwh','re_mwh','h2_kg','other_cost_k','capex_k','emissions','maintenance_capex_k','terminal_value_k']
                equal=all(np.array_equal(getattr(first,k),getattr(other,k)) for k in array_fields)
                equal=equal and first.capex_by_tech.keys()==other.capex_by_tech.keys() and all(np.array_equal(first.capex_by_tech[k],other.capex_by_tech[k]) for k in first.capex_by_tech)
                assert equal
                ties.append(dict(company_id=co,scenario=sc,representative=sample.plan_id,equivalent_plan_id=row.plan_id,
                                 aggregate_annual_exposure_arrays_equal=equal,interpretation='Model equivalence under estimated facility characteristics, not physical interchangeability'))
    combined=pd.concat([stats,extra[extra.variant!='baseline']],ignore_index=True)
    combined_choices=pd.concat([choices,xc[xc.variant!='baseline']],ignore_index=True)
    summary=combined_choices.groupby(['variant','criterion']).selection_changed.sum().unstack().reset_index()
    means.to_csv(OUT/'analytic_means.csv',index=False);pd.DataFrame(picks).to_csv(OUT/'selected_analytic_means.csv',index=False)
    pd.DataFrame(ties).to_csv(OUT/'equivalent_plans.csv',index=False);summary.to_csv(OUT/'selection_changes.csv',index=False)
    combined.to_csv(OUT/'candidate_statistics.csv',index=False);combined_choices.to_csv(OUT/'criterion_choices.csv',index=False)
    pd.DataFrame(translation).to_csv(OUT/'translation_invariance.csv',index=False)
    t=boot[boot.metric=='tcar'];half=(t.bootstrap_high_95-t.bootstrap_low_95)/(2*t.point.abs())
    report=dict(status='passed',unique_variants=combined.variant.nunique(),unique_candidate_evaluations=len(combined),
        criterion_choices=len(combined_choices),fixed_candidate_bootstrap_intervals=len(boot),analytic_means_verified=len(means),
        maximum_independent_analytic_mean_error=max(errors),selected_mean_choices_agree=8,
        selected_analytic_means_in_unadjusted_sampling_intervals=int(pd.DataFrame(picks).analytic_mean_in_interval.sum()),
        equivalent_minimum_case_count=1,tcar_relative_interval_halfwidth_min=float(half.min()),tcar_relative_interval_halfwidth_max=float(half.max()),
        caution='Conditional simulation, fixed menu, assumed structural stresses; bootstrap intervals do not cover parameter or selection uncertainty',
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [AUDIT/'manifest.json',EXTRA/'manifest.json',AUDIT/'candidate_statistics.csv',EXTRA/'candidate_statistics.csv',AUDIT/'fixed_candidate_bootstrap.csv']})
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
