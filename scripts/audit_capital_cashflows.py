"""Isolate capital accounting effects on the saved candidate menu.

This does not regenerate schedules or fix the production engine. Removing book
entries is a controlled counterfactual, not a complete cash-flow valuation.
"""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C
from cap.e1_constraints import COMPANY_REGION
from cap.e2_milp import _prep_company
from cap.e3_prices import load_shocks
from cap.e4_revalue import _central_px
from cap.e5_metrics import _carbon_npv, _empty_plan
from cap.plancost import auction_share, build_profile, simulate_cost, support_params
from cap.risk_metrics import loss_summary
from cap.schemas import load_input


def split_capital(plan, fac, tech, years, cfg, profile):
    n = len(years)
    construction, conversion, retirement, terminal = (np.zeros(n) for _ in range(4))
    conversion_by_tech = {}
    company = plan.company_id.iloc[0]
    tf = tech.set_index("tech_id")
    for row in plan.itertuples():
        if pd.isna(row.tech_id): continue
        fr = fac.loc[row.facility_id]
        ta = int(row.adopt_year)
        if not years[0] <= ta <= years[-1]: continue
        i = ta-int(years[0])
        cycle = float(fr.reinvest_cycle_yr)
        anchor = float(fr.last_reline_year) + max(1,np.ceil((ta-fr.last_reline_year)/cycle))*cycle
        inc = fr.get("incumbent_capex_unit",200.)
        inc = 200. if pd.isna(inc) else float(inc)
        book = max(0.,anchor-ta-cfg.milp.reinvest_window_halfwidth)/cycle * inc * fr.capacity * cfg.get("incumbent_capex_scale",1.)
        if row.tech_id=="retire":
            retirement[i] += book
            continue
        tk = tf.loc[row.tech_id]
        base = float(tk.capex_unit*fr.capacity)
        build = tk.get("build_years",1)
        build = 1 if pd.isna(build) else max(1,int(build))
        for j in range(build):
            if i+j<n: construction[i+j]+=base/build
        conversion[i]+=book
        conversion_by_tech.setdefault(row.tech_id,np.zeros(n))[i]+=book
        used = int(years[-1])-int(row.op_year)+1
        terminal[-1] += base * max(0.,1.-used/float(tk.lifetime))
    np.testing.assert_allclose(profile.capex_k,construction+conversion,atol=1e-6,rtol=1e-12)
    by_tech={k:v-conversion_by_tech.get(k,0.) for k,v in profile.capex_by_tech.items()}
    np.testing.assert_allclose(sum(by_tech.values(),np.zeros(n)),construction,atol=1e-6,rtol=1e-12)
    stripped = replace(profile,capex_k=construction,capex_by_tech=by_tech,
                       other_cost_k=profile.other_cost_k-retirement)
    # This conditional recurrence is a diagnostic of what the baseline omits,
    # not verified maintenance expenditure or an adopted replacement assumption.
    recurring_proxy=np.zeros(n)
    for fr in fac[fac.company_id==company].itertuples():
        cycle=float(fr.reinvest_cycle_yr)
        assert cycle>0
        inc=getattr(fr,"incumbent_capex_unit",200.)
        inc=200. if pd.isna(inc) else float(inc)
        for k in range(1,max(1,int((years[-1]-fr.last_reline_year)/cycle)+1)):
            year=fr.last_reline_year+k*cycle
            if year in years:
                recurring_proxy[int(year-years[0])]+=inc*fr.capacity*cfg.get("incumbent_capex_scale",1.)
    arrays=dict(construction_cash_k=construction,conversion_writeoff_k=conversion,
                retirement_writeoff_k=retirement,terminal_book_value_credit_k=terminal,
                baseline_reinvestment_proxy_not_in_model_k=recurring_proxy)
    return arrays, {"legacy":profile,"book_excluded_terminal_proxy_retained":stripped,
                    "book_and_terminal_proxy_excluded":replace(stripped,other_cost_k=stripped.other_cost_k+terminal)}


