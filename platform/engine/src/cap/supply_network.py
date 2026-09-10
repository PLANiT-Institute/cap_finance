"""Static, same-product delivery feasibility and consolidated cash accounting.

Physical quantities are committed year profiles, never draw-by-year controls.
A passing balance does not establish a valid adaptive policy, engineering yield,
source calibration, tax treatment, or complete life-cycle emissions.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class SiteSupply:
    production: object
    external_purchase: object
    delivery: object
    closing_inventory: object
    initial_inventory: float
    production_limit: object
    purchase_limit: object
    inventory_limit: object


@dataclass(frozen=True)
class Transfer:
    identifier: str
    origin: str
    destination: str
    quantity: object
    capacity: object


def _array(value, shape, name, nonnegative=True):
    raw=np.asarray(value)
    if raw.dtype.kind not in 'iuf' or raw.dtype.kind=='b':
        raise ValueError('Explicit numeric inputs required: '+name)
    a=raw.astype(float)
    if a.shape!=shape or not np.isfinite(a).all() or (nonnegative and (a<0).any()):
        raise ValueError('Finite aligned inputs required: '+name)
    return a


def _transfers(transfers, names):
    ids=set()
    for t in transfers:
        if not isinstance(t.identifier,str) or not t.identifier.strip() or t.identifier in ids:
            raise ValueError('Unique nonempty transfer identifiers required')
        if t.origin not in names or t.destination not in names or t.origin==t.destination:
            raise ValueError('Transfer must link two distinct sites inside the boundary')
        ids.add(t.identifier)
    return ids


def delivery_balance(sites, transfers, *, years, product_specification, required_delivery, inventory_boundary, atol=1e-8):
    """Require local conservation and identical committed customer deliveries.

    All quantities are tonnes of the same explicitly named product/grade. The
    caller must verify substitution/transport lead-time assumptions. Transfers
    arrive within the period without loss; more complex timing is not modeled.
    Initial inventory is an explicit endowment and is NOT newly produced output.
    Inventory boundary targets (initial, terminal) are shared across candidates;
    changing them requires a separate endowment/terminal valuation comparison.
    Returns diagnostics only for feasible plans, with an absolute tonne tolerance.
    """
    if not sites or any(not isinstance(k,str) or not k.strip() for k in sites):
        raise ValueError('Nonempty named sites required')
    if not isinstance(product_specification,str) or not product_specification.strip():
        raise ValueError('A common product specification is required')
    if not years or any(isinstance(y,bool) or not isinstance(y,int) for y in years) or any(b!=a+1 for a,b in zip(years,years[1:])):
        raise ValueError('Consecutive integer annual periods required')
    if isinstance(atol,bool) or not np.isfinite(atol) or not 0<=atol<=1e-3:
        raise ValueError('Explicit small absolute tonne tolerance required')
    shape=(len(years),);names=set(sites);transfers=list(transfers)
    _transfers(transfers,names)
    if set(required_delivery)!=names or set(inventory_boundary)!=names:raise ValueError('Every site needs delivery and inventory boundary targets')
    net={k:np.zeros(shape) for k in names}
    for t in transfers:
        q=_array(t.quantity,shape,t.identifier);cap=_array(t.capacity,shape,t.identifier+' capacity')
        if (q>cap+atol).any():raise ValueError('Transfer capacity exceeded')
        net[t.origin]-=q;net[t.destination]+=q
    residuals={};total_production=np.zeros(shape);total_external=np.zeros(shape);total_delivery=np.zeros(shape)
    stock_change=np.zeros(shape)
    for key,s in sites.items():
        q,p,d,closing,qlim,plim,ilim=[_array(getattr(s,k),shape,key+' '+k) for k in
            ['production','external_purchase','delivery','closing_inventory','production_limit','purchase_limit','inventory_limit']]
        initial=_array(s.initial_inventory,(),key+' initial inventory').item()
        opening=np.r_[initial,closing[:-1]]
        # The first period storage limit also applies to its opening inventory.
        if (opening>ilim+atol).any() or (q>qlim+atol).any() or (p>plim+atol).any() or (closing>ilim+atol).any():
            raise ValueError('Site capacity exceeded: '+key)
        stock_target=_array(inventory_boundary[key],(2,),key+' initial/terminal inventory target')
        if abs(initial-stock_target[0])>atol or abs(closing[-1]-stock_target[1])>atol:
            raise ValueError('Initial or terminal inventory differs: '+key)
        target=_array(required_delivery[key],shape,key+' customer requirement')
        if (np.abs(d-target)>atol).any():raise ValueError('Customer delivery differs: '+key)
        residual=q+p+opening+net[key]-d-closing
        if (np.abs(residual)>atol).any():raise ValueError('Local material balance fails: '+key)
        residuals[key]=residual;total_production+=q;total_external+=p;total_delivery+=d;stock_change+=closing-opening
    return dict(local_residuals=residuals,production=total_production,external_purchase=total_external,
                delivery=total_delivery,inventory_change=stock_change,
                consolidated_residual=total_production+total_external-total_delivery-stock_change)


def consolidate_cash(site_external_cash, transfers, settlements, external_freight, *, shape):
    """Sum aligned path/year cash, cancelling both sides of internal settlement.

    Site inputs must ALREADY include production, external purchases, fixed and
    inventory cash costs in one currency/base-year basis, with no internal trades
    or transfer freight embedded. Each freight amount is an external cash charge
    attributed to the origin. These are cash amounts, not prices or quantities.
    Accounting/financing/tax consequences of transfer pricing are not modeled.
    Shape alignment does not verify that callers used the same random paths.
    """
    if len(shape)!=2 or any(isinstance(n,bool) or not isinstance(n,int) or n<=0 for n in shape):
        raise ValueError('Positive path/year shape required')
    if not site_external_cash:raise ValueError('Explicit external cash for all sites required')
    transfers=list(transfers);ids=_transfers(transfers,set(site_external_cash))
    if set(settlements)!=ids or set(external_freight)!=ids:
        raise ValueError('Every transfer requires settlement and external freight cash')
    posted={k:_array(v,shape,k+' cash',False).copy() for k,v in site_external_cash.items()}
    external_total=sum(posted.values(),np.zeros(shape));freight_total=np.zeros(shape)
    for t in transfers:
        payment=_array(settlements[t.identifier],shape,t.identifier+' settlement',False)
        freight=_array(external_freight[t.identifier],shape,t.identifier+' freight',False)
        posted[t.origin]-=payment;posted[t.destination]+=payment
        posted[t.origin]+=freight;freight_total+=freight
    # Compute the group result directly from external cash, avoiding numerical
    # cancellation when an arbitrary internal transfer price is extremely large.
    return dict(consolidated_cash=external_total+freight_total,site_posted_cash=posted,
                external_freight=freight_total,internal_settlement_in_group_cash=False)
