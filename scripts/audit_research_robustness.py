"""Independent simulation batches and declared structural stresses over a fixed candidate menu."""
from pathlib import Path
import argparse
import copy
from dataclasses import replace
from datetime import datetime, timezone
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
from cap.e3_prices import simulate_factors, load_shocks
from cap.e4_revalue import _central_px
from cap.e5_metrics import _empty_plan
from cap.plancost import build_profile, simulate_cost, support_params
from cap.risk_metrics import sampled_dominance_witnesses
from cap.price_process import PriceShocks, positive_exp
from cap.schemas import load_input
from verify_research_case import independent_stats


def bootstrap_statistics(values, indices, alpha=.9):
    samples=values[indices]
    median, upper=np.quantile(samples,[.5,alpha],axis=1)
    mass=(1-alpha)*samples.shape[1];whole=int(np.floor(mass));fraction=mass-whole
    count=whole+(fraction>0)
    tail=np.partition(samples,samples.shape[1]-count,axis=1)[:,-count:]
    if fraction:
        boundary=tail.min(axis=1)
        es=(tail.sum(axis=1)-(1-fraction)*boundary)/mass
    else:es=tail.mean(axis=1)
    return dict(mean=samples.mean(axis=1),p50=median,p90=upper,tcar=upper-median,es_alpha=es)


def variants(seed):
    return [
        dict(name='baseline',seed=seed),
        dict(name='independent_seed_1',seed=20260905),
        dict(name='independent_seed_2',seed=20260906),
        dict(name='initial_forecast_uncertainty',seed=seed,initial_forecast_uncertainty=True),
        dict(name='ou_10yr',seed=seed,process='ou'),
        dict(name='h2_vol_half',seed=seed,h2_vol_multiplier=.5),
        dict(name='h2_vol_1_5',seed=seed,h2_vol_multiplier=1.5),
        dict(name='capex_vol_double',seed=seed,capex_vol_multiplier=2.),
        dict(name='correlation_0_5',seed=seed,correlation=.5),
        dict(name='h2_price_0_7',seed=seed,h2_price_multiplier=.7),
        dict(name='h2_price_1_3',seed=seed,h2_price_multiplier=1.3),
        dict(name='carbon_price_half',seed=seed,carbon_price_multiplier=.5),
        dict(name='carbon_price_zero',seed=seed,carbon_price_multiplier=0.),
        dict(name='no_capital_renewals',seed=seed,include_capital_renewals=False),
        dict(name='terminal_straight_line',seed=seed,terminal_value_rule='straight_line_proxy'),
        dict(name='discount_3_5pct',seed=seed,discount_rate=.035),
        dict(name='discount_6_5pct',seed=seed,discount_rate=.065),
    ]


