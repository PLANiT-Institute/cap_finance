"""Normalize collector-delivered data/raw/*.csv into pipeline-ready data/prepared/D*.csv.

Raw files are NEVER modified. Every transformation, unit conversion, and injected
assumption is logged to data/prepared/PREP_LOG.md — the audit trail for §8-3/§8-4
방어 (시설 단위 절대값은 구간·순서 정보로 취급).

Run: .venv/bin/python scripts/prepare_raw.py
"""

from __future__ import annotations

import pathlib
import re

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "prepared"
OUT.mkdir(parents=True, exist_ok=True)
LOG: list[str] = ["# 데이터 준비 로그 (scripts/prepare_raw.py 자동 생성)", ""]

USDKRW = 1350.0   # 2024-25 평균 근사 (D4 usdkrw 연평균 1100~1400 범위)
JPYKRW = 9.2
NM3_PER_KG_H2 = 11.13
MBTU_PER_T_LNG = 52.0


def log(msg):
    LOG.append(f"- {msg}")


def read(name):
    return pd.read_csv(RAW / f"{name}.csv", encoding="utf-8-sig")


# ---------------------------------------------------------------- D1a static
fs = read("facility_static")
fs["company_id"] = fs.company_id.replace({"MITSUI": "MCI"})
log("company_id MITSUI → MCI 통일 (엔진 지역 매핑 키)")

# BF capacity from inner volume: calibration point 광양1고로 6,000m3 = 5.48Mt/yr
vol = fs.unit_name.str.extract(r"([\d,]+)\s*m³")[0].str.replace(",", "").astype(float)
T_PER_M3 = 5_480_000 / 6_000
est = vol * T_PER_M3
fill = fs.capacity.isna() & est.notna()
fs.loc[fill, "capacity"] = est[fill]
fs.loc[fill, "capacity_unit"] = "t용선/yr (내용적 추정)"
log(f"고로 능력 결측 {int(fill.sum())}기: 내용적 x {T_PER_M3:,.0f} t/m³/yr로 추정 "
    "(광양1고로 6,000m³=5.48Mt 단일 캘리브레이션 — 시설 절대값은 구간 정보)")

# exclusions
drop_closed = fs.status.str.contains("폐쇄예정", na=False)
drop_future = fs.commissioning_year > 2026
drop_nocap = fs.capacity.isna()
for mask, why in [(drop_closed, "폐쇄예정"), (drop_future, "2027+ 신설(미가동)"), (drop_nocap, "능력 산정 불가")]:
    for fid in fs[mask & ~(drop_closed & drop_future)].facility_id:
        pass
excl = fs[drop_closed | drop_future | drop_nocap]
log(f"모형 제외 {len(excl)}기: " + ", ".join(f"{r.facility_id}({r.status})" for r in excl.itertuples()))
fs = fs[~(drop_closed | drop_future | drop_nocap)].copy()

# reinvest fields for facilities without cycle (EAF/FINEX new builds kept)
m = fs.next_reinvest_year.isna()
fs.loc[m, "reinvest_cycle_yr"] = 20
fs.loc[m, "next_reinvest_year"] = np.maximum(fs.loc[m, "commissioning_year"] + 20, 2030)
log(f"재투자 창 결측 {int(m.sum())}기(신설 EAF/FINEX): commissioning+20년으로 설정")
fs["last_reline_year"] = fs.last_reline_year.fillna(fs.commissioning_year)

# 감가상각용 기존 설비 재조달가 (천원/t능력) — 캠페인(개수 주기) 정액상각의 원가 기준.
# 고로 개수비 실적(포항4고로 ~1조원/5.1Mt ≈ 200천원/t) 앵커, 나머지는 상대 추정 주입.
INC_CAPEX = {"BF": 200.0, "FINEX": 300.0, "EAF": 250.0, "NCC": 150.0}
fs["incumbent_capex_unit"] = fs.unit_type.map(INC_CAPEX).fillna(150.0)
log("D1a incumbent_capex_unit 주입: " + ", ".join(f"{k} {v:.0f}천원/t" for k, v in INC_CAPEX.items())
    + " — 개수·대정비 재조달가 기준(포항4고로 개수비 앵커), 조기 전환 좌초비용=캠페인 정액상각 잔존가")

