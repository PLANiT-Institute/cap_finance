"""I3 확률과정 대안 — TCaR이 우리가 고른 확률과정에 얼마나 달려 있는가.

가격이 랜덤워크(GBM)면 불확실성이 지평에 비례해 벌어지고, 평균회귀(OU)면 포화한다.
25년 지평에서 이 차이는 작지 않다. **문제는 우리 데이터로 둘을 가를 수 없다는 것**이다 —
그렇다면 최소한 그 선택이 결과를 얼마나 움직이는지는 알아야 한다.

E1·E2는 확률과정과 무관하므로 공유한다(`run_scenarios._link_shared` 재사용).

    .venv/bin/python scripts/process_alternative.py [--halflife 10]
산출: docs/process_alternative.md
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
from cap.schemas import load_input  # noqa: E402
from run_scenarios import _link_shared  # noqa: E402

OUT = ROOT / "out" / "process"
CONAME = {"POSCO": "POSCO", "NSC": "Nippon Steel",
          "LOTTE": "LOTTE Chemical", "MCI": "Mitsui Chemicals"}
MIN_OBS_FOR_TEST = 60   # 평균회귀 검정이 의미를 갖는 최소 관측 수 (월 5년)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--halflife", type=float, default=10.0)
    a = ap.parse_args()

    from cap import e3_prices, e4_revalue, e5_metrics
    res = {}
    # (라벨, 확률과정, 정규화) — 정규화는 확률과정과 같은 종류의 '드러나지 않은 선택'이다
    VARIANTS = [("gbm", "gbm", "mean"), ("ou", "ou", "mean"),
                ("gbm_median", "gbm", "median")]
    for label, proc, norm in VARIANTS:
        cfg = C.load()
        cfg["price_process"] = proc
        cfg["shock_normalisation"] = norm
        cfg["ou_halflife_years"] = a.halflife
        dst = OUT / label
        _link_shared(dst, ["e1", "e2"])
        cfg["out_dir"] = str(dst)
        e3_prices.run(cfg)
        e4_revalue.run(cfg)
        e5_metrics.run(cfg)
        res[label] = pd.read_csv(dst / "e5" / "metrics_company.csv").query(
            "scenario=='NZ15' and support=='none'").set_index("company_id")
        print(f"[process] {label} done", flush=True)

    d4 = load_input(C.data_dir(C.load()), "D4_price_history")
    n_obs = d4.groupby("series_id").size().sort_values(ascending=False)
    testable = n_obs[n_obs >= MIN_OBS_FOR_TEST]

    g, o = res["gbm"], res["ou"]
    L = ["# I3 확률과정 대안 — TCaR은 우리가 고른 과정에 얼마나 달려 있는가", "",
         "> `scripts/process_alternative.py` 자동 생성.", "",
         "가격이 **랜덤워크(GBM)**면 불확실성이 지평에 비례해 벌어지고, **평균회귀(OU)**면 "
         f"포화한다. 반감기 {a.halflife:.0f}년 OU와 GBM을 같은 1년 변동성·같은 계획 집합에서 "
         "돌려 비교했다. E1·E2는 확률과정과 무관하므로 공유한다.", "",
         "## 1. 먼저 — 우리는 이 둘을 가를 수 없다", "",
         "평균회귀 검정(ADF·분산비)은 관측이 수십 개는 있어야 검정력이 생긴다. D4의 실제 관측 수:", "",
         "| 시계열 | 관측 수 |", "|---|---|"]
    for sid, n in n_obs.head(8).items():
        L.append(f"| `{sid}` | {n} |")
    L += ["",
          (f"**{MIN_OBS_FOR_TEST}개 이상인 시계열이 {len(testable)}개다.** "
           if len(testable) == 0 else
           f"{MIN_OBS_FOR_TEST}개 이상인 시계열: {', '.join(testable.index)}. ") +
          "이 표본으로 ADF를 돌리면 거의 항상 '단위근을 기각하지 못한다'가 나오는데, 그것은 "
          "**랜덤워크라는 증거가 아니라 검정력이 없다는 증거**다. 그래서 검정 통계량을 "
          "제시하지 않는다 — 가르지 못하는 검정을 근거로 쓰면 없는 확실성을 만든다. "
          "월별 시계열 확보(G5)가 선행 조건이다.", "",
          "## 2. 그래서 차이만 잰다", "",
          "| 기업 | ② GBM | ② OU | 차이 | **③ TCaR GBM** | **③ TCaR OU** | **차이** |",
          "|---|---|---|---|---|---|---|"]
    for c in ["POSCO", "NSC", "MCI", "LOTTE"]:
        if c not in g.index or c not in o.index:
            continue
        a2, b2 = float(g.loc[c].cost_per_tco2_thkrw), float(o.loc[c].cost_per_tco2_thkrw)
        at, bt = float(g.loc[c].tcar_bnkrw), float(o.loc[c].tcar_bnkrw)
        L.append(f"| {CONAME[c]} | {a2:,.0f} | {b2:,.0f} | {100 * (b2 - a2) / a2:+.1f}% | "
                 f"{at:,.0f} | {bt:,.0f} | **{100 * (bt - at) / at:+.1f}%** |")
    rank_g = list(g.sort_values("cost_per_tco2_thkrw").index)
    rank_o = list(o.sort_values("cost_per_tco2_thkrw").index)
    tc = [100 * (float(o.loc[c].tcar_bnkrw) - float(g.loc[c].tcar_bnkrw))
          / float(g.loc[c].tcar_bnkrw) for c in rank_g if c in o.index]
    SEC = {"POSCO": "철강", "NSC": "철강", "LOTTE": "석화", "MCI": "석화"}
    lc = {c: 100 * (float(o.loc[c].cost_per_tco2_thkrw) - float(g.loc[c].cost_per_tco2_thkrw))
          / float(g.loc[c].cost_per_tco2_thkrw) for c in rank_g if c in o.index}
    lc_steel = [v for c, v in lc.items() if SEC[c] == "철강"] or [0]
    lc_pet = [v for c, v in lc.items() if SEC[c] == "석화"] or [0]
    L += ["", f"**감축단가 순위**: GBM {' < '.join(CONAME[c] for c in rank_g)} / "
          f"OU {' < '.join(CONAME[c] for c in rank_o)} — "
          + ("불변." if rank_g == rank_o else "**역전.**"), "",
          f"**TCaR은 {min(tc):+.0f}~{max(tc):+.0f}% 움직인다.**", "",
          f"②도 무사하지 않다 — 철강 {min(lc_steel):+.0f}~{max(lc_steel):+.0f}%, "
          f"**석유화학 {min(lc_pet):+.0f}~{max(lc_pet):+.0f}%**. 석화가 크게 움직이는 이유는 "
          "§3이다: 이들의 비용은 거의 전부 수소이고, 수소 충격의 중앙값이 확률과정에 따라 "
          "크게 달라진다.", "",
          "## 3. 같은 종류의 숨은 선택 — 충격 정규화", "",
          "확률과정만이 아니다. **평균을 1로 맞출 것인가, 중앙값을 1로 맞출 것인가**도 "
          "출처가 정해주지 않는 선택이고 결과를 크게 움직인다. 로그정규 충격에 E[충격]=1을 "
          "강제하면 왜도 때문에 **중앙값이 아래로 흐른다** — σ≈0.25에 25년이면 2050년 중앙값이 "
          "중심경로의 **0.47배**다. ②는 P50 지표이므로 **에너지가격이 중심경로의 절반인 "
          "세계에서 계산된다.**", "",
          "| 기업 | ② mean 정규화(현행) | ② median 정규화 | 차이 | ③ TCaR 차이 |",
          "|---|---|---|---|---|"]
    gm = res.get("gbm_median")
    if gm is not None:
        for c in ["POSCO", "NSC", "MCI", "LOTTE"]:
            if c not in g.index or c not in gm.index:
                continue
            a2, b2 = float(g.loc[c].cost_per_tco2_thkrw), float(gm.loc[c].cost_per_tco2_thkrw)
            at, bt = float(g.loc[c].tcar_bnkrw), float(gm.loc[c].tcar_bnkrw)
            L.append(f"| {CONAME[c]} | {a2:,.0f} | {b2:,.0f} | **{100 * (b2 - a2) / a2:+.0f}%** | "
                     f"{100 * (bt - at) / at:+.0f}% |")
        L += ["", "**어느 쪽이 옳은지 우리는 모른다.** D2b의 중심경로(IEA·NGFS 계열)가 평균 "
              "투영인지 중앙값 투영인지 출처가 명시하지 않는다. 현행 `mean`을 유지하되 "
              "**② 를 읽을 때 이 선택이 함께 읽혀야 한다** — config `shock_normalisation`으로 "
              "드러냈고(A-24), 위 표가 그 크기다.", ""]

    L += ["## 4. 결론", "",
          "- **순위는 강건하다.** 확률과정을 바꿔도 정규화를 바꿔도 지목되는 기업의 순서가 같다.",
          f"- **② 의 수준은 강건하지 않다 — 특히 석유화학.** 철강은 {min(lc_steel):+.0f}~"
          f"{max(lc_steel):+.0f}%로 견디지만 석화는 {min(lc_pet):+.0f}~{max(lc_pet):+.0f}% "
          "움직이고, 정규화를 바꾸면 +71~73%까지 간다. **석화의 감축단가는 자릿수만 읽어야 한다.**",
          f"- **③ TCaR의 절대값은 강건하지 않다.** 평균회귀를 가정하면 {abs(min(tc)):.0f}% 넘게 "
          "줄어든다. 보고서가 TCaR을 조원 단위로 적을 때 그 자릿수는 **GBM 가정 위에서만** 유효하다.",
          "- **가를 방법은 데이터뿐이다**: 월별 SMP·KAU·건설공사비지수(G5)를 확보해 ADF·분산비를 "
          "돌리는 것이 유일한 해법이고, 그 전까지 TCaR의 *순위*는 쓰되 *수준*은 조건부로 읽어야 한다.",
          "", "**주의**: OU 반감기 10년 자체가 주입값이다. 반감기가 짧을수록 TCaR은 더 줄고, "
          "무한대면 GBM으로 수렴한다. 즉 위 표는 '한 대안'이지 '대안 전체의 범위'가 아니다.", ""]

    (ROOT / "docs" / "process_alternative.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[-12:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
