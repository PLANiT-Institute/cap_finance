"""Make source-consistent, machine-readable process ledgers for reference use.

This permits bounded energy/feedstock calculations; full company-cost imports
remain blocked until costs, procurement, emissions and site mapping are verified.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/research_v2'
OUT=DATA/'technology_packages'


def read(path):
    with path.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    inputs=[DATA/'evidence/primary_process_observations.csv',DATA/'evidence/layritz_preprint_inventory_cells.csv',
            DATA/'gcam_reference/steel_default_energy_coefficients.csv']
    primary,layritz,gcam=[read(p) for p in inputs]
    packages=[]

    def flow(identifier,amount,unit,role,source,**extra):
        assert amount>=0
        return dict(flow_id=identifier,quantity=amount,unit=unit,role=role,
                    source_observation=source,**extra)

    def package(identifier,product,scope,flows,limitations):
        assert len({f['flow_id'] for f in flows})==len(flows)
        billable={f['flow_id'] for f in flows if f['role']=='purchased'}
        assert not any(f.get('included_in') in billable and f['role']=='purchased' for f in flows)
        packages.append(dict(package_id=identifier,functional_unit=product,boundary=scope,
            flows=flows,use_status='reference_energy_and_material_ledger',
            full_company_cost_import_allowed=False,performance_distribution_calibrated=False,
            limitations=limitations))

    v=[r for r in primary if r['source_id']=='vogl_2018']
    def vobs(param,condition=None):
        a=[r for r in v if r['parameter']==param and (condition is None or condition in r['condition'])]
        assert len(a)==1,(param,condition);return a[0]
    elec=vobs('total_electricity');h2=vobs('hydrogen_input','100%');ore=vobs('pellet_input','100%');eaf=vobs('EAF_electricity_DRI')
    package('VOGL2018_ONSITE_H2_BASE','1 t liquid steel',
        'Onsite electrolyser, heat recovery, shaft, EAF; purchased pellets; no casting/rolling',[
        flow('electricity_total',float(elec['value']),elec['unit'],'purchased',elec['observation_id']),
        flow('pellets',float(ore['value'])/1000,'t/t_liquid_steel','purchased',ore['observation_id'],conversion='kg/1000'),
        flow('hydrogen_internal',float(h2['value']),h2['unit'],'internal_transfer',h2['observation_id'],electricity_included_in='electricity_total'),
        flow('EAF_electricity',float(eaf['value']),eaf['unit'],'component',eaf['observation_id'],included_in='electricity_total')],
        ['Rounded published model outputs, not plant measurements','Hot-base interpretation; private author clarification not independently accessed',
         'Cannot switch to purchased H2 by charging51kg plus3.48MWh','Pellet upstream energy is embodied in purchased pellet price',
         'Lime, carbon additions, oxygen coproduct, capital and operating costs require separate completion'])

    for route,pid in [('conventional_naphtha','LAYRITZ2021_NCC_BASE'),('electrified_naphtha','LAYRITZ2021_NCC_ELECTRIC')]:
        rr=[r for r in layritz if r['route']==route]
        def lo(stream,field):
            a=[r for r in rr if r['stream']==stream and r['field']==field];assert len(a)==1;return a[0]
        flows=[]
        for stream,field,role in [('naphtha','mass','purchased'),('electricity','energy','purchased'),
                                   ('hydrogen_export','mass','potential_export'),('methane_export','mass','potential_export')]:
            r=lo(stream,field);flows.append(flow(stream,float(r['value']),r['unit'],role,r['observation_id']))
        if route=='conventional_naphtha':
            for stream,field in [('methane_fuel','mass'),('heat','energy')]:
                r=lo(stream,field);flows.append(flow(stream,float(r['value']),r['unit'],'internal_transfer',r['observation_id']))
        else:
            r=lo('furnace_electricity','energy');flows.append(flow('furnace_electricity',float(r['value']),r['unit'],'component',r['observation_id'],included_in='electricity'))
        package(pid,'1 t ethylene with coproducts','Naphtha cracker; excludes added LCA system-expansion power',flows,
            ['Institutional preprint, final-version match pending','Published furnace-efficiency equivalence is a process assumption',
             'Export methane saleability and netback must be supplied, not assumed','Rounded0.55 export differs from0.545 system-expansion value',
             'Held carbon cells cannot be imported; steam integration, capital, compression and coproduct values incomplete'])

    rr=[r for r in gcam if r['technology']=='Hydrogen-based DRI' and r['year']=='2025']
    assert len(rr)==4,len(rr)
    package('PUBLIC_GCAM2026_H2DRI_2025','1 t GCAM steel',
        'Native public default input; Zang2023 source boundary includes upstream pelletizing; not solved Korean/KAIST output',
        [flow(r['native_input'],float(r['native_value']),r['native_unit'],'source_energy_input',
              r['source_sha256']+':'+r['steel_region']+':'+r['subsector']+':'+r['technology']+':'+r['native_input']+':2025') for r in rr],
        ['75%DRI iron feed; reductant energy83%H2/17%NG','Boundary mapping required before treating energy as plant purchases',
         'Do not add upstream pellet energy to purchased pellets again','Non-energy cost is not standalone CAPEX',
         'Commodity prices and regional overrides must match GCAM version'])
    payload=dict(schema_version='0.1',packages=packages,
        source_registers=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs])
    (OUT/'reference_process_packages.json').write_text(json.dumps(payload,indent=2)+'\n')
    # A deterministic accounting exercise with explicit illustrative price assumptions.
    base,electric=packages[1:3]
    q={p['package_id']:{r['flow_id']:r['quantity'] for r in p['flows']} for p in [base,electric]}
    delta_e=q[electric['package_id']]['electricity']-q[base['package_id']]['electricity']
    delta_methane=next(float(r['value']) for r in layritz if r['stream']=='methane_fuel' and r['field']=='mass')
    assert abs(delta_e-6.78)<1e-10 and abs(delta_methane-.488)<1e-10
    diagnostic=dict(exercise='NCC incremental electricity and potential methane sale only',
        electricity_price_assumption_EUR_per_MWh=100,methane_netback_assumption_EUR_per_t=500,
        added_electricity_MWh_per_t_ethylene=delta_e,freed_internal_methane_t_per_t_ethylene=delta_methane,
        no_export_incremental_cost_EUR_per_t=delta_e*100,
        full_export_incremental_cost_EUR_per_t=delta_e*100-delta_methane*500,
        independent_hand_check='678-244=434; not13.77*100 and not avoided purchased natural gas',
        price_assumptions_status='illustrative_not_observed_or_forecast',
        use_status='partial_ledger_verification_not_total_transition_cost_or_TCaR',
        engine_input_replaced=False)
    assert abs(diagnostic['full_export_incremental_cost_EUR_per_t']-434)<1e-8
    (OUT/'ledger_exercise.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    print(json.dumps(dict(packages=len(packages),full_company_import_allowed=0,
        ledger_exercise_EUR_per_t=diagnostic['full_export_incremental_cost_EUR_per_t']),indent=2))


if __name__=='__main__':main()