# 조기폐쇄 기회비용 = 상실 마진 (천원/t). 철강 = 포스코 별도 영업이익/톤 2019-25 평균(~70원/kg→70천원/t),
# 석화 = 에틸렌-납사 스프레드 2022-25 공표 연평균(~215 USD/t ×1350 ≈ 290천원/t, 변동비 일부 미차감 = 상한 성격).
MARGIN = {"steel": 70.0, "petchem": 290.0}
fs["margin_kthou_t"] = fs.sector.map(MARGIN)
log(f"D1a margin_kthou_t 주입: 철강 {MARGIN['steel']:.0f}·석화 {MARGIN['petchem']:.0f}천원/t "
    "(D4 마진 시계열 평균 — 조기폐쇄의 상실 마진, 석화는 스프레드라 상한 성격)")

d1a = fs[["facility_id", "company_id", "sector", "site", "unit_type", "unit_name",
          "capacity", "capacity_unit", "commissioning_year", "last_reline_year",
          "reinvest_cycle_yr", "next_reinvest_year", "incumbent_capex_unit", "margin_kthou_t", "status", "source_id"]]

# ---------------------------------------------------------------- D1b panel
fp = read("facility_panel")
# G1 사업소 실측 (EEGS 온대법 공표, T1) — 있으면 배분 분포에 쓴다
_se = RAW / "jp_site_emissions.csv"
SITE_EM = pd.read_csv(_se, encoding="utf-8-sig") if _se.exists() else None
if SITE_EM is not None:
    SITE_EM = SITE_EM[SITE_EM.fiscal_year == SITE_EM.fiscal_year.max()]
    log(f"사업소 실측 배출 로드: {len(SITE_EM)}행 "
        f"({', '.join(sorted(SITE_EM.company_id.unique()))}, EEGS_GHG_2023)")
# 루트별 물리 타당 배출원단위 대역 (tCO₂/t) — 새 데이터가 불가능한 값을 만들면 잡는다
EF_BAND = {"BF": (1.2, 3.0), "FINEX": (1.2, 3.0), "EAF": (0.1, 1.0), "NCC": (0.4, 2.0)}
ROUTE = {  # (EF tCO2/t, elec MWh/t, coal GJ/t, gas GJ/t) — 업계 표준 원단위, 문서화된 주입 가정
    "BF": (2.15, 0.08, 13.5, 0.4),
    "FINEX": (2.05, 0.10, 13.0, 0.4),
    "EAF": (0.45, 0.55, 0.0, 1.0),
    "NCC": (0.95, 0.35, 0.0, 8.0),
}
log("에너지 원단위 전면 결측 → 루트 표준값 주입: " +
    "; ".join(f"{k}: EF {v[0]}, 전력 {v[1]}MWh/t, 원료탄 {v[2]}GJ/t, 가스 {v[3]}GJ/t" for k, v in ROUTE.items()))

