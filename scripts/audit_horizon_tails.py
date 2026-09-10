"""Multi-horizon tail audit and joint technology x price exposure (cycle 5, 2026-09-07).

Part A. Does the FIN assumption (iid Gaussian log shocks, variance ~ horizon) match
observed multi-year price moves? Uses World Bank monthly log returns (2010M02-2025M12,
191 months, six benchmarks; data/research_v2/price_history). Overlapping h-month sums;
empirical 5/95 quantiles vs Gaussian +-1.645 sigma_1 sqrt(h) and vs an AR(1)-adjusted
Gaussian. Overlapping windows are not independent; no p-values are reported.

Part B. Which uncertainty dominates purchased-energy cost per tonne: the technology
specification set theta (cycles 2-3) or the price tail? Uses D2b Korea NZ15 2030
central prices and the FIN factor volatilities (elec 0.242 from D4 SMP; h2 0.25 PRIOR;
correlation identity because D4 lacks joint series). theta is a set of alternatives,
not a distribution; no average across specs.

Nothing here changes FIN/EFF inputs.
Outputs: data/research_v2/price_model_audit/horizon_tail_audit.csv
         data/research_v2/price_model_audit/theta_price_exposure.csv
         output/research_v2/figures/horizon_tails_and_theta_exposure.png
         docs/research_cycles/2026-09-07/JOINT_TAIL_AUDIT.md
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RET = ROOT / "data/research_v2/price_history/aligned_monthly_log_returns.csv"
OUT_A = ROOT / "data/research_v2/price_model_audit/horizon_tail_audit.csv"
OUT_B = ROOT / "data/research_v2/price_model_audit/theta_price_exposure.csv"
FIG = ROOT / "output/research_v2/figures/horizon_tails_and_theta_exposure.png"
MD = ROOT / "docs/research_cycles/2026-09-07/JOINT_TAIL_AUDIT.md"
HORIZONS = [1, 12, 36, 60]
Z95 = 1.6448536

# FIN calibration reproduced from D4 (cycle 5 log): annual log-vol
def _fin_vol():
    """FIN annual log-vol from D4 via the engine calibration (elec), fallback priors for h2/capex."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from cap.calibration import calibrate
    cal = calibrate(pd.read_csv(ROOT / "data/prepared/D4_price_history.csv"))
    return {"elec": round(cal.vol["elec"], 4), "h2": cal.vol["h2"], "capex": cal.vol["capex"]}


FIN_VOL = _fin_vol()  # elec 0.2424 reproduced from D4; h2 and capex are fallback priors, corr = identity
# D2b Korea NZ15 2030 central prices
P_ELEC = 123_200.0   # KRW/MWh grid; re_price 175,000 for transition power
P_RE = 175_000.0
P_H2 = 3_500.0       # KRW/kg (MOTIE 2030 target)
HORIZON_YEARS = 5    # 2025 -> 2030
# theta alternatives (cycles 2-3), per t product
STEEL_SPECS = {
    "FIN 0.85MWh+51kg": (0.85, 51.0),
    "Vogl residual hot 1.119+51": (1.119, 51.0),
    "Vogl cold 1.278+51": (1.278, 51.0),
    "GCAM 1.167+60.8(+3.6GJ gas)": (1.167, 60.8),
    "50% scrap: 0.85+25 (elec unverified)": (0.85, 25.0),
}
NCC_SPECS = {"FIN 2.8": 2.8, "Linde A3+base 3.25": 3.25, "Linde A2 3.79+0.21": 4.00, "Linde A1 4.51+0.21": 4.72, "Layritz 6.99": 6.99}


def part_a():
    r = pd.read_csv(RET).set_index("period")
    rows = []
    for s in r.columns:
        x = r[s].to_numpy()
        sd1 = x.std(ddof=1)
        acf1 = np.corrcoef(x[:-1], x[1:])[0, 1]
        for h in HORIZONS:
            if h == 1:
                y = x
            else:
                y = np.convolve(x, np.ones(h), mode="valid")  # overlapping h-month sums
            q05, q95 = np.quantile(y, [0.05, 0.95])
            # Match location before comparing tail widths. Raw h-period returns
            # include drift and cannot be compared to a zero-mean Gaussian.
            cq05, cq95 = np.quantile(y-y.mean(), [0.05, 0.95])
            g = Z95 * sd1 * np.sqrt(h)
            # AR(1) variance of an h-sum: sd1^2 * [h + 2*sum_{k=1}^{h-1}(h-k)rho^k]
            var_ar = sd1 ** 2 * (h + 2 * sum((h - k) * acf1 ** k for k in range(1, h)))
            g_ar = Z95 * np.sqrt(var_ar)
            ku = pd.Series(y).kurt()
            rows.append(dict(series=s, horizon_months=h, n_windows=len(y), empirical_q05=q05, empirical_q95=q95,
                             horizon_mean=y.mean(), centered_q05=cq05, centered_q95=cq95,
                             gaussian_iid_95=g, gaussian_ar1_95=g_ar, ratio_q95_to_iid=cq95 / g, ratio_q05_to_iid=-cq05 / g,
                             legacy_uncentered_ratio_q95=q95/g,
                             excess_kurtosis=ku, acf1_monthly=acf1, sd_monthly=sd1, note="centered overlapping windows; descriptive; no mean-reversion identification"))
    df = pd.DataFrame(rows)
    df.to_csv(OUT_A, index=False)
    return df


