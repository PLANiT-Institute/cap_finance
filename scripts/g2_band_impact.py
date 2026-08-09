"""G2 (D10) — 기술 파라미터에 문헌 [low, high]를 붙였을 때 ③ TCaR이 어떻게 달라지는가.

D9 발견 1이 G2의 완료 기준을 바꿨다: 값을 승급하는 것이 아니라 **범위를 함께 받는 것**이
완료 기준이다. 여기서는 (a) 붙은 밴드와 그 유래, (b) 밴드가 base_param 승수로 옮겨졌을 때의
구간, (c) 그 구간으로 F3을 다시 돌린 결과 대 ±규약 결과를 한 표로 낸다.

    .venv/bin/python scripts/g2_band_impact.py
산출: out/g2/{bands,f3_compare,summary}.csv, docs/tech_band_upgrade.md

전제: `prepare_raw.py` → `uncertainty_propagation.py` (기본) → 같은 스크립트 `--bands`.
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from uncertainty_propagation import evidence_bands  # noqa: E402

sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402

STEEL = ["POSCO", "NSC"]


def main() -> int:
    cfg = C.load(data_dir="data/prepared")
    prep = C.data_dir(cfg)
    tb = pd.read_csv(prep / "D3b_tech_bands.csv")
    d3 = pd.read_csv(prep / "D3_tech_options.csv")

    tb["value"] = [float(d3.loc[d3.tech_id == r.tech_id, r.field].iloc[0])
                   for r in tb.itertuples()]
    tb["inside"] = (tb.value_low <= tb.value) & (tb.value <= tb.value_high)
    tb["mult_low"] = tb.value_low / tb.value
    tb["mult_high"] = tb.value_high / tb.value

    env = evidence_bands(cfg)
    conv = pd.read_csv(ROOT / "out/uncertainty/decomposition.csv")
    band = pd.read_csv(ROOT / "out/uncertainty/decomposition_bands.csv")
    k = ["company_id", "width", "tcar_param", "param_share_pct", "tcar_joint"]
    cmp = conv[k].merge(band[k], on=["company_id", "width"], suffixes=("_conv", "_band"))
    cmp["ratio"] = cmp.tcar_param_band / cmp.tcar_param_conv

    odir = ROOT / "out" / "g2"
    odir.mkdir(parents=True, exist_ok=True)
    tb.to_csv(odir / "bands.csv", index=False)
    cmp.to_csv(odir / "f3_compare.csv", index=False)

    w = cmp.width.min()                       # 규약 폭 의존을 덜 타는 쪽(±15%)에서 읽는다
    st = cmp[(cmp.width == w) & cmp.company_id.isin(STEEL)]
    summary = pd.DataFrame([
        ("g2_bands_added", len(tb)),
        ("g2_bands_outside", int((~tb.inside).sum())),
        ("f3_param_share_steel_conv_w15", round(st.param_share_pct_conv.mean())),
        ("f3_param_share_steel_band_w15", round(st.param_share_pct_band.mean())),
    ], columns=["key", "value"])
    summary.to_csv(odir / "summary.csv", index=False)

    L = ["# G2 — 기술 파라미터 증거 밴드와 ③ TCaR", "",
         "> `scripts/g2_band_impact.py` 자동 생성.", "",
         "## 1. 붙은 밴드", "",
         "| 기술.항목 | 현행 값 | [low, high] | 등급 | 출처 | 값이 밴드 안 |", "|---|---|---|---|---|---|"]
    for r in tb.itertuples():
        L.append(f"| `{r.tech_id}.{r.field}` | {r.value:g} | [{r.value_low:g}, {r.value_high:g}] "
                 f"| {r.evidence_tier} | `{r.source_id}` | {'예' if r.inside else '**아니오**'} |")
    L += ["", "유래는 `data/raw/tech_bands.csv`의 `derivation` 열에 한 줄씩 있다. "
          "밴드가 현행 값을 배제해도 **값을 고치지 않았다** — 경계·표본이 다를 수 있고, "
          "조용한 교체가 이 저장소의 반복 실패 방식이다.", "",
          "## 2. base_param 승수 구간 (F3 투입)", "",
          "| base_param | [low, high] 승수 | 규약 ±30% 대비 |", "|---|---|---|"]
    for p, (lo, hi) in sorted(env.items()):
        note = ("전 구간 ≥ 1 — 규약은 1을 중심으로 대칭 추첨하므로 **절반이 증거가 배제하는 영역**"
                if lo >= 1.0 else
                "전 구간 ≤ 1 — 같은 이유로 규약의 위쪽 절반이 증거 밖" if hi <= 1.0 else "양측")
        L.append(f"| `{p}` | [{lo:.3f}, {hi:.3f}] | {note} |")
    L += ["", "## 3. F3 재실행 — 규약 대 증거", "",
          "| 기업 | 폭 | TCaR_param 규약 | 증거 밴드 | 배율 | 파라미터 몫 규약→증거 |",
          "|---|---|---|---|---|---|"]
    for r in cmp.sort_values(["width", "company_id"]).itertuples():
        L.append(f"| {r.company_id} | ±{r.width:.0%} | {r.tcar_param_conv:,.0f} | "
                 f"{r.tcar_param_band:,.0f} | ×{r.ratio:.2f} | "
                 f"{r.param_share_pct_conv:.0f}% → {r.param_share_pct_band:.0f}% |")
    L += ["", "단위 십억원. `tcar_price`는 두 실행에서 동일하다(가격 축을 건드리지 않았다).", ""]
    (ROOT / "docs" / "tech_band_upgrade.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"[G2] 밴드 {len(tb)}건, 값이 밴드 밖 {int((~tb.inside).sum())}건")
    print(f"[G2] 승수 구간 " + ", ".join(f"{p} [{lo:.3f}, {hi:.3f}]" for p, (lo, hi) in env.items()))
    print(f"[G2] 철강 파라미터 몫 ±{w:.0%}: {st.param_share_pct_conv.mean():.0f}% "
          f"→ {st.param_share_pct_band.mean():.0f}%")
    print(f"[G2] wrote {odir}/ + docs/tech_band_upgrade.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
