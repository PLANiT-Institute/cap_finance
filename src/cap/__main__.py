"""CLI: python -m cap {e1|e2|e3|e4|e5|render|all} [--data DIR] [--sims N]"""

from __future__ import annotations

import argparse
import sys
import time

from . import config as C

STAGES = ["e1", "e2", "e3", "e4", "e5", "render"]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cap", description="CAP v2 pipeline (REDESIGN_SPEC.md)")
    ap.add_argument("stage", choices=STAGES + ["all"])
    ap.add_argument("--data", help="input CSV directory (default: config data_dir)")
    ap.add_argument("--sims", type=int, help="override simulation.n_sims")
    ap.add_argument("--frontier-points", type=int, help="override milp.frontier_points")
    a = ap.parse_args(argv)

    cfg = C.load()
    if a.data:
        cfg["data_dir"] = a.data
    if a.sims:
        cfg["simulation"] = dict(cfg["simulation"], n_sims=a.sims)
    if a.frontier_points:
        cfg["milp"] = dict(cfg["milp"], frontier_points=a.frontier_points)

    from . import e1_constraints, e2_milp, e3_prices, e4_revalue, e5_metrics, render
    fns = {"e1": e1_constraints.run, "e2": e2_milp.run, "e3": e3_prices.run,
           "e4": e4_revalue.run, "e5": e5_metrics.run, "render": render.run}
    stages = STAGES if a.stage == "all" else [a.stage]
    for s in stages:
        t0 = time.time()
        print(f"[{s}] running (data={cfg.data_dir}) ...", flush=True)
        fns[s](cfg)
        print(f"[{s}] done in {time.time() - t0:.1f}s -> {C.out_dir(cfg, s)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