rows = []
years = [2022, 2023, 2024]
for company, grp in d1a.groupby("company_id"):
    tot = fp[fp.facility_id == {"POSCO": "POSCO_TOTAL", "NSC": "NSC_TOTAL",
                                "LOTTE": "LOTTE_TOTAL", "MCI": "MITSUI_TOTAL"}[company]]
    tot = tot[tot.year.isin(years)]
    # Scope 2 배분 가중치 = 시설 전력 소비 (구매전력 배출이므로 인과적으로 맞는 축).
    # 이전 판은 회사가 보고한 Scope 2를 전부 0으로 덮어썼다 — 원자료 36/37행에 값이
    # 있고 NSC는 11.9 MtCO₂(Scope 1의 19%)다. 수집한 것을 버리지 않는다.
    w_elec = grp.apply(lambda r: r.capacity * ROUTE[r.unit_type][1], axis=1)

    if company in ("POSCO", "NSC"):
        # steel: 회사 합계(생산·배출 실측)를 능력 x 루트가중으로 시설 배분.
        # G1: 사업소 실측이 있으면 **분포는 사업소 공시에서, 수준은 회사 공시에서** 가져온다.
        # EEGS 온대법 산정배출량은 에너지기원 CO₂(S1+S2)라 수준을 그대로 쓸 수 없다 —
        # 그래서 사업소 간 '몫'만 취하고 회사 Scope1 총량에 재척도한다. 배분 오차가
        # 회사 전체에서 사업소 내부로 줄어들고, 고로 1기 사이트는 사실상 실측이 된다.
        site_w, conflict = None, set()
        if SITE_EM is not None:
            se = SITE_EM[SITE_EM.company_id == company]
            if len(se):
                site_tot = se.groupby("site_key").emissions_tco2.sum()
                keys = grp.facility_id.str.split("_").str[1]
                have = site_tot.reindex(keys.unique()).dropna()
                if len(have) >= 2:                      # 최소 2개 사업소가 맞아야 의미
                    site_w = (have / have.sum()).to_dict()
                    # **물리 타당성 가드**: 사업소 공시와 설비 목록이 어긋나면 새 데이터가
                    # 불가능한 원단위를 만든다. 실제로 室蘭은 사업소 배출 0.68 Mt에 고로
                    # 2.75 Mt 능력이라 0.28 tCO₂/t가 나왔다 — 고로로는 불가능하다.
                    # 그런 시설은 **옛 규칙으로 되돌리고 충돌을 로그로 남긴다.**
                    prod_t0 = float(tot[tot.year == max(years)].production.iloc[0])
                    for x in grp.itertuples():
                        k = x.facility_id.split("_")[1]
                        sib_w = sum(y.capacity * ROUTE[y.unit_type][0]
                                    for y in grp.itertuples()
                                    if y.facility_id.split("_")[1] == k)
                        pr = prod_t0 * x.capacity / grp.capacity.sum()
                        ef_imp = (float(tot[tot.year == max(years)].emissions_s1.iloc[0])
                                  * site_w.get(k, 0) * (x.capacity * ROUTE[x.unit_type][0])
                                  / sib_w) / pr if pr else 0
                        lo, hi = EF_BAND.get(x.unit_type, (0.0, 9.9))
                        if not (lo <= ef_imp <= hi):
                            conflict.add(x.facility_id)
                            log(f"{company} **충돌**: {x.facility_id}({k}) 사업소 배출로 배분하면 "
                                f"원단위 {ef_imp:.2f} tCO₂/t — {x.unit_type} 타당 대역 "
                                f"[{lo}, {hi}] 밖. 사업소 공시와 설비 목록이 어긋난다 "
                                f"(능력 과대 또는 사업소 경계 차이). **이 시설은 옛 규칙 유지**")
                    log(f"{company}: 사업소 실측 배출로 **분포** 대체 "
                        f"({len(have)}개 사업소, EEGS_GHG_2023). 수준은 회사 Scope1 공시 유지 "
                        f"— 온대법 산정배출량은 S1+S2라 수준 직접 사용 불가")
        w_ef = grp.apply(lambda r: r.capacity * ROUTE[r.unit_type][0], axis=1)
        w_cap = grp.capacity
        # 충돌 시설은 옛 규칙 몫을 그대로 갖고, 나머지가 남은 몫을 사업소 분포로 나눈다
        fb_wsum = sum(x.capacity * ROUTE[x.unit_type][0]
                      for x in grp.itertuples() if x.facility_id in conflict) or 1.0
        fb_share = fb_wsum / w_ef.sum() if conflict else 0.0
        renorm = (1.0 - fb_share) / sum(
            v for k, v in (site_w or {}).items()
            if any(x.facility_id.split("_")[1] == k and x.facility_id not in conflict
                   for x in grp.itertuples())) if site_w else 1.0
        for y in years:
            t = tot[tot.year == y]
            prod_t = float(t.production.iloc[0]) if len(t) and pd.notna(t.production.iloc[0]) else np.nan
            s1_t = float(t.emissions_s1.iloc[0]) if len(t) else np.nan
            s2_t = float(t.emissions_s2.iloc[0]) if len(t) and pd.notna(t.emissions_s2.iloc[0]) else 0.0
            for fid, r in grp.set_index("facility_id").iterrows():
                prod = prod_t * r.capacity / w_cap.sum()
                if site_w and fid not in conflict:
                    # 사업소 몫 × 사업소 내부 능력×EF 몫
                    sk = fid.split("_")[1]
                    sib = grp[(grp.facility_id.str.split("_").str[1] == sk)
                              & (~grp.facility_id.isin(conflict))]
                    inner = (r.capacity * ROUTE[r.unit_type][0]) / sum(
                        x.capacity * ROUTE[x.unit_type][0] for x in sib.itertuples())
                    s1 = s1_t * renorm * site_w.get(sk, 0.0) * inner
                elif site_w:            # 사업소 데이터는 있으나 이 시설은 충돌 → 옛 몫 유지
                    s1 = s1_t * fb_share * (r.capacity * ROUTE[r.unit_type][0]) / fb_wsum
                else:                   # 사업소 데이터 자체가 없는 회사 → 옛 규칙 그대로
                    s1 = s1_t * (r.capacity * ROUTE[r.unit_type][0]) / w_ef.sum()
                s2 = s2_t * (r.capacity * ROUTE[r.unit_type][1]) / w_elec.sum()
                ef = ROUTE[r.unit_type]
                rows.append([fid, y, prod, s1, s2, prod * ef[2], prod * ef[3], prod * ef[1], "", "PREP_ALLOC"])
        s2_last = tot[tot.year == max(years)].emissions_s2
        log(f"{company}: 회사 실측 합계(생산·Scope1)를 능력x루트EF 가중으로 {len(grp)}기 배분 "
            f"(연도 {years}). Scope2는 전력 소비 가중 배분 "
            f"({float(s2_last.iloc[0]) / 1e6:.2f} MtCO₂ @{max(years)})")
    else:
        # petchem: 회사 합계에 비NCC 설비 다수 포함 → 상향식(능력 x 가동률 0.9 x 루트EF)
        util = 0.9
        cov_s1 = sum(r.capacity * util * ROUTE[r.unit_type][0] for _, r in grp.iterrows())
        t24 = tot[tot.year == tot.year.max()]
        # Scope1이 상향식이므로 Scope2도 같은 경계로 맞춘다: 회사 보고 Scope2에
        # Scope1 커버리지를 곱한 뒤 전력 소비로 배분. 회사 전력 소비 공시가 없어
        # 직접 배출강도를 쓸 수 없다 — 커버리지 정합이 차선의 정직한 선택.
        cover = (cov_s1 / float(t24.emissions_s1.iloc[0])) if len(t24) else 1.0
        for y in years:
            t = tot[tot.year == y]
            s2_t = float(t.emissions_s2.iloc[0]) if len(t) and pd.notna(t.emissions_s2.iloc[0]) else 0.0
            for fid, r in grp.set_index("facility_id").iterrows():
                prod = r.capacity * util
                ef = ROUTE[r.unit_type]
                s2 = s2_t * cover * (r.capacity * ef[1]) / w_elec.sum()
                rows.append([fid, y, prod, prod * ef[0], s2, prod * ef[2], prod * ef[3],
                             prod * ef[1], "", "PREP_BOTTOMUP"])
        if len(t24):
            log(f"{company}: 상향식 추정 (능력x0.9xEF). 회사 보고 Scope1 대비 커버리지 "
                f"{cover:.0%} — 비분해로 설비는 모형 밖. Scope2는 같은 커버리지로 축소 후 "
                f"전력 가중 배분")
