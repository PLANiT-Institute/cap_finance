"""시나리오 분석 페이지 (web/scenarios.html) — 가정을 바꾸면 답이 어떻게 움직이는가.

`out/scenarios/summary.csv`(run_scenarios.py 산출)를 하나의 대화형 화면으로 만든다.
묶음을 고르면 네 기업의 감축단가·꼬리위험·조달부담이 기준 대비 얼마나 움직였는지,
그리고 **기업 간 순서가 뒤집혔는지**를 즉시 보여준다. 결론의 강건성은 숫자 하나가
아니라 "가정을 흔들어도 같은 기업을 지목하는가"로 판단된다.

    .venv/bin/python scripts/build_scenario_page.py
"""

from __future__ import annotations

import json
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _style import CSS, DOCTYPE  # noqa: E402

WEB = ROOT / "web"
SUMMARY = ROOT / "out" / "scenarios" / "summary.csv"
CONAME = {"POSCO": "POSCO", "NSC": "Nippon Steel",
          "LOTTE": "LOTTE Chemical", "MCI": "Mitsui Chemicals"}


def main() -> int:
    if not SUMMARY.exists():
        raise SystemExit(f"{SUMMARY.relative_to(ROOT)} 없음 — "
                         "`.venv/bin/python scripts/run_scenarios.py` 먼저 실행")
    df = pd.read_csv(SUMMARY)
    df = df[(df.scenario == "NZ15") & (df.support == "none")]
    if "base" not in set(df.bundle):
        raise SystemExit("base 묶음이 없다 — 기준이 없으면 비교가 성립하지 않는다")

    cols = ["bundle", "bundle_label", "replanned", "company_id", "capex_total_bnkrw",
            "capex_peak_bnkrw", "capex_peak_year", "cost_per_tco2_thkrw", "tcar_bnkrw",
            "p50_bnkrw", "capex_peak_to_ebitda", "netdebt_to_ebitda_post", "funding_verdict"]
    d = df[[c for c in cols if c in df.columns]].round(3)
    D = {
        "rows": json.loads(d.to_json(orient="records")),
        "bundles": [{"id": b, "label": g.bundle_label.iloc[0],
                     "replanned": bool(g.replanned.iloc[0])}
                    for b, g in df.groupby("bundle", sort=False)],
        "companies": [c for c in CONAME if c in set(df.company_id)],
        "coname": CONAME,
    }
    html = (TEMPLATE.replace("__CSS__", CSS)
            .replace("__DATA__", json.dumps(D, ensure_ascii=False)))
    WEB.mkdir(exist_ok=True)
    (WEB / "scenarios.html").write_text(DOCTYPE + html + "</body></html>")
    print(f"[scenarios] web/scenarios.html ({(WEB / 'scenarios.html').stat().st_size:,} bytes)")
    return 0


