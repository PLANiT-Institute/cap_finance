"""Reprice the current menu with the tested positive log-price scaling formula.

Keeps all other accounting assumptions unchanged to isolate this correction.
"""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
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
from cap.e5_metrics import _carbon_npv,_empty_plan
from cap.plancost import build_profile,simulate_cost,auction_share,support_params
from cap.risk_metrics import loss_summary
from cap.schemas import load_input
from positive_price_model import log_variance_path,scale_lognormal_multiplier


def main():
    cfg=C.load(capex_shock_scaling="legacy_linear", allow_legacy_price_paths=True, capital_accounting="legacy_mixed", energy_balance_mode="legacy_retrofit_all", carbon_accounting_mode="legacy_auction_discount", transition_loss_basis="incremental_ex_carbon", plan_selection_criterion="p50")
    assert cfg.price_process=='gbm' and cfg.shock_normalisation=='mean', 'This audit targets the saved GBM mean-normalized run'
    ddir=C.data_dir(cfg);out=ROOT/'docs/research_cycles/2026-09-05/positive_prices';out.mkdir(parents=True,exist_ok=True)
    points_path=C.out_dir(cfg,'e5')/'frontier_points.csv'
    prices_path=C.out_dir(cfg,'e1')/'price_paths_central.csv'
    report_path=C.out_dir(cfg,'e3')/'calibration_report.csv'
    points,prices,report=pd.read_csv(points_path),pd.read_csv(prices_path),pd.read_csv(report_path)
    sigma=float(report.set_index('param').loc['vol_capex','value'])
    years=np.arange(cfg.years.start,cfg.years.end+1);disc=(1+cfg.discount_rate)**-(years-years[0])
    shocks=load_shocks(cfg);v=log_variance_path(sigma,len(years),'gbm')
    fac,tech,cal=_prep_company(cfg,ddir);d5=load_input(ddir,'D5_policy_support');auc=auction_share(years,cfg)
    rows,choices,diagnostics=[],[],[]
    positive={}
    for tid,u in tech[['tech_id','capex_uncertainty']].itertuples(index=False,name=None):
        a=u/40.;pos=scale_lognormal_multiplier(shocks['capex'],a,v,'mean');positive[tid]=pos
        linear=1+(shocks['capex']-1)*a
        diagnostics.append(dict(tech_id=tid,amplitude=a,linear_min=float(linear.min()),positive_min=float(pos.min()),
            positive_max=float(pos.max()),linear_negative_cells=int((linear<0).sum()),positive_negative_cells=int((pos<=0).sum())))
    files={Path(__file__),ROOT/'scripts/positive_price_model.py',ROOT/'config.yaml',points_path,prices_path,report_path,C.out_dir(cfg,'e3')/'price_sims.parquet'}
    files.update(ddir.glob('*.csv'));files.update((ROOT/'src/cap').glob('*.py'))
    for (co,sc,supp),g in points.groupby(['company_id','scenario','support']):
        px=_central_px(prices,COMPANY_REGION[co],sc,years,cfg,cal);sp=support_params(d5,supp,years)
        base=build_profile(_empty_plan(co),fac,tech,px,years,cfg)
        base_draws=simulate_cost(base,px,shocks,sp,cfg);base_carbon=_carbon_npv(base,px,disc,auc)
        for r in g.itertuples():
            path=C.out_dir(cfg,'e2')/'plans'/f'plan_{r.base_plan_id}.csv';files.add(path)
            prof=build_profile(pd.read_csv(path),fac,tech,px,years,cfg)
            prof=replace(prof,ppa=r.ppa_share,epc=int(r.epc),ccfd=int(r.ccfd))
            old=simulate_cost(prof,px,shocks,sp,cfg)-base_draws-(_carbon_npv(prof,px,disc,auc)-base_carbon)
            stats=loss_summary(old)
            np.testing.assert_allclose([stats['p50'],stats['tcar']],[r.p50,r.tcar],atol=1e-6,rtol=0)
            delta=np.zeros_like(old)
            if not prof.epc:
                for tid,arr in prof.capex_by_tech.items():
                    sub=sp['subsidy'].get(tid,sp['subsidy'].get('all',0.))
                    linear=1+(shocks['capex']-1)*prof.capex_unc[tid]/40.
                    delta+=((positive[tid]-linear)*(arr*(1-sub)*disc)[None,:]).sum(axis=1)*1e-6
            new=loss_summary(old+delta)
            rows.append(dict(company_id=co,scenario=sc,support=supp,plan_id=r.plan_id,
                is_disclosed=r.is_disclosed,budget_ok=r.budget_ok,ppa_share=r.ppa_share,epc=r.epc,
                old_p50=stats['p50'],old_mean=stats['mean'],old_tcar=stats['tcar'],old_es_alpha=stats['es_alpha'],**new))
    result=pd.DataFrame(rows)
    for key,g in result[~result.is_disclosed & result.budget_ok].groupby(['company_id','scenario','support']):
        for metric in ['p50','mean','tcar','es_alpha']:
            old=g.sort_values(['old_'+metric,'plan_id']).iloc[0];new=g.sort_values([metric,'plan_id']).iloc[0]
            choices.append(dict(zip(['company_id','scenario','support'],key))|dict(criterion=metric,old_plan_id=old.plan_id,new_plan_id=new.plan_id,changed=old.plan_id!=new.plan_id))
    result.to_csv(out/'risk_comparison.csv',index=False)
    pd.DataFrame(choices).to_csv(out/'choice_comparison.csv',index=False)
    pd.DataFrame(diagnostics).to_csv(out/'price_domain_checks.csv',index=False)
    manifest=dict(scope='Saved GBM mean-normalized candidate menu; price scaling only; no reoptimization or other accounting corrections',evaluated_candidates=len(result),
        changed_choices=sum(r['changed'] for r in choices),choice_comparisons=len(choices),base_capex_sigma=sigma,
        max_abs_tcar_change=float((result.tcar-result.old_tcar).abs().max()),production_engine_changed=False,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()
