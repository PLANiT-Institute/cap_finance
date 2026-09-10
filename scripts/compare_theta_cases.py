"""Compare isolated theta-alternative runs (cycle 6, 2026-09-07).

Reads tmp/research_v2_theta/<case>/run/e5/metrics_company.csv for every case and
reports, per company x scenario, the change versus base_fin in selected plan,
p50, mean, TCaR, ES and capex. Reduced-search runs (frontier 4, 4,000 paths):
differences below the MC half-width (~3-5% of TCaR per the 2026-09-05 audit)
are not interpreted.

Output: data/research_v2/technology_packages/theta_case_comparison.csv
        docs/research_cycles/2026-09-07/THETA_CASE_COMPARISON.md
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "tmp/research_v2_theta"
OUT_CSV = ROOT / "data/research_v2/technology_packages/theta_case_comparison.csv"
OUT_MD = ROOT / "docs/research_cycles/2026-09-07/THETA_CASE_COMPARISON.md"
CASES = ["base_fin", "steel_vogl_hot", "steel_vogl_cold", "ncc_linde3", "ncc_layritz", "h2fuel_102"]
COLS = ["p50_bnkrw", "mean_bnkrw", "tcar_bnkrw", "es_alpha_bnkrw", "capex_total_bnkrw", "selected_plan_id"]


def tech_mix(case, company, scen, plan_id):
    p = WORK / case / "run/e2/plans" / f"plan_{plan_id.split('.')[0]}.csv"
    if not p.exists():
        return ""
    d = pd.read_csv(p)
    col = next((c for c in d.columns if "tech" in c.lower()), None)
    return ";".join(sorted(set(d[col].dropna().astype(str)))) if col else ""


def main():
    frames = []
    for c in CASES:
        m = pd.read_csv(WORK / c / "run/e5/metrics_company.csv")
        m["case"] = c
        frames.append(m)
    m = pd.concat(frames)
    base = m[m.case == "base_fin"].set_index(["company_id", "scenario"])
    rows = []
    for _, r in m.iterrows():
        b = base.loc[(r.company_id, r.scenario)]
        rows.append(dict(case=r.case, company=r.company_id, scenario=r.scenario, selected_plan=r.selected_plan_id,
                         techs=tech_mix(r.case, r.company_id, r.scenario, r.selected_plan_id),
                         plan_changed=tech_mix(r.case, r.company_id, r.scenario, r.selected_plan_id) != tech_mix("base_fin", r.company_id, r.scenario, b.selected_plan_id),
                         p50=r.p50_bnkrw, d_p50=r.p50_bnkrw - b.p50_bnkrw, mean=r.mean_bnkrw, d_mean=r.mean_bnkrw - b.mean_bnkrw,
                         tcar=r.tcar_bnkrw, d_tcar=r.tcar_bnkrw - b.tcar_bnkrw, d_tcar_pct=(r.tcar_bnkrw / b.tcar_bnkrw - 1) * 100,
                         es=r.es_alpha_bnkrw, d_es=r.es_alpha_bnkrw - b.es_alpha_bnkrw, capex=r.capex_total_bnkrw, d_capex=r.capex_total_bnkrw - b.capex_total_bnkrw))
    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)
    v = df[df.case != "base_fin"]
    md = ["# θ 대안 격리 실행 비교 (회차 6, 2026-09-07)", "",
          "선택 변경은 선택 계획의 기술 구성(설비×기술) 비교이며 plan_id는 사례마다 재번호되므로 쓰지 않는다. 재현 입력 17개 CSV 복사 후 D3 행만 패치. 규약 cash_v1·explicit_retention·strict·incremental_cash·mean 선택. 탐색 축소(frontier 4, 4,000경로)라 절대값은 v1.0 결과가 아니며 base_fin과의 **쌍 비교**만 읽는다. MC 반폭(TCaR 3–5%) 이하 차이는 해석하지 않는다. 재생성: `scripts/compare_theta_cases.py`. 정본 무변경.", "",
          "| 사례 | 회사 | 시나리오 | 선택 변경 | Δ평균 십억원 | ΔTCaR 십억원 (%) | ΔES | ΔCAPEX |", "|---|---|---|---|---:|---:|---:|---:|"]
    for _, r in v.iterrows():
        md.append(f"| {r.case} | {r.company} | {r.scenario} | {'예' if r.plan_changed else '아니오'} | {r.d_mean:,.0f} | {r.d_tcar:,.0f} ({r.d_tcar_pct:+.1f}%) | {r.d_es:,.0f} | {r.d_capex:,.0f} |")
    steel = v[v.case.str.startswith("steel") & v.company.isin(["POSCO", "NSC"])]
    ncc = v[v.case.str.startswith("ncc") & v.company.isin(["LOTTE", "MCI"])]
    h2 = v[(v.case == "h2fuel_102") & v.company.isin(["LOTTE", "MCI"])]
    md += ["", "## 읽기", "",
           f"- 철강 전력 사양(0.85→1.119/1.278): 선택 변경 {int(steel.plan_changed.sum())}/{len(steel)}건, 평균 비용 변화 {steel.d_mean.min():,.0f}~{steel.d_mean.max():,.0f}십억원, TCaR 변화 {steel.d_tcar_pct.min():+.1f}~{steel.d_tcar_pct.max():+.1f}%.",
           f"- 석화 전기가열 사양(2.8→3.25/6.99): 선택 변경 {int(ncc.plan_changed.sum())}/{len(ncc)}건, 평균 비용 변화 {ncc.d_mean.min():,.0f}~{ncc.d_mean.max():,.0f}십억원, TCaR 변화 {ncc.d_tcar_pct.min():+.1f}~{ncc.d_tcar_pct.max():+.1f}%.",
           f"- 수소 연료 83→102kg: 선택 변경 {int(h2.plan_changed.sum())}/{len(h2)}건, 평균 {h2.d_mean.min():,.0f}~{h2.d_mean.max():,.0f}. 구조 문제(내부 메탄 넷백)는 이 실행에서 고치지 않았으므로 절감 과대 가능성이 남는다.",
           "", "선택 변경이 0이어도 사양이 검증됐다는 뜻이 아니다. 후보 집합이 4점 frontier로 축소돼 있어 사양 변화가 후보 순서를 바꾸지 못했을 수 있다. 전체 탐색(frontier 6–10, 10,000경로)·θ 대안별 재최적화·가스/탄소 확률화는 미완료다."]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    assert len(df) == len(CASES) * 8
    print(v[["case", "company", "scenario", "plan_changed", "d_mean", "d_tcar_pct"]].round(1).to_string())


if __name__ == "__main__":
    main()
