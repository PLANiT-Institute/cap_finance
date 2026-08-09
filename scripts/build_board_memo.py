"""이사회 1페이지 메모 (web/memo.html) — 보고서를 60초 안에 읽는 형식.

진단 보고서는 방법과 근거를 다 싣기 때문에 길다. 이 페이지는 같은 산출물에서
**의사결정에 필요한 것만** 뽑아 A4 한 장으로 낸다: 무엇을, 언제, 얼마에, 감당 가능한가.
브라우저 인쇄(Cmd+P)로 그대로 PDF가 된다.

    .venv/bin/python scripts/build_board_memo.py
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _style import DOCTYPE  # noqa: E402

E5 = ROOT / "out" / "e5"
WEB = ROOT / "web"
CONAME = {"POSCO": "POSCO", "NSC": "Nippon Steel",
          "LOTTE": "LOTTE Chemical", "MCI": "Mitsui Chemicals"}
SECTOR = {"POSCO": "철강 · 한국", "NSC": "철강 · 일본",
          "LOTTE": "석유화학 · 한국", "MCI": "석유화학 · 일본"}


def main() -> int:
    need = ["metrics_company", "affordability", "frontier_points", "gap"]
    missing = [n for n in need if not (E5 / f"{n}.csv").exists()]
    if missing:
        raise SystemExit(f"out/e5에 {missing} 없음 — `python -m cap all` 먼저 실행")

    m = pd.read_csv(E5 / "metrics_company.csv").query("scenario=='NZ15' and support=='none'")
    a = pd.read_csv(E5 / "affordability.csv").query("scenario=='NZ15' and support=='none'")
    fr = pd.read_csv(E5 / "frontier_points.csv").query("scenario=='NZ15' and support=='none'")
    gap = pd.read_csv(E5 / "gap.csv").query("scenario=='NZ15' and support=='none'")

    d = m.merge(a.drop(columns=["capex_total_bnkrw", "capex_peak_year", "capex_peak_bnkrw"]),
                on=["company_id", "scenario", "support"], how="left")
    D = {
        "co": json.loads(d.to_json(orient="records")),
        "frontier": json.loads(fr[fr.on_frontier | fr.is_disclosed][
            ["company_id", "p50", "tcar", "is_disclosed", "on_frontier"]]
            .round(1).to_json(orient="records")),
        "gap": json.loads(gap.drop_duplicates("company_id")[
            ["company_id", "gap_cost_bnkrw", "gap_risk_bnkrw"]].round(1).to_json(orient="records")),
        "coname": CONAME, "sector": SECTOR,
        "date": dt.date.today().isoformat(),
    }
    WEB.mkdir(exist_ok=True)
    (WEB / "memo.html").write_text(
        DOCTYPE + TEMPLATE.replace("__DATA__", json.dumps(D, ensure_ascii=False)) + "</body></html>")
    print(f"[memo] web/memo.html ({(WEB / 'memo.html').stat().st_size:,} bytes)")
    return 0


TEMPLATE = r"""<title>CAP — 이사회 메모 (NZ15)</title>
<style>
@page{size:A4 portrait;margin:14mm}
:root{--ink:#15181f;--ink2:#4d5361;--ink3:#8a909c;--line:#DEDED8;--line2:#EFEFEA;
  --bg:#fff;--panel:#FAFAF7;--nz:#2a78d6;--disc:#e34948;--ok:#1b8f63;--warn:#c07a00}
*{box-sizing:border-box}
body{margin:0;background:#EFEFEA;color:var(--ink);
  font-family:"Apple SD Gothic Neo",Pretendard,"Noto Sans KR",system-ui,sans-serif}
.sheet{width:210mm;min-height:297mm;margin:18px auto;background:var(--bg);padding:14mm;
  box-shadow:0 2px 20px rgba(0,0,0,.13)}
.hd{display:flex;justify-content:space-between;align-items:baseline;
  border-bottom:2px solid var(--ink);padding-bottom:8px}
h1{font-size:19px;margin:0;font-weight:800;letter-spacing:-.01em}
.sub{font-size:10.5px;color:var(--ink3)}
.q{font-size:11.5px;color:var(--ink2);margin:9px 0 0;line-height:1.55}
h2{font-size:11px;margin:15px 0 7px;font-weight:750;letter-spacing:.04em;color:var(--ink2);
  text-transform:uppercase;border-bottom:1px solid var(--line);padding-bottom:3px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.card{border:1px solid var(--line);border-radius:7px;padding:9px 10px;background:var(--panel)}
.card .n{font-size:12px;font-weight:750}
.card .s{font-size:9.5px;color:var(--ink3);margin-bottom:6px}
.kv{display:flex;justify-content:space-between;font-size:10px;color:var(--ink2);
  padding:3px 0;border-top:1px solid var(--line2)}
.kv b{color:var(--ink);font-variant-numeric:tabular-nums;font-weight:700}
.verdict{margin-top:6px;font-size:9.5px;font-weight:700;padding:3px 6px;border-radius:4px;text-align:center}
.v-ok{background:#E7F5EE;color:var(--ok)} .v-warn{background:#FBF1DC;color:var(--warn)}
.v-bad{background:#FBEAE7;color:var(--disc)}
table{width:100%;border-collapse:collapse;font-size:10.5px;font-variant-numeric:tabular-nums}
th{text-align:right;font-size:9.5px;color:var(--ink3);font-weight:650;padding:4px 6px;
  border-bottom:1px solid var(--line)}
td{text-align:right;padding:4px 6px;border-bottom:1px solid var(--line2)}
th:first-child,td:first-child{text-align:left}
svg{display:block;width:100%;height:auto}
.ax{font-size:8px;fill:var(--ink3)}
ol,ul{margin:5px 0 0;padding-left:16px}
li{font-size:10.5px;color:var(--ink2);margin:3px 0;line-height:1.5}
li b{color:var(--ink)}
.two{display:grid;grid-template-columns:1.15fr 1fr;gap:14px}
.ft{margin-top:14px;padding-top:6px;border-top:1px solid var(--line);
  font-size:9px;color:var(--ink3);line-height:1.5}
@media print{body{background:#fff}.sheet{margin:0;box-shadow:none;width:auto;padding:0}}
</style>
<div class="sheet">
<div class="hd">
  <h1>전환 자본배분 진단 — 1.5℃ 정합 시나리오(NZ15)</h1>
  <div class="sub">지원정책 없음 기준 · 실질 할인율 5% · KRW 2025 · <span id="dt"></span></div>
</div>
<p class="q"><b>물음.</b> 각 사가 선택할 수 있는 전환 계획 전체 중 기대비용과 꼬리위험의 효율 경계는
어디이고, 공시된 계획은 거기서 얼마나 떨어져 있으며, <b>그 돈을 감당할 수 있는가.</b>
<b>재는 것.</b> ② 감축 단가(자원비용 기준, 탄소비용 분리) · ③ TCaR = P90−P50 · ⑥ 조달 부담.</p>

<h2>1. 네 기업 요약</h2>
<div class="grid" id="cards"></div>

<div class="two">
<div>
  <h2>2. 효율 경계와 공시 계획의 거리</h2>
  <div id="fr"></div>
</div>
<div>
  <h2>3. 자본 규모와 시점</h2>
  <div class="tbl"><table id="cap"></table></div>
  <h2 style="margin-top:12px">4. 읽을 때 유의</h2>
  <ul id="caveats"></ul>
</div>
</div>

<h2>5. 결론</h2>
<ol id="concl"></ol>

<div class="ft" id="ft"></div>
</div>
<script>
const D=__DATA__;
const CO=["POSCO","NSC","LOTTE","MCI"];
const f=(v,d=0)=>v==null||isNaN(v)?"—":Number(v).toLocaleString("ko-KR",{maximumFractionDigits:d});
const jo=(v,d=1)=>v==null||isNaN(v)?"—":f(v/1000,d);
const get=c=>D.co.find(x=>x.company_id===c)||{};
const gp=c=>D.gap.find(x=>x.company_id===c)||{};
document.getElementById("dt").textContent=D.date;

document.getElementById("cards").innerHTML=CO.map(c=>{
  const r=get(c); if(!r.company_id) return "";
  const pk=r.capex_peak_to_ebitda;
  const cls=(r.ebitda_ref_bnkrw==null||r.ebitda_ref_bnkrw<=0)?"v-bad":pk>1?"v-warn":"v-ok";
  return `<div class="card"><div class="n">${D.coname[c]}</div><div class="s">${D.sector[c]}</div>
  <div class="kv"><span>② 감축단가</span><b>${f(r.cost_per_tco2_thkrw)} 천원/t</b></div>
  <div class="kv"><span>③ TCaR</span><b>${jo(r.tcar_bnkrw)} 조원</b></div>
  <div class="kv"><span>① 총 CAPEX</span><b>${jo(r.capex_total_bnkrw)} 조원</b></div>
  <div class="kv"><span>⑥ 피크배수</span><b>${pk==null||isNaN(pk)?"산출 불가":f(pk,1)+"×"}</b></div>
  <div class="verdict ${cls}">${r.funding_verdict||"—"}</div></div>`;}).join("");

(()=>{ // frontier sketch: normalized per company so four scales fit one panel
  const W=430,H=170,P={l:34,r:8,t:10,b:22},col={POSCO:"#2a78d6",NSC:"#1baf7a",LOTTE:"#eda100",MCI:"#8a5cd6"};
  let s=`<svg viewBox="0 0 ${W} ${H}">`;
  s+=`<text class="ax" x="4" y="${P.t+6}" >꼬리위험</text>
      <text class="ax" x="${W-P.r}" y="${H-6}" text-anchor="end">기대 전환비용 →</text>`;
  for(const c of CO){
    const pts=D.frontier.filter(p=>p.company_id===c);
    if(pts.length<2) continue;
    const xs=pts.map(p=>p.p50), ys=pts.map(p=>p.tcar);
    const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
    const X=v=>P.l+(x1>x0?(v-x0)/(x1-x0):.5)*(W-P.l-P.r);
    const Y=v=>H-P.b-(y1>y0?(v-y0)/(y1-y0):.5)*(H-P.t-P.b);
    const on=pts.filter(p=>p.on_frontier).sort((a,b)=>a.p50-b.p50);
    if(on.length>1) s+=`<path d="${on.map((p,i)=>(i?"L":"M")+X(p.p50)+","+Y(p.tcar)).join("")}"
       fill="none" stroke="${col[c]}" stroke-width="1.6" opacity=".85"/>`;
    for(const p of on) s+=`<circle cx="${X(p.p50)}" cy="${Y(p.tcar)}" r="2.4" fill="${col[c]}"/>`;
    for(const p of pts.filter(p=>p.is_disclosed))
      s+=`<path d="M${X(p.p50)-3.4},${Y(p.tcar)-3.4}l6.8,6.8M${X(p.p50)+3.4},${Y(p.tcar)-3.4}l-6.8,6.8"
        stroke="${col[c]}" stroke-width="1.8"/>`;
  }
  s+=`</svg><div style="font-size:9px;color:var(--ink3);margin-top:4px">
    선·점 = 효율 경계, ✕ = 공시 계획. 기업마다 축을 정규화했으므로 <b>형태와 거리</b>를 읽는 그림이고
    기업 간 절대 비교용이 아니다. 공시 커밋이 강제 불가능한 기업은 ✕가 없다(측정 불가 판정).</div>`;
  document.getElementById("fr").innerHTML=s;
})();

document.getElementById("cap").innerHTML=
 `<tr><th>기업</th><th>총 CAPEX</th><th>피크 연도</th><th>피크 지출</th><th>경계까지 거리</th></tr>`+
 CO.map(c=>{const r=get(c),g=gp(c); if(!r.company_id)return"";
  return `<tr><td>${D.coname[c]}</td><td>${jo(r.capex_total_bnkrw)}조</td>
   <td>${r.capex_peak_year??"—"}</td><td>${jo(r.capex_peak_bnkrw)}조</td>
   <td>${g.gap_cost_bnkrw==null?"측정 불가":jo(g.gap_cost_bnkrw)+"조"}</td></tr>`;}).join("");

document.getElementById("caveats").innerHTML=[
 "<b>시설 배출은 배분값이다.</b> 회사 실측을 능력×루트 배출계수로 나눈 값이라 시설 단위 절대값은 순서 정보로만 읽는다.",
 "<b>TCaR 수준은 사전 변동성에 의존한다.</b> 수소·설비비 월별 이력 확보 전까지 순위는 방어 가능하나 절대값은 아니다.",
 "<b>Scope 1 기준이다.</b> 보고된 Scope 2는 데이터에 보존돼 있으나 지표에 넣지 않았다.",
].map(x=>`<li>${x}</li>`).join("");

(()=>{
  const rank=[...D.co].filter(r=>r.cost_per_tco2_thkrw!=null)
    .sort((a,b)=>a.cost_per_tco2_thkrw-b.cost_per_tco2_thkrw);
  const burden=[...D.co].filter(r=>r.capex_total_to_ebitda!=null&&!isNaN(r.capex_total_to_ebitda))
    .sort((a,b)=>b.capex_total_to_ebitda-a.capex_total_to_ebitda);
  const neg=D.co.filter(r=>r.ebitda_ref_bnkrw!=null&&r.ebitda_ref_bnkrw<=0);
  const out=[];
  if(rank.length&&burden.length){
    const same=rank[0].company_id===burden[0].company_id;
    out.push(same
      ? `<b>가장 싸게 줄이는 곳이 동시에 가장 무겁다.</b> ${D.coname[rank[0].company_id]}는 감축 단가가
         최저(${f(rank[0].cost_per_tco2_thkrw)}천원/tCO₂)지만 총 CAPEX가 기준 EBITDA의
         ${f(burden[0].capex_total_to_ebitda,1)}배다. 효율이 좋다는 것과 감당된다는 것은 다른 문장이고,
         단가만 보고 자본을 배분하면 조달이 병목인 곳에 배분하게 된다.`
      : `<b>가장 싸게 줄이는 곳과 가장 무겁게 부담하는 곳이 다르다.</b> 감축 단가는
         ${D.coname[rank[0].company_id]}가 최저(${f(rank[0].cost_per_tco2_thkrw)}천원/tCO₂)지만
         총 CAPEX/EBITDA는 ${D.coname[burden[0].company_id]}가 최고(${f(burden[0].capex_total_to_ebitda,1)}배)다.
         단가만 보고 자본을 배분하면 조달이 막히는 곳에 배분한다.`);
  }
  if(neg.length) out.push(`<b>${neg.map(r=>D.coname[r.company_id]).join(", ")}는 기준 EBITDA가 음수다.</b>
    전환 CAPEX가 절대 규모로는 가장 작아도(${jo(neg[0].capex_total_bnkrw)}조) 자체 현금흐름으로는 불가능하다 —
    이 기업의 제약은 기술이 아니라 조달이다.`);
  const gsum=D.gap.reduce((s,g)=>s+(g.gap_cost_bnkrw||0),0);
  if(gsum>0) out.push(`<b>공시 계획은 경계 안쪽에 있다.</b> 측정 가능한 기업 합산 ${jo(gsum)}조원만큼
    같은 꼬리위험에서 더 쓸 여지가 있었다. 지출 부족은 절약이 아니라 <b>에너지 가격 리스크 포지션</b>이다.`);
  document.getElementById("concl").innerHTML=out.map(x=>`<li>${x}</li>`).join("");
})();

document.getElementById("ft").textContent=
 "산출: cap_finance v2 파이프라인 (E1 제약 → E2 시설 MILP·경계 추적 → E3 확률가격 → E4 경로별 재평가 → E5 지표). "
 +"형식 명세 METHODOLOGY.md, 데이터 진위·활용 감사 docs/data_audit.md, 가정별 민감도는 증거 페이지 참조. "
 +"시설 단위 산출은 비공개(설계서 §8-2).";
</script>"""


if __name__ == "__main__":
    raise SystemExit(main())
