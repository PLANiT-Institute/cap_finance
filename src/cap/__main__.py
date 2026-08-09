"""CLI: python -m cap {e1|e2|e3|e4|e5|render|all} [--data DIR] [--sims N]"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

from . import config as C

STAGES = ["e1", "e2", "e3", "e4", "e5", "render"]


def _stamp(cfg, stage: str) -> None:
    """out/의 각 단계가 **어떤 설정으로** 만들어졌는지 남긴다.

    D10 뒤 out/e2·e4는 `--sims`를 줄인 실행으로 조용히 갈아치워졌고, 정본을 인용하는
    페이퍼 §0 대장이 어긋났다. 그때 실패 메시지는 "페이퍼가 out/과 다르다"였다 —
    틀린 것은 페이퍼가 아니라 out/이었는데도. 산출물이 자기 출처를 들고 있지 않으면
    다음 사이클은 낡은 쪽을 정본으로 착각한다.
    """
    p = pathlib.Path(C.out_dir(cfg, stage)).parent / "run_manifest.json"
    m = json.loads(p.read_text()) if p.exists() else {}
    m[stage] = {"data_dir": str(cfg.data_dir), "n_sims": int(cfg.simulation["n_sims"]),
                "n_sims_flex": int(cfg.simulation["n_sims_flex"]),
                "frontier_points": int(cfg.milp["frontier_points"]),
                "solver_threads": int(cfg.milp["solver_threads"]),
                "seed": int(cfg.seed), "finished": time.strftime("%Y-%m-%dT%H:%M:%S")}
    p.write_text(json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True))


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
        _stamp(cfg, s)
        print(f"[{s}] done in {time.time() - t0:.1f}s -> {C.out_dir(cfg, s)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