def lognormal_q(p0, vol_annual, years, q):
    from statistics import NormalDist
    z = NormalDist().inv_cdf(q)
    sig = vol_annual * np.sqrt(years)
    return p0 * np.exp(sig * z - 0.5 * sig ** 2)  # mean-normalised, as FIN shock_normalisation: mean


def part_b():
    rows = []
    # Conditional demonstration, not a firm procurement model: stochastic grid
    # electricity, independently sampled purchased H2; common draws across theta.
    z = np.random.default_rng(20260907).standard_normal((100000, 2))
    sigma = np.array([FIN_VOL['elec'], FIN_VOL['h2']])*np.sqrt(HORIZON_YEARS)
    prices = np.array([P_ELEC, P_H2])*np.exp(z*sigma-sigma**2/2)
    for name, (el, h2) in STEEL_SPECS.items():
        if 'GCAM' in name or '50% scrap' in name:
            continue  # incomplete/mismatched flows are not comparable total ledgers
        cost_e, cost_h = el*prices[:, 0], h2*prices[:, 1]
        for q in (0.5, 0.95):
            rows.append(dict(sector="steel_h2dri", spec=name, price_quantile=q, elec_mwh=el, h2_kg=h2,
                             elec_cost_krw_t=np.quantile(cost_e, q), h2_cost_krw_t=np.quantile(cost_h, q), total_krw_t=np.quantile(cost_e+cost_h, q),
                             note="total quantile of joint cost samples, component quantiles do not add; illustrative stochastic grid price, not PPA; no heat-boundary validation"))
    for name, el in NCC_SPECS.items():
        for q in (0.5, 0.95):
            pe = lognormal_q(P_ELEC, FIN_VOL["elec"], HORIZON_YEARS, q)
            rows.append(dict(sector="petchem_ecracker", spec=name, price_quantile=q, elec_mwh=el, h2_kg=0.0,
                             elec_cost_krw_t=el * pe, h2_cost_krw_t=0.0, total_krw_t=el * pe, note="per t ethylene; methane netback excluded"))
    df = pd.DataFrame(rows)
    df.to_csv(OUT_B, index=False)
    return df


def figure(a, b):
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    # A: ratio of empirical q95 to Gaussian iid by horizon
    for s, g in a.groupby("series"):
        ax[0].plot(g.horizon_months, g.ratio_q95_to_iid, marker="o", label=s)
    ax[0].axhline(1, color="k", lw=0.8, ls="--")
    ax[0].set_xticks(HORIZONS); ax[0].set_xlabel("horizon (months)"); ax[0].set_ylabel("centered empirical q95 / Gaussian iid q95")
    ax[0].set_title("A. Upper tail vs FIN-type iid Gaussian, World Bank 2010-2025 (overlapping windows)", fontsize=9)
    ax[0].legend(fontsize=7)
    # B: steel theta x price
    st = b[b.sector == "steel_h2dri"]
    specs = list(st.spec.unique())
    x = np.arange(len(specs))
    p50 = [st[(st.spec == s) & (st.price_quantile == 0.5)].total_krw_t.iloc[0] / 1000 for s in specs]
    p95 = [st[(st.spec == s) & (st.price_quantile == 0.95)].total_krw_t.iloc[0] / 1000 for s in specs]
    ax[1].bar(x - 0.2, p50, 0.4, label="cost P50"); ax[1].bar(x + 0.2, p95, 0.4, label="joint cost P95")
    ax[1].set_xticks(x); ax[1].set_xticklabels(specs, rotation=25, ha="right", fontsize=7)
    ax[1].set_ylabel("purchased elec+H2, thousand KRW / t steel"); ax[1].set_title("B. H2-DRI: spec set theta vs joint price sensitivity (2030 KR)", fontsize=9); ax[1].legend(fontsize=7)
    nc = b[b.sector == "petchem_ecracker"]
    specs2 = list(NCC_SPECS); x2 = np.arange(len(specs2))
    p50 = [nc[(nc.spec == s) & (nc.price_quantile == 0.5)].total_krw_t.iloc[0] / 1000 for s in specs2]
    p95 = [nc[(nc.spec == s) & (nc.price_quantile == 0.95)].total_krw_t.iloc[0] / 1000 for s in specs2]
    ax[2].bar(x2 - 0.2, p50, 0.4, label="cost P50"); ax[2].bar(x2 + 0.2, p95, 0.4, label="price P95")
    ax[2].set_xticks(x2); ax[2].set_xticklabels(specs2, rotation=25, ha="right", fontsize=7)
    ax[2].set_ylabel("purchased elec, thousand KRW / t ethylene"); ax[2].set_title("C. e-cracker: spec set theta vs price tail", fontsize=9); ax[2].legend(fontsize=7)
    fig.tight_layout(); FIG.parent.mkdir(parents=True, exist_ok=True); fig.savefig(FIG, dpi=150)