d1b = pd.DataFrame(rows, columns=["facility_id", "year", "production", "emissions_s1", "emissions_s2",
                                  "energy_coal", "energy_gas", "energy_elec", "energy_naphtha", "source_id"])

# 배분 항등식 — 철강은 회사 공시 총량에 재척도하므로 시설 합계가 총량과 같아야 한다.
# 이 한 줄이 없어서 배분 버그(POSCO 배출 전량 0)가 파이프라인 20분을 지나 E5까지 갔다.
_chk = d1b.merge(d1a[["facility_id", "company_id"]], on="facility_id")
for _co in ("POSCO", "NSC"):
    for _y in years:
        _got = _chk[(_chk.company_id == _co) & (_chk.year == _y)].emissions_s1.sum()
        _row = fp[(fp.facility_id == {"POSCO": "POSCO_TOTAL", "NSC": "NSC_TOTAL"}[_co])
                  & (fp.year == _y)]
        if not len(_row):
            continue
        _want = float(_row.emissions_s1.iloc[0])
        if abs(_got - _want) > max(1.0, _want * 1e-6):
            raise SystemExit(f"배분 항등식 위반: {_co} {_y} 시설합 {_got:,.0f} != 공시 {_want:,.0f}")
log("배분 항등식 확인: 철강 2사 전 연도에서 시설 합계 = 회사 공시 Scope1 총량")

