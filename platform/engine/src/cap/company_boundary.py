"""Explicit denominator and coverage assumptions; no company calibration implied."""
import math

def finite(value,name,lower=0,upper=math.inf):
 if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lower<=value<=upper:
  raise ValueError('Explicit finite value required: '+name)
 return value

def reported_electricity_mwh(reported_gj,*,reported_gj_per_purchased_mwh):
 """Invert the REPORT'S accounting coefficient, not a guessed heat equivalent."""
 e=finite(reported_gj,'reported_gj');k=finite(reported_gj_per_purchased_mwh,'reported conversion coefficient')
 if k==0:raise ValueError('Positive report-specific coefficient required')
 return e/k

def process_intensity(site_energy_gj,capacity_t_per_year,*,utilization,process_energy_fraction):
 e=finite(site_energy_gj,'site energy');k=finite(capacity_t_per_year,'capacity')
 u=finite(utilization,'utilization',upper=1);fraction=finite(process_energy_fraction,'process energy fraction',upper=1)
 if k==0 or u==0:raise ValueError('Positive capacity and actual output required')
 return fraction*e/(u*k)

def coverage_requirement(total_emissions,covered_emissions,*,covered_residual_fraction,target_fraction):
 """Fixed baseline and outside activity. Outside reductions cannot erase covered residuals."""
 total=finite(total_emissions,'total emissions');covered=finite(covered_emissions,'covered emissions',upper=total)
 r=finite(covered_residual_fraction,'covered residual fraction',upper=1);target=finite(target_fraction,'target fraction',upper=1)
 outside=total-covered;covered_floor=covered*r;floor=outside+covered_floor
 needed=max(floor-total*target,0.)
 return dict(outside_baseline=outside,covered_residual=covered_floor,residual_without_outside_action=floor,
             additional_outside_reduction_required=needed,
             possible_using_outside_reduction_only=needed<=outside+1e-12)