def main():
    a = part_a(); b = part_b(); figure(a, b)
    pivot = a.pivot(index="series", columns="horizon_months", values="ratio_q95_to_iid")
    md = """# 다기간 꼬리와 기술 사양 민감도 — 수정 감사, 2026-09-07

## 수정 이유

이전 버전은 평균이 제거되지 않은 h개월 로그가격변화의 q95를 평균 0 가우시안과 비교했다. 현재는 각 지평의 겹침 합에서 그 표본평균을 뺀 뒤 분위수를 계산한다. 원래 분위수와 비중심 비율은 CSV에 보존했다. 이 비율만으로 가격수준의 평균회귀나 로그 OU 반감기를 식별할 수 없다. 종전의 ‘평균회귀가 확인됐다’는 해석은 철회한다.

철강 그림은 각 가격요인의 P95를 더하던 방식에서 전력·수소의 같은 경로 비용을 먼저 더한 뒤 총비용 P50·P95를 계산하는 방식으로 바꿨다(100,000경로, 독립 요인, 시드 20260907). 전력은 로컬 D2 2030 한국 그리드 앵커 123,200KRW/MWh, 수소는 정책 목표 기반 가정 3,500KRW/kg이다. 이전 그림의 PPA 175,000에 현물 충격을 가하던 경계도 바꿨다. 둘 다 조건부 민감도이며 검증된 기업 조달 가격분포가 아니다.

## 평균을 맞춘 비교

| 계열 | 1개월 | 12개월 | 36개월 | 60개월 |
|---|---:|---:|---:|---:|
"""
    for name, row in pivot.iterrows():
        md += "| " + name + " | " + " | ".join(f"{row[h]:.3f}" for h in HORIZONS) + " |\n"
    md += """
비교 대상은 World Bank 2010–2025년 벤치마크 6종의 중심화 로그변화 합과 1.645·월 표준편차·√h다. 비율 1 초과는 이 표본에서 중심화 상위 분위수 간격이 더 크다는 뜻이다. 분포 전체의 꼬리 두께, 미래 확률, 평균회귀의 통계적 입증은 아니다. 겹치는 창, 표본 길이와 가격 정의 변경의 영향을 포함하며 유의확률은 제시하지 않는다.

## 공정 사양 비교의 해석

철강 그림은 FIN 기준, Vogl 총전력에서 수전해 전력을 뺀 잔여값, 그 잔여에 냉간 장입 차이를 더한 대안을 비교한다. 잔여값을 검증된 구매수소 공정의 총전력으로 승인하지 않는다. GCAM의 별도 가스·액체연료 및 스크랩·상류 경계를 누락한 비교와 미검증 50% 스크랩 전력 조합은 제외했다.

석화 사양은 Linde 열통합 구성과 Layritz 단순 치환 모델에 의존한다. 제시한 값들은 공정 완전성의 보편적인 상·하한이 아니다. 증기 공급, 압축기 및 부생 메탄 판매를 제외한 전력비 비교다. 그림에서 총비용 P50/P95라고 표시한 값도 이 명시된 에너지 항에만 한정된다.

FIN 기본 전력 변동성 0.2424는 비교용 값이며, 수소 0.25는 사전 가정이다. 가스·석탄·탄소 무충격 등 기존 기업 사례의 한계는 그대로다. 새 블록 재표집 모듈은 별도 연구 후보이고 FIN 입력을 교체하지 않았다.

재현: `scripts/audit_horizon_tails.py`. CSV: `horizon_tail_audit.csv`, `theta_price_exposure.csv`. 그림: `output/research_v2/figures/horizon_tails_and_theta_exposure.png`.
"""
    MD.write_text(md, encoding="utf-8")
    assert a.n_windows.min() == 132
    print(pivot.round(3).to_string())


if __name__ == "__main__":
    main()
