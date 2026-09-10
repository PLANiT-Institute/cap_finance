"""Revalue an explicit NCC incremental energy ledger through the FIN engine.

This is a conditional procurement experiment, not a company valuation. The
Japan-LNG benchmark multiplier is an explicitly assumed common index for
electricity's indexed share and methane netback. No pass-through is estimated.
Capital, steam, compression, emissions and other changing flows are excluded.
"""
from dataclasses import replace
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from cap import config as C
from cap.commodity_ledger import CommodityFlow
from cap.plancost import PlanProfile, simulate_cost
from cap.risk_metrics import loss_summary


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'data/research_v2/technology_packages/ledger_exercise.json'
    paths_source = ROOT/'data/research_v2/block_price_paths/annual_multipliers.npz'
    paths_manifest = ROOT/'data/research_v2/block_price_paths/manifest.json'
    q = json.loads(source.read_text())
    meta = json.loads(paths_manifest.read_text())
    paths = np.load(paths_source)
    j = meta['factors'].index('japan_lng')
    qe = q['added_electricity_MWh_per_t_ethylene']
    qm = q['freed_internal_methane_t_per_t_ethylene']
    pe = q['electricity_price_assumption_EUR_per_MWh']
    pm = q['methane_netback_assumption_EUR_per_t']
    hedge_beta = qm*pm/(qe*pe)
    N,T,_ = paths[meta['models'][0]].shape
    production = 1e6  # t ethylene/year, explicit constant reference scale
    fx = 1500.  # KRW/EUR fixed illustrative conversion, not observed FX
    rate = .05
    cfg = C.Config(dict(years=dict(start=2027,end=2027+T-1),discount_rate=rate,
        contracts=dict(ppa_premium_pct=0.,epc_premium_pct=0.,ccfd_fee_pct=0.),
        carbon_accounting_mode='gross_obligation_proxy'))
    z = np.zeros(T)
    base = PlanProfile(z.copy(),np.full(T,qe*production),z.copy(),z.copy(),z.copy(),
                       {},{},z.copy(),0.,0,0,coal_t=z.copy(),gas_t=z.copy())
    prices = {k:np.zeros(T) for k in ('elec','re','h2','coal','gas','co2')}
    prices['re'] = np.full(T,pe*fx)
    prices['methane_netback'] = np.full(T,pm*fx)
    disc = (1+rate)**-np.arange(T)
    rows=[]
    max_error = 0.
    for model in meta['models']:
        g = paths[model][:,:,j]
        for sale in (0.,.5,1.):
            for beta in (0.,hedge_beta,.5,1.):
                # Prices are formed at monthly scale by an affine index, so
                # arithmetic annual aggregation commutes with this mapping.
                flow = CommodityFlow('incremental_freed_methane','methane_netback',
                    np.full(T,-qm*production*sale),'tCH4','export_netback',
                    'Layritz preprint A.2: internal0.488t; sale fraction is assumption')
                p = replace(base,additional_commodity_flows=(flow,))
                for pairing in (('same_path','permuted_netback_paths') if beta==.5 and sale==1 else ('same_path',)):
                    gas = g if pairing=='same_path' else g[np.random.default_rng(20260907).permutation(N)]
                    shocks = dict(elec=(1-beta)+beta*g,h2=np.ones((N,T)),
                                  capex=np.ones((N,T)),methane_netback=gas)
                    costs = simulate_cost(p,prices,shocks,dict(subsidy={}),cfg)
                    hand = ((qe*pe*((1-beta)+beta*g)-qm*pm*sale*gas)*disc).sum(axis=1)*production*fx/1e9
                    error = float(np.max(np.abs(costs-hand)))
                    max_error = max(max_error,error)
                    np.testing.assert_allclose(costs,hand,rtol=1e-12,atol=1e-9)
                    if sale==1 and beta==hedge_beta:
                        np.testing.assert_allclose(costs,(qe*pe-qm*pm)*disc.sum()*production*fx/1e9,
                                                   rtol=1e-12,atol=1e-9)
                    rows.append(dict(model=model,sale_fraction=sale,power_indexed_share=beta,
                        pairing=pairing,**loss_summary(costs,.95),
                        central_npv=(qe*pe-qm*pm*sale)*disc.sum()*production*fx/1e9,
                        gas_index_cost_loading_EUR_per_t=qe*pe*beta-qm*pm*sale,
                        unit='bnKRW_partial_incremental_energy_NPV',
                        status='conditional_illustration_not_firm_TCaR'))
    out = ROOT/'data/research_v2/ncc_joint_ledger'
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'conditional_risk_metrics.csv',index=False)
    manifest=dict(source_files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
                   for p in (source,paths_source,paths_manifest,Path(__file__),
                             ROOT/'src/cap/plancost.py',ROOT/'src/cap/commodity_ledger.py')],
        paths=N,years=T,production_t_per_year=production,fixed_KRW_per_EUR=fx,
        discount_rate=rate,cashflow_timing='t0 purchase in2027, equal annual quantity',
        electricity_EUR_per_MWh=pe,methane_netback_EUR_per_t=pm,
        exact_hedge_power_indexed_share=hedge_beta,rows=len(rows),
        independent_formula_max_error_bnKRW=max_error,
        FIN_simulate_cost_used=True,full_company_cost=False,E2_reoptimized=False,
        representative_firm_mapped=False,procurement_mapping_estimated=False,
        declared_mapping='P_e=100 EUR/MWh*((1-beta)+beta*JapanLNG_multiplier); P_m=500 EUR/t*JapanLNG_multiplier',
        interpretation='Shared benchmark assumption demonstrates dependence, netback sign and hedge cancellation only',
        omissions=['Capital and other operating changes','Steam and compression engineering',
                   'Carbon and coproduct changes','Actual electricity, methane and FX contracts',
                   'Plant saleability, infrastructure and market volume constraints',
                   'Calibration uncertainty and unobserved future crises'],
        sample_permutation='Whole netback paths permuted only in named dependence diagnostic; marginal paths unchanged')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    main()
