"""Explicit company observation perimeters; no facility-allocation assumptions."""
import numpy as np
import pandas as pd

COMPANY_TOTAL_IDS = {'POSCO':'POSCO_TOTAL','NSC':'NSC_TOTAL','MCI':'MITSUI_TOTAL','LOTTE':'LOTTE_TOTAL'}
# Exhaustive components declared by the LOTTE source table. These are entire
# sites, not a claim that all activity belongs to the two modeled crackers.
COMPANY_COMPONENTS = {'LOTTE':('LOTTE_YEO1_TOTAL','LOTTE_YEO2_TOTAL','LOTTE_DAE_TOTAL','LOTTE_ULS_TOTAL','LOTTE_OTH_TOTAL')}


def company_observations(panel, company, years):
    """Use reported totals per field, otherwise sum all declared components.

    Missing/incomplete perimeters remain NaN. A present total and its components
    are never added together. Each returned value carries its derivation.
    """
    if company not in COMPANY_TOTAL_IDS:
        raise ValueError(f'Company perimeter is not declared: {company}')
    fields = [f for f in ('production','emissions_s1','emissions_s2') if f in panel]
    rows = []
    components = COMPANY_COMPONENTS.get(company, ())
    ids = [COMPANY_TOTAL_IDS[company], *components]
    selected = panel[panel.facility_id.isin(ids)]
    if selected.duplicated(['facility_id','year']).any():
        raise ValueError(f'Duplicate company/site observations for {company}')
    for year in years:
        direct = selected[(selected.facility_id == COMPANY_TOTAL_IDS[company]) & (selected.year == year)]
        parts = selected[(selected.facility_id.isin(components)) & (selected.year == year)]
        complete = bool(components) and set(parts.facility_id) == set(components)
        row = {'facility_id':COMPANY_TOTAL_IDS[company], 'year':int(year)}
        for field in fields:
            if len(direct) and pd.notna(direct[field].iloc[0]):
                value = float(direct[field].iloc[0]); basis = 'reported_company_total'
            elif complete and parts[field].notna().all():
                value = float(parts[field].sum()); basis = 'sum_of_declared_whole_site_components'
            else:
                value = np.nan; basis = 'unavailable_or_incomplete_perimeter'
            row[field] = value;row[field+'_basis'] = basis
        rows.append(row)
    return pd.DataFrame(rows)