TEMPLATE = r"""<title>CAP — 시나리오 분석</title>
<style>
__CSS__
.bsel{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 6px}
.bsel button{font:inherit;font-size:12.5px;font-weight:640;padding:7px 13px;border-radius:999px;
  border:1px solid var(--line);background:var(--panel);color:var(--ink2);cursor:pointer}
.bsel button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.qline{color:var(--ink2);font-size:13.5px;margin:8px 0 0;min-height:20px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(238px,1fr));gap:14px;margin-top:20px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 17px}
.card .co{font-size:12.5px;font-weight:700;color:var(--ink2)}
.card .v{font-size:27px;font-weight:800;margin-top:5px;font-variant-numeric:tabular-nums}
.card .u{font-size:11.5px;color:var(--ink3);font-weight:600}
.card .row{display:flex;justify-content:space-between;font-size:12.5px;color:var(--ink2);
  margin-top:7px;padding-top:7px;border-top:1px solid var(--line2)}
.dlt{font-weight:700;font-variant-numeric:tabular-nums}
.up{color:var(--danger)} .dn{color:#1b8f63} .flat{color:var(--ink3)}
.verdict{margin-top:24px;font-size:13.5px}
.verdict b{font-size:15px}
</style>
<div class="wrap">
<div class="eyebrow">CAP · 시나리오 분석</div>
<h1>가정을 바꾸면 답이 어디까지 움직이는가</h1>
<p class="lede">하나의 숫자는 하나의 세계에서만 참이다. 아래 묶음은 각각 기업이 실제로 묻는 질문
하나에 대응한다 — 자본비용이 낮으면? 무상할당이 오래 가면? 수소가 비싸면? 같은 계획 메뉴를
그 세계에서 다시 평가한 결과다. 중요한 것은 값의 이동폭이 아니라 <b>지목되는 기업이 바뀌는가</b>다.</p>

<section>
<h2><span class="secno">1</span>묶음 선택</h2>
<div class="bsel" id="bsel"></div>
<p class="qline" id="qline"></p>
<div class="cards" id="cards"></div>
<div class="verdict" id="verdict"></div>
</section>

<section>
<h2><span class="secno">2</span>순위 이동 — 기준에서 선택 묶음으로</h2>
<p class="secnote">왼쪽이 기준, 오른쪽이 선택한 묶음의 감축단가(천원/tCO₂). 선이 교차하면
그 가정에서 <b>기업 간 순서가 뒤집혔다</b>는 뜻이고, 결론이 그 가정에 의존한다는 신호다.</p>
<div class="panel"><div id="slope"></div></div>
</section>

<section>
<h2><span class="secno">3</span>전 묶음 대조표</h2>
<p class="secnote">② 감축단가 (천원/tCO₂, NZ15 · 지원 없음). 괄호는 기준 대비 변화율.</p>
<div class="tblwrap"><table id="gtable"></table></div>
</section>

<div class="footer">
계획 메뉴(E2 MILP 산출)는 묶음 간 공유하고 E3–E5만 다시 계산한다. 따라서 이 화면은
<b>"같은 선택지를 다른 세계에서 평가한 값"</b>이며, 가정이 최적 계획 자체를 바꾸는 효과는
<code>run_scenarios.py --replan</code>으로 따로 확인해야 한다. 그 경우 표에 replan 표시가 붙는다.
</div>
</div>

<script>
const D=__DATA__;
const CO=D.companies, NAME=D.coname;
const fmt=(v,d=0)=>v==null||isNaN(v)?"—":Number(v).toLocaleString("ko-KR",{maximumFractionDigits:d});
const get=(b,c)=>D.rows.find(r=>r.bundle===b&&r.company_id===c);
const pct=(v,b)=>(b==null||v==null||!isFinite(b)||b===0)?null:100*(v-b)/Math.abs(b);
const dspan=p=>{ if(p==null) return `<span class="dlt flat">—</span>`;
  const c=Math.abs(p)<0.5?"flat":p>0?"up":"dn";
  return `<span class="dlt ${c}">${p>0?"+":""}${p.toFixed(1)}%</span>`;};
const rank=b=>CO.map(c=>[c,get(b,c)?.cost_per_tco2_thkrw])
              .filter(x=>x[1]!=null).sort((a,b)=>a[1]-b[1]).map(x=>x[0]);

let cur="base";

const sel=document.getElementById("bsel");
sel.innerHTML=D.bundles.map(b=>
  `<button data-b="${b.id}" aria-pressed="${b.id===cur}">${b.id}${b.replanned?" ⟳":""}</button>`).join("");
sel.addEventListener("click",e=>{const b=e.target.closest("button"); if(!b)return;
  cur=b.dataset.b; [...sel.children].forEach(x=>x.setAttribute("aria-pressed",x.dataset.b===cur)); render();});

function render(){
  const meta=D.bundles.find(b=>b.id===cur);
  document.getElementById("qline").innerHTML=`<b>${cur}</b> — ${meta.label}`;

  document.getElementById("cards").innerHTML=CO.map(c=>{
    const r=get(cur,c), b=get("base",c); if(!r) return "";
    const pk=r.capex_peak_to_ebitda;
    return `<div class="card"><div class="co">${NAME[c]}</div>
      <div class="v">${fmt(r.cost_per_tco2_thkrw)}<span class="u"> 천원/tCO₂</span></div>
      <div class="row"><span>기준 대비</span>${dspan(pct(r.cost_per_tco2_thkrw,b?.cost_per_tco2_thkrw))}</div>
      <div class="row"><span>TCaR (조원)</span><span>${fmt(r.tcar_bnkrw/1000,1)} ${
        dspan(pct(r.tcar_bnkrw,b?.tcar_bnkrw)).replace('class="dlt','class="dlt')}</span></div>
      <div class="row"><span>피크배수</span><span>${pk==null||isNaN(pk)?"산출 불가":fmt(pk,1)+"×"}</span></div>
      </div>`;}).join("");

  const r0=rank("base"), r1=rank(cur);
  const same=r0.join()===r1.join();
  document.getElementById("verdict").innerHTML= cur==="base"
    ? `<b>기준</b> — 감축단가 순서: ${r0.map(c=>NAME[c]).join(" < ")}`
    : same
      ? `<b>결론 불변.</b> 감축단가 순서가 기준과 같다 (${r1.map(c=>NAME[c]).join(" < ")}).
         이 가정은 값을 옮기되 지목되는 기업을 바꾸지 않는다.`
      : `<b>순위 역전.</b> 기준 ${r0.map(c=>NAME[c]).join(" < ")} →
         ${cur} ${r1.map(c=>NAME[c]).join(" < ")}. 결론이 이 가정에 의존한다 — 해당 파라미터의
         증거 등급을 먼저 올려야 한다.`;

  drawSlope();
}

function drawSlope(){
  const W=760,H=300,P={l:120,r:130,t:18,b:26};
  const pairs=CO.map(c=>({c, a:get("base",c)?.cost_per_tco2_thkrw, b:get(cur,c)?.cost_per_tco2_thkrw}))
                .filter(p=>p.a!=null&&p.b!=null);
  if(!pairs.length){document.getElementById("slope").innerHTML="";return;}
  const vals=pairs.flatMap(p=>[p.a,p.b]);
  const lo=Math.min(...vals)*0.9, hi=Math.max(...vals)*1.08;
  const Y=v=>P.t+(1-(v-lo)/(hi-lo))*(H-P.t-P.b);
  const x0=P.l, x1=W-P.r;
  const col=["var(--accent)","#1baf7a","#eda100","#e34948"];
  let s=`<svg viewBox="0 0 ${W} ${H}">
    <line x1="${x0}" y1="${P.t}" x2="${x0}" y2="${H-P.b}" class="gridline"/>
    <line x1="${x1}" y1="${P.t}" x2="${x1}" y2="${H-P.b}" class="gridline"/>
    <text class="axislab" x="${x0}" y="${H-8}" text-anchor="middle">기준</text>
    <text class="axislab" x="${x1}" y="${H-8}" text-anchor="middle">${cur}</text>`;
  pairs.forEach((p,i)=>{
    const c=col[i%col.length];
    s+=`<line x1="${x0}" y1="${Y(p.a)}" x2="${x1}" y2="${Y(p.b)}" stroke="${c}" stroke-width="2" opacity=".85"/>
      <circle cx="${x0}" cy="${Y(p.a)}" r="4" fill="${c}"/><circle cx="${x1}" cy="${Y(p.b)}" r="4" fill="${c}"/>
      <text class="axis" x="${x0-9}" y="${Y(p.a)+4}" text-anchor="end">${NAME[p.c]} ${fmt(p.a)}</text>
      <text class="axis" x="${x1+9}" y="${Y(p.b)+4}">${fmt(p.b)}</text>`;});
  document.getElementById("slope").innerHTML=s+"</svg>";
}

(()=>{
  let t=`<tr><th>묶음</th><th>질문</th>${CO.map(c=>`<th>${NAME[c]}</th>`).join("")}</tr>`;
  for(const b of D.bundles){
    t+=`<tr><td class="co">${b.id}${b.replanned?" ⟳":""}</td>
      <td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink2)">${b.label}</td>`;
    for(const c of CO){
      const r=get(b.id,c), bs=get("base",c);
      const p=b.id==="base"?null:pct(r?.cost_per_tco2_thkrw,bs?.cost_per_tco2_thkrw);
      t+=`<td>${fmt(r?.cost_per_tco2_thkrw)}${p==null?"":" "+dspan(p)}</td>`;
    }
    t+=`</tr>`;
  }
  document.getElementById("gtable").innerHTML=t;
})();
render();
</script>"""


if __name__ == "__main__":
    raise SystemExit(main())