def add_initial_forecast_uncertainty(shocks,cal,seed=2026090502):
    """Add an independent initial state while preserving every future innovation."""
    rng=np.random.default_rng(seed);factors=['elec','h2','capex']
    initial=rng.standard_normal((shocks['elec'].shape[0],3)) @ np.linalg.cholesky(cal.corr.loc[factors,factors]).T
    draws={f:initial[:,j] for j,f in enumerate(factors)}
    draws['electrolyzer']=rng.standard_normal(shocks['elec'].shape[0])
    arrays={};variances={};maximum_error=0.
    for factor,values in shocks.items():
        sigma=shocks.metadata['innovation_sigma'][factor]
        process=shocks.metadata['factor_process'][factor]
        phi=1. if process=='gbm' else np.exp(-np.log(2)/shocks.metadata['ou_half_life'])
        decay=phi**np.arange(values.shape[1]);extra=sigma*sigma*decay*decay
        correction=extra/2 if shocks.normalisation=='mean' else 0.
        arrays[factor]=positive_exp(np.log(values)+sigma*draws[factor][:,None]*decay-correction)
        variances[factor]=shocks.log_variance[factor]+extra
        change=np.log(arrays[factor])-np.log(values)+correction
        error=float(np.max(np.abs(change[:,1:]-phi*change[:,:-1])))
        maximum_error=max(maximum_error,error)
    assert maximum_error<1e-12
    return PriceShocks(arrays,variances,shocks.normalisation,{**shocks.metadata,
        'initial_forecast_uncertainty':True,'initial_state_seed':seed,
        'maximum_future_innovation_change':maximum_error})


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--bootstrap',type=int,default=400)
    ap.add_argument('--only',nargs='*')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    cfg=C.load(args.config);run=Path(cfg.out_dir)
    source_manifest=json.loads((run/'run_manifest.json').read_text());assert source_manifest['status']=='completed'
    for name,expected in source_manifest['source_sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,f'Stale source: {name}'
    points=pd.read_csv(run/'e5/frontier_points.csv')
    assert points.budget_ok.all() and not points.is_disclosed.any()
    fac,tech,cal=_prep_company(cfg,C.data_dir(cfg));d5=load_input(C.data_dir(cfg),'D5_policy_support')
    prices=pd.read_csv(run/'e1/price_paths_central.csv');years=np.arange(cfg.years.start,cfg.years.end+1)
    plans={pid:pd.read_csv(run/'e2/plans'/f'plan_{pid}.csv') for pid in points.base_plan_id.unique()}
    report=dict(status='running',started_at_utc=datetime.now(timezone.utc).isoformat(),
                source_run_manifest_sha256=hashlib.sha256((run/'run_manifest.json').read_bytes()).hexdigest(),
                code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                n_sims=cfg.simulation.n_sims,alpha=.9,bootstrap_replicates=args.bootstrap,
                menu_scope='Fixed previously verified schedules and contract variants; no new E2 optimization under stresses',
                probability_scope='Conditional simulated-price draws; independent seeds are not empirical out-of-sample observations',
                uncertainty_scope='Stress multipliers are declared hypotheses, not empirically identified parameter confidence intervals',
                completed_variants=[])
    def save(): (args.out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    save();all_rows=[];choices=[];intervals=[];paired=[];baseline_choices={};baseline_errors=[]
    selected_variants=variants(cfg.seed)
    if args.only:selected_variants=[v for v in selected_variants if v['name'] in args.only]
    assert selected_variants and selected_variants[0]['name']=='baseline'
    for variant in selected_variants:
        print('START',variant['name'],flush=True)
        settings=C.Config(copy.deepcopy(dict(cfg)))
        for field in ['include_capital_renewals','terminal_value_rule','discount_rate']:
            if field in variant:settings[field]=variant[field]
        vc=copy.deepcopy(cal)
        for factor in ['h2','capex']:
            vc.vol[factor]*=variant.get(factor+'_vol_multiplier',1.)
        if 'correlation' in variant:
            rho=variant['correlation'];vc.corr=pd.DataFrame(np.eye(3)*(1-rho)+rho,index=['elec','h2','capex'],columns=['elec','h2','capex'])
        shocks=simulate_factors(vc,years,cfg.simulation.n_sims,np.random.default_rng(variant['seed']),
                                variant.get('process',cfg.price_process),cfg.ou_halflife_years,cfg.shock_normalisation)
        if variant.get('initial_forecast_uncertainty'):
            shocks=add_initial_forecast_uncertainty(shocks,vc)
            report['initial_forecast_test']=dict(method='Same future innovations plus independent initial state',
                initial_state_seed=shocks.metadata['initial_state_seed'],
                maximum_future_innovation_change=shocks.metadata['maximum_future_innovation_change'])
        if variant['name']=='baseline':
            stored=load_shocks(cfg)
            for factor in shocks:np.testing.assert_array_equal(shocks[factor],stored[factor])
        for (company,scenario,support),group in points.groupby(['company_id','scenario','support']):
            px=_central_px(prices,COMPANY_REGION[company],scenario,years,settings,vc)
            px['h2']=px['h2']*variant.get('h2_price_multiplier',1.)
            px['co2']=px['co2']*variant.get('carbon_price_multiplier',1.)
            sp=support_params(d5,support,years)
            baseline=build_profile(_empty_plan(company),fac,tech,px,years,settings)
            base_cost=simulate_cost(baseline,px,shocks,sp,settings)
            profiles={pid:build_profile(plans[pid],fac,tech,px,years,settings) for pid in group.base_plan_id.unique()}
            losses={};local=[]
            for row in group.itertuples():
                profile=replace(profiles[row.base_plan_id],ppa=row.ppa_share,epc=row.epc,ccfd=row.ccfd)
                loss=simulate_cost(profile,px,shocks,sp,settings)-base_cost;losses[row.plan_id]=loss
                stats=independent_stats(loss)
                if variant['name']=='baseline':
                    baseline_errors.extend(abs(value-getattr(row,key)) for key,value in stats.items())
                local.append(dict(variant=variant['name'],company_id=company,scenario=scenario,support=support,
                                  plan_id=row.plan_id,ppa_share=row.ppa_share,epc=row.epc,**stats))
            dominated=sampled_dominance_witnesses(losses)
            for row in local:
                row['sampled_dominated']=row['plan_id'] in dominated
                row['dominance_witness']=dominated.get(row['plan_id'],'')
            frame=pd.DataFrame(local);eligible=frame[~frame.sampled_dominated];all_rows.extend(local)
            picks=[]
            for criterion in ['mean','tcar','es_alpha']:
                ranked=eligible.sort_values([criterion,'mean','plan_id']);pick=ranked.iloc[0]
                key=(company,scenario,support,criterion)
                if variant['name']=='baseline':baseline_choices[key]=pick.plan_id
                original=baseline_choices[key];original_value=float(frame.set_index('plan_id').loc[original,criterion])
                choices.append(dict(variant=variant['name'],company_id=company,scenario=scenario,support=support,
                                    criterion=criterion,selected_plan_id=pick.plan_id,baseline_selected_plan_id=original,
                                    selection_changed=pick.plan_id!=original,minimum_value=pick[criterion],
                                    original_choice_value=original_value,sample_excess_of_original_choice=original_value-pick[criterion],
                                    original_choice_eligible=original not in dominated,
                                    mean=pick['mean'],p50=pick.p50,p90=pick.p90,tcar=pick.tcar,es_alpha=pick.es_alpha,
                                    ppa_share=pick.ppa_share,epc=pick.epc,sampled_dominated_candidates=len(dominated)))
                picks.append(pick.plan_id)
            if variant['name']=='baseline' and args.bootstrap:
                # Same resampled path IDs across candidates preserve paired comparisons.
                indices=np.random.default_rng(2026090501).integers(0,len(base_cost),size=(args.bootstrap,len(base_cost)),dtype=np.int32)
                for pid in sorted(set(picks)):
                    boot=bootstrap_statistics(losses[pid],indices);point=frame.set_index('plan_id').loc[pid]
                    for metric,values in boot.items():
                        lo,hi=np.quantile(values,[.025,.975]);intervals.append(dict(company_id=company,scenario=scenario,support=support,
                            plan_id=pid,metric=metric,point=point[metric],bootstrap_low_95=lo,bootstrap_high_95=hi,
                            interval_scope='Conditional fixed-candidate Monte Carlo sampling interval; no parameter or selection adjustment'))
                ranked=eligible.sort_values(['mean','es_alpha','plan_id'])
                first,second=ranked.iloc[0].plan_id,ranked.iloc[1].plan_id
                delta=losses[second]-losses[first];boot_delta=delta[indices].mean(axis=1);lo,hi=np.quantile(boot_delta,[.025,.975])
                paired.append(dict(company_id=company,scenario=scenario,selected=first,runner_up=second,
                                   mean_cost_difference=float(delta.mean()),paired_bootstrap_low_95=lo,paired_bootstrap_high_95=hi,
                                   interval_scope='Paired runner-up minus selected mean; fixed candidates, unadjusted for selection'))
        pd.DataFrame(all_rows).to_csv(args.out/'candidate_statistics.csv',index=False)
        pd.DataFrame(choices).to_csv(args.out/'criterion_choices.csv',index=False)
        pd.DataFrame(intervals).to_csv(args.out/'fixed_candidate_bootstrap.csv',index=False)
        pd.DataFrame(paired).to_csv(args.out/'paired_mean_differences.csv',index=False)
        report['completed_variants'].append(variant);save();print('DONE',variant['name'],flush=True)
    assert max(baseline_errors)<1e-6
    report.update(status='completed',finished_at_utc=datetime.now(timezone.utc).isoformat(),
                  candidate_evaluations=len(all_rows),criterion_comparisons=len(choices),bootstrap_intervals=len(intervals),
                  maximum_baseline_statistic_error=max(baseline_errors))
    save();print(json.dumps(report,indent=2))


if __name__=='__main__':main()
