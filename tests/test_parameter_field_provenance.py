"""Cell evidence must follow its transformation, not its row's publisher."""
from pathlib import Path
import sys
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_parameter_inventory import field_provenance


def test_company_volume_does_not_verify_derived_capacity_or_margin():
    row=SimpleNamespace(source_id='NSC_DATABOOK_2025',capacity_unit='t용선/yr (내용적 추정)')
    for field in ('capacity','margin_kthou_t','incumbent_capex_unit','reinvest_cycle_yr','next_reinvest_year'):
        tier,source=field_provenance(row,'FIN','facility',field)
        assert tier=='T5' and 'anchor=NSC_DATABOOK_2025' in source


def test_reported_capacity_retains_source_without_upgrading_other_cells():
    row=SimpleNamespace(source_id='POSCO_GY_EAF',capacity_unit='t조강/yr')
    assert field_provenance(row,'FIN','facility','capacity')==('T2','POSCO_GY_EAF')
    assert field_provenance(row,'FIN','facility','incumbent_capex_unit')[0]=='T5'


def test_independent_eff_evidence_is_not_overridden():
    row=SimpleNamespace(source_id='reported',capacity_unit='Mtpa')
    assert field_provenance(row,'EFF','facility','reinvestment_year')==('T2','reported')


def test_demo_announcement_does_not_verify_commercial_normalized_technology_cells():
    row=SimpleNamespace(source_id='BASF_ECRACKER_2024',tech_id='petchem_ecracker')
    for field in ('capex_unit','elec_intensity','emission_factor','capex_uncertainty','build_years'):
        tier,source=field_provenance(row,'FIN','technology',field)
        assert tier=='T5' and 'anchor=BASF_ECRACKER_2024' in source


def test_policy_document_does_not_verify_an_entire_forward_price_curve_or_tax_discount():
    row=SimpleNamespace(source_id='KETS_P4_CONFIRM_2025')
    for group in ('price_path','policy_assumption'):
        assert field_provenance(row,'FIN',group,'co2_price')[0]=='T5'