# ---------------------------------------------------------------- D2a budget
d2a = read("scenario_budget")
# 단조성 보정: 1.5°C 예산이 어느 해든 2°C보다 느슨할 수 없다. 수집본은 2030-35 구간에서
# 역전(B20 < NZ15) — NZ15 := min(NZ15, B20)로 보정. 경로 형태 재추정은 2차 수집 몫.
piv = d2a.pivot_table(index=["region", "sector", "year"], columns="scenario", values="carbon_budget")
if {"NZ15", "B20"} <= set(piv.columns):
    fixed_n = int((piv.NZ15 > piv.B20).sum())
    piv["NZ15"] = piv[["NZ15", "B20"]].min(axis=1)
    fix_map = piv.NZ15.to_dict()
    m = d2a.scenario == "NZ15"
    d2a.loc[m, "carbon_budget"] = d2a[m].apply(
        lambda r: fix_map[(r.region, r.sector, r.year)], axis=1)
    log(f"D2a 단조성 보정: NZ15 > B20 역전 {fixed_n}개 연도-지역-섹터에서 NZ15 := min(NZ15, B20). "
        "초반 급감형 재보간은 2차 수집(F항) 대상")
d2a.to_csv(OUT / "D2a_scenario_budget.csv", index=False)

# ---------------------------------------------------------------- D2b prices
sp = read("scenario_prices")
out_rows = []
for r in sp.itertuples():
    v, u = r.value, str(r.unit)
    var = r.variable
    if var == "carbon_price":
        var, v, u = "co2_price", v * USDKRW, "KRW/tCO2"
    elif var == "elec_price" and "원/kWh" in u:
        v, u = v * 1000, "KRW/MWh"
    elif var == "elec_price" and "円/kWh" in u:
        v, u = v * 1000 * JPYKRW, "KRW/MWh"
    elif var == "coal_price":
        v, u = v * USDKRW, "KRW/t"
    elif var == "gas_price":
        v, u = v * MBTU_PER_T_LNG * USDKRW, "KRW/t"
    elif var == "h2_price" and "JPY/Nm3" in u:
        v, u = v * NM3_PER_KG_H2 * JPYKRW, "KRW/kg"
    elif var == "h2_price":
        u = "KRW/kg"
    out_rows.append([r.scenario, r.region, var, r.year, v, u, r.source_id])
d2b = pd.DataFrame(out_rows, columns=["scenario", "region", "variable", "year", "value", "unit", "source_id"])
log(f"D2b 단위 정규화: carbon_price→co2_price(x{USDKRW:.0f}), 원·円/kWh→KRW/MWh, "
    f"USD/t·MBtu→KRW/t (LNG {MBTU_PER_T_LNG}MBtu/t), JPY/Nm3→KRW/kg (환율 USD {USDKRW:.0f}, JPY {JPYKRW})")

# v2.1 재생 조달가(re_price): 전환 기술의 전력은 재생 PPA 계약가 수준으로 조달.
# 앵커 = 실거래 보도(한국 태양광 170원대 중반, 일본 물리 PPA 총비용 ~21.5 JPY/kWh),
# 경로 = 실질 flat 가정 (계약가 성격 — 시나리오 무관). 시나리오별 전망 수령 시 교체.
RE_ANCHOR = {"Korea": 175_000.0, "Japan": 198_000.0}  # KRW/MWh
re_rows = []
for scen in ["NZ15", "B20"]:
    for region, v in RE_ANCHOR.items():
        for year in range(2025, 2051):
            re_rows.append([scen, region, "re_price", year, v, "KRW/MWh", "KR_PPA_2026/REI_JP_PPA_2025"])
