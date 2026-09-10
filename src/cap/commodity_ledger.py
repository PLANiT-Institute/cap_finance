"""Explicit additional commodity purchases and coproduct netback cashflows.

Quantities are physical annual totals; positive means purchase, negative means
sale. Prices are KRW per the declared quantity unit. A netback price must already
deduct selling/conditioning/transport costs, or those costs need another leg.
Internal transfers and components of an already charged total are not billable.
This ledger supplies no implicit price, saleability, or technology validation.
"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CommodityFlow:
    flow_id: str
    price_key: str
    quantity: np.ndarray
    quantity_unit: str
    role: str
    evidence: str


def additional_commodity_cost_k(flows, prices, shocks, shape, freeze=None):
    """Price explicit flows in KRW thousands, retaining paired path indices.

    Unlike legacy fuel channels, every added stream needs an explicit shock
    array, even when it is an array of ones declaring a fixed price.
    """
    result = np.zeros(shape)
    seen = set()
    for flow in flows:
        if not all(isinstance(x, str) and x.strip() for x in
                   (flow.flow_id, flow.price_key, flow.quantity_unit, flow.evidence)):
            raise ValueError('Commodity flow identifiers, units and evidence are required')
        if flow.flow_id in seen:
            raise ValueError('Duplicate commodity flow would double count cashflow')
        seen.add(flow.flow_id)
        q = np.asarray(flow.quantity, dtype=float)
        if q.shape != (shape[1],) or not np.isfinite(q).all():
            raise ValueError('Commodity quantities must cover exactly the modeled years')
        if flow.role not in ('purchased', 'export_netback'):
            raise ValueError('Only external purchases and export netbacks are billable')
        if (flow.role == 'purchased' and (q < 0).any()) or (
                flow.role == 'export_netback' and (q > 0).any()):
            raise ValueError('Purchase quantities are nonnegative; exports are nonpositive')
        if flow.price_key not in prices or flow.price_key not in shocks:
            raise ValueError(f'Explicit central price and shock required for {flow.price_key}')
        price = np.asarray(prices[flow.price_key], dtype=float)
        shock = np.asarray(shocks[flow.price_key], dtype=float)
        if price.shape != (shape[1],) or not np.isfinite(price).all():
            raise ValueError('Commodity prices must be finite and cover modeled years')
        if shock.shape != shape or not np.isfinite(shock).all() or (shock <= 0).any():
            raise ValueError('Commodity shocks must be positive and use the same paths and years')
        # Negative netback is allowed: disposal/conditioning can exceed proceeds.
        result += q[None, :] * price[None, :] * (1. if freeze == flow.price_key else shock) / 1000.
    return result


def fuel_price_adjustment_k(quantity, central_price, shock, shape):
    """Add only the deviation from fuel costs already in other_cost_k.

    This preserves legacy central-cost accounting and prevents charging gas or
    coal twice. Missing shock means the caller chose the legacy fixed channel.
    """
    if shock is None:
        return np.zeros(shape)
    if quantity is None:
        raise ValueError('Stochastic fuel needs an explicit purchased-quantity profile')
    q, p, s = (np.asarray(a, dtype=float) for a in (quantity, central_price, shock))
    if q.shape != (shape[1],) or p.shape != q.shape or s.shape != shape:
        raise ValueError('Fuel quantities, prices and shocks must align by year and path')
    if not all(np.isfinite(a).all() for a in (q, p, s)) or (q < 0).any() or (s <= 0).any():
        raise ValueError('Fuel requires finite prices, nonnegative purchases and positive shocks')
    return q[None, :] * p[None, :] * (s - 1.) / 1000.
