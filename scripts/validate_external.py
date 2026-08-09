"""H3 외부 대조 — 우리 값이 실제 프로젝트·문헌 범위 안에 있는가.

내부 일관성(H1)은 "스스로 모순되지 않는가"만 본다. 이 검증은 **바깥과 맞는가**를 본다.
두 축으로 대조한다.

  (a) 기술 CAPEX  ↔ 공시된 실제 프로젝트 (EFF `technology_cost_evidence`, 1차 공시)
                  ↔ 문헌 범위 (DIW DP2082, Vogl 2018)
  (b) 감축 단가 ② ↔ 문헌 한계감축비용·정책 섀도가격 (Nature 2025, 한은·금감원 NGFS)

판정은 세 가지만 쓴다: **범위 안 / 범위 밖(사유) / 대조 불가(사유)**.
범위 밖을 "보수적"이라고 부르지 않는다 — 방향과 크기를 적는다.

    .venv/bin/python scripts/validate_external.py
산출: docs/validation_external.md
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.schemas import load_input  # noqa: E402

EFF = pathlib.Path.home() / "Documents" / "cap-efficient"
DOCS = ROOT / "docs"

# 환율: D6·D3 준비 단계와 동일 기준을 쓴다 (prepare_raw.py USDKRW/JPYKRW).
# EUR는 준비 단계에 없어 여기서 처음 도입하므로 값·근거를 명시한다.
USDKRW, JPYKRW, EURKRW = 1350.0, 9.2, 1450.0
FX_NOTE = (f"USD {USDKRW:,.0f} · JPY {JPYKRW:.1f} · EUR {EURKRW:,.0f} KRW. "
           "USD·JPY는 `prepare_raw.py`와 동일 기준. EUR는 이 문서에서 처음 쓰는 값으로 "
           "2024–25 근사이며, 문헌이 €2022 기준이라 물가·환율 이중 근사가 들어간다 "
           "— 배수 판정(0.5~2배)에는 견디지만 소수점 비교에는 쓸 수 없다.")

# 문헌 앵커. 모두 source_register에 등록된 출처의 quality_note에서 그대로 옮긴 값이고
# 재계산·보정하지 않았다. 새 수치를 여기서 만들지 않는다.
LIT_CAPEX = [
    # (라벨, 저·고 (원화 천원/t능력), source_id, 비고)
    ("EAF 문헌 중앙값", 254 * EURKRW / 1000, 254 * EURKRW / 1000, "DIW_DP2082", "€2022, 그린필드"),
    ("EAF 발표 프로젝트", 467 * EURKRW / 1000, 467 * EURKRW / 1000, "DIW_DP2082", "€2022"),
    ("POSCO 광양 EAF (DIW 수록)", 170.15 * EURKRW / 1000, 170.15 * EURKRW / 1000,
     "DIW_DP2082", "€2023, 기존 부지·인프라 재활용 추정"),
    ("DRP+EAF 문헌 (전해조 제외)", 592 * EURKRW / 1000, 592 * EURKRW / 1000,
     "DIW_DP2082", "€2022"),
    ("DRP+EAF 발표 프로젝트", 751 * EURKRW / 1000, 751 * EURKRW / 1000, "DIW_DP2082", "€2022"),
    ("H2-DRI 전체 (Vogl)", 574 * EURKRW / 1000, 574 * EURKRW / 1000, "VOGL_2018",
     "€2011, 전해조 160 포함 — 우리 모형은 수소를 사서 쓰므로 전해조분 제외 비교"),
]

# 우리 기술 ↔ 어떤 문헌 항목과 비교 가능한가 (범위는 [저, 고] 천원/t능력)
TECH_MAP = {
    "steel_h2dri": ("DRP+EAF (전해조 제외)", 592 * EURKRW / 1000, 751 * EURKRW / 1000, "DIW_DP2082"),
    "steel_hyrex": ("DRP+EAF (전해조 제외)", 592 * EURKRW / 1000, 751 * EURKRW / 1000, "DIW_DP2082"),
    "steel_eaf": ("EAF (문헌~발표 범위)", 254 * EURKRW / 1000, 467 * EURKRW / 1000, "DIW_DP2082"),
}


def verdict(v: float, lo: float, hi: float) -> str:
    if lo <= v <= hi:
        return "범위 안"
    ratio = v / (lo if v < lo else hi)
    side = "하단 아래" if v < lo else "상단 위"
    return f"범위 밖 — {side} ×{ratio:.2f}"


def main() -> int:
    cfg = C.load()
    ddir = C.data_dir(cfg)
    d3 = load_input(ddir, "D3_tech_options").set_index("tech_id")
    d1a = load_input(ddir, "D1a_facility_static")

    ev_path = EFF / "data" / "technology_cost_evidence.csv"
    ev = pd.read_csv(ev_path) if ev_path.exists() else pd.DataFrame()

    m = pd.read_csv(ROOT / "out" / "e5" / "metrics_company.csv").query(
        "scenario=='NZ15' and support=='none'")

    L = ["# H3 외부 대조 — 우리 값은 바깥과 맞는가",
         "", "> `scripts/validate_external.py` 자동 생성. 내부 일관성(H1)과 달리 **모형 밖의 "
         "실제 프로젝트 공시와 문헌 범위**에 우리 값을 견준다.",
         "", f"**환율.** {FX_NOTE}", ""]

    # ---------------------------------------------------------------- (a-1) 실제 프로젝트
    L += ["## 1. 기술 CAPEX ↔ 공시된 실제 프로젝트", "",
          "출처는 EFF `data/technology_cost_evidence.csv` — 전부 기업 1차 공시(T2)에서 "
          "용량으로 나눈 값이다. 비교 시 **범위(scope)가 결정적**이다: 노(爐)만 센 값과 "
          "물류·수전설비·후공정까지 센 값은 5~12배 차이가 난다.", ""]
    if ev.empty:
        L += ["*EFF 증거 파일을 찾지 못했다 (`~/Documents/cap-efficient/data/"
              "technology_cost_evidence.csv`). 대조 불가.*", ""]
    else:
        L += ["| 프로젝트 | 기술 | 천원/t능력 | 범위 | 등급 |", "|---|---|---|---|---|"]
        for r in ev.sort_values("normalized_capex_bn_krw_per_mtpa").itertuples():
            L.append(f"| {r.project_id} | {r.technology_id} | "
                     f"{r.normalized_capex_bn_krw_per_mtpa:,.0f} | {r.comparability} | "
                     f"{r.confidence_grade} |")
        L.append("")
        eaf = ev[ev.technology_id == "SCRAP_EAF"].normalized_capex_bn_krw_per_mtpa
        L += [f"**EAF 실적 분포**: {eaf.min():,.0f} ~ {eaf.max():,.0f} 천원/t "
              f"(중앙 {eaf.median():,.0f}). 최저값은 POSCO 광양(노 중심, 기존 부지 재활용), "
              "최고값은 NSC 야하타(물류·수전·후공정 포함). 우리 D3의 "
              f"`steel_eaf` = {d3.loc['steel_eaf'].capex_unit:,.0f} 천원/t는 **최저값과 같은 "
              "출처에서 왔다** — 즉 우리는 EAF 비용을 이 분포의 하단으로 잡고 있다. "
              "(모형은 BF→EAF 전면 전환을 허용하지 않으므로 결과에 직접 영향은 없다. A-10)", ""]

        # incumbent reline anchor — 이것이 stranded cost(A-13)를 통해 투자 시점을 좌우한다
        rl = ev[ev.technology_id == "BF_RELINE"]
        if not rl.empty:
            real = float(rl.normalized_capex_bn_krw_per_mtpa.iloc[0])
            ours = float(d1a[d1a.unit_type == "BF"].incumbent_capex_unit.median())
            L += ["### 1-1. 개수(reline) 재조달가 — 투자 시점을 좌우하는 앵커", "",
                  f"모형의 `incumbent_capex_unit`(BF 중앙값) = **{ours:,.0f}** 천원/t, "
                  f"공시된 실제 개수(고베제강 3고로 2016, 외피 재사용 90일) = **{real:,.0f}** 천원/t "
                  f"→ **우리 값이 ×{ours / real:.1f} 크다**.", "",
                  "이 값은 좌초비용(A-13) = 개수 캠페인 자산의 잔존 장부가를 정한다. 과대하면 "
                  "**조기 전환의 벌점이 과대**해지고 투자가 재투자 창(relining anchor)으로 과도하게 "
                  "몰린다. 실제 우리 결과의 CAPEX 피크가 2040–41에 집중된 것과 방향이 일치한다.", "",
                  "다만 단일 관측(1개 프로젝트, 2016년, 외피 재사용 = 저비용 사례)이므로 "
                  "**교체가 아니라 범위 부여의 근거**로 쓴다: `incumbent_capex_unit`을 "
                  f"[{real:,.0f}, {ours:,.0f}] 범위의 T5로 승급하고 민감도로 결론 불변성을 "
                  "확인하는 것이 다음 작업이다.", ""]

    # ---------------------------------------------------------------- (a-2) 문헌 범위
    L += ["## 2. 기술 CAPEX ↔ 문헌 범위", "",
          "| 우리 기술 | 우리 값 | 문헌 비교 대상 | 문헌 범위 | 판정 | 출처 |",
          "|---|---|---|---|---|---|"]
    for tech, (label, lo, hi, sid) in TECH_MAP.items():
        if tech not in d3.index:
            continue
        v = float(d3.loc[tech].capex_unit)
        L.append(f"| `{tech}` | {v:,.0f} | {label} | {lo:,.0f} ~ {hi:,.0f} | "
                 f"**{verdict(v, lo, hi)}** | {sid} |")
    L += ["", "*단위: 천원/t 능력. 문헌 원값은 €2022/2011이며 위 환율로 환산했다.*", "",
          "**참조 앵커 원값**", "", "| 항목 | €/t | 천원/t | 출처 | 비고 |", "|---|---|---|---|---|"]
    for label, lo, _hi, sid, note in LIT_CAPEX:
        L.append(f"| {label} | {lo * 1000 / EURKRW:,.0f} | {lo:,.0f} | {sid} | {note} |")
    L.append("")

    # ---------------------------------------------------------------- (b) 감축 단가
    lo2, hi2 = m.cost_per_tco2_thkrw.min(), m.cost_per_tco2_thkrw.max()
    L += ["## 3. 감축 단가 ② ↔ 문헌·정책 섀도가격", "",
          f"우리 값 (NZ15, 지원 없음): **{lo2:,.0f} ~ {hi2:,.0f} 천원/tCO₂** "
          f"= US${lo2 * 1000 / USDKRW:,.0f} ~ {hi2 * 1000 / USDKRW:,.0f}/tCO₂.", "",
          "| 비교 대상 | 값 | 우리 값과의 관계 | 출처 |", "|---|---|---|---|",
          f"| NGFS 1.5℃ 섀도 탄소가격 2030 | US$150/tCO₂ | 우리 하단(US${lo2 * 1000 / USDKRW:,.0f})이 "
          f"이보다 {'낮다' if lo2 * 1000 / USDKRW < 150 else '높다'} | BOK_FSS_CST_2025 |",
          f"| NGFS 1.5℃ 섀도 탄소가격 2050 | US$1,700/tCO₂ | 우리 상단(US${hi2 * 1000 / USDKRW:,.0f})이 "
          f"×{1700 / (hi2 * 1000 / USDKRW):.1f} 낮다 | BOK_FSS_CST_2025 |",
          "| 철강 BAT 리트로핏 평균 | US$15/tCO₂ | 우리 전 기업이 이보다 높다 — 우리 계획은 "
          "리트로핏이 아니라 **루트 전환**을 포함하므로 대상이 다르다 | NATURE_STEELEFF_2025 |",
          "| 에너지효율 단독 | −US$8.5/tCO₂ (비용절감형) | 우리 `steel_eff`는 CAPEX 120천원/t·"
          "EF 2.15→1.60으로 20년 환산 시 약 US$8/tCO₂ (양수) — 문헌이 운영비 절감을 포함해 "
          "음수인 반면 우리는 CAPEX만 센 값이라 부호가 갈린다 | NATURE_STEELEFF_2025 |", "",
          "**판정.** 감축 단가는 2050 섀도 탄소가격보다 한 자릿수 낮고 2030 가격과 같은 "
          "자릿수다. 즉 **전환은 그것이 마주할 탄소가격보다 싸다** — 시나리오 러너의 "
          "`carbon_fast` 묶음에서 탄소 포함 P50이 크게 음수로 가는 결과와 같은 이야기다. "
          "이것은 결론을 지지하는 방향이지 검증의 종료가 아니다: 문헌의 LCOA(수소환원 "
          "US$/tCO₂ 직접 비교)는 아직 추출하지 않았다.", ""]

    # ---------------------------------------------------------------- 남은 것
    L += ["## 4. 아직 못 한 대조 (없는 것을 있다고 하지 않는다)", "",
          "- **문헌 LCOA 직접 대조**: Vogl·Agora·IEA ISTR·Material Economics·MPP의 "
          "수소환원 LCOA(US$/tCO₂) 수치를 아직 추출하지 않았다. 위 3절은 섀도 탄소가격과 "
          "리트로핏 비용만으로 자릿수를 확인한 것이다.",
          "- **석유화학 대조 없음**: `technology_cost_evidence`가 철강 프로젝트뿐이다. "
          "LOTTE·MCI의 CAPEX는 외부 프로젝트 대조 없이 D3 주입값에만 의존한다 — "
          "석화 결과의 가장 약한 고리.",
          "- **범위 정합 미보정**: 실제 프로젝트의 `comparability` 라벨이 "
          "`partial_scope_comparator`~`broad_scope_upper_comparator`로 갈리는데 "
          "범위를 맞춘 재계산은 하지 않았다. 배수 판정까지만 유효하다.", ""]

    DOCS.mkdir(exist_ok=True)
    (DOCS / "validation_external.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[validate_external] docs/validation_external.md ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
