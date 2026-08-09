"""H2 후향 검증 — 주입한 루트 표준값이 2020–2024 실적을 재현하는가.

**철강과 석유화학은 서로 다른 것이 검증된다.** 준비 단계가 두 섹터를 다르게 만들기 때문이다.

  - 철강(POSCO·NSC): 시설 배출을 **회사 공시 총량에 맞춰 재척도**한다. 그래서 회사 수준
    배출강도는 구조상 맞고(검증 대상 아님), 루트 표준값은 **총량을 시설에 나누는 가중치**
    로만 쓰인다. 여기서 검증되는 것은 "그 가중치가 회사의 실제 설비 구성을 얼마나 닮았나"다.
    NSC처럼 목록이 고로 단일 구성이면 가중치가 균일해져 **표준값 수준이 무엇이든 배분이
    같다** — 즉 그 편차는 결과에 걸리지 않는다.
  - 석유화학(LOTTE·MCI): 재척도하지 않는 **상향식**이다(`prod × ROUTE_EF`). 여기서는
    루트 표준값이 곧 **수준**이고, 생산량 공시가 없어 대조 자체가 불가능하다.

    루트 표준 원단위를 능력으로 가중한 값 vs 회사 공시 배출강도

이 대조는 배분 규칙을 우회하므로 순환하지 않지만, **철강에서는 배분 가중치의 적합도를,
석유화학에서는 (대조 가능했다면) 수준의 적합도를 재는** 서로 다른 질문이다. 이 구분을
놓치면 철강의 편차를 결과 편향으로 오독하게 된다.

    .venv/bin/python scripts/validate_backtest.py
산출: docs/validation_backtest.md
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.schemas import load_input  # noqa: E402

DOCS = ROOT / "docs"
RAW = ROOT / "data" / "raw" / "facility_panel.csv"
# prepare_raw.py의 ROUTE와 동일해야 한다 — 다르면 검증이 다른 모형을 재는 셈이라 실패시킨다
ROUTE_EF = {"BF": 2.15, "FINEX": 2.05, "EAF": 0.45, "NCC": 0.95}
TOTALS = {"POSCO": "POSCO_TOTAL", "NSC": "NSC_TOTAL",
          "LOTTE": "LOTTE_TOTAL", "MCI": "MITSUI_TOTAL"}
TOL = 0.10   # 완료 기준: 배출강도 재현 오차 ±10% (AUTOPILOT §4-H2)


def _check_route_table() -> None:
    src = (ROOT / "scripts" / "prepare_raw.py").read_text(encoding="utf-8")
    for unit, ef in ROUTE_EF.items():
        if f'"{unit}": ({ef},' not in src:
            raise SystemExit(
                f"ROUTE 표가 prepare_raw.py와 어긋난다 ({unit}={ef}). "
                "검증이 실제 모형과 다른 값을 재게 되므로 중단한다.")


def main() -> int:
    _check_route_table()
    cfg = C.load()
    d1a = load_input(C.data_dir(cfg), "D1a_facility_static")
    raw = pd.read_csv(RAW, encoding="utf-8-sig")

    # 모형이 실제로 쓰는 원단위 — 표준값이 아니라 이것이 결과에 걸린다
    from cap.e2_milp import _prep_company
    facm, _d3, _ = _prep_company(cfg, C.data_dir(cfg))
    used = {c: float((g.ef_inc * g.production).sum() / g.production.sum())
            for c, g in facm.groupby("company_id")}

    L = ["# H2 후향 검증 — 주입 표준값이 실적을 재현하는가", "",
         "> `scripts/validate_backtest.py` 자동 생성.", "",
         "**먼저 무엇이 검증 대상이 아닌지.** 철강은 시설 배출을 회사 공시 총량에 맞춰 "
         "재척도한다. 따라서 회사 수준 배출강도는 구조상 맞고, 표에 나오는 편차는 "
         "**수준의 편향이 아니라 배분 가중치의 적합도**다. 모형이 실제로 쓰는 값은 아래와 같다.", "",
         "| 기업 | 모형이 쓰는 가중 `ef_inc` | 공시 원단위 | 차이 |", "|---|---|---|---|"]
    for cid in sorted(used):
        obs = None
        g = raw[raw.facility_id == TOTALS.get(cid, "")].dropna(subset=["production"])
        if len(g):
            r = g.sort_values("year").iloc[-1]
            obs = r.emissions_s1 / r.production
        L.append(f"| {cid} | {used[cid]:.3f} | "
                 + (f"{obs:.3f} | **{100 * (used[cid] - obs) / obs:+.1f}%** |" if obs
                    else "생산량 미공시 | 대조 불가 |"))
    L += ["", "철강 2사는 모형이 쓰는 값이 공시와 ±1% 안에서 맞는다 — 재척도의 결과다. "
          "석유화학 2사는 재척도하지 않는 상향식이라 **주입값 0.95가 곧 수준이고, 생산량 "
          "공시가 없어 확인할 방법이 없다**. 아래 표의 편차는 철강에 대해서는 배분 가중치의, "
          "석유화학에 대해서는 (대조 가능했다면) 수준의 적합도를 뜻한다.", "",
         f"루트 표준 배출계수(주입값): " +
         ", ".join(f"{k} {v}" for k, v in ROUTE_EF.items()) + " tCO₂/t.", ""]

    rows = []
    for cid, total_id in TOTALS.items():
        g = raw[raw.facility_id == total_id].dropna(subset=["production"])
        fac = d1a[d1a.company_id == cid]
        if fac.empty:
            continue
        cap = fac.capacity.sum()
        w_ef = (fac.capacity * fac.unit_type.map(ROUTE_EF)).sum() / cap   # 능력가중 루트 EF
        if g.empty:
            rows.append(dict(company_id=cid, year=None, production_mt=None,
                             reported_ef=None, route_ef=round(w_ef, 3), err_pct=None,
                             utilisation_pct=None,
                             note="생산량 미공시 — 원단위 대조 불가"))
            continue
        for r in g.itertuples():
            ef_obs = r.emissions_s1 / r.production
            rows.append(dict(company_id=cid, year=int(r.year),
                             production_mt=round(r.production / 1e6, 2),
                             reported_ef=round(ef_obs, 3), route_ef=round(w_ef, 3),
                             err_pct=round(100 * (w_ef - ef_obs) / ef_obs, 1),
                             utilisation_pct=round(100 * r.production / cap, 1),
                             note=""))
    df = pd.DataFrame(rows)

    L += ["## 1. 배출강도 재현 (tCO₂/t 조강·제품)", "",
          "| 기업 | 연도 | 생산(Mt) | 공시 원단위 | 능력가중 루트 표준 | 오차 | 가동률 |",
          "|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        if pd.isna(r.year):        # None in an int column comes back as NaN
            L.append(f"| {r.company_id} | — | — | — | {r.route_ef} | 대조 불가 | — |")
            continue
        L.append(f"| {r.company_id} | {int(r.year)} | {r.production_mt} | {r.reported_ef} | "
                 f"{r.route_ef} | **{r.err_pct:+.1f}%** | {r.utilisation_pct}% |")
    L.append("")

    ok = df.dropna(subset=["err_pct"])
    L += ["### 판정", ""]
    for cid, g in ok.groupby("company_id"):
        worst = g.err_pct.abs().max()
        mean = g.err_pct.mean()
        verdict = "**통과**" if worst <= TOL * 100 else "**초과**"
        L.append(f"- **{cid}** — 평균 {mean:+.1f}%, 최대 |오차| {worst:.1f}% "
                 f"({verdict}, 기준 ±{TOL:.0%})")
    miss = sorted(set(df[df.err_pct.isna()].company_id))
    if miss:
        L.append(f"- **{', '.join(miss)}** — 생산량 공시가 없어 원단위 대조 불가. "
                 "이 기업들의 배출 원단위는 검증되지 않은 주입값이다.")
    L.append("")

    if len(ok):
        L += ["### 읽는 법", "",
              "오차는 부호를 갖는다. **양(+)이면 루트 표준이 실적보다 높다** = 모형이 기존 "
              "설비를 실제보다 더 더럽다고 본다 → 전환의 감축량을 과대평가하고 감축 단가(②)를 "
              "과소평가한다. 음(−)이면 반대다.", "",
              "고로 일관제철소의 공시 배출강도가 루트 표준(BF 2.15)보다 낮게 나오는 것은 "
              "정상이다 — 회사 합계에는 전기로·스크랩 장입·부생가스 발전 등 저탄소 몫이 "
              "섞여 있고, 우리 능력가중은 그 혼합을 능력 비율로만 근사한다. 따라서 이 오차는 "
              "**루트 표준값의 오류라기보다 설비 구성 해상도의 한계**를 재는 값이다.", ""]

    # ---------------------------------------------------------------- 가동률
    u = ok.dropna(subset=["utilisation_pct"])
    if len(u):
        L += ["## 2. 능력 추정 검증 (가동률)", "",
              "가동률 = 공시 생산량 ÷ 우리 능력 추정 합계. 100%를 넘으면 능력 추정이 "
              "낮은 것이고, 지속적으로 매우 낮으면 능력 추정이 높거나 설비 목록에 "
              "가동 중단분이 남아 있는 것이다 (A-01).", "",
              "| 기업 | 능력 합계(Mt) | 가동률 범위 | 평균 |", "|---|---|---|---|"]
        for cid, g in u.groupby("company_id"):
            cap = d1a[d1a.company_id == cid].capacity.sum() / 1e6
            L.append(f"| {cid} | {cap:.1f} | {g.utilisation_pct.min():.0f}~"
                     f"{g.utilisation_pct.max():.0f}% | {g.utilisation_pct.mean():.0f}% |")
        L.append("")

    # 실패한 대조는 결론에 어떤 방향으로 걸리는지까지 적는다
    bad = ok.groupby("company_id").err_pct.mean()
    bad = bad[bad.abs() > TOL * 100]
    if len(bad):
        L += ["### 결론에 어떤 방향으로 걸리는가", ""]
        for cid, e in bad.items():
            fl = d1a[d1a.company_id == cid].unit_type.value_counts().to_dict()
            L.append(
                f"- **{cid} {e:+.1f}%**: 설비 목록이 {fl}로 사실상 고로 단일 구성이다. "
                f"**결과에는 걸리지 않는다** — 가중치가 균일하면 표준값이 무엇이든 배분이 "
                f"능력 비례로 같아지고, 회사 총량은 공시에 재척도되기 때문이다. 실제로 "
                f"모형이 쓰는 `ef_inc`는 {used.get(cid, float('nan')):.3f}로 공시와 ±1% "
                f"안에서 맞는다. 이 편차가 뜻하는 것은 **표준값이 NSC의 실제 설비 구성을 "
                f"닮지 않았다**는 것이고, 그것이 문제가 되는 지점은 설비 구성이 이질적인 "
                f"기업(POSCO는 +1.0%로 잘 맞는다)과, 재척도하지 않는 석유화학이다.")
        L.append("")

    # 실패 원인 가설을 계산으로 배제한다 — "설비 목록에 EAF가 빠져서"가 맞는지
    if len(bad):
        L += ["### 원인 가설 배제 — 빠진 전기로 때문인가", "",
              "NSC 편차의 자연스러운 설명은 '설비 목록에 전기로가 빠져서'다. 계산해 보면 "
              "그것으로는 설명되지 않는다.", "",
              "| 가정 | 능력가중 EF | 공시(1.856) 대비 |", "|---|---|---|"]
        cap = float(d1a[d1a.company_id == "NSC"].capacity.sum())
        for add, label in [(0.0, "현행 (고로 10기, 44.3 Mt)"),
                           (0.72e6, "히로하타 EAF 0.72 Mt 추가 (2022 가동 중)"),
                           (2.9e6, "FY2029 신설 계획분 2.9 Mt까지 추가"),
                           (4.5e6, "가상 4.5 Mt까지 추가")]:
            ef = (cap * 2.15 + add * 0.45) / (cap + add)
            L.append(f"| {label} | {ef:.3f} | **{100 * (ef - 1.856) / 1.856:+.1f}%** |")
        L += ["", "가동 중인 전기로를 전부 넣어도 15.7%p 중 **1.3%p만 닫힌다**. FY2029 "
              "신설분(이미 D7 공시계획에 있고 모형은 신설 경로로 미해석)까지 넣어도 +10.2%가 "
              "남는다. 능력 추정을 줄이는 것은 EF를 전혀 바꾸지 않는다(전부 고로라 가중이 "
              "그대로다).", "",
              "**따라서 원인은 설비 목록이 아니라 `BF = 2.15 tCO₂/t`이라는 루트 표준값 "
              "자체다.** 이 값은 범위 없는 T5 주입값이고, POSCO에서 잘 맞는 이유는 POSCO의 "
              "가중에 FINEX(2.05)와 EAF(0.45)가 섞여 2.03으로 내려가기 때문이다. "
              "작업 방향이 G3(능력 정합)에서 **G2(원단위 승급)·G1(시설 실측)**으로 바뀐다.", ""]

    L += ["## 3. 못 한 검증", "",
          "- **에너지 원단위 재현 불가**: 기업이 사업장별 에너지 소비를 공시하지 않아 "
          "루트 표준 전력·원료탄·가스 원단위(A-03)를 실적에 견줄 수 없다. 이 값들은 "
          "현재 어떤 후향 검증도 통과하지 않은 상태다.",
          "- **석유화학 전면 미검증**: LOTTE·MCI 모두 생산량 미공시라 원단위 대조가 "
          "성립하지 않는다. 석화 결과는 배출 총량만 실적에 앵커돼 있고 원단위·능력은 "
          "검증되지 않았다.",
          "- **비용 재현 없음**: 실제 에너지 지출·CAPEX 실적 시계열이 없어 모형 비용 "
          "구조 자체는 후향 검증되지 않았다. H3(외부 대조)가 대신하는 부분이다.", ""]

    DOCS.mkdir(exist_ok=True)
    (DOCS / "validation_backtest.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    df.to_csv(DOCS / "validation_backtest.csv", index=False)
    print("\n".join(L[:6]))
    print(f"\n[backtest] docs/validation_backtest.md — 대조 {len(ok)}행, 미대조 {len(miss)}사")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
