"""Source-native component renewal audit; not a harmonized company cost case."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cap.component_capital import CapitalComponent, component_capital_cashflows
from cap import config as C
from cap.plancost import PlanProfile, simulate_cost


def main():
    source_path = ROOT / 'data/research_v2/steel_cost_reference/vogl_main_text_package.json'
    source = json.loads(source_path.read_text())
    pdf = ROOT / source['source']['local_path']
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == source['source']['sha256']
    components = [CapitalComponent(c['component'], c['capex_EUR_per_t_annual_capacity'], c['lifetime_years'])
                  for c in source['capital_components']]
    years = np.arange(2027, 2051)
    capacity, rate, conversion = 1e6, .05, 1500.
    discount = (1 + rate) ** -(years - years[0])
    variants = {'source_components': components,
                'all_20_years': [CapitalComponent('whole_process', 574., 20)],
                'all_10_years': [CapitalComponent('whole_process', 574., 10)]}
    cfg = C.load(discount_rate=rate, carbon_accounting_mode='gross_obligation_proxy')
    cfg['years'] = {'start': 2027, 'end': 2050}
    zero = np.zeros(len(years))
    prices = {k: zero.copy() for k in ['elec', 're', 'h2', 'co2', 'coal', 'gas']}
    shocks = {k: np.ones((1, len(years))) for k in ['elec', 'h2', 'capex']}
    rows, summaries, ledgers = [], [], {}
    for variant, cs in variants.items():
        for terminal in ['none', 'straight_line_proxy']:
            ledger = component_capital_cashflows(cs, capacity, 2027, 3, years,
                        unit_of_account='EUR_source_composite', terminal_rule=terminal)
            ledgers[variant, terminal] = ledger
            for ci, component in enumerate(ledger.component_ids):
                for ti, year in enumerate(years):
                    rows.append(dict(variant=variant, terminal_rule=terminal, component=component,
                        year=int(year), construction_EUR=ledger.construction[ci,ti],
                        renewal_EUR=ledger.renewal[ci,ti], terminal_receipt_EUR=ledger.terminal_receipt[ci,ti]))
            # Explicit numerical unit mapping only: 1500 is NOT an observed FX quote
            # or a conversion of the composite source price basis to real 2024 KRW.
            scale = conversion / 1000
            p = PlanProfile(grid_mwh=zero, re_mwh=zero, h2_kg=zero, other_cost_k=zero,
                capex_k=ledger.cash_payments * scale,
                capex_by_tech={c: ledger.construction[i]*scale for i,c in enumerate(ledger.component_ids)},
                capex_unc={c: 40. for c in ledger.component_ids}, emissions=zero, ppa=0., epc=0, ccfd=0,
                maintenance_capex_k=ledger.renewal.sum(axis=0)*scale,
                terminal_value_k=ledger.terminal_receipt.sum(axis=0)*scale,
                embedded_price_basis={}, profile_years=tuple(int(y) for y in years))
            calculated = simulate_cost(p, prices, shocks, {'subsidy': {}}, cfg, freeze='capex')[0]
            independent = float(ledger.net_cash_payments @ discount)
            np.testing.assert_allclose(calculated, independent*conversion/1e9, rtol=1e-13)
            summaries.append(dict(variant=variant, terminal_rule=terminal,
                gross_cash_EUR=ledger.cash_payments.sum(), terminal_EUR=ledger.terminal_receipt.sum(),
                npv_EUR=independent, FIN_numerical_mapping_bnKRW=calculated))
    correct = ledgers['source_components','none']
    expected = np.zeros(len(years)); expected[:3] = 574e6/3
    expected[2040-2027] = 160e6; expected[2050-2027] = 574e6
    np.testing.assert_allclose(correct.cash_payments, expected)
    annuity = sum(c.cost_per_capacity*rate/(1-(1+rate)**-c.lifetime_years) for c in components)
    np.testing.assert_allclose(annuity, source['annualized_capital_EUR_t'])
    duplicate = float((annuity * capacity * (years>=2030)) @ discount)
    out = ROOT / 'data/research_v2/component_capital'; out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'annual_cashflows.csv', index=False)
    pd.DataFrame(summaries).to_csv(out/'comparison.csv', index=False)
    fig, ax = plt.subplots(1,2,figsize=(11.5,4.3),layout='constrained')
    ax[0].bar(years,correct.construction.sum(axis=0)/1e6,label='Construction')
    ax[0].bar(years,correct.renewal[0]/1e6,bottom=correct.construction.sum(axis=0)/1e6,label='Electrolyser renewal')
    ax[0].bar(years,correct.renewal[1:].sum(axis=0)/1e6,bottom=(correct.construction.sum(axis=0)+correct.renewal[0])/1e6,label='Shaft + EAF renewal')
    ax[0].set(xlabel='Year (operation starts 2030)',ylabel='Source-composite EUR million',title='Different component lives change cash timing')
    ax[0].legend(fontsize=8)
    for i, terminal in enumerate(['none','straight_line_proxy']):
        vals=[r['npv_EUR']/1e6 for r in summaries if r['terminal_rule']==terminal]
        ax[1].bar(np.arange(3)+i*.35,vals,width=.35,label=terminal.replace('_',' '))
    ax[1].set(xticks=np.arange(3)+.175,xticklabels=['Source lives','All 20 years','All 10 years'],
              ylabel='NPV: source-composite EUR million',title='5% discount; terminal convention matters')
    ax[1].legend(fontsize=8)
    fig.suptitle('Illustrative 1 Mt/year plant, 2027–2050 | Vogl et al. component assumptions',fontsize=12)
    fig.savefig(out/'component_capital.png',dpi=180);plt.close(fig)
    manifest = dict(source=source['source'], source_package_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
        unit_of_account='EUR_source_composite', source_price_basis=source['price_basis'],
        assumed_capacity_t_annual=capacity, assumed_adoption=2027, assumed_build_years=3,
        assumed_discount_rate=rate, assumed_numerical_unit_mapping_KRW_per_source_EUR=conversion,
        verified_company_price_year_conversion=False, includes_operating_cost=False,
        includes_incumbent_capital=False, includes_stochastic_capital=False,
        checks={'dated_schedule_matches_independent_hand_ledger':True,'FIN_cash_NPV_cases':6,
                'source_annualized_charge_reproduced':True},
        annualized_capital_EUR_per_t_at_full_utilization=annuity,
        erroneous_extra_NPV_if_annualized_charge_also_added_EUR=duplicate,
        assumptions=['Flat three-year construction draws', 'Constant native replacement costs',
                     'Instantaneous renewal with no downtime', 'Default no terminal receipt',
                     'Optional straight-line proxy is not observed resale value',
                     'Terminal end-year remaining life credited in final model-year bucket'],
        findings=summaries)
    manifest['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [out/'annual_cashflows.csv',out/'comparison.csv',out/'component_capital.png']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'checks':manifest['checks'],'annualized':annuity,'double_count_NPV_EUR':duplicate,'comparisons':summaries},indent=2))

if __name__=='__main__':main()
