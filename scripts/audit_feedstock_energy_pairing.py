"""Feedstock plus energy FIN accounting with paired counterfactual paths.

Reference NCC quantities; illustrative Brent-indexed naphtha and LNG-indexed
electricity/netback prices. These mappings are not estimated company contracts.
Equal feedstock purchases must cancel pathwise in incremental transition cost.
An intentionally unpaired comparator exposes spurious baseline simulation risk.
"""
from dataclasses import replace
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C
from cap.commodity_ledger import CommodityFlow
from cap.plancost import PlanProfile,simulate_cost
from cap.risk_metrics import loss_summary


def main():
    folder=ROOT/'data/research_v2/block_price_paths'
    packages_path=ROOT/'data/research_v2/technology_packages/reference_process_packages.json'
    packages=json.loads(packages_path.read_text())
    # Trace back to the transcribed source registers, not only cached quantities.
    for item in packages['source_registers']:
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
    byid={p['package_id']:p for p in packages['packages']}
    base,post=[{f['flow_id']:f['quantity'] for f in byid[k]['flows']}
               for k in ('LAYRITZ2021_NCC_BASE','LAYRITZ2021_NCC_ELECTRIC')]
    assert base['naphtha']==post['naphtha']==3.58
    meta=json.loads((folder/'manifest.json').read_text())
    paths=np.load(folder/'annual_multipliers.npz')
    oilj,gasj=[meta['factors'].index(k) for k in ('brent','japan_lng')]
    N,T,_=paths[meta['models'][0]].shape
    Q=1e6; fx=1500.; rate=.05; pn=600.; pe=100.; pm=500.; beta=.5
    cfg=C.Config(dict(years=dict(start=2027,end=2027+T-1),discount_rate=rate,
        contracts=dict(ppa_premium_pct=0.,epc_premium_pct=0.,ccfd_fee_pct=0.),
        carbon_accounting_mode='gross_obligation_proxy'))
    z=np.zeros(T)
    naphtha=CommodityFlow('naphtha_purchase','naphtha',np.full(T,base['naphtha']*Q),
                        't_naphtha','purchased','Layritz preprint A.2/A.3 LAY001/LAY007')
    baseline=PlanProfile(np.full(T,base['electricity']*Q),z.copy(),z.copy(),z.copy(),
        z.copy(),{}, {},z.copy(),0.,0,0,coal_t=z.copy(),gas_t=z.copy(),
        additional_commodity_flows=(naphtha,))
    methane=CommodityFlow('freed_methane','methane_netback',np.full(T,-base['methane_fuel']*Q),
        'tCH4','export_netback','LAY015 internal methane; full sale explicitly assumed')
    transition=replace(baseline,re_mwh=np.full(T,(post['electricity']-base['electricity'])*Q),
        additional_commodity_flows=(naphtha,methane))
    prices={k:np.zeros(T) for k in ('elec','re','h2','gas','coal','co2')}
    for k,v in dict(elec=pe,re=pe,naphtha=pn,methane_netback=pm).items():
        prices[k]=np.full(T,v*fx)
    disc=(1+rate)**-np.arange(T)
    rows=[]; maxerr=0.
    for model in meta['models']:
        oil,gas=paths[model][:,:,oilj],paths[model][:,:,gasj]
        shocks=dict(elec=(1-beta)+beta*gas,naphtha=oil,methane_netback=gas,
                    h2=np.ones((N,T)),capex=np.ones((N,T)))
        cb=simulate_cost(baseline,prices,shocks,dict(subsidy={}),cfg)
        cp=simulate_cost(transition,prices,shocks,dict(subsidy={}),cfg)
        energy=((post['electricity']-base['electricity'])*pe*shocks['elec']
                -base['methane_fuel']*pm*gas)
        hand=(energy*disc).sum(axis=1)*Q*fx/1e9
        maxerr=max(maxerr,float(np.max(np.abs(cp-cb-hand))))
        np.testing.assert_allclose(cp-cb,hand,atol=1e-8,rtol=1e-12)
        for pairing,baseline_cost in [('paired_counterfactual',cb),
                ('invalid_permuted_baseline',cb[np.random.default_rng(20260907).permutation(N)])]:
            rows.append(dict(model=model,pairing=pairing,
                **{'baseline_'+k:v for k,v in loss_summary(cb,.95).items()},
                **{'transition_'+k:v for k,v in loss_summary(cp,.95).items()},
                **{'incremental_'+k:v for k,v in loss_summary(cp-baseline_cost,.95).items()},
                status='partial_reference_cost_with_illustrative_procurement_mapping',
                eligible_for_inference=pairing=='paired_counterfactual'))
    out=ROOT/'data/research_v2/feedstock_energy_pairing';out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'risk_comparison.csv',index=False)
    sources=[packages_path,folder/'manifest.json',folder/'annual_multipliers.npz',Path(__file__),
             ROOT/'src/cap/plancost.py',ROOT/'src/cap/commodity_ledger.py']
    manifest=dict(rows=len(rows),paths=N,years=T,production_t_per_year=Q,
        price_assumptions=dict(naphtha_EUR_t=pn,electricity_EUR_MWh=pe,methane_netback_EUR_t=pm,
                               power_gas_indexed_share=beta,fixed_KRW_EUR=fx,discount_rate=rate),
        feedstock_before_and_after_t_per_t=base['naphtha'],
        maximum_paired_cancellation_error_bnKRW=maxerr,
        mappings='naphtha=600*Brent index; power=100*(0.5+0.5*Japan LNG index); methane netback=500*Japan LNG index',
        mappings_empirically_estimated=False,FIN_used=True,full_company_cost=False,
        interpretation='Raw materials enter both level costs; unchanged quantities and contracts cancel in paired incremental cost',
        invalid_control='Permuting baseline states is deliberately wrong for the same-state counterfactual; never a risk estimate',
        omitted='CAPEX, nonenergy OPEX, carbon, other coproduct changes, company-specific contracts, process/parameter uncertainty',
        sources=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(rows=len(rows),max_error=maxerr,out=str(out)),indent=2))


if __name__=='__main__':main()
