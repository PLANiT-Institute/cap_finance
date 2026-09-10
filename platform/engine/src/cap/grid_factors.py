"""Select historical electricity factors without silently changing their scope.

This is a metadata/units gate, not a corporate inventory certification or a
future grid scenario. A scenario bridge must separately state its assumptions.
"""
import math


CONTEXT_FIELDS = ('country', 'gas', 'gwp_basis', 'energy_boundary', 'accounting_basis',
                  'period_start', 'period_end', 'statistic', 'allowed_use')


def select_grid_factor(records, identifier, *, context):
    if set(context) != set(CONTEXT_FIELDS):
        raise ValueError('Complete explicit grid-factor context required')
    matches = [r for r in records if r.get('identifier') == identifier]
    if len(matches) != 1:
        raise ValueError('Grid factor must resolve to one unique record')
    record = matches[0]
    if record.get('status') != 'verified_primary':
        raise ValueError('Conflicted, provisional or superseded factor is not selectable')
    if context['allowed_use'] not in ('regional_reference', 'reporting_parameter'):
        raise ValueError('Corporate calibration and scenario extrapolation are not supported')
    for key in CONTEXT_FIELDS:
        a, b = context[key], record.get(key)
        if key in ('period_start', 'period_end'):
            if type(a) is not int or type(b) is not int or a < 1900 or b < 1900:
                raise ValueError('Exact historical years required')
        elif not isinstance(a, str) or not a.strip():
            raise ValueError('Explicit nonempty context required: '+key)
        if a != b:
            raise ValueError('Grid-factor context mismatch: '+key)
    if context['period_end'] < context['period_start']:
        raise ValueError('Reversed observation period')
    gas = record['gas']
    if gas not in ('CO2', 'CO2e', 'CH4', 'N2O'):
        raise ValueError('Unsupported gas; no implicit GWP conversion')
    if gas == 'CO2e' and record['gwp_basis'] in ('unspecified','not_applicable'):
        raise ValueError('CO2-equivalent use needs an identified GWP basis')
    if gas != 'CO2e' and record['gwp_basis'] != 'not_applicable':
        raise ValueError('Physical gas mass does not use GWP conversion')
    factors = {f't{gas}/MWh': 1., f'kg{gas}/MWh': .001,
               f't{gas}/kWh': 1000., f'kg{gas}/kWh': 1.}
    unit = record.get('unit')
    if unit not in factors:
        raise ValueError('Native unit does not match gas and electricity denominator')
    value = record.get('value')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError('Finite nonnegative observed factor required')
    if not isinstance(record.get('source_url'), str) or not record['source_url'].startswith('https://'):
        raise ValueError('Source URL required')
    return dict(identifier=identifier, value=value*factors[unit], unit=f't{gas}/MWh',
                context=dict(context), source_url=record['source_url'],
                corporate_calibration=False, future_scenario=False)
