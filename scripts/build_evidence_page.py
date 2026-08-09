"""Render the evidence/sensitivity diagnostics page (web/evidence.html).

Turns docs/parameter_inventory.csv + out/sensitivity/ranking.csv into the
picture that drives the whole v2 workplan: which parameters move the answer, and
how weak the evidence under them is.

    .venv/bin/python scripts/build_evidence_page.py
"""

from __future__ import annotations

import json
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
from _style import CSS, DOCTYPE  # noqa: E402

TIER_LABEL = {"T1": "규제·검증", "T2": "기업 1차 공시", "T3": "동료심사·공적기관",
              "T4": "업계·시장 인용", "T5": "모델 추정"}
# ordinal ramp with a deliberate status break at T4/T5 — those are the evidence risks
TIER_COLOR = {"T1": "#1a4d8f", "T2": "#2a78d6", "T3": "#6fa8e0", "T4": "#eda100", "T5": "#e34948"}

PARAM_KR = {
    "fac.ef_inc": "기존 설비 배출 원단위", "tech.emission_factor": "전환기술 배출계수",
    "cfg.discount": "할인율", "vol.h2": "수소 가격 변동성", "tech.h2_intensity": "수소 원단위",
    "price.h2": "수소 가격 수준", "vol.elec": "전력 가격 변동성", "fac.capacity": "설비 능력",
    "tech.capex": "전환기술 CAPEX", "tech.elec_intensity": "전환기술 전력 원단위",
    "price.re": "재생전력 조달가", "tech.opex_fixed": "전환기술 고정 OPEX",
    "price.elec": "계통 전력가", "price.co2": "탄소가격", "fac.margin": "제품 마진",
    "tech.opex_var": "전환기술 변동 OPEX", "fac.elec_int_inc": "기존 전력 원단위",
    "fac.coal_int_inc": "기존 원료탄 원단위", "cfg.auction_share": "유상할당 비율",
    "vol.capex": "설비비 변동성", "price.coal": "원료탄 가격", "price.gas": "가스 가격",
    "tech.steel_capex": "철강 전환 CAPEX", "cfg.ppa_premium": "PPA 프리미엄",
    "cfg.epc_premium": "EPC 프리미엄",
}


def main():
    inv = pd.read_csv(ROOT / "docs/parameter_inventory.csv")
    rank = pd.read_csv(ROOT / "out/sensitivity/ranking.csv")
    scr = pd.read_csv(ROOT / "out/sensitivity/screening.csv")

    rank["label"] = rank.base_param.map(PARAM_KR).fillna(rank.base_param)
    rank["tier_main"] = rank.tier.str.split("/").str[-1]
    top = rank.head(14).copy()

    tier_dist = (inv.groupby(["model", "evidence_tier"]).size().unstack(fill_value=0)
                 .reindex(columns=["T1", "T2", "T3", "T4", "T5"], fill_value=0))
    D = dict(
        top=top[["label", "base_param", "tier", "tier_main", "d_lcoa_pct",
                 "d_tcar_pct", "score"]].round(1).to_dict("records"),
        tier_dist={m: {t: int(v) for t, v in row.items()} for m, row in tier_dist.iterrows()},
        n_params=int(len(inv)),
        n_norange=int(inv.needs_range.sum()) if "needs_range" in inv else 0,
        by_company=(scr[scr.param.str.contains("high")]
                    .pivot_table(index="param", columns="company", values="d_lcoa_pct")
                    .round(1).reset_index().to_dict("records")),
    )

    html = (TEMPLATE.replace("__CSS__", CSS)
            .replace("__DATA__", json.dumps(D, ensure_ascii=False)))
    WEB.mkdir(exist_ok=True)
    (WEB / "evidence.html").write_text(DOCTYPE + html + "</body></html>")
    print(f"[evidence] web/evidence.html ({(WEB / 'evidence.html').stat().st_size:,} bytes)")


