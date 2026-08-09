"""I4 표본 안정성 — 우리가 적는 자릿수가 실제로 의미가 있는가.

②를 "115천원/tCO₂"라고 적으면 1천원 자리까지 의미가 있다고 주장하는 것이다. 몬테카를로
표본이 바뀌면 그 자리가 흔들린다면 그렇게 적으면 안 된다. 시드를 바꿔 E3–E5를 다시 돌리고
헤드라인 지표의 표준편차를 잰다.

E1·E2는 시드와 무관하므로 공유한다 — 공유는 `run_scenarios._link_shared`를 **그대로
재사용**한다. 그 함수는 묶음이 직접 쓰는 단계의 낡은 링크를 지우도록 고쳐진 판본이고,
같은 위험한 로직을 두 번 구현하지 않는다(2026-08-09에 그 로직이 실산출물을 파괴했다).

    .venv/bin/python scripts/seed_stability.py [--seeds 5]
산출: docs/seed_stability.md
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cap import config as C  # noqa: E402
from run_scenarios import _link_shared  # noqa: E402

OUT = ROOT / "out" / "seeds"
METRICS = [("cost_per_tco2_thkrw", "② 감축단가", "천원/tCO₂", 0),
           ("tcar_bnkrw", "③ TCaR", "십억원", 0),
           ("p50_bnkrw", "② P50", "십억원", 0),
           ("flex_value_bnkrw", "⑤ 유연성", "십억원", 1)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()

    base_cfg = C.load()
    seed0 = int(base_cfg["seed"])
    seeds = [seed0 + i for i in range(a.seeds)]

    from cap import e3_prices, e4_revalue, e5_metrics
    frames = []
    for sd in seeds:
        cfg = C.load()
        cfg["seed"] = sd
        dst = OUT / str(sd)
        _link_shared(dst, ["e1", "e2"])       # 시드와 무관한 단계만 공유
        cfg["out_dir"] = str(dst)
        e3_prices.run(cfg)
        e4_revalue.run(cfg)
        e5_metrics.run(cfg)
        m = pd.read_csv(dst / "e5" / "metrics_company.csv")
        frames.append(m.assign(seed=sd))
        print(f"[seed] {sd} done", flush=True)

    df = pd.concat(frames, ignore_index=True).query(
        "scenario=='NZ15' and support=='none'")

    L = ["# I4 표본 안정성 — 보고한 자릿수가 실제인가", "",
         "> `scripts/seed_stability.py` 자동 생성.", "",
         f"시드 {seeds[0]}…{seeds[-1]} ({len(seeds)}개)로 E3–E5만 다시 돌렸다. E1(제약)·E2(계획 "
         f"탐색)는 시드와 무관하므로 공유한다 — 즉 **같은 계획을 다른 난수로 평가했을 때의 "
         f"흔들림**이다. n_sims = {base_cfg['simulation']['n_sims']:,}.", "",
         "표기 규칙: **변동계수(CV) = 표준편차 ÷ 평균**. CV가 1%를 넘으면 그 지표의 유효 "
         "자릿수는 우리가 적는 것보다 적다.", ""]

    worst = 0.0
    for col, label, unit, dec in METRICS:
        if col not in df.columns:
            continue
        g = df.groupby("company_id")[col].agg(["mean", "std", "min", "max"])
        g["cv_pct"] = 100 * g["std"] / g["mean"].abs()
        worst = max(worst, float(g.cv_pct.max()))
        L += [f"## {label} ({unit})", "",
              "| 기업 | 평균 | 표준편차 | 최소~최대 | CV | 판정 |", "|---|---|---|---|---|---|"]
        for cid, r in g.iterrows():
            v = "안정" if r.cv_pct < 1 else ("주의" if r.cv_pct < 3 else "**불안정**")
            L.append(f"| {cid} | {r['mean']:,.{dec}f} | {r['std']:,.{dec + 1}f} | "
                     f"{r['min']:,.{dec}f}~{r['max']:,.{dec}f} | {r.cv_pct:.2f}% | {v} |")
        L.append("")

    L += ["## 판정", "",
          f"최대 CV **{worst:.2f}%**. " +
          ("전 지표가 1% 안에서 안정적이다 — 보고서의 표기 자릿수는 표본 잡음에 "
           "묻히지 않는다." if worst < 1 else
           "1%를 넘는 지표가 있다. 해당 지표는 **표기 자릿수를 줄이거나 n_sims를 "
           "올려야 한다** — 지금 표기는 없는 정밀도를 주장한다."), "",
          "**이 검증이 재지 않는 것**: 계획 선택(E2)의 안정성. 시드는 가격 경로만 바꾸고 "
          "계획 메뉴는 고정이다. MILP의 해 안정성은 별개 문제이며 `solve_status`로 관리한다.",
          "", "**주의**: 시드 안정성은 *정밀도*이지 *정확도*가 아니다. 모든 시드가 같은 "
          "잘못된 사전 변동성(A-17)을 쓰면 결과는 일관되게 틀린다.", ""]

    (ROOT / "docs" / "seed_stability.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    df.to_csv(ROOT / "docs" / "seed_stability.csv", index=False)
    print("\n".join(L[-6:]))
    print(f"[seed] docs/seed_stability.md — 최대 CV {worst:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