d2b = pd.concat([d2b, pd.DataFrame(re_rows, columns=d2b.columns)], ignore_index=True)
log(f"D2b re_price 생성: 한국 {RE_ANCHOR['Korea']:,.0f}·일본 {RE_ANCHOR['Japan']:,.0f} KRW/MWh 실질 flat "
    "(재생 PPA 실거래 앵커) — 전환 기술 전력은 이 가격, 기존 조업은 계통(elec_price)")

# Korea NZ15 carbon: BOK-FSS 경로는 섀도가격(한계감축비용, 출처 노트 스스로 '실거래 전망 아님')
# — 현금흐름 탄소비용으로 쓰면 일본(IEA 시장가 앵커)과 의미가 어긋나고 기준선 비용이 폭증.
# IEA NZE 선진국 앵커로 교체해 지역 간 의미 통일. 섀도 경로는 원본에 보존.
NZE_KR = {2025: 7.0, 2030: 140.0, 2035: 180.0, 2040: 205.0, 2045: 227.0, 2050: 250.0}
m = (d2b.scenario == "NZ15") & (d2b.region == "Korea") & (d2b.variable == "co2_price")
d2b.loc[m, "value"] = d2b.loc[m, "year"].map(NZE_KR) * USDKRW
d2b.loc[m, "source_id"] = "IEA_GECM_DOC_2025 (NZE adv., PREP 대체)"
log("한국 NZ15 co2_price: BOK-FSS 섀도가격(2050 USD1,700) → IEA NZE 선진국 시장가 앵커"
    f"(2030 140 / 2050 250 USD)로 대체 — 탄소비용의 현금흐름 의미 통일. 섀도 경로는 raw에 보존")

# ---------------------------------------------------------------- D3 tech
to = read("tech_options")
to = to[~to.tech_id.str.endswith("_alt")].copy()
log("D3: *_alt 행(출처 대안 추정) 본 실행에서 제외 — 민감도 전용")
to = to[~to.tech_id.str.contains("ccus")].copy()
log("D3: CCUS 옵션 제외 (사용자 결정 2026-08-06 — 저장 용량·비용 데이터 확보 전까지 수단에서 제외)")
FILL = {  # (col, tech, value, why)
    ("capex_unit", "steel_ccus"): (550.0, "IEAGHG 고로 CCUS 리트로핏 ~400-500USD/t 환산 추정"),
    ("capex_unit", "steel_eff"): (120.0, "BAT 리트로핏 저CAPEX 추정"),
    ("capex_unit", "petchem_h2fuel"): (150.0, "버너 교체 경량 리트로핏 추정"),
    ("capex_unit", "petchem_eff"): (60.0, "운전최적화 저CAPEX 추정"),
    ("opex_var", "petchem_bio"): (2600.0, "바이오나프타 프리미엄 ~600USD/t x 3.2t나프타/t에틸렌 환산"),
    ("h2_intensity", "petchem_h2fuel"): (100.0, "NCC 연료 20GJ/t 중 60% 수소 대체 가정 (LHV 120MJ/kg)"),
}
for (col, tech), (val, why) in FILL.items():
    m = to.tech_id == tech
    if to.loc[m, col].isna().any():
        to.loc[m, col] = val
        log(f"D3 결측 주입: {tech}.{col} = {val} — {why}")
# v2.1 정합 보정: 수소를 외부 조달로 전환했으므로 전해조 전력을 원단위에서 제거한다.
# Vogl 2018의 3.48 MWh/tLS는 수전해(51kg x ~51kWh/kg ≈ 2.6MWh)를 포함한 총 SEC이므로,
# 외부 조달 시 그대로 두면 수소 대금과 전해조 전력을 이중 계상한다. 잔여 = 샤프트+EAF+부대.
H2_EXTERNAL_ELEC = {"steel_h2dri": 0.85, "steel_hyrex": 0.85}
for tid, v in H2_EXTERNAL_ELEC.items():
    m = to.tech_id == tid
    if m.any():
        old = float(to.loc[m, "elec_intensity"].iloc[0])
        to.loc[m, "elec_intensity"] = v
        log(f"D3 {tid} elec_intensity {old:.2f} → {v:.2f} MWh/t — 수소 외부조달(v2.1)에 맞춰 "
            f"전해조 전력({51*51/1000:.1f}MWh/t 상당) 제거, 이중계상 방지 (VOGL_2018 총 SEC 분해)")

