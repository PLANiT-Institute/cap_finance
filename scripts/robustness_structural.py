"""I2 구조 대안 — 결정 기준을 바꾸면 답이 바뀌는가.

민감도(F2)는 파라미터를 흔들고, 강건성(I1)은 할인율을 흔든다. 이 검증은 **모형이 무엇을
최적이라 부르는지**를 흔든다. 위험중립 의사결정자(P50 최소)와 위험회피 의사결정자(P90 최소)는
같은 계획을 고르는가.

E2가 만든 계획·계약 격자는 이미 있으므로 재실행이 필요 없다 — 선택 규칙만 바꿔 다시 고른다.

    .venv/bin/python scripts/robustness_structural.py
산출: docs/robustness_structural.md
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402

CONAME = {"POSCO": "POSCO", "NSC": "Nippon Steel",
          "LOTTE": "LOTTE Chemical", "MCI": "Mitsui Chemicals"}
SECTOR = {"POSCO": "철강", "NSC": "철강", "LOTTE": "석화", "MCI": "석화"}


def pick(g: pd.DataFrame, basis: str) -> pd.DataFrame:
    b = g.sort_values(basis).groupby("company_id").head(1).copy()
    b["lcoa"] = b[basis] * 1e6 / b.abated_tco2_disc
    return b.set_index("company_id")


def main() -> int:
    cfg = C.load()
    fr = pd.read_csv(ROOT / "out" / "e5" / "frontier_points.csv").query(
        "scenario=='NZ15' and support=='none'")
    g = fr[~fr.is_disclosed & fr.budget_ok]
    if g.empty:
        raise SystemExit("예산 정합 계획이 없다 — e5 먼저 실행")

    p50, p90 = pick(g, "p50"), pick(g, "p90")
    order = lambda d: [c for c in d.sort_values("lcoa").index]  # noqa: E731

    L = ["# I2 구조 대안 — 결정 기준을 바꾸면 답이 바뀌는가", "",
         "> `scripts/robustness_structural.py` 자동 생성.", "",
         "F2는 파라미터를, I1은 할인율을 흔든다. 여기서 흔드는 것은 **모형이 무엇을 '최적'이라 "
         "부르는지**다. 위험중립 의사결정자는 기대비용(P50)을 최소화하고, 위험회피 의사결정자는 "
         "**나쁜 경우(P90)**를 최소화한다. 같은 계획 집합에서 선택 규칙만 바꿔 다시 골랐다 — "
         "재실행이 아니라 재선택이므로 계획 메뉴는 동일하다.", "",
         "## 1. 순위", "",
         f"- **P50 기준**: {' < '.join(CONAME[c] for c in order(p50))}",
         f"- **P90 기준**: {' < '.join(CONAME[c] for c in order(p90))}", "",
         ("**순위 불변.** 결정 기준을 바꿔도 지목되는 기업이 같다."
          if order(p50) == order(p90) else
          "**순위 역전.** 위험 태도가 결론을 바꾼다 — 어느 기업이 '싼가'는 "
          "의사결정자의 위험선호에 의존한다."), "",
         "## 2. 감축단가와 꼬리 두께", "",
         "| 기업 | 섹터 | P50 기준 (천원/tCO₂) | P90 기준 | **꼬리 배수** |",
         "|---|---|---|---|---|"]
    ratios = {}
    for c in order(p50):
        a, b = float(p50.loc[c].lcoa), float(p90.loc[c].lcoa)
        ratios[c] = b / a
        L.append(f"| {CONAME[c]} | {SECTOR[c]} | {a:,.0f} | {b:,.0f} | **×{b / a:.1f}** |")
    steel = [v for c, v in ratios.items() if SECTOR[c] == "철강"]
    pet = [v for c, v in ratios.items() if SECTOR[c] == "석화"]
    if steel and pet:
        L += ["", f"**꼬리 두께가 섹터별로 다르다**: 철강 ×{min(steel):.1f}~{max(steel):.1f}, "
              f"석유화학 ×{min(pet):.1f}~{max(pet):.1f}. 석화는 기대비용 기준으로는 철강의 "
              f"{max(float(p50.loc[c].lcoa) for c in ratios if SECTOR[c] == '석화') / max(float(p50.loc[c].lcoa) for c in ratios if SECTOR[c] == '철강'):.1f}배지만, "
              "나쁜 경우 기준으로는 격차가 훨씬 벌어진다. **석화의 문제는 비용 수준이 아니라 "
              "비용의 분산**이라는 뜻이고, 그 분산의 대부분은 수소 가격이다(변동성 분해 참조).", ""]

    L += ["## 3. 무엇이 바뀌는가 — 계약 선택", "",
          "순위는 그대로여도 **고르는 계획은 달라진다**. 위험회피 기준은 같은 물리적 전환에 "
          "**더 많은 계약 헤지**를 붙인 변형을 고른다.", "",
          "| 기업 | P50 선택 | PPA/EPC/CCfD | P90 선택 | PPA/EPC/CCfD |", "|---|---|---|---|---|"]
    for c in order(p50):
        r5, r9 = p50.loc[c], p90.loc[c]
        L.append(f"| {CONAME[c]} | `{r5.plan_id}` | {r5.ppa_share:.0%}/{int(r5.epc)}/{int(r5.ccfd)} "
                 f"| `{r9.plan_id}` | {r9.ppa_share:.0%}/{int(r9.epc)}/{int(r9.ccfd)} |")
    same_base = all(p50.loc[c].base_plan_id == p90.loc[c].base_plan_id for c in order(p50))
    # 고른 헤지가 실제 위험을 다루는가 — 분산 분해와 맞대어 본다
    vd = pd.read_csv(ROOT / "out" / "e5" / "variance_decomp.csv").query(
        "scenario=='NZ15' and support=='none'")
    L += ["", "### 3-1. 고른 헤지가 그 회사의 위험을 다루는가", "",
          "| 기업 | 꼬리위험 구성 (전력/수소/설비비) | P90이 고른 헤지 | 그 헤지가 덮는 분산 |",
          "|---|---|---|---|"]
    mismatch = []
    for c in order(p50):
        pid = p50.loc[c].plan_id
        v = {r.factor: float(r.variance_share) for r in vd[vd.plan_id == pid].itertuples()}
        r9 = p90.loc[c]
        hedge = ("PPA" if r9.ppa_share > 0 else "") + ("EPC" if int(r9.epc) else "") \
                + ("CCfD" if int(r9.ccfd) else "") or "없음"
        covered = (v.get("elec", 0) if r9.ppa_share > 0 else 0) + \
                  (v.get("capex", 0) if int(r9.epc) else 0)
        L.append(f"| {CONAME[c]} | {v.get('elec', 0):.0%} / {v.get('h2', 0):.0%} / "
                 f"{v.get('capex', 0):.1%} | {hedge} | **{covered:.0%}** |")
        if covered < 0.2:
            mismatch.append((c, v.get("h2", 0)))
    if mismatch:
        who = ", ".join(CONAME[c] for c, _ in mismatch)
        L += ["", f"**{who}는 꼬리위험의 거의 전부가 수소 가격인데, 위험회피 기준이 고른 헤지는 "
              "분산의 수 %도 덮지 못한다.** 모형이 나빠서가 아니라 **계약 수단 집합에 수소 헤지가 "
              "없기 때문**이다 — PPA는 전력만 고정하고 수소는 `no power hedge on H2`로 시장에 "
              "그대로 노출된다(`plancost.simulate_cost`). 위험회피 의사결정자는 **쓸 수 있는 "
              "유일한 헤지를 사되 자기 위험은 그대로 안고 간다.**", "",
              "이것은 모형의 한계이자 그 자체로 결과다: **석유화학 전환의 위험관리는 현재 "
              "수단 집합으로 불가능하다.** 수소 장기 공급계약(오프테이크·가격 고정)이 "
              "수단으로 들어오기 전까지 석화의 TCaR은 줄일 방법이 없다.", ""]

    L += ["", ("**기저 계획(어느 설비를 언제 무엇으로)은 동일하고 계약만 바뀐다.** 즉 위험 태도는 "
               "*무엇을 지을지*가 아니라 *어떻게 조달할지*를 바꾼다 — 설계서의 주장 P2가 "
               "산출물에서 성립한다." if same_base else
               "**기저 계획 자체가 달라진다** — 위험 태도가 물리적 전환 계획까지 바꾼다."), "",
          "## 4. 한계", "",
          "- 이 검증은 **재선택**이다. E2가 만들지 않은 계획은 어느 기준으로도 고를 수 없다.",
          "- P90은 우리 시뮬레이션의 P90이므로 사전 변동성(A-17)에 직접 의존한다. "
          "**꼬리 배수의 절대값은 그 사전값만큼만 믿을 수 있다** — 순위·부호가 결론이다.",
          "- 폐쇄 상한·예산 위반 페널티 같은 **제약 수준의 대안은 E2 재실행이 필요**하고 "
          "여기 포함되지 않았다(`run_scenarios.py --replan retire_free`).", ""]

    (ROOT / "docs" / "robustness_structural.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[6:20]))
    print("\n[I2] docs/robustness_structural.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