TEMPLATE = r"""<title>CAP — 증거 등급과 민감도 진단</title>
<style>
__CSS__</style>
<div class="wrap">
<div class="eyebrow">CAP · 방법론 부속서</div>
<h1>무엇이 답을 움직이고, 그 아래 증거는 얼마나 단단한가</h1>
<p class="lede">모델의 신뢰도는 파라미터 개수가 아니라 <b>영향력이 큰 파라미터의 증거 등급</b>으로 결정된다.
전 입력을 T1(규제·검증)~T5(모델 추정)로 등급화하고, 각각을 ±30% 흔들어 헤드라인 지표가 얼마나 움직이는지
측정했다. 두 결과를 겹치면 <b>"많이 움직이는데 증거가 약한"</b> 항목이 드러나고, 그것이 데이터 보강 작업의
순서가 된다.</p>
<div class="kpis" id="kpis"></div>

<section><h2><span class="secno">1</span>우선순위 매트릭스 — 위험 구역</h2>
<p class="secnote">가로 = 영향력(±30% 변동 시 헤드라인 최대 변화율), 세로 = 증거 등급. <b>오른쪽 아래(붉은 구역)</b>가
위험 지대 — 답을 크게 움직이는데 근거가 모델 추정인 항목이다. 여기 있는 것부터 실측·문헌으로 승급해야 한다.</p>
<div class="panel"><svg id="matrix" viewBox="0 0 900 420" role="img" aria-label="영향력 대 증거등급 매트릭스"></svg></div>
</section>

<section><h2><span class="secno">2</span>영향력 순위 (토네이도)</h2>
<p class="secnote">막대 길이 = 4사 중 최대 |변화율|. 색 = 증거 등급. LCOA(전환비용 단가)와 TCaR(비용 변동폭)에
대한 영향을 나눠 표시 — 어떤 파라미터는 비용 수준을, 어떤 것은 위험 크기를 움직인다.</p>
<div class="legend" id="tierlegend"></div>
<div class="panel"><svg id="tornado" viewBox="0 0 900 520" role="img" aria-label="파라미터 영향력 순위"></svg></div>
</section>

<section><h2><span class="secno">3</span>증거 등급 분포</h2>
<p class="secnote">FIN은 기업 공시(T2)를 주력으로 하고, EFF는 설계상 모든 모형 입력을 자기선언 추정(T5)으로 두되
실제 프로젝트 비용을 별도 증거층으로 보유한다. 두 저장소를 합쳐야 증거 체계가 완성되는 구조다.</p>
<div class="panel"><svg id="tiers" viewBox="0 0 900 160" role="img" aria-label="증거 등급 분포"></svg></div>
</section>

<section><h2><span class="secno">4</span>데이터 승급 작업 순서</h2>
<div class="callout" id="actions"></div>
</section>

<section><h2><span class="secno">5</span>방법과 한계</h2>
<ul class="tight">
<li><b>방법</b>: E2가 생성한 계획 집합을 고정한 뒤 E4/E5 경제성만 재평가(OAT, ±30%, n=3,000, 4사×NZ15).
파라미터당 계약 격자 4종을 훑어 경계 폭도 함께 관측.</li>
<li><b>한계 1 — 계획 선택 채널 미반영</b>: 파라미터가 바뀌면 최적 계획 자체가 바뀌지만, 이 스크리닝은 계획을
고정했다(perturbation마다 MILP 재해에 7분 소요). 해당 채널은 전체 재실행 강건성 분석에서 별도로 확인한다.</li>
<li><b>한계 2 — 상호작용 미측정</b>: OAT는 파라미터 간 상호작용을 잡지 못한다. 전역 민감도(Sobol)는 계산량
때문에 보류했고, 대신 상위 항목에 대해 구조 대안 분석을 병행한다.</li>
<li><b>한계 3 — 등급의 주관성</b>: T1~T5 배정은 출처 유형에 따른 규칙 기반이지만 경계 사례(예: 언론이 인용한
기업 공시)는 판단이 들어간다. 배정 규칙과 전체 목록은 저장소에 공개돼 있다.</li>
</ul>
</section>

<div class="footer">CAP v2 · AUTOPILOT F1·F2 산출 · <a href="/">← 홈</a> · <a href="/report">진단 보고서</a></div>
</div>
<div class="tip" id="tip"></div>
<script>
const D=__DATA__;
const TIERC={T1:"#1a4d8f",T2:"#2a78d6",T3:"#6fa8e0",T4:"#eda100",T5:"#e34948"};
const TIERL={T1:"규제·검증",T2:"기업 1차 공시",T3:"동료심사·공적기관",T4:"업계·시장 인용",T5:"모델 추정"};
const tip=document.getElementById("tip");
document.addEventListener("mousemove",e=>{const t=e.target.closest("[data-tip]");
  if(t){tip.innerHTML=t.getAttribute("data-tip");tip.style.opacity=1;
    tip.style.left=Math.min(e.clientX+14,innerWidth-310)+"px";tip.style.top=(e.clientY+12)+"px";}
  else tip.style.opacity=0;});

const weak=D.top.slice(0,10).filter(d=>d.tier_main==="T5"||d.tier_main==="T4");
document.getElementById("kpis").innerHTML=`
<div class="kpi"><div class="l">등급 부여 파라미터</div><div class="v">${D.n_params}</div><div class="d">FIN + EFF 전 입력</div></div>
<div class="kpi"><div class="l">최대 영향 파라미터</div><div class="v">${D.top[0].d_lcoa_pct}%</div><div class="d">${D.top[0].label} · ${D.top[0].tier_main}</div></div>
<div class="kpi"><div class="l">상위 10 중 증거 취약</div><div class="v">${weak.length}건</div><div class="d">T4·T5 — 승급 대상</div></div>
<div class="kpi"><div class="l">범위 미지정 T5</div><div class="v">${D.n_norange}</div><div class="d">v2 규칙 위반, 보정 예정</div></div>`;

document.getElementById("tierlegend").innerHTML=Object.keys(TIERC).map(t=>
  `<span><span class="sw" style="background:${TIERC[t]}"></span>${t} ${TIERL[t]}</span>`).join("");

// ---- 1. priority matrix
(()=>{const W=900,H=420,P={l:64,r:150,t:22,b:52};
 const tiers=["T1","T2","T3","T4","T5"];
 const xmax=Math.max(...D.top.map(d=>d.score))*1.08;
 const X=v=>P.l+v/xmax*(W-P.l-P.r), Y=t=>P.t+(tiers.indexOf(t)+0.5)*((H-P.t-P.b)/5);
 let s="";
 // danger zone shading: high influence x weak evidence
 s+=`<rect x="${X(xmax*0.25)}" y="${Y("T4")-26}" width="${W-P.r-X(xmax*0.25)}" height="${(H-P.t-P.b)/5*2}"
   fill="var(--danger)" opacity=".07"/>`;
 s+=`<text x="${W-P.r-8}" y="${Y("T5")+30}" text-anchor="end" font-size="11" fill="var(--danger)" font-weight="700">위험 구역 — 영향 크고 증거 약함</text>`;
 tiers.forEach(t=>{
   s+=`<line class="gridline" x1="${P.l}" y1="${Y(t)}" x2="${W-P.r}" y2="${Y(t)}"/>`;
   s+=`<text class="axis" x="${P.l-8}" y="${Y(t)+4}" text-anchor="end">${t} ${TIERL[t]}</text>`;});
 for(let i=0;i<=4;i++){const v=xmax*i/4;
   s+=`<text class="axis" x="${X(v)}" y="${H-30}" text-anchor="middle">${v.toFixed(0)}%</text>`;}
 s+=`<text class="axislab" x="${(P.l+W-P.r)/2}" y="${H-10}" text-anchor="middle">영향력 — ±30% 변동 시 헤드라인 최대 변화율 →</text>`;
 const placed=[];
 D.top.forEach(d=>{
   const cx=X(d.score), cy0=Y(d.tier_main);
   let cy=cy0; while(placed.some(p=>Math.abs(p.x-cx)<58&&Math.abs(p.y-cy)<15)) cy+=15;
   placed.push({x:cx,y:cy});
   const r=6+Math.min(8,d.score/12);
   s+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="${TIERC[d.tier_main]}" opacity=".85" stroke="var(--panel)" stroke-width="1.5"
     data-tip="<b>${d.label}</b><br>${d.tier} · ${TIERL[d.tier_main]}<br>LCOA ${d.d_lcoa_pct}% · TCaR ${d.d_tcar_pct}%"/>`;
   if(d.score>12) s+=`<text x="${cx+r+5}" y="${cy+4}" font-size="11" fill="var(--ink)">${d.label}</text>`;});
 document.getElementById("matrix").innerHTML=s;})();

// ---- 2. tornado
(()=>{const rows=D.top,W=900,rh=34,P={l:190,r:60,t:26,b:28};
 const H=P.t+rows.length*rh+P.b;
 const svg=document.getElementById("tornado"); svg.setAttribute("viewBox",`0 0 ${W} ${H}`);
 const xmax=Math.max(...rows.map(d=>Math.max(d.d_lcoa_pct,d.d_tcar_pct)))*1.05;
 const X=v=>P.l+v/xmax*(W-P.l-P.r);
 let s=`<text class="axislab" x="${P.l}" y="${P.t-10}">■ 위 = LCOA 영향 · ■ 아래 = TCaR 영향 (4사 중 최대 |Δ|%)</text>`;
 for(let i=0;i<=4;i++){const v=xmax*i/4;
   s+=`<line class="gridline" x1="${X(v)}" y1="${P.t}" x2="${X(v)}" y2="${H-P.b}"/>
       <text class="axis" x="${X(v)}" y="${H-10}" text-anchor="middle">${v.toFixed(0)}%</text>`;}
 rows.forEach((d,i)=>{const y=P.t+i*rh;
   s+=`<text x="${P.l-10}" y="${y+18}" text-anchor="end" font-size="12.5" fill="var(--ink)">${d.label}</text>`;
   s+=`<rect x="${P.l}" y="${y+4}" width="${Math.max(1,X(d.d_lcoa_pct)-P.l)}" height="11" rx="3"
     fill="${TIERC[d.tier_main]}" data-tip="<b>${d.label}</b> · LCOA ${d.d_lcoa_pct}%"/>`;
   s+=`<rect x="${P.l}" y="${y+17}" width="${Math.max(1,X(d.d_tcar_pct)-P.l)}" height="11" rx="3"
     fill="${TIERC[d.tier_main]}" opacity=".45" data-tip="<b>${d.label}</b> · TCaR ${d.d_tcar_pct}%"/>`;
   s+=`<text x="${W-P.r+6}" y="${y+20}" font-size="11" fill="var(--ink3)">${d.tier_main}</text>`;});
 svg.innerHTML=s;})();

// ---- 3. tier distribution
(()=>{const W=900,H=160,P={l:64,r:20,t:26,b:34};
 const models=Object.keys(D.tier_dist),tiers=["T1","T2","T3","T4","T5"];
 const tot=m=>tiers.reduce((a,t)=>a+(D.tier_dist[m][t]||0),0);
 const maxTot=Math.max(...models.map(tot));
 let s="";
 models.forEach((m,i)=>{const y=P.t+i*46; let x=P.l;
   const w=(W-P.l-P.r)*tot(m)/maxTot;
   s+=`<text x="${P.l-10}" y="${y+20}" text-anchor="end" font-size="13" font-weight="700" fill="var(--ink)">${m}</text>`;
   tiers.forEach(t=>{const n=D.tier_dist[m][t]||0; if(!n)return;
     const bw=w*n/tot(m);
     s+=`<rect x="${x}" y="${y+4}" width="${Math.max(1,bw-2)}" height="26" rx="4" fill="${TIERC[t]}"
       data-tip="${m} · ${t} ${TIERL[t]}<br>${n}건 (${(100*n/tot(m)).toFixed(0)}%)"/>`;
     if(bw>46) s+=`<text x="${x+bw/2}" y="${y+22}" text-anchor="middle" font-size="11.5" fill="#fff" font-weight="600">${t} ${n}</text>`;
     x+=bw;});
   s+=`<text x="${x+8}" y="${y+22}" font-size="11.5" fill="var(--ink3)">계 ${tot(m)}</text>`;});
 document.getElementById("tiers").innerHTML=s;})();

// ---- 4. actions
document.getElementById("actions").innerHTML=`<b>승급 순서 — 영향력 큰 것부터, 증거 약한 것부터.</b>
<ul class="tight">
<li><b>1순위 · ${D.top[0].label} (${D.top[0].tier_main})</b> — LCOA를 ${D.top[0].d_lcoa_pct}% 움직이는 최대 영향
파라미터가 현재 루트 표준값 주입이다. 한국 GIR 명세서·일본 SHK 사업소별 실측 배출량으로 대체해야 한다.</li>
<li><b>2순위 · 수소 3종(가격·변동성·원단위)</b> — TCaR의 30~42%를 좌우. 청정수소 계약가 시계열이 없어 변동성을
사전값 0.25로 두고 있다. CHPS 낙찰가·일본 CfD 기준가 확보가 관건.</li>
<li><b>3순위 · 설비 능력</b> — 내용적×단일 계수 추정. 공표 능력으로 대체하고, 두 모형 간 12% 괴리를 해소한다.</li>
<li><b>승급 대상 아님 · 할인율</b> — 데이터가 아니라 분석자의 선택이다. 3.5/5.0/6.5% 병기로 강건성을 보인다.</li>
</ul>`;
</script>"""


if __name__ == "__main__":
    main()