to["opex_fixed"] = to.opex_fixed.fillna(0.0)
to["opex_var"] = to.opex_var.fillna(0.0)
log("D3: opex 잔여 결측 0 처리 (증분 비용 기준 — 공통 유지비 상쇄 가정)")
to["applies_to_unit"] = np.select(
    [to.sector.eq("steel"), to.sector.eq("petchem")], ["BF", "NCC"], default=to.applies_to_unit)
# 시설-기술 매칭 (산업 특성): BF-BOF의 '전환'은 수소환원제철만 가능. BF→EAF 전면 전환은
# 스크랩 수급·고급강 품질 제약으로 비현실 — EAF는 신설 경로이지 기존 고로 전환 옵션이 아님.
# CCUS·효율개선은 리트로핏(설비 유지)이라 BF에 계속 적용.
to.loc[to.tech_id == "steel_eaf", "applies_to_unit"] = "NONE"
to.loc[to.tech_id == "steel_hyrex", "applies_to_unit"] = "FINEX"
log("D3 applies_to_unit 정규화: 석화→NCC, 철강 BF→수소환원+부분감축 리트로핏(수소취입·스크랩·HBI·효율), "
    "FINEX→HyREX(2035). steel_eaf는 신설 경로라 제거. 2차 수집 수단 반영: 감축률 기준으로 당사 시설 EF에 재스케일, "
    "부분 적용 상한(스크랩 15%p·HBI 30%·바이오 10%·열펌프 15%·수소취입 20%·하이브리드 40%)은 EF에 blended")
RETROFIT = ["steel_ccus", "steel_eff", "steel_h2inj", "steel_scrap", "steel_hbi",
            "petchem_h2fuel", "petchem_ccus", "petchem_eff", "petchem_bio",
            "petchem_ecracker_hybrid", "petchem_hp_whr"]
to["retrofit"] = to.tech_id.isin(RETROFIT).astype(int)
log("D3 retrofit 구분: " + ", ".join(RETROFIT) + " — 기존 공정 에너지 유지 + 기술 원단위 가산 "
    "(하이브리드 전기로의 연료 40% 감축분은 미반영 = 보수적). 대체형(H2DRI·HyREX·e-cracker 완전)만 공정 에너지 교체")

# ---------------------------------------------------------------- D4 prices
d4 = read("price_history")
m = d4.series_id == "electrolyzer_capex"
d4.loc[m, "value"] = d4.loc[m, "value"] * USDKRW
d4.loc[m, "unit"] = "KRW/kW"
log(f"D4 electrolyzer_capex USD→KRW x{USDKRW:.0f}. 관측 2개(2022 상승 구간)뿐 → "
    "감소율은 캘리브레이션 사전값(연 5%) 사용, 앵커는 최종 관측값")
d4.to_csv(OUT / "D4_price_history.csv", index=False)

# ---------------------------------------------------------------- D5 policy
ps = read("policy_support")
ps2 = ps.rename(columns=str)



def _instrument(r) -> str:
    """Machine key for the collected instrument. Flattening every row to 'other'
    (previous behaviour) destroyed the one distinction that matters: K-ETS 4기의
    유상할당 비율은 발전부문 50%와 발전외(철강·석화) 15%로 갈리고, 우리 4사는
    전부 발전외다. 그 구분을 잃으면 배출권 비용이 3배 이상 어긋난다."""
    label, kind = str(r.instrument), str(r.param_type)
    if "유상할당" in kind:
        return "auction_share_power" if "발전부문" in label else "auction_share"
    if "상한" in kind:
        return "price_cap"
    if "하한" in kind:
        return "price_floor"
    return "other"


ps2["instrument"] = [_instrument(r) for r in ps2.itertuples()]
d5 = ps2[["support_scenario", "instrument", "tech_id", "param_type", "value", "unit",
          "valid_from", "valid_to", "source_id"]]
log("D5: 수집된 수단은 K-ETS 유상할당·GX-ETS 프라이스칼라 — CAPEX 보조·CCfD 아님 → "
    "subsidy/ccfd 경로에는 미적용(확정된 직접 지원 부재 = net=gross, 그 자체가 발견). "
    "다만 유상할당 비율은 탄소비용의 직접 입력이므로 instrument를 "
    "auction_share(발전외=철강·석화) / auction_share_power(발전부문) / price_cap / price_floor로 "
    "분류해 엔진이 발전외 행만 읽게 한다 (plancost.auction_share)")

