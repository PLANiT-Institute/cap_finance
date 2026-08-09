"""Build the HTML results report from out/ (professional edition).

Reads e2/e4/e5 outputs fresh each run — every number on the page is computed.
Run: .venv/bin/python scripts/build_report.py <output_html_path>
"""

from __future__ import annotations

import json
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.e2_milp import _prep_company  # noqa: E402
from cap.plancost import stranded_cost_k  # noqa: E402
from cap.schemas import load_input  # noqa: E402

OUT_HTML = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "render" / "report.html"
cfg = C.load(data_dir="data/prepared")
e5 = C.out_dir(cfg, "e5")
e2d = C.out_dir(cfg, "e2")

# ---------------- load ----------------
fr = pd.read_csv(e5 / "frontier_points.csv")
fr = fr[fr.support == "none"]
idx = pd.read_csv(e2d / "plan_index.csv")
metrics = pd.read_csv(e5 / "metrics_company.csv")
metrics = metrics[metrics.support == "none"]
afford = pd.read_csv(e5 / "affordability.csv")
afford = afford[(afford.support == "none") & (afford.scenario == "NZ15")]
gap = pd.read_csv(e5 / "gap.csv")
gap = gap[gap.support == "none"].drop_duplicates(["company_id", "scenario"])
dec = pd.read_csv(e5 / "variance_decomp.csv")
dec = dec[dec.support == "none"]
ep = pd.read_csv(e5 / "emissions_pathway.csv")
cdist = pd.read_csv(e5 / "cost_distribution.csv")
lam = pd.read_csv(e5 / "lambda_tangency.csv")
wedge = pd.read_csv(e5 / "policy_wedge.csv")
conv = pd.read_csv(C.out_dir(cfg, "e4") / "convergence.csv")

fac, d3, _cal = _prep_company(cfg, C.data_dir(cfg))
d3i = d3.set_index("tech_id")

TECH_KR = {"steel_h2dri": "수소환원제철", "steel_eff": "효율개선(BAT)", "steel_eaf": "전기로",
           "retire": "조기폐쇄", "steel_h2inj": "수소취입", "steel_scrap": "스크랩 증대",
           "steel_hbi": "HBI 장입", "steel_hyrex": "HyREX(FINEX)",
           "petchem_ecracker_hybrid": "하이브리드 전기로", "petchem_hp_whr": "열펌프·폐열",
           "petchem_ecracker": "전기가열 분해로", "petchem_h2fuel": "수소 연료전환",
           "petchem_bio": "바이오나프타", "petchem_eff": "운전최적화"}

# ---------------- per-plan composition (for tooltips & labels) ----------------
plan_comp = {}
for pid in fr.base_plan_id.unique():
    p = pd.read_csv(e2d / "plans" / f"plan_{pid}.csv")
    a = p.dropna(subset=["tech_id"])
    n_h2 = int(a.tech_id.isin(["steel_h2dri", "petchem_h2fuel"]).sum())
    techs = sorted(set(TECH_KR.get(t, t) for t in a.tech_id))
    plan_comp[pid] = dict(n=len(a), n_h2=n_h2, techs=techs,
                          yrs=f"{int(a.adopt_year.min())}–{int(a.adopt_year.max())}" if len(a) else "—")

# ---------------- facility detail (NZ15 cost-min vs disclosed) ----------------
fac_rows = []
for co in sorted(fr.company_id.unique()):
    sub = fr[(fr.company_id == co) & (fr.scenario == "NZ15")]
    picks = {}
    nd = sub[~sub.is_disclosed & sub.budget_ok]
    if len(nd):
        picks["cost_min"] = nd.loc[nd.p50.idxmin()].base_plan_id
    dd = sub[sub.is_disclosed]
    if len(dd):
        picks["disclosed"] = dd.base_plan_id.iloc[0]
    cf = fac[fac.company_id == co]
    adopt = {}
    for label, pid in picks.items():
        p = pd.read_csv(e2d / "plans" / f"plan_{pid}.csv").dropna(subset=["tech_id"])
        adopt[label] = {r.facility_id: r for r in p.itertuples()}
    for fid, r in cf.iterrows():
        base_e = r.ef_inc * r.production / 1e6
        row = dict(company_id=co, facility=fid, unit=r.unit_name, type=r.unit_type,
                   cap_mt=round(r.capacity / 1e6, 2), reinvest=int(r.next_reinvest_year),
                   base_emis_mt=round(base_e, 2))
        for label in ["cost_min", "disclosed"]:
            a = adopt.get(label, {}).get(fid)
            if a is None:
                row[label] = None
            elif a.tech_id == "retire":
                str_ = stranded_cost_k(r, int(a.adopt_year), cfg) * 1e-6
                row[label] = dict(tech="조기폐쇄", adopt=int(a.adopt_year), op=int(a.op_year),
                                  capex_bn=0.0, stranded_bn=round(str_, 0), new_emis_mt=0.0,
                                  cut_pct=100, retrofit=False)
            else:
                tk = d3i.loc[a.tech_id]
                retro = bool(int(tk.get("retrofit", 0) or 0))
                new_e = tk.emission_factor * r.production / 1e6
                capex = tk.capex_unit * r.capacity * 1e-6
                str_ = stranded_cost_k(r, int(a.adopt_year), cfg) * 1e-6
                row[label] = dict(tech=TECH_KR.get(a.tech_id, a.tech_id), adopt=int(a.adopt_year),
                                  op=int(a.op_year), capex_bn=round(capex, 0),
                                  stranded_bn=round(str_, 0),
                                  new_emis_mt=round(new_e, 2),
                                  cut_pct=round(100 * (1 - new_e / base_e)) if base_e > 0 else 0,
                                  retrofit=retro)
        fac_rows.append(row)

# ---------------- decomp: market-exposed vs contracted plan per company ----------------
dec_pairs = []
for (co, scen), g in fr[fr.on_frontier & ~fr.is_disclosed].groupby(["company_id", "scenario"]):
    lo = g.loc[g.tcar.idxmin()]  # most contracted / low risk
    hi = g.loc[g.tcar.idxmax()]  # most market-exposed
    for label, r in [("contracted", lo), ("market", hi)]:
        d = dec[dec.plan_id == r.plan_id]
        e = {row.factor: row.variance_share for row in d.itertuples()}
        tot = sum(e.values()) or 1
        dec_pairs.append(dict(company_id=co, scenario=scen, kind=label, plan_id=r.plan_id,
                              tcar=round(r.tcar, 1), ppa=round(r.ppa_share or 0, 2), epc=int(r.epc),
                              elec=round(e.get("elec", 0) / tot, 3), h2=round(e.get("h2", 0) / tot, 3),
                              capex=round(e.get("capex", 0) / tot, 3)))

D = dict(
    frontier=fr[["company_id", "scenario", "plan_id", "base_plan_id", "p50", "tcar", "is_disclosed",
                 "on_frontier", "ppa_share", "epc", "ccfd"]].round(2).to_dict("records"),
    plan_comp=plan_comp,
    metrics=metrics.round(1).to_dict("records"),
    gap=gap.round(1).to_dict("records"),
    dec_pairs=dec_pairs,
    pathway=ep.round(0).to_dict("records"),
    cost_dist=cdist.round(2).to_dict("records"),
    lam=lam.to_dict("records"),
    wedge=wedge.to_dict("records"),
    facilities=fac_rows,
    # to_json (not to_dict) so missing financials arrive as null, not NaN —
    # a float column cannot hold None in pandas, and NaN==null is false in JS
    afford=json.loads(afford.round(2).to_json(orient="records")),
    convergence_max_pct=round(float(conv[["p50_reldiff", "tcar_reldiff"]].max().max()) * 100, 2),
    n_plans=int(len(idx)),
)
mNZ = metrics[metrics.scenario == "NZ15"].set_index("company_id")
epNZ = ep[(ep.scenario == "NZ15") & (ep.plan == "cost_min")]
cut = (1 - epNZ[epNZ.year == 2050].groupby("company_id").emissions_tco2.sum()
       / epNZ[epNZ.year == 2025].groupby("company_id").emissions_tco2.sum())