def main():
    cfg=C.load(capex_shock_scaling="legacy_linear", allow_legacy_price_paths=True, capital_accounting="legacy_mixed", energy_balance_mode="legacy_retrofit_all", carbon_accounting_mode="legacy_auction_discount", transition_loss_basis="incremental_ex_carbon", plan_selection_criterion="p50"); out=ROOT/"docs/research_cycles/2026-09-05/capital_accounting"
    out.mkdir(parents=True,exist_ok=True)
    fac,tech,cal=_prep_company(cfg,C.data_dir(cfg))
    years=np.arange(cfg.years.start,cfg.years.end+1)
    discount=(1+cfg.discount_rate)**-(years-years[0])
    auction=auction_share(years,cfg)
    prices_path=C.out_dir(cfg,"e1")/"price_paths_central.csv"
    points_path=C.out_dir(cfg,"e5")/"frontier_points.csv"
    prices,points=pd.read_csv(prices_path),pd.read_csv(points_path)
    shocks=load_shocks(cfg);d5=load_input(C.data_dir(cfg),"D5_policy_support")
    rows,annual,profiles,choices,negative_exposure=[],[],[],[],[]
    files={Path(__file__),ROOT/"config.yaml",prices_path,points_path,C.out_dir(cfg,"e3")/"price_sims.parquet"}
    files.update(C.data_dir(cfg).glob("*.csv"));files.update((ROOT/"src/cap").glob("*.py"))
    for (company,scenario),group in points.groupby(["company_id","scenario"]):
        px=_central_px(prices,COMPANY_REGION[company],scenario,years,cfg,cal)
        baseline=build_profile(_empty_plan(company),fac,tech,px,years,cfg)
        assert not baseline.capex_k.any(), "Baseline capital premise changed; revisit this audit"
        base_carbon=_carbon_npv(baseline,px,discount,auction)
        cache={}
        for bid in group.base_plan_id.unique():
            path=C.out_dir(cfg,"e2")/"plans"/f"plan_{bid}.csv";files.add(path)
            plan=pd.read_csv(path)
            prof=build_profile(plan,fac,tech,px,years,cfg)
            arrays,variants=split_capital(plan,fac,tech,years,cfg,prof)
            cache[bid]=variants
            for tid,arr in prof.capex_by_tech.items():
                multiplier=1+(shocks['capex']-1)*prof.capex_unc[tid]/40.
                negative_exposure.append(dict(company_id=company,scenario=scenario,base_plan_id=bid,
                    tech_id=tid,negative_active_price_cells=int(((multiplier<0)&(arr[None,:]>0)).sum()),
                    min_multiplier_all_years=float(multiplier.min())))
            summary=dict(company_id=company,scenario=scenario,base_plan_id=bid)
            for name,a in arrays.items():
                summary[name.replace("_k","_bn")]=float(a.sum()*1e-6)
                summary[name.replace("_k","_npv_bn")]=float((a*discount).sum()*1e-6)
            profiles.append(summary)
            for i,year in enumerate(years):
                annual.append(dict(company_id=company,scenario=scenario,base_plan_id=bid,year=year,
                                   **{k:float(v[i]) for k,v in arrays.items()}))
        for support,sg in group.groupby("support"):
            sp=support_params(d5,support,years)
            base=simulate_cost(baseline,px,shocks,sp,cfg)
            for r in sg.itertuples():
                for basis,profile in cache[r.base_plan_id].items():
                    prof=replace(profile,ppa=r.ppa_share,epc=int(r.epc),ccfd=int(r.ccfd))
                    dcarbon=_carbon_npv(prof,px,discount,auction)-base_carbon
                    losses=simulate_cost(prof,px,shocks,sp,cfg)-base-dcarbon
                    stats=loss_summary(losses)
                    if basis=="legacy":
                        np.testing.assert_allclose([stats['p50'],stats['tcar']],[r.p50,r.tcar],atol=1e-6,rtol=0)
                    rows.append(dict(company_id=company,scenario=scenario,support=support,plan_id=r.plan_id,
                        base_plan_id=r.base_plan_id,basis=basis,is_disclosed=r.is_disclosed,budget_ok=r.budget_ok,
                        ppa_share=r.ppa_share,epc=r.epc,saved_p50=r.p50,saved_tcar=r.tcar,**stats))
        print(company,scenario,len(cache),'schedules',flush=True)
    result=pd.DataFrame(rows)
    for key,g in result[~result.is_disclosed & result.budget_ok].groupby(['company_id','scenario','support','basis']):
        for metric in ['p50','mean','tcar','es_alpha']:
            r=g.sort_values([metric,'plan_id']).iloc[0]
            choices.append(dict(zip(['company_id','scenario','support','basis'],key))|
                           dict(criterion=metric,plan_id=r.plan_id,ppa_share=r.ppa_share,epc=r.epc,
                                p50=r.p50,mean=r['mean'],tcar=r.tcar,es_alpha=r.es_alpha))
    pd.DataFrame(annual).to_csv(out/'capital_annual_ledger.csv',index=False)
    pd.DataFrame(profiles).to_csv(out/'capital_profile_summary.csv',index=False)
    result.to_csv(out/'accounting_risk_comparison.csv',index=False)
    choice_df=pd.DataFrame(choices)
    choice_df.to_csv(out/'accounting_criterion_choices.csv',index=False)
    keys=['company_id','scenario','support','criterion']
    legacy=choice_df.query("basis=='legacy'")[keys+['plan_id']].rename(columns={'plan_id':'legacy_plan_id'})
    changes=choice_df.query("basis!='legacy'").merge(legacy,on=keys)
    changes['changed']=changes.plan_id!=changes.legacy_plan_id
    changes.to_csv(out/'selection_changes.csv',index=False)
    negative=[]
    for tid,u in tech[['tech_id','capex_uncertainty']].itertuples(index=False,name=None):
        multiplier=1+(shocks['capex']-1)*u/40.
        for i,j in np.argwhere(multiplier<0):
            negative.append(dict(tech_id=tid,path_index=int(i),year=int(years[j]),
                                 raw_shock=float(shocks['capex'][i,j]),multiplier=float(multiplier[i,j])))
    pd.DataFrame(negative).to_csv(out/'negative_capex_multipliers.csv',index=False)
    pd.DataFrame(negative_exposure).to_csv(out/'negative_capex_exposure_audit.csv',index=False)
    wide=result.pivot(index=['company_id','scenario','support','plan_id'],columns='basis',values='tcar')
    invariant=(wide.book_and_terminal_proxy_excluded-wide.book_excluded_terminal_proxy_retained).abs().max()
    assert invariant<1e-6
    checks=dict(terminal_credit_tcar_invariance_max_abs_error=float(invariant),
        max_absolute_legacy_p50_error=float((result.query("basis=='legacy'").p50-result.query("basis=='legacy'").saved_p50).abs().max()),
        annual_capital_decomposition_rows=len(annual),reported_unit='bn KRW existing model convention',
        capital_input_includes_conversion_book=True,baseline_recurring_capital_included=False,
        changed_choices=int(changes.changed.sum()),choice_comparisons=len(changes),
        negative_technology_path_year_cells=len(negative),
        negative_active_construction_cells=sum(v['negative_active_price_cells'] for v in negative_exposure))
    (out/'invariance_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    manifest=dict(unique_schedules=len(profiles),evaluations=len(result),n_price_paths=len(shocks['elec']),
        annual_rows=len(annual),production_engine_changed=False,
        scope='Same saved schedules and same price paths; only book entries removed; carbon delta excluded as in saved E5',
        limitations='No reoptimization; not complete cash flows; recurrence is an uncalibrated diagnostic using existing incumbent assumptions; terminal book value is not observed liquidation value',
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()