# ---------------------------------------------------------------- D6 financials
d6 = read("company_financials")
d6["company_id"] = d6.company_id.replace({"MITSUI": "MCI"})
d6.to_csv(OUT / "D6_company_financials.csv", index=False)

# ---------------------------------------------------------------- D7 disclosed
dp = read("disclosed_plan")
dp["company_id"] = dp.company_id.replace({"MITSUI": "MCI"})
log("D7: EAF 신설 커밋(NSC_YAW_EAF1·NSC_HIR_EAF2·POSCO_GWY_EAF1)은 기존 시설의 '전환'이 아니라 "
    "신설 경로 — BF→EAF 전환 불허 규칙에 따라 모형 커밋으로 미해석(경고로 드롭). "
    "NSC 공시 좌표는 KIM_BF2 수소환원 실증 커밋으로 측정")
dp.to_csv(OUT / "D7_disclosed_plan.csv", index=False)

d1a.to_csv(OUT / "D1a_facility_static.csv", index=False)
d1b.to_csv(OUT / "D1b_facility_panel.csv", index=False)
d2b.to_csv(OUT / "D2b_scenario_prices.csv", index=False)
to.to_csv(OUT / "D3_tech_options.csv", index=False)

# ---------------------------------------------------------------- D3b tech bands (G2, D10)
# 문헌 [low, high]. 값이 아니라 **범위**를 받는 것이 G2의 완료 기준이다 (D9 발견 1) —
# 등급 T2·T3·T4의 257행이 전부 점 추정이었던 것은 수집 규약의 결함이었다.
_tb = RAW / "tech_bands.csv"
if _tb.exists():
    tb = pd.read_csv(_tb, encoding="utf-8-sig")
    tb = tb[tb.tech_id.isin(to.tech_id)]          # 본 실행에서 빠진 기술(*_alt·ccus)은 제외
    for r in tb.itertuples():
        v = float(to.loc[to.tech_id == r.tech_id, r.field].iloc[0])
        flag = "" if r.value_low <= v <= r.value_high else "  ** 현행 값이 밴드 밖 **"
        log(f"D3b 밴드 {r.tech_id}.{r.field}: [{r.value_low:g}, {r.value_high:g}] "
            f"vs 현행 {v:g} ({r.evidence_tier}, {r.source_id}){flag}")
        # 밴드 밖이어도 값을 고치지 않는다. 경계·표본이 다를 수 있고, 조용한 교체가
        # 이 저장소의 반복 실패 방식이다. 사실만 남기고 판단은 문서(G2)에서 한다.
    tb.to_csv(OUT / "D3b_tech_bands.csv", index=False)
else:
    log("D3b: tech_bands.csv 없음 — 밴드 없이 진행")
d5.to_csv(OUT / "D5_policy_support.csv", index=False)

# 공개 출처 등록부 동기화. data/raw는 gitignore이므로 이걸 안 하면 저장소를 클론한
# 사람은 대부분 수치의 출처를 추적할 수 없다 (실제로 50건 뒤처져 있었다).
# 자료 자체가 아니라 인용 메타데이터만 옮긴다 — data/manifests/README 정책.
_sr = RAW / "source_register.csv"
if _sr.exists():
    import csv as _csv
    _rows = list(_csv.DictReader(_sr.open(encoding="utf-8-sig")))
    _dst = ROOT / "data" / "manifests" / "source_register.csv"
    with _dst.open("w", encoding="utf-8-sig", newline="") as _f:
        _w = _csv.DictWriter(_f, fieldnames=list(_rows[0]), quoting=_csv.QUOTE_ALL)
        _w.writeheader(); _w.writerows(_rows)
    log(f"출처 등록부 공개 사본 동기화: {len(_rows)}건 -> data/manifests/source_register.csv")

(OUT / "PREP_LOG.md").write_text("\n".join(LOG) + "\n")
print("\n".join(LOG))
print(f"\nprepared {len(d1a)} facilities, {len(d1b)} panel rows -> {OUT}")