gNZ = gap[gap.scenario == "NZ15"]
D["kpi"] = dict(tot_capex_jo=round(mNZ.capex_total_bnkrw.sum() / 1000, 1),
                cut_2050_pct=round(100 * float(cut.mean())),
                tot_gap_jo=round(gNZ.gap_cost_bnkrw.sum() / 1000, 1),
                tot_gap_risk_jo=round(gNZ.gap_risk_bnkrw.sum() / 1000, 1))

HTML = r"""<title>CAP 진단 보고서 — 전환비용·TCaR·효율경계</title>
<style>
:root{
  --surface:#FBFBF9; --panel:#FFFFFF; --panel2:#F4F4F0; --ink:#191C24; --ink2:#565B66; --ink3:#8B909C;
  --line:#E4E4DE; --line2:#EEEEE8; --accent:#2a78d6;
  --s-elec:#2a78d6; --s-h2:#1baf7a; --s-capex:#eda100; --s-disc:#e34948;
  --s-nz:#2a78d6; --s-b20:#1baf7a; --warn-bg:#FBF3E2; --warn-line:#E5C878; --bad-bg:#FCEDEA; --bad-ink:#B22C1B;
}
@media (prefers-color-scheme: dark){
  :root:where(:not([data-theme="light"])){
    --surface:#15171C; --panel:#1C1F26; --panel2:#22252D; --ink:#EDEEF0; --ink2:#A8ADB8; --ink3:#747A87;
    --line:#2E323B; --line2:#262A32; --accent:#3987e5;
    --s-elec:#3987e5; --s-h2:#199e70; --s-capex:#c98500; --s-disc:#e66767;
    --s-nz:#3987e5; --s-b20:#199e70; --warn-bg:#2A2517; --warn-line:#6B5A2A; --bad-bg:#2E1A17; --bad-ink:#F08C7A;
  }
}
:root[data-theme="dark"]{
  --surface:#15171C; --panel:#1C1F26; --panel2:#22252D; --ink:#EDEEF0; --ink2:#A8ADB8; --ink3:#747A87;
  --line:#2E323B; --line2:#262A32; --accent:#3987e5;
  --s-elec:#3987e5; --s-h2:#199e70; --s-capex:#c98500; --s-disc:#e66767;
  --s-nz:#3987e5; --s-b20:#199e70; --warn-bg:#2A2517; --warn-line:#6B5A2A; --bad-bg:#2E1A17; --bad-ink:#F08C7A;
}
:root[data-theme="light"]{
  --surface:#FBFBF9; --panel:#FFFFFF; --panel2:#F4F4F0; --ink:#191C24; --ink2:#565B66; --ink3:#8B909C;
  --line:#E4E4DE; --line2:#EEEEE8; --accent:#2a78d6;
  --s-elec:#2a78d6; --s-h2:#1baf7a; --s-capex:#eda100; --s-disc:#e34948;
  --s-nz:#2a78d6; --s-b20:#1baf7a; --warn-bg:#FBF3E2; --warn-line:#E5C878; --bad-bg:#FCEDEA; --bad-ink:#B22C1B;
}
*{box-sizing:border-box}
body{margin:0;background:var(--surface);color:var(--ink);
  font-family:"Apple SD Gothic Neo",Pretendard,"Noto Sans KR","Malgun Gothic",system-ui,sans-serif;
  line-height:1.62;font-size:15px;}
.wrap{max-width:1140px;margin:0 auto;padding:52px 30px 90px}
.eyebrow{font-size:11.5px;letter-spacing:.15em;color:var(--accent);font-weight:700;text-transform:uppercase}
h1{font-size:31px;line-height:1.22;margin:8px 0 6px;font-weight:800;letter-spacing:-.015em;text-wrap:balance}
.sub{color:var(--ink2);max-width:70ch;margin:0;font-size:14.5px}
h2{font-size:20px;margin:0 0 4px;font-weight:760;letter-spacing:-.008em}
.secno{color:var(--ink3);font-weight:600;margin-right:8px}
section{margin-top:64px}
.secnote{color:var(--ink2);font-size:13.5px;margin:0 0 20px;max-width:80ch}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
.badge{font-size:12px;padding:3px 11px;border-radius:999px;border:1px solid var(--line);color:var(--ink2)}
.badge.warn{background:var(--warn-bg);border-color:var(--warn-line);color:var(--ink)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:13.5px}
th{font-size:11.5px;color:var(--ink2);font-weight:650;text-align:right;padding:9px 10px;border-bottom:1.5px solid var(--line);white-space:nowrap;letter-spacing:.01em}
th:first-child,td:first-child{text-align:left}
td{padding:7.5px 10px;border-bottom:1px solid var(--line2);text-align:right;white-space:nowrap}
tr:last-child td{border-bottom:none}
td.warn{background:var(--warn-bg);font-weight:640}
td.bad{background:var(--bad-bg);color:var(--bad-ink);font-weight:660}
.tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel);padding:8px 12px}
.co{font-weight:700}
.scen{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:7px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:16px}
.grid4{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 16px 10px}
.panel h3{margin:0 0 1px;font-size:14.5px;font-weight:720}
.panel .cap{font-size:12px;color:var(--ink3);margin:0 0 8px}
svg{display:block;width:100%;height:auto}
.axis{font-size:10px;fill:var(--ink3)}
.axislab{font-size:10.5px;fill:var(--ink2);font-weight:600}
.gridline{stroke:var(--line2);stroke-width:1}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;color:var(--ink2);margin:12px 0 16px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:10px;height:10px;border-radius:2px;display:inline-block}
.sw.line{height:3px;border-radius:1.5px;width:16px}
.sw.dash{height:0;border-top:2px dashed var(--ink3);width:16px;border-radius:0}
.star{color:var(--s-disc);font-size:14px}
.callout{background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:12px;padding:16px 20px;font-size:13.5px}
.confid{border:1px dashed var(--s-disc);border-radius:12px;padding:4px 14px 2px;margin-top:8px}
.confid .tag{font-size:11px;color:var(--s-disc);font-weight:700;letter-spacing:.08em}
ul.tight{margin:8px 0 0;padding-left:18px}
ul.tight li{margin:4px 0;font-size:13.5px;color:var(--ink2)}
ul.tight li b{color:var(--ink)}
.tip{position:fixed;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:9px;
  padding:8px 11px;font-size:12px;box-shadow:0 6px 18px rgba(0,0,0,.14);opacity:0;transition:opacity .1s;z-index:9;
  font-variant-numeric:tabular-nums;max-width:300px;white-space:normal;line-height:1.5}
.footer{margin-top:72px;padding-top:20px;border-top:1px solid var(--line);font-size:12.5px;color:var(--ink3)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin-top:22px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.kpi .l{font-size:12px;color:var(--ink2);font-weight:600}
.kpi .v{font-size:26px;font-weight:800;font-variant-numeric:tabular-nums;margin-top:3px;letter-spacing:-.01em}
.kpi .d{font-size:12px;color:var(--ink3);margin-top:3px}
.chip{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:999px;font-weight:650;vertical-align:1px}
.chip.retro{background:color-mix(in srgb,var(--s-capex) 18%,transparent);color:var(--s-capex)}
.chip.repl{background:color-mix(in srgb,var(--s-elec) 15%,transparent);color:var(--s-elec)}
.cotab{display:flex;gap:6px;margin:0 0 14px;flex-wrap:wrap}
.cotab button{font:inherit;font-size:13px;font-weight:650;padding:6px 14px;border-radius:999px;border:1px solid var(--line);
  background:var(--panel);color:var(--ink2);cursor:pointer}
.cotab button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.cotab button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.muted{color:var(--ink3)}
@media (max-width:640px){ .wrap{padding:34px 16px 60px} h1{font-size:24px} .grid2{grid-template-columns:1fr} }
</style>
<div class="wrap">
<header>
  <div class="eyebrow">Capital Allocation Pathway · 진단 보고서</div>
  <h1>기대값에서 싸 보이는 전환 계획은, 꼬리에서 비싸다</h1>
  <p class="sub">POSCO · Nippon Steel · LOTTE Chemical · Mitsui Chemicals — 시설 단위 최적화로 생성한
  투자계획 <span id="nplans"></span>개를 몬테카를로 2만 경로로 재평가. 지출을 아끼는 계획은 비용을 줄인 것이 아니라 에너지 가격 위험을 산 것 —
  기업별 효율 경계에서 공시 계획이 <b>같은 지출로 지고 있는 불필요한 P90 부담</b>을 측정. 시설별 전환 스케줄 포함. 수집 데이터 상당수가 잠정 추정(EST_v0)으로
  <b>절대값은 구간, 구조·순서가 유효 정보.</b></p>
  <div class="badges">
    <span class="badge">NZ15 (1.5°C) · B20 (2°C)</span>
    <span class="badge" id="convbadge"></span>
    <span class="badge">할인율 실질 5% · KRW 2025</span>
    <span class="badge">CCUS 제외 · BF 전환=수소환원 · 감가상각 좌초비용</span>
    <span class="badge warn">데이터 등급: 잠정</span>
  </div>
  <div class="kpis" id="kpis"></div>
</header>

<section><h2><span class="secno">1</span>기업 종합 — 지표 ①–⑤</h2>
<p class="secnote">② 기대 전환비용은 자원비용 기준(CAPEX+운영+에너지 증분, 탄소비용 분리) NPV의 P50.
③ TCaR = P90−P50, 전력·수소·설비비 가격 변동에서만 발생. ④ = NZ15−B20. ⑤ = 경로별 계획 전환 가치(하한).</p>
<div class="tblwrap"><table id="mtable"></table></div></section>

<section><h2><span class="secno">2</span>조달 부담 — 비용을 물을 수 있는가, 감당할 수 있는가</h2>
<p class="secnote">전환비용(②)은 <b>얼마 드는가</b>를, 이 절은 <b>그 돈이 어디서 나오는가</b>를 묻는다. 기준이익 = 최근 3개 회계연도
EBITDA 평균(경기 평활 — 석화는 저점 구간이라 단년으로 보면 결론이 뒤집힌다). 피크배수 = 피크연도 CAPEX ÷ 기준 EBITDA.
사후 순차입배수는 <b>전액 차입 가정의 상한</b>이며 조달 구성 예측이 아니다. CAPEX는 기술별 공사기간(D3 build_years)에
균등 분산 — 이것을 채택연도 일시 계상하면 피크가 최대 공사기간 배수만큼 과대해진다.</p>
<div class="tblwrap"><table id="atable"></table></div>
<div id="abars" style="margin-top:14px"></div></section>

<section><h2><span class="secno">3</span>배출 경로 — 전환은 계단으로 온다</h2>
<p class="secnote">시설 단위 결정이라 감축이 연속이 아니라 <b>가동 연도의 계단</b>으로 발생. 파랑 = 비용최소 계획,
빨강 = 공시 계획, 점선 = 기업 탄소예산, 회색 = 무전환 기준선. 예산 아래로 못 내려간 구간은 잔여 미달분
(소프트 페널티 300천원/tCO₂ 이상으로 계상).</p>
<div class="legend">
  <span><span class="sw line" style="background:var(--s-nz)"></span>비용최소 계획</span>
  <span><span class="sw line" style="background:var(--s-disc)"></span>공시 계획</span>
  <span><span class="sw dash"></span>탄소예산</span>
  <span><span class="sw" style="background:var(--ink3);opacity:.4"></span>무전환 기준선</span>
</div>
<div class="grid4" id="ppanels"></div></section>

<section><h2><span class="secno">3</span>전환비용 분포 — 하나의 숫자가 아니라 분포다</h2>
<p class="secnote">NZ15 비용최소 계획의 자원비용 NPV 분포 (몬테카를로 2만 경로). P50 = 기대 전환비용,
P90−P50 = TCaR. 빨간 외곽선 = 공시 계획의 분포 — 오른쪽·넓을수록 비싸고 흔들리는 계획.</p>
<div class="legend">
  <span><span class="sw" style="background:var(--s-nz);opacity:.75"></span>비용최소 계획</span>
  <span><span class="sw line" style="background:var(--s-disc)"></span>공시 계획 (외곽선)</span>
</div>
<div class="grid4" id="hpanels"></div></section>

<section><h2><span class="secno">4</span>시설별 전환 — 무엇을 언제 교체하는가</h2>
<p class="secnote">NZ15 비용최소 계획 기준. 타임라인의 ◇ = 재투자 창(개수·대정비 도래), 막대 = 착수→가동(건설 기간),
색 = 기술. 좌초비용 = 조기 전환 시 상각 못 한 기존 설비(개수 캠페인) 잔존 장부가. 공시 계획과 다른 시설은 표에 병기.</p>
<div class="cotab" id="cotab" role="tablist"></div>
<div class="confid"><span class="tag">CONFIDENTIAL — 시설 단위 산출 · 설계서 §8-2 비공개 원칙 · 외부 공유 금지</span>
<div id="gantt" style="margin:12px 0 4px"></div>
<div class="tblwrap" style="border:none;padding:0;margin:10px 0 8px"><table id="ftable"></table></div></div>
</section>

<section><h2><span class="secno">5</span>효율 경계 — 지출 부족은 에너지 리스크 포지션이다</h2>
<p class="secnote">설계서 (기대비용, TCaR) 평면 — <b>가로 = 기대 전환비용, 세로 = TCaR</b>. 각 점 = 탄소예산을
만족하는 계획 (호버: 기술 구성·계약). 경계 구간의 숫자 = <b>안정의 가격</b> (TCaR 1조원 축소당 기대비용).
<span class="star">★</span> = 공시 계획: 왼쪽 점선 = 동일 위험 절감액, 아래 점선 = 동일 비용 위험축소.
경계가 짧은 기업은 현 기술 DB에서 선택지가 적다는 뜻(2차 수집으로 확충 예정).</p>
<div class="legend">
  <span><span class="sw line" style="background:var(--s-nz)"></span>NZ15</span>
  <span><span class="sw line" style="background:var(--s-b20)"></span>B20</span>
  <span><span class="sw" style="background:var(--ink3);opacity:.45"></span>지배당한 계획</span>
  <span><span class="star">★</span> 공시 계획 (점선 = frontier 투영)</span>
</div>
<div class="grid2" id="fpanels"></div>
<div class="tblwrap" style="margin-top:16px"><table id="gtable"></table></div>
<p class="secnote" style="margin-top:10px" id="gapnote"></p>
<h2 style="margin-top:34px;font-size:16.5px">위험회피도(λ)별 최적 계획 — 그림 5</h2>
<p class="secnote">λ = 기대비용 1조원과 TCaR 1조원의 교환비율(투자자 외생 선호). λ가 커질수록(위험회피적일수록)
접점이 계약형으로 이동 — 모형은 이 선택을 대신하지 않고 좌표만 제공.</p>
<div class="tblwrap"><table id="ltable"></table></div>
<h2 style="margin-top:34px;font-size:16.5px">정책강도 민감도 — 두 경계의 간격 (그림 6)</h2>
<p class="secnote"><b>같은 계획</b>(NZ15 경계의 스케줄·계약 고정)을 1.5°C와 2.0°C 가격·예산 아래에서 각각 재평가.
점선으로 이어진 두 점의 간격 = 확률적 가격위험이 아니라 <b>정책 강도에 대한 경로 민감도</b>(지표 ④의 계획별 버전).
계약화(오른쪽 아래로 이동)할수록 세로 간격이 좁아짐 — 계약은 가격 위험과 정책 위험을 함께 줄인다.</p>
<div class="legend">
  <span><span class="sw line" style="background:var(--s-nz)"></span>1.5°C 정합 평가</span>
  <span><span class="sw line" style="background:var(--s-b20)"></span>2.0°C 정합 평가</span>
  <span><span class="sw dash"></span>같은 계획 연결 = wedge</span>
</div>
<div class="grid2" id="wpanels"></div></section>

<section><h2><span class="secno">6</span>TCaR 요인 분해 — 계약화는 크기와 구성을 함께 바꾼다</h2>
<p class="secnote">비용 채널 기준: <b>수소 = 조달비 변동 전체</b>(원천 무관), <b>전력 = 직접 전력요금</b>,
<b>설비비 = CAPEX</b>. 기업마다 두 막대 — 시장노출형(경계 우단)과 계약형(경계 좌단) 계획. 막대 길이 = TCaR 크기(조원),
색 구성 = 요인 비중. 설계서 그림 3의 논리: 계약화는 시장가격 요인을 제거하고 잔여 위험만 남긴다.</p>
<div class="legend">
  <span><span class="sw" style="background:var(--s-elec)"></span>전력 (직접 요금)</span>
  <span><span class="sw" style="background:var(--s-h2)"></span>수소 (조달비 전체)</span>
  <span><span class="sw" style="background:var(--s-capex)"></span>설비비 (CAPEX)</span>
</div>
<div id="dbars"></div></section>

<section><h2><span class="secno">7</span>읽기 전 필수 — 데이터 품질과 주입 가정</h2>
<div class="callout"><b>신뢰 등급: 구조·순서는 유효, 절대값은 구간.</b>
<ul class="tight" id="qlist"></ul></div></section>

<section><h2><span class="secno">8</span>방법과 다음 단계</h2>
<ul class="tight">
<li><b>체인:</b> 섹터 제약 추출(안분 없음) → 시설 MILP + ε-constraint (재투자 창·감가상각 내생, 시설-기술 매칭)
→ 상관 몬테카를로 → 경로별 재평가 → 지표·경계·gap.</li>
<li><b>v2.1 예정(2차 수집 후):</b> 수소 외부조달 독립 요인화, 전력 이원화(계통/재생 PPA), 기술 수단 확충(부분감축 포함)
— 경계의 점 개수와 계약화 축이 이 수집에 달려 있음.</li>
<li><b>한계:</b> GBM 장기 분산 과대 가능, EPC의 CAPEX 위험 전액 제거, ⑤ 하한 근사, EAF 신설 경로 모형 밖.</li>
</ul></section>

<div class="footer">CAP v2 파이프라인 (REDESIGN_SPEC.md) · 데이터 컷오프 2026-08-06 · 본 문서는 내부 진단용 —
시설 단위 표는 비공개 부속(설계서 §8-2), 외부 공개 시 §3 제거 후 배포</div>
</div>
<div class="tip" id="tip"></div>
<script>
const D=__DATA__;
// section numbers follow document order — inserting a section never renumbers by hand
document.querySelectorAll(".secno").forEach((e,i)=>e.textContent=i+1);
const fmt=(v,d=1)=>v==null||isNaN(v)?"—":Number(v).toLocaleString("ko-KR",{maximumFractionDigits:d});
const jo=(v,d=1)=>fmt(v/1000,d);
const CO=["POSCO","NSC","LOTTE","MCI"];
const CONAME={POSCO:"POSCO",NSC:"Nippon Steel",LOTTE:"LOTTE Chemical",MCI:"Mitsui Chemicals"};
const tip=document.getElementById("tip");
document.addEventListener("mousemove",e=>{const t=e.target.closest("[data-tip]");
  if(t){tip.innerHTML=t.getAttribute("data-tip");tip.style.opacity=1;
  tip.style.left=Math.min(e.clientX+14,innerWidth-320)+"px";tip.style.top=(e.clientY+12)+"px";}
  else tip.style.opacity=0;});
const planTip=(p)=>{const c=D.plan_comp[p.base_plan_id||p.plan_id]||{};
  return `<b>${p.plan_id}</b> · ${p.scenario}${p.is_disclosed?" · 공시":""}<br>`+
  `전환 ${c.n||0}기 (${(c.techs||[]).join(", ")||"없음"}) · ${c.yrs||""}<br>`+
  `PPA ${Math.round((p.ppa_share||0)*100)}% · EPC ${p.epc?"O":"X"} · CCfD ${p.ccfd?"O":"X"}<br>`+
  `P50 ${jo(p.p50)}조 · TCaR ${jo(p.tcar)}조`;};

document.getElementById("nplans").textContent=D.n_plans;
document.getElementById("convbadge").textContent=`N=20,000 · 수렴 ${D.convergence_max_pct}%`;
document.getElementById("kpis").innerHTML=`
<div class="kpi"><div class="l">4사 정합 CAPEX 소요 ① (NZ15)</div><div class="v">${D.kpi.tot_capex_jo}조원</div><div class="d">비용최소 계획 합, 2025–2050</div></div>
<div class="kpi"><div class="l">2050 배출 감축률 (NZ15 평균)</div><div class="v">${D.kpi.cut_2050_pct}%</div><div class="d">비용최소 계획, 2025 대비</div></div>
<div class="kpi"><div class="l">준비 부재의 가격 (NZ15)</div><div class="v">+${D.kpi.tot_gap_risk_jo}조원</div><div class="d">공시 계획이 같은 지출로 지고 있는 불필요한 P90 부담 (측정 기업 합)</div></div>
<div class="kpi"><div class="l">TCaR 지배 요인</div><div class="v" id="kpi4v">—</div><div class="d" id="kpi4d"></div></div>`;

// KPI4 from dec_pairs market kind NZ15
(()=>{const m=D.dec_pairs.filter(d=>d.kind==="market"&&d.scenario==="NZ15");
 if(!m.length)return; const avg=k=>m.reduce((s,d)=>s+d[k],0)/m.length;
 const arr=[["전력",avg("elec")],["수소",avg("h2")],["설비비",avg("capex")]].sort((a,b)=>b[1]-a[1]);
 document.getElementById("kpi4v").textContent=arr[0][0];
 document.getElementById("kpi4d").textContent=`시장노출형 계획 평균 ${(100*arr[0][1]).toFixed(0)}% · 2위 ${arr[1][0]} ${(100*arr[1][1]).toFixed(0)}%`;})();

// 1. metrics
let rows=`<tr><th>기업</th><th>시나리오</th><th>① CAPEX (조원)</th><th>① 피크</th><th>② P50 (조원)</th><th>② 천원/tCO₂</th><th>③ TCaR (조원)</th><th>④ 정책노출 (조원)</th><th>⑤ 유연성 (조원)</th></tr>`;
for(const co of CO) for(const sc of ["NZ15","B20"]){
  const m=D.metrics.find(x=>x.company_id===co&&x.scenario===sc); if(!m) continue;
  rows+=`<tr><td class="co">${sc==="NZ15"?CONAME[co]:""}</td>
  <td style="text-align:left"><span class="scen" style="background:var(--s-${sc==="NZ15"?"nz":"b20"})"></span>${sc}</td>
  <td>${jo(m.capex_total_bnkrw)}</td><td>${m.capex_peak_year??"—"}</td><td>${jo(m.p50_bnkrw)}</td>
  <td>${fmt(m.cost_per_tco2_thkrw,0)}</td><td>${jo(m.tcar_bnkrw)}</td>
  <td>${sc==="NZ15"?jo(m.policy_exposure_bnkrw):"—"}</td><td>${jo(m.flex_value_bnkrw)}</td></tr>`;
}
document.getElementById("mtable").innerHTML=rows;

// 2. affordability (NZ15, support=none)
(()=>{
 const A=D.afford||[]; if(!A.length) return;
 const x=v=>v==null||isNaN(v)?"—":fmt(v,1)+"×";
 let r=`<tr><th>기업</th><th>총 CAPEX (조원)</th><th>피크연도</th><th>피크 CAPEX (조원)</th>
 <th>기준 EBITDA (조원)</th><th>피크배수</th><th>총 CAPEX/EBITDA</th><th>순차입/EBITDA 현재→사후</th><th>판정</th></tr>`;
 for(const co of CO){
  const a=A.find(x=>x.company_id===co); if(!a) continue;
  const risk=a.ebitda_ref_bnkrw==null||a.ebitda_ref_bnkrw<0?"bad":a.capex_peak_to_ebitda>1?"warn":"";
  const nd=a.netdebt_to_ebitda_now==null||isNaN(a.netdebt_to_ebitda_now)?"공시 미확보"
    :`${fmt(a.netdebt_to_ebitda_now,1)} → ${fmt(a.netdebt_to_ebitda_post,1)}`;
  r+=`<tr><td class="co">${CONAME[co]}</td><td>${jo(a.capex_total_bnkrw)}</td><td>${a.capex_peak_year??"—"}</td>
  <td>${jo(a.capex_peak_bnkrw)}</td>
  <td data-tip="기준연도 ${a.ebitda_years||"—"}">${jo(a.ebitda_ref_bnkrw)}</td>
  <td class="${risk}">${x(a.capex_peak_to_ebitda)}</td>
  <td>${x(a.capex_total_to_ebitda)}</td>
  <td>${nd}</td><td style="text-align:left">${a.funding_verdict}</td></tr>`;
 }
 document.getElementById("atable").innerHTML=r;

 // peak-year CAPEX against one year of earnings — the bar the company must clear
 const vals=A.filter(a=>a.capex_peak_to_ebitda!=null).map(a=>a.capex_peak_to_ebitda);
 const vmax=Math.max(2,...vals)*1.12, W=760, H=26, L=118;
 let s=`<svg viewBox="0 0 ${W} ${A.length*(H+12)+26}" style="width:100%;height:auto">`;
 A.forEach((a,i)=>{
   const y=i*(H+12), v=a.capex_peak_to_ebitda;
   s+=`<text class="axis" x="${L-8}" y="${y+H*0.68}" text-anchor="end">${CONAME[a.company_id]}</text>`;
   if(v==null){
     s+=`<text class="axis" x="${L+6}" y="${y+H*0.68}" fill="var(--s-disc)">EBITDA 음수 — 자체 조달 불가</text>`;
   }else{
     const w=(W-L-70)*Math.min(v,vmax)/vmax;
     s+=`<rect x="${L}" y="${y+4}" width="${w}" height="${H-8}" rx="2"
       fill="${v>1?"var(--s-disc)":"var(--s-nz)"}" opacity="${v>1?.9:.75}"/>
       <text class="axis" x="${L+w+8}" y="${y+H*0.68}">${v.toFixed(1)}×</text>`;
   }
 });
 const x1=L+(W-L-70)/vmax;   // the 1.0× line = one year of earnings
 s+=`<line x1="${x1}" y1="0" x2="${x1}" y2="${A.length*(H+12)}" stroke="var(--ink3)" stroke-dasharray="3 3"/>
 <text class="axis" x="${x1+4}" y="${A.length*(H+12)+16}">연간 EBITDA 1배</text></svg>`;
 document.getElementById("abars").innerHTML=s;
})();

// 2. emissions pathway
const pp=document.getElementById("ppanels");
for(const co of CO){
  const g=D.pathway.filter(p=>p.company_id===co&&p.scenario==="NZ15");
  if(!g.length) continue;
  const years=[...new Set(g.map(p=>p.year))].sort((a,b)=>a-b);
  const W=310,H=210,P={l:42,r:10,t:12,b:26};
  const vmax=Math.max(...g.map(p=>Math.max(p.emissions_tco2,p.budget_tco2)))*1.06/1e6;
  const X=y=>P.l+(y-years[0])/(years.at(-1)-years[0])*(W-P.l-P.r);
  const Y=v=>P.t+(1-v/vmax)*(H-P.t-P.b);
  const step=pts=>{let d=`M${X(pts[0][0])},${Y(pts[0][1])}`;
    for(let i=1;i<pts.length;i++)d+=`H${X(pts[i][0])}V${Y(pts[i][1])}`;return d+`H${X(years.at(-1))}`;};
  let s="";
  for(let i=0;i<=3;i++){const gy=P.t+i*(H-P.t-P.b)/3;
    s+=`<line class="gridline" x1="${P.l}" y1="${gy}" x2="${W-P.r}" y2="${gy}"/>
        <text class="axis" x="${P.l-5}" y="${gy+3}" text-anchor="end">${fmt(vmax*(3-i)/3,0)}</text>`;}
  for(const y of years.filter(y=>y%5===0)) s+=`<text class="axis" x="${X(y)}" y="${H-8}" text-anchor="middle">${y}</text>`;
  const ser=p=>g.filter(r=>r.plan===p).sort((a,b)=>a.year-b.year).map(r=>[r.year,r.emissions_tco2/1e6]);
  s+=`<path d="${step(g.filter(p=>p.plan==="cost_min").sort((a,b)=>a.year-b.year).map(r=>[r.year,r.budget_tco2/1e6]))}"
      fill="none" stroke="var(--ink2)" stroke-width="1.5" stroke-dasharray="5 4"/>`;
  for(const [pl,col,op,wd] of [["baseline","var(--ink3)",.4,1.5],["disclosed","var(--s-disc)",1,2],["cost_min","var(--s-nz)",1,2.5]]){
    const pts=ser(pl); if(pts.length) s+=`<path d="${step(pts)}" fill="none" stroke="${col}" opacity="${op}" stroke-width="${wd}"/>`;
  }
  pp.insertAdjacentHTML("beforeend",`<div class="panel"><h3>${CONAME[co]}</h3>
    <p class="cap">Scope 1 (MtCO₂/yr) · NZ15</p><svg viewBox="0 0 ${W} ${H}">${s}</svg></div>`);
}

// 3. facility table with company tabs
const cotab=document.getElementById("cotab");
function renderFac(co){
  renderGantt(co);
  document.querySelectorAll(".cotab button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.co===co));
  const rows=D.facilities.filter(f=>f.company_id===co);
  let h=`<tr><th>설비</th><th>유형</th><th>능력 (Mt/yr)</th><th>재투자 창</th><th>현 배출 (Mt)</th>
  <th>전환 기술</th><th>착수→가동</th><th>CAPEX (조원)</th><th>좌초 (조원)</th><th>전환후 (Mt)</th><th>감축</th></tr>`;
  let tot={cap:0,base:0,capex:0,str:0,after:0};
  for(const f of rows){
    const a=f.cost_min, d=f.disclosed;
    tot.cap+=f.cap_mt; tot.base+=f.base_emis_mt;
    tot.capex+=a?a.capex_bn:0; tot.str+=a?a.stranded_bn:0; tot.after+=a?a.new_emis_mt:f.base_emis_mt;
    const discNote = d && (!a || d.tech!==a.tech || d.adopt!==a.adopt)
      ? `<div style="font-size:11px;color:var(--s-disc)">공시: ${d.tech} ${d.adopt}</div>` : "";
    h+=`<tr><td><b>${f.unit}</b><div class="muted" style="font-size:11px">${f.facility}</div></td>
    <td style="text-align:left">${f.type}</td><td>${fmt(f.cap_mt,2)}</td><td>${f.reinvest}</td><td>${fmt(f.base_emis_mt,2)}</td>
    <td style="text-align:left">${a?`${a.tech} <span class="chip ${a.retrofit?"retro":"repl"}">${a.retrofit?"리트로핏":"대체"}</span>`:`<span class="muted">현행 유지</span>`}${discNote}</td>
    <td>${a?`${a.adopt}→${a.op}`:"—"}</td><td>${a?jo(a.capex_bn):"—"}</td>
    <td>${a?(a.stranded_bn>0?jo(a.stranded_bn):"0"):"—"}</td>
    <td>${a?fmt(a.new_emis_mt,2):fmt(f.base_emis_mt,2)}</td>
    <td>${a?`<b>−${a.cut_pct}%</b>`:"—"}</td></tr>`;
  }
  h+=`<tr style="background:var(--panel2)"><td class="co">합계</td><td></td><td>${fmt(tot.cap,1)}</td><td></td>
  <td>${fmt(tot.base,1)}</td><td></td><td></td><td class="co">${jo(tot.capex)}</td><td>${jo(tot.str)}</td>
  <td>${fmt(tot.after,1)}</td><td class="co">−${Math.round(100*(1-tot.after/tot.base))}%</td></tr>`;
  document.getElementById("ftable").innerHTML=h;
}
CO.forEach((co,i)=>{const b=document.createElement("button");
  b.textContent=CONAME[co]; b.dataset.co=co; b.setAttribute("role","tab");
  b.onclick=()=>renderFac(co); cotab.appendChild(b);});
// initial tab render moved to end (TECHCOL TDZ)

// 5. frontier — 가로=기대비용(P50), 세로=TCaR (설계서 평면)
const fp=document.getElementById("fpanels");
for(const co of CO){
  const pts=D.frontier.filter(p=>p.company_id===co);
  if(!pts.length) continue;
  const W=520,H=330,P={l:56,r:16,t:16,b:42};
  const cmin=Math.min(...pts.map(p=>p.p50),0), cmax=Math.max(...pts.map(p=>p.p50))*1.1+1e-9;
  const tmax=Math.max(...pts.map(p=>p.tcar))*1.12+1e-9;
  const X=v=>P.l+((v-cmin)/(cmax-cmin))*(W-P.l-P.r);
  const Y=v=>P.t+(1-v/tmax)*(H-P.t-P.b);
  let s="";
  for(let i=0;i<=4;i++){const gy=P.t+i*(H-P.t-P.b)/4;
    s+=`<line class="gridline" x1="${P.l}" y1="${gy}" x2="${W-P.r}" y2="${gy}"/>
        <text class="axis" x="${P.l-6}" y="${gy+3}" text-anchor="end">${jo(tmax*(4-i)/4)}</text>`;}
  for(let i=0;i<=4;i++){const xv=cmin+(cmax-cmin)*i/4;
    s+=`<text class="axis" x="${X(xv)}" y="${H-24}" text-anchor="middle">${jo(xv)}</text>`;}
  s+=`<text class="axislab" x="${(P.l+W-P.r)/2}" y="${H-6}" text-anchor="middle">기대 전환비용 P50 (조원) →</text>`;
  s+=`<text class="axislab" transform="rotate(-90 12 ${(P.t+H-P.b)/2})" x="12" y="${(P.t+H-P.b)/2}" text-anchor="middle">TCaR — 비용의 흔들림 (조원)</text>`;
  for(const sc of ["NZ15","B20"]){
    const col=sc==="NZ15"?"var(--s-nz)":"var(--s-b20)";
    const f=pts.filter(p=>p.scenario===sc&&p.on_frontier&&!p.is_disclosed).sort((a,b)=>a.p50-b.p50);
    if(f.length>1){
      s+=`<polyline points="${f.map(p=>X(p.p50)+","+Y(p.tcar)).join(" ")}" fill="none" stroke="${col}" stroke-width="2.2"/>`;
      for(let i=0;i<f.length-1;i++){
        const a=f[i],b=f[i+1],dr=(b.p50-a.p50)/((a.tcar-b.tcar)||1e-9);
        const mx=(X(a.p50)+X(b.p50))/2, my=(Y(a.tcar)+Y(b.tcar))/2;
        s+=`<g data-tip="안정의 가격 (${sc})<br>TCaR 1조원 축소당 기대비용 +${fmt(dr,2)}조원">
        <circle cx="${mx}" cy="${my}" r="9" fill="transparent"/>
        <text x="${mx+6}" y="${my-6}" font-size="9.5" fill="${col}" font-weight="600">${fmt(dr,1)}</text></g>`;
      }
    }
    for(const p of pts.filter(p=>p.scenario===sc&&!p.is_disclosed))
      s+=`<circle cx="${X(p.p50)}" cy="${Y(p.tcar)}" r="${p.on_frontier?5:4}" fill="${p.on_frontier?col:"var(--ink3)"}"
        opacity="${p.on_frontier?1:.38}" stroke="var(--panel)" stroke-width="1.5" data-tip="${planTip(p).replace(/"/g,"&quot;")}"/>`;
    for(const p of pts.filter(p=>p.scenario===sc&&p.is_disclosed)){
      const g=D.gap.find(x=>x.company_id===co&&x.scenario===sc);
      if(g&&g.gap_cost_bnkrw>0){ // 동일 위험 절감: 수평 왼쪽
        const fx=X(p.p50-g.gap_cost_bnkrw);
        s+=`<line x1="${X(p.p50)}" y1="${Y(p.tcar)}" x2="${fx}" y2="${Y(p.tcar)}" stroke="var(--s-disc)"
          stroke-dasharray="3 3" stroke-width="1.2" opacity=".85"/>
        <text x="${(X(p.p50)+fx)/2}" y="${Y(p.tcar)-5}" text-anchor="middle" font-size="9.5" fill="var(--s-disc)">−${jo(g.gap_cost_bnkrw)}조</text>`;}
      if(g&&g.gap_risk_bnkrw>0){ // 동일 비용 위험축소: 수직 아래
        const fy=Y(p.tcar-g.gap_risk_bnkrw);
        s+=`<line x1="${X(p.p50)}" y1="${Y(p.tcar)}" x2="${X(p.p50)}" y2="${fy}" stroke="var(--s-disc)"
          stroke-dasharray="3 3" stroke-width="1.2" opacity=".85"/>`;}
      s+=`<text x="${X(p.p50)}" y="${Y(p.tcar)+5.5}" text-anchor="middle" font-size="17" fill="var(--s-disc)"
        data-tip="${planTip(p).replace(/"/g,"&quot;")}">★</text>`;
    }
  }
  fp.insertAdjacentHTML("beforeend",`<div class="panel"><h3>${CONAME[co]}</h3>
    <p class="cap">경계 구간 숫자 = 안정의 가격 (TCaR 1조 축소당 기대비용, 조원)</p>
    <svg viewBox="0 0 ${W} ${H}">${s}</svg></div>`);
}

// 3. cost distribution histograms
const hp=document.getElementById("hpanels");
for(const co of CO){
  const g=D.cost_dist.filter(d=>d.company_id===co&&d.scenario==="NZ15");
  if(!g.length) continue;
  const cm=g.filter(d=>d.plan_kind==="cost_min"), dc=g.filter(d=>d.plan_kind==="disclosed");
  const all=[...cm,...dc];
  const W=310,H=190,P={l:12,r:12,t:14,b:28};
  const lo=Math.min(...all.map(d=>d.bin_lo)), hi=Math.max(...all.map(d=>d.bin_hi));
  const nmax=Math.max(...all.map(d=>d.count));
  const X=v=>P.l+(v-lo)/(hi-lo)*(W-P.l-P.r), Y=v=>P.t+(1-v/nmax)*(H-P.t-P.b);
  let s="";
  for(const d of cm){
    s+=`<rect x="${X(d.bin_lo)}" y="${Y(d.count)}" width="${Math.max(0.8,X(d.bin_hi)-X(d.bin_lo)-0.6)}"
     height="${H-P.b-Y(d.count)}" fill="var(--s-nz)" opacity=".72"/>`;
  }
  if(dc.length){
    const pts=dc.map(d=>`${X(d.bin_lo)},${Y(d.count)} ${X(d.bin_hi)},${Y(d.count)}`).join(" ");
    s+=`<polyline points="${pts}" fill="none" stroke="var(--s-disc)" stroke-width="1.6" opacity=".95"/>`;
  }
  if(cm.length){
    const p50=cm[0].p50, p90=cm[0].p90;
    for(const [v,lab,colv] of [[p50,"P50","var(--ink2)"],[p90,"P90","var(--s-disc)"]]){
      s+=`<line x1="${X(v)}" y1="${P.t}" x2="${X(v)}" y2="${H-P.b}" stroke="${colv}" stroke-dasharray="4 3" stroke-width="1.2"/>
      <text class="axis" x="${X(v)}" y="${P.t-3}" text-anchor="middle">${lab} ${jo(v)}</text>`;
    }
    s+=`<text class="axis" x="${(X(p50)+X(p90))/2}" y="${H-P.b+12}" text-anchor="middle" fill="var(--s-disc)">TCaR ${jo(cm[0].p90-cm[0].p50)}조</text>`;
  }
  s+=`<text class="axis" x="${P.l}" y="${H-4}">${jo(lo)}</text><text class="axis" x="${W-P.r}" y="${H-4}" text-anchor="end">${jo(hi)}조원</text>`;
  hp.insertAdjacentHTML("beforeend",`<div class="panel"><h3>${CONAME[co]}</h3>
   <p class="cap">자원비용 NPV (조원) · NZ15</p><svg viewBox="0 0 ${W} ${H}">${s}</svg></div>`);
}

// 4b. facility replacement gantt
const TECHCOL={"조기폐쇄":"var(--s-disc)","수소취입":"var(--s-h2)","HBI 장입":"var(--s-capex)","스크랩 증대":"var(--s-capex)","HyREX(FINEX)":"var(--s-h2)","하이브리드 전기로":"var(--s-elec)","열펌프·폐열":"var(--s-capex)","수소환원제철":"var(--s-h2)","효율개선(BAT)":"var(--s-capex)","전기가열 분해로":"var(--s-elec)",
 "수소 연료전환":"var(--s-h2)","바이오나프타":"var(--s-h2)","운전최적화":"var(--s-capex)","전기로":"var(--s-elec)"};
function renderGantt(co){
  const rows=D.facilities.filter(f=>f.company_id===co);
  const y0=2025,y1=2050,W=980,RH=26,P={l:190,r:20,t:24,b:8};
  const H=P.t+rows.length*RH+P.b;
  const X=y=>P.l+(y-y0)/(y1-y0)*(W-P.l-P.r);
  let s="";
  for(const y of [2025,2030,2035,2040,2045,2050])
    s+=`<line x1="${X(y)}" y1="${P.t-4}" x2="${X(y)}" y2="${H-P.b}" class="gridline"/>
        <text class="axis" x="${X(y)}" y="${P.t-8}" text-anchor="middle">${y}</text>`;
  rows.forEach((f,i)=>{
    const cy=P.t+i*RH+RH/2;
    s+=`<text x="0" y="${cy+3.5}" font-size="11.5" fill="var(--ink)" font-weight="600">${f.unit.length>14?f.unit.slice(0,14)+"…":f.unit}</text>`;
    s+=`<line x1="${X(y0)}" y1="${cy}" x2="${X(y1)}" y2="${cy}" stroke="var(--line)" stroke-width="1"/>`;
    if(f.reinvest>=y0&&f.reinvest<=y1)
      s+=`<path d="M${X(f.reinvest)},${cy-5} l5,5 l-5,5 l-5,-5 z" fill="none" stroke="var(--ink3)" stroke-width="1.3"
        data-tip="${f.unit} 재투자 창 ${f.reinvest}"/>`;
    const a=f.cost_min;
    if(a){
      const col=TECHCOL[a.tech]||"var(--s-elec)";
      s+=`<rect x="${X(a.adopt)}" y="${cy-6}" width="${Math.max(4,X(a.op)-X(a.adopt))}" height="12" rx="3" fill="${col}"
        data-tip="<b>${f.unit}</b><br>${a.tech} (${a.retrofit?"리트로핏":"대체"})<br>착수 ${a.adopt} → 가동 ${a.op}<br>CAPEX ${jo(a.capex_bn)}조 · 좌초 ${jo(a.stranded_bn)}조<br>배출 ${f.base_emis_mt}→${a.new_emis_mt}Mt (−${a.cut_pct}%)"/>`;
      s+=`<text x="${X(a.op)+5}" y="${cy+3.5}" font-size="10" fill="var(--ink2)">${a.tech}</text>`;
    } else {
      s+=`<text x="${X(y1)-2}" y="${cy+3.5}" font-size="10" fill="var(--ink3)" text-anchor="end">현행 유지</text>`;
    }
  });
  document.getElementById("gantt").innerHTML=
   `<svg viewBox="0 0 ${W} ${H}" style="min-width:720px">${s}</svg>`;
  document.getElementById("gantt").style.overflowX="auto";
}
// gap table
const maxgr=Math.max(...D.gap.map(g=>g.gap_risk_bnkrw||0),1);
let gr=`<tr><th>기업</th><th>시나리오</th><th>공시 P50 (조원)</th><th>공시 TCaR (조원)</th><th>불필요 P90 부담 (조원)</th><th></th><th>동일 위험 절감액 (조원)</th></tr>`;
for(const g of D.gap){
  gr+=`<tr><td class="co">${CONAME[g.company_id]}</td>
  <td style="text-align:left"><span class="scen" style="background:var(--s-${g.scenario==="NZ15"?"nz":"b20"})"></span>${g.scenario}</td>
  <td>${jo(g.p50)}</td><td>${jo(g.tcar)}</td><td><b>+${jo(g.gap_risk_bnkrw)}</b></td>
  <td style="width:130px;text-align:left"><span style="height:12px;border-radius:3px;background:var(--s-disc);display:inline-block;vertical-align:middle;width:${Math.max(2,110*(g.gap_risk_bnkrw||0)/maxgr)}px"></span></td>
  <td>${jo(g.gap_cost_bnkrw)}</td></tr>`;
}
document.getElementById("gtable").innerHTML=gr;
document.getElementById("gapnote").innerHTML=`<b>불필요 P90 부담</b> = 동일 지출의 경계 계획으로 갈아탔을 때
사라지는 TCaR — 에너지 가격이 불리한 상위 10% 상황에서 공시 계획이 추가로 무는 금액. 지출을 아낀 게 아니라
그 금액만큼의 에너지 리스크 포지션을 보유 중이라는 뜻이며, PPA·EPC 체결로 닫을 수 있는 종류의 공백.
표에 없는 기업 = 공시 좌표 미식별(시설 특정 커밋 부재, 설계서 §8-4 해상도 문제) — "공시가 검증 가능한
형태가 아니다"라는 진단 그 자체.`;

// 5. decomp — market vs contracted, width = TCaR
const db=document.getElementById("dbars");
const maxT=Math.max(...D.dec_pairs.map(d=>d.tcar),1);
let dh="";
for(const co of CO){
  for(const sc of ["NZ15"]){
    const pair=D.dec_pairs.filter(d=>d.company_id===co&&d.scenario===sc);
    if(!pair.length) continue;
    dh+=`<div style="margin:14px 0 6px;font-size:13.5px;font-weight:700">${CONAME[co]} <span class="muted" style="font-weight:400">· ${sc}</span></div>`;
    for(const kind of ["market","contracted"]){
      const d=pair.find(x=>x.kind===kind); if(!d) continue;
      const wpct=Math.max(3,96*d.tcar/maxT);
      let seg="";
      for(const [f,cvar] of [["elec","--s-elec"],["h2","--s-h2"],["capex","--s-capex"]]){
        const w=100*d[f];
        if(w>0.5) seg+=`<div data-tip="${CONAME[co]} · ${kind==="market"?"시장노출형":"계약형"} (${d.plan_id})<br>${f==="elec"?"전력":f==="h2"?"수소":"설비비"} ${w.toFixed(0)}% · TCaR ${jo(d.tcar)}조" style="width:${w}%;background:var(${cvar});border-right:2px solid var(--surface)"></div>`;
      }
      dh+=`<div style="display:flex;align-items:center;gap:12px;margin:5px 0">
      <div style="width:180px;font-size:12.5px;color:var(--ink2)">${kind==="market"?"시장노출형":"계약형"}
      <span class="muted">PPA ${Math.round(d.ppa*100)}%${d.epc?" · EPC":""}</span></div>
      <div style="flex:1"><div style="width:${wpct}%;display:flex;height:20px;border-radius:4px;overflow:hidden">${seg}</div></div>
      <div style="width:80px;font-size:12px;color:var(--ink2);text-align:right;font-variant-numeric:tabular-nums">${jo(d.tcar)}조</div></div>`;
    }
  }
}
db.innerHTML=dh||'<p class="secnote">경계 계획 부족으로 비교 불가 — 2차 수집 후 생성.</p>';

// policy wedge (그림 6)
const wp=document.getElementById("wpanels");
for(const co of CO){
  const g=D.wedge.filter(d=>d.company_id===co);
  if(!g.length) continue;
  const ids=[...new Set(g.map(d=>d.plan_id))];
  const W=520,H=300,P={l:56,r:16,t:14,b:42};
  const cmin=Math.min(...g.map(d=>d.p50))*0.97, cmax=Math.max(...g.map(d=>d.p50))*1.03;
  const tmax=Math.max(...g.map(d=>d.tcar))*1.1+1e-9;
  const X=v=>P.l+((v-cmin)/(cmax-cmin))*(W-P.l-P.r), Y=v=>P.t+(1-v/tmax)*(H-P.t-P.b);
  let s2="";
  for(let i=0;i<=4;i++){const gy=P.t+i*(H-P.t-P.b)/4;
    s2+=`<line class="gridline" x1="${P.l}" y1="${gy}" x2="${W-P.r}" y2="${gy}"/>
    <text class="axis" x="${P.l-6}" y="${gy+3}" text-anchor="end">${jo(tmax*(4-i)/4)}</text>`;}
  for(let i=0;i<=4;i++){const xv=cmin+(cmax-cmin)*i/4;
    s2+=`<text class="axis" x="${X(xv)}" y="${H-24}" text-anchor="middle">${jo(xv)}</text>`;}
  s2+=`<text class="axislab" x="${(P.l+W-P.r)/2}" y="${H-6}" text-anchor="middle">기대 전환비용 P50 (조원) →</text>`;
  s2+=`<text class="axislab" transform="rotate(-90 12 ${(P.t+H-P.b)/2})" x="12" y="${(P.t+H-P.b)/2}" text-anchor="middle">TCaR (조원)</text>`;
  for(const pid of ids){
    const a=g.find(d=>d.plan_id===pid&&d.scen_eval==="NZ15"), b=g.find(d=>d.plan_id===pid&&d.scen_eval==="B20");
    if(a&&b) s2+=`<line x1="${X(a.p50)}" y1="${Y(a.tcar)}" x2="${X(b.p50)}" y2="${Y(b.tcar)}"
      stroke="var(--ink3)" stroke-dasharray="3 4" stroke-width="1" opacity=".55"
      data-tip="${pid}<br>정책 wedge: 비용 +${jo(a.p50-b.p50)}조 · TCaR +${jo(a.tcar-b.tcar)}조 (1.5°C 대비 2°C)"/>`;
  }
  for(const [sc,col] of [["NZ15","var(--s-nz)"],["B20","var(--s-b20)"]]){
    const f=g.filter(d=>d.scen_eval===sc).sort((a,b)=>a.p50-b.p50);
    s2+=`<polyline points="${f.map(d=>X(d.p50)+","+Y(d.tcar)).join(" ")}" fill="none" stroke="${col}" stroke-width="2"/>`;
    for(const d of f) s2+=`<circle cx="${X(d.p50)}" cy="${Y(d.tcar)}" r="4.5" fill="${col}" stroke="var(--panel)"
      stroke-width="1.5" data-tip="${d.plan_id} · ${sc==="NZ15"?"1.5°C":"2.0°C"}<br>P50 ${jo(d.p50)}조 · TCaR ${jo(d.tcar)}조"/>`;
  }
  wp.insertAdjacentHTML("beforeend",`<div class="panel"><h3>${CONAME[co]}</h3>
   <p class="cap">동일 계획 집합(NZ15 경계) · 시나리오별 재평가</p><svg viewBox="0 0 ${W} ${H}">${s2}</svg></div>`);
}

// λ tangency table (NZ15)
let lr=`<tr><th>기업</th>`+[0,0.25,0.5,1,2,4].map(l=>`<th>λ=${l}</th>`).join("")+`</tr>`;
for(const co of CO){
  const g=D.lam.filter(d=>d.company_id===co&&d.scenario==="NZ15");
  if(!g.length) continue;
  lr+=`<tr><td class="co">${CONAME[co]}</td>`+[0,0.25,0.5,1,2,4].map(l=>{
    const d=g.find(x=>Math.abs(x.lam-l)<1e-9); if(!d) return "<td>—</td>";
    const tag=d.ppa_share>=0.99?(d.epc?"완전계약":"PPA100"):d.ppa_share>0?`PPA${Math.round(d.ppa_share*100)}`:"스팟";
    return `<td data-tip="${CONAME[co]} λ=${l}<br>P50 ${jo(d.p50)}조 · TCaR ${jo(d.tcar)}조<br>PPA ${Math.round(d.ppa_share*100)}% · EPC ${d.epc?"O":"X"}"><b>${tag}</b><div class="muted" style="font-size:10.5px">TCaR ${jo(d.tcar)}조</div></td>`;
  }).join("")+`</tr>`;
}
document.getElementById("ltable").innerHTML=lr;

// 6. quality
document.getElementById("qlist").innerHTML=[
"<b>시설-기술 매칭:</b> BF 전환=수소환원만, 효율=리트로핏, CCUS 제외(사용자 결정), BF→EAF 전면 전환 불허. EAF 신설(야하타·광양)은 모형 밖.",
"<b>감가상각·좌초:</b> 조기 전환 좌초비용 = 개수 캠페인 정액상각 잔존 장부가(재조달가 BF 200천원/t 등 주입 앵커), 만기 잔존가치는 회수 처리.",
"<b>시설 배분:</b> 생산·배출 패널이 전사/사이트 합계 — 능력×루트EF 가중 배분. 포항 2고로는 능력 미상으로 제외. 시설 절대값은 순서 정보.",
"<b>예산 위반 페널티:</b> max(2×탄소가, 300천원/tCO₂) — 바닥 없으면 심전환 대신 위반 선택(1차 실행 실증).",
"<b>탄소가격(한국 NZ15):</b> 한은·금감원 섀도가격 대신 IEA NZE 앵커($250)로 대체.",
"<b>변동성:</b> 전력 0.21(연간 관측 10~11개), 설비비 사전값 0.06, 상관 항등. TCaR 절대값 직결 — 월별 이력 보강 필요.",
"<b>기술비용:</b> 효율·연료전환 CAPEX, 바이오나프타 프리미엄 등 주입 추정(data/prepared/PREP_LOG.md 전수 기록).",
"<b>섹터 예산·가격:</b> EST_v0 잠정 + 예산 단조성 결함(B20<NZ15 구간) — 재추정 대상."
].map(q=>`<li>${q}</li>`).join("");
renderFac("POSCO");
</script>"""

OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
OUT_HTML.write_text(HTML.replace("__DATA__", json.dumps(D, ensure_ascii=False)))
print(f"report -> {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes)")
