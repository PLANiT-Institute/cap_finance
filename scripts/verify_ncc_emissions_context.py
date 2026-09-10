"""Independently audit saved emissions with rational source coefficients."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT/'data/research_v2/ncc_emissions_context'
    m = json.loads((out/'manifest.json').read_text())
    for group in ['input_sha256','artifact_sha256']:
        for name,h in m[group].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    source = pd.read_csv(out/'direct_emissions_observations.csv')
    assert list(source.value)==[.397,0.]
    assert source.iloc[1].status=='source_model_assumption_not_measurement'
    threshold=F(397,1859)
    np.testing.assert_allclose(m['threshold_tCO2_MWh'],float(threshold),rtol=0,atol=1e-15)
    assert (F(397,1000)+F(83,1000)*threshold)/F(303,1000)==F(1942,1000)*threshold/F(303,1000)
    intensity=pd.read_csv(out/'intensity_sensitivity.csv')
    for r in intensity.itertuples():
        direct=F(397,1000) if r.case=='conventional' else F(0)
        power=F(83,1000) if r.case=='conventional' else F(1942,1000)
        expected=float((direct+power*F(str(r.grid_tCO2_MWh))+F(str(r.common_residual_tCO2_t_naphtha)))/F(303,1000))
        np.testing.assert_allclose(r.total_tCO2_t_ethylene,expected,rtol=1e-12,atol=1e-12)
        np.testing.assert_allclose(r.total_tCO2_t_ethylene,r.direct_tCO2_t_ethylene+r.grid_tCO2_t_ethylene+r.residual_tCO2_t_ethylene,rtol=1e-12)
    # Different common residuals leave each paired increment unchanged.
    pivot=intensity.pivot(index=['grid_tCO2_MWh','common_residual_tCO2_t_naphtha'],columns='case',values='total_tCO2_t_ethylene')
    delta=(pivot.electric-pivot.conventional).unstack()
    np.testing.assert_allclose(delta.iloc[:,0],delta.iloc[:,1],rtol=0,atol=1e-12)
    annual=pd.read_csv(out/'annual_boundary_diagnostic.csv')
    for r in annual.itertuples():
        electric=r.case=='replace_2030' and r.year>=2030
        intensity=(0 if electric else .397)+(1.942 if electric else .083)*r.grid_tCO2_MWh+r.common_residual_tCO2_t_naphtha
        expected=920000/.303*intensity
        budget=920000/.303*(.397+.083*r.grid_tCO2_MWh+r.common_residual_tCO2_t_naphtha)*(2050-r.year)/23
        np.testing.assert_allclose([r.total_tCO2,r.budget_tCO2],[expected,budget],rtol=1e-12,atol=1e-7)
        assert r.feasible==(expected<=budget+1e-7)
    feasible=pd.read_csv(out/'feasibility_diagnostic.csv')
    assert len(feasible)==12 and (feasible.first_violation_year==2028).all()
    assert not feasible.all_years_feasible.any()
    terminal=feasible[feasible.terminal_feasible]
    assert len(terminal)==1 and terminal.iloc[0]['case']=='replace_2030'
    assert terminal.iloc[0].grid_tCO2_MWh==terminal.iloc[0].common_residual_tCO2_t_naphtha==0
    residual=pd.read_csv(out/'residual_plot_values.csv')
    np.testing.assert_allclose(residual.zero_grid_electric_tCO2_t_ethylene,residual.residual_tCO2_t_naphtha/.303,rtol=1e-12)
    paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
    table=pd.read_csv(out/'illustrative_table.csv')
    checks=0
    for r in table.itertuples():
        c=(.397+.083*r.grid_tCO2_MWh)/.303
        e=1.942*r.grid_tCO2_MWh/.303
        np.testing.assert_allclose([r.conventional,r.electric,r.incremental],[c,e,e-c],atol=1e-12)
        assert f'| {r.grid_tCO2_MWh:.1f} | {c:.4f} | {e:.4f} | {e-c:+.4f} |' in paper
        checks+=3
    assert f'{float(threshold):.4f}tCO2/MWh' in paper
    assert f'{float(F(50,303)):.4f}tCO2/t 에틸렌' in paper
    checks+=2
    for marker in ['### 2.3 산업 맥락','### 4.3.2 산업 맥락','### 6.15 전기화','288행을 보존','2028년부터 줄어드는']:
        assert paper.count(marker)==1,marker
    version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
    report=dict(new_selected_numeric_values=checks,intensity_rows_checked=84,
                annual_rows_independently_checked=288,feasibility_cases_checked=12,
                exact_rational_threshold_identity=True,common_residual_cancellation_checks=21,
                residual_plot_values_checked=3,new_execution_claims_checked=1,
                actual_corporate_emissions_validated=False,full_suite_reexecuted=False,
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
    (ROOT/f'docs/research_cycles/2026-09-07-hourly/ncc_emissions_{version}_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if k!='sha256'})


if __name__=='__main__':main()
