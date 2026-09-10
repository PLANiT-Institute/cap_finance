"""Analytical allowance-accounting examples, not company policy calibration."""
import json
from pathlib import Path


def main():
    examples = [
        ("fixed_allocation_both_short",120.,110.,100.,100.,10.,10.),
        ("fixed_allocation_surplus_sale",100.,80.,100.,100.,20.,0.),
        ("allocation_falls_with_activity",100.,80.,100.,80.,0.,0.),
    ]
    rows=[]
    for name,e0,ex,a0,ax,expected_net,expected_buy in examples:
        # Unit allowance price one; sign is baseline cost minus plan cost.
        net_saving=(e0-a0)-(ex-ax)
        purchase_saving=max(e0-a0,0)-max(ex-ax,0)
        legacy_saving=.15*(e0-ex)
        assert net_saving==expected_net and purchase_saving==expected_buy
        rows.append(dict(example=name,baseline_emissions=e0,plan_emissions=ex,
            baseline_free_allocation=a0,plan_free_allocation=ax,net_trade_saving=net_saving,
            purchase_only_saving=purchase_saving,legacy_15pct_emission_charge_saving=legacy_saving))
    out=Path(__file__).resolve().parents[1]/"docs/research_cycles/2026-09-05/allowance_cost_examples.json"
    out.write_text(json.dumps(dict(unit_price=1,examples=rows,
        assumptions="One period; no banking borrowing transaction costs or bid-ask spread",
        production_engine_fixed=False),indent=2)+"\n")
    print(json.dumps(rows,indent=2))


if __name__=="__main__":
    main()
