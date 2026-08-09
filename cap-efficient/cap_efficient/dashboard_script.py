from __future__ import annotations


DASHBOARD_SCRIPT = r'''
const D=JSON.parse(document.getElementById("data").textContent);
const $=id=>document.getElementById(id);
const NS="http://www.w3.org/2000/svg";
const svgEl=(tag,attrs,text)=>{const el=document.createElementNS(NS,tag);Object.entries(attrs||{}).forEach(pair=>el.setAttribute(pair[0],pair[1]));if(text!==undefined)el.textContent=text;return el};
const fmt=(value,d)=>Number(value||0).toLocaleString("ko-KR",{minimumFractionDigits:d===undefined?1:d,maximumFractionDigits:d===undefined?1:d});
const signed=(value,d)=>(value>0?"+":"")+fmt(value,d);
const pct=(value,d)=>fmt(100*value,d===undefined?0:d)+"%";
const shortBn=value=>Math.abs(Number(value||0))>=10000?fmt(Number(value)/1000,1)+"조":fmt(value,0)+"bn";
const sum=(items,key)=>items.reduce((total,row)=>total+Number(typeof key==="function"?key(row):(row[key]||0)),0);
const riskConfig={
  cost:{label:"비용 중심",copy:"효율경계에서 P50 경제적 순비용이 가장 낮은 대안"},
  balanced:{label:"균형",copy:"효율경계의 TCaR 중앙값 이하를 만족하는 대안 중 P50 비용이 가장 낮은 대안"},
  stable:{label:"안정성",copy:"효율경계에서 TCaR가 가장 낮은 대안"}
};
let company=D.companies[0].company_id;
let scenario=(D.scenarios.find(s=>s.scenario_id==="ACCELERATED_15C")||D.scenarios[0]).scenario_id;
let plan="CURRENT";
let risk="balanced";
const companyInfo=()=>D.companies.find(c=>c.company_id===company);
const rows=()=>D.aggregates.filter(r=>r.company_id===company&&r.scenario_id===scenario).sort((a,b)=>a.plan_order-b.plan_order);
const selected=()=>rows().find(r=>r.plan_id===plan)||rows()[0];
const current=()=>rows().find(r=>r.is_disclosed_plan);
const planInfo=(id)=>D.plans.find(p=>p.company_id===company&&p.plan_id===(id||plan));
const facilities=()=>D.facility_rows.filter(r=>r.company_id===company&&r.scenario_id===scenario&&r.plan_id===plan);
const scenarioPath=()=>D.scenario_paths[company][scenario];
const scenarioInfo=()=>D.scenarios.find(s=>s.scenario_id===scenario);
const scenarioLabel=id=>(D.scenarios.find(s=>s.scenario_id===id)||{label:id}).label;
const candidateScenarioRows=()=>((D.refined_candidate_metrics||D.candidate_scenario_metrics)||[]).filter(r=>r.company_id===company);
const candidateRobustRows=()=>((D.refined_candidate_robust_summary||D.candidate_robust_summary)||[]).filter(r=>r.company_id===company);
const lambdaValue=()=>risk==="cost"?0:risk==="stable"?4:1;
const robustRecommendation=()=>{
  const eligible=candidateRobustRows().filter(r=>r.robust_feasible),lambda=lambdaValue();
  const pool=eligible.length?eligible:candidateRobustRows().filter(r=>r.feasible_scenario_count===Math.max(...candidateRobustRows().map(x=>x.feasible_scenario_count)));
  return pool.reduce((a,b)=>(a.maximum_regret_p50_kkrw_per_tco2_mean+lambda*a.worst_case_tcar_kkrw_per_tco2_mean)<=(b.maximum_regret_p50_kkrw_per_tco2_mean+lambda*b.worst_case_tcar_kkrw_per_tco2_mean)?a:b);
};
const scenarioComparison=()=>{
  const candidates=D.scenario_comparisons.filter(r=>r.company_id===company&&r.plan_id===plan&&(r.from_scenario_id===scenario||r.to_scenario_id===scenario));
  if(!candidates.length)return null;
  const origin=selected().portfolio_origin_scenario_id;
  const row=candidates.find(r=>(r.from_scenario_id===scenario?r.to_scenario_id:r.from_scenario_id)===origin)||candidates[0];
  const direction=row.to_scenario_id===scenario?1:-1;
  return {other:direction===1?row.from_scenario_id:row.to_scenario_id,p50:direction*row.delta_p50_common_kkrw_per_tco2_mean,tcar:direction*row.delta_tcar_kkrw_per_tco2_mean,npv:direction*row.delta_absolute_npv_p50_bn_krw_mean,cash:direction*row.delta_net_cash_cost_p50_bn_krw_mean,carbon:direction*row.delta_avoided_carbon_value_p50_bn_krw_mean};
};
function pareto(input){
  return input.filter(p=>!input.some(q=>q.plan_id!==p.plan_id&&q.expected_cost_p50_kkrw_per_tco2_mean<=p.expected_cost_p50_kkrw_per_tco2_mean&&q.tcar_kkrw_per_tco2_mean<=p.tcar_kkrw_per_tco2_mean&&(q.expected_cost_p50_kkrw_per_tco2_mean<p.expected_cost_p50_kkrw_per_tco2_mean||q.tcar_kkrw_per_tco2_mean<p.tcar_kkrw_per_tco2_mean))).sort((a,b)=>a.expected_cost_p50_kkrw_per_tco2_mean-b.expected_cost_p50_kkrw_per_tco2_mean);
}
const frontier=()=>pareto(rows().filter(r=>!r.is_disclosed_plan&&r.scenario_feasible));
const recommended=()=>{
  const fr=frontier();
  if(risk==="cost")return fr.reduce((a,b)=>a.expected_cost_p50_kkrw_per_tco2_mean<b.expected_cost_p50_kkrw_per_tco2_mean?a:b);
  if(risk==="stable")return fr.reduce((a,b)=>a.tcar_kkrw_per_tco2_mean<b.tcar_kkrw_per_tco2_mean?a:b);
  const risks=fr.map(r=>r.tcar_kkrw_per_tco2_mean).sort((a,b)=>a-b),riskLimit=risks[Math.floor(risks.length/2)];
  return fr.filter(row=>row.tcar_kkrw_per_tco2_mean<=riskLimit).reduce((a,b)=>a.expected_cost_p50_kkrw_per_tco2_mean<b.expected_cost_p50_kkrw_per_tco2_mean?a:b);
};
function dominator(target){
  return rows().filter(r=>r.scenario_feasible&&r.plan_id!==target.plan_id&&r.expected_cost_p50_kkrw_per_tco2_mean<=target.expected_cost_p50_kkrw_per_tco2_mean&&r.tcar_kkrw_per_tco2_mean<=target.tcar_kkrw_per_tco2_mean&&(r.expected_cost_p50_kkrw_per_tco2_mean<target.expected_cost_p50_kkrw_per_tco2_mean||r.tcar_kkrw_per_tco2_mean<target.tcar_kkrw_per_tco2_mean)).sort((a,b)=>(a.expected_cost_p50_kkrw_per_tco2_mean+a.tcar_kkrw_per_tco2_mean)-(b.expected_cost_p50_kkrw_per_tco2_mean+b.tcar_kkrw_per_tco2_mean))[0];
}
function emissionsAt(year,fr){return sum(fr||facilities(),row=>year>=row.transition_year?row.residual_emissions_mtco2:row.baseline_emissions_mtco2)}
function setupControls(){
  $("company-buttons").innerHTML=D.companies.map(c=>'<button class="btn '+(c.company_id===company?"on":"")+'" data-company="'+c.company_id+'">'+(c.country_code==="KR"?"KR":"JP")+' · '+c.company_name+'</button>').join("");
  $("scenario-buttons").innerHTML=D.scenarios.map(s=>'<button class="btn '+(s.scenario_id===scenario?"on":"")+'" data-scenario="'+s.scenario_id+'">'+s.label+'</button>').join("");
  $("plan-select").innerHTML=rows().map(r=>'<option value="'+r.plan_id+'" '+(r.plan_id===plan?"selected":"")+'>'+r.plan_id+' · '+r.plan_name+'</option>').join("");
  $("risk-buttons").innerHTML=Object.entries(riskConfig).map(pair=>'<button class="risk '+(pair[0]===risk?"on":"")+'" data-risk="'+pair[0]+'">'+pair[1].label+'</button>').join("");
  document.querySelectorAll("[data-company]").forEach(b=>b.onclick=()=>{company=b.dataset.company;plan="CURRENT";render()});
  document.querySelectorAll("[data-scenario]").forEach(b=>b.onclick=()=>{scenario=b.dataset.scenario;plan="CURRENT";render()});
  document.querySelectorAll("[data-risk]").forEach(b=>b.onclick=()=>{risk=b.dataset.risk;render()});
  $("plan-select").onchange=e=>{plan=e.target.value;render()};
  $("show-recommended").onclick=()=>{plan=recommended().plan_id;render();$("frontier-chart").scrollIntoView({behavior:"smooth",block:"center"})};
}
function decision(){
  const reco=recommended(),cur=current(),cfg=riskConfig[risk];
  const costSave=cur.expected_cost_p50_bn_krw_mean-reco.expected_cost_p50_bn_krw_mean;
  const riskSave=cur.tcar_kkrw_per_tco2_mean-reco.tcar_kkrw_per_tco2_mean;
  $("decision-kicker").textContent=companyInfo().company_name+" · "+cfg.label+" 기준 추천";
  $("decision-title").textContent=reco.plan_id+" "+reco.plan_name;
  $("decision-copy").innerHTML=cfg.copy+'. 연도별 탄소예산을 충족하는 고정 포트폴리오만 대상으로 공시전략 프록시 대비 P50 NPV <strong>'+(costSave>=0?fmt(costSave,0)+"bn 절감":fmt(-costSave,0)+"bn 증가")+'</strong>, TCaR <strong>'+(riskSave>=0?fmt(riskSave,1)+"천원 축소":fmt(-riskSave,1)+"천원 확대")+"</strong>. 권고안은 모델 대안이며 실제 승인 전 설비별 원가 검증이 필요합니다.";
}
function kpis(){
  const c=companyInfo(),r=selected(),fr=facilities(),base=sum(fr,"baseline_emissions_mtco2"),res=emissionsAt(2040,fr),cur=current();
  $("kpi-baseline").textContent=fmt(base,1)+" Mt";
  $("kpi-baseline-note").textContent="공식 "+fmt(c.scope12_emissions_mtco2,1)+"Mt · 설비블록 합계";
  $("kpi-residual").textContent=fmt(res,1)+" Mt";
  $("kpi-residual-note").innerHTML='기준 대비 <span class="delta good">−'+fmt(100*(1-res/base),0)+"%</span> · 2030 "+fmt(emissionsAt(2030,fr),1)+"Mt";
  $("kpi-cost").textContent=shortBn(r.expected_cost_p50_bn_krw_mean);
  const delta=r.expected_cost_p50_bn_krw_mean-cur.expected_cost_p50_bn_krw_mean;
  $("kpi-cost-note").innerHTML="현금 "+shortBn(r.net_cash_cost_after_support_p50_bn_krw_mean)+" − 탄소회피가치 "+shortBn(r.avoided_carbon_cost_value_p50_bn_krw_mean)+' · 현재 대비 <span class="delta '+(delta<=0?"good":"bad")+'">'+signed(delta,0)+"bn</span>";
  $("kpi-tcar").textContent=fmt(r.tcar_kkrw_per_tco2_mean,1)+" 천원";
  $("kpi-tcar-note").textContent="P90 "+fmt(r.expected_cost_p50_kkrw_per_tco2_mean+r.tcar_kkrw_per_tco2_mean,1)+"천원/tCO₂ · P90/EBITDA "+fmt(r.p90_cost_to_ebitda_x_mean,2)+"×";
  $("kpi-capex").textContent=shortBn(r.aligned_capex_bn_krw);
  $("kpi-capex-note").textContent="피크 "+r.peak_capex_year+" · "+fmt(r.peak_capex_bn_krw,0)+"bn";
  $("avoided-total").textContent=fmt(r.avoided_emissions_mtco2,0)+" MtCO₂";
}
function axisText(svg,x,y,text,anchor){
  svg.append(svgEl("text",{x:x,y:y,"text-anchor":anchor||"middle","font-size":10,fill:"#6b788a"},text));
}
function emissionsChart(){
  const svg=$("emissions-chart");svg.innerHTML="";
  const path=scenarioPath(),fr=facilities(),base=sum(fr,"baseline_emissions_mtco2");
  const data=path.map(p=>Object.assign({},p,{emissions:emissionsAt(p.year,fr)}));
  const L=58,R=22,T=24,B=48,W=900-L-R,H=390-T-B;
  const maxY=Math.max(base,...data.map(d=>d.carbon_budget_mtco2))*1.08;
  const x=year=>L+(year-path[0].year)/(path[path.length-1].year-path[0].year)*W;
  const y=value=>T+(maxY-value)/maxY*H;
  for(let i=0;i<=5;i++){const value=maxY*i/5;svg.append(svgEl("line",{x1:L,y1:y(value),x2:L+W,y2:y(value),stroke:"#e5eaf0"}));axisText(svg,L-9,y(value)+3,fmt(value,0),"end")}
  data.forEach((d,i)=>{if(i%2===0||i===data.length-1)axisText(svg,x(d.year),T+H+22,d.year)});
  const area="M "+x(data[0].year)+" "+y(base)+" "+data.map(d=>"L "+x(d.year)+" "+y(d.emissions)).join(" ")+" L "+x(data[data.length-1].year)+" "+y(base)+" Z";
  svg.append(svgEl("path",{d:area,fill:"#dfeef4",opacity:.8}));
  const line=fn=>data.map((p,i)=>(i?"L ":"M ")+x(p.year)+" "+y(fn(p))).join(" ");
  svg.append(svgEl("path",{d:line(p=>p.carbon_budget_mtco2),fill:"none",stroke:"#b57717","stroke-width":2.2,"stroke-dasharray":"7 5"}));
  svg.append(svgEl("path",{d:line(p=>p.emissions),fill:"none",stroke:"#1769aa","stroke-width":3.2,"stroke-linejoin":"round"}));
  Array.from(new Set(fr.map(r=>r.transition_year))).sort().forEach(year=>{
    const affected=fr.filter(r=>r.transition_year===year),cy=y(emissionsAt(year,fr));
    svg.append(svgEl("circle",{cx:x(year),cy:cy,r:5,fill:"#fff",stroke:"#1769aa","stroke-width":3}));
    axisText(svg,x(year),Math.max(T+10,cy-12),year+" · "+(affected.length===1?affected[0].facility_name.split(" ")[0]:affected.length+"개 설비"));
  });
  axisText(svg,12,T+H/2,"MtCO₂","start");
}
function logic(){
  const r=selected(),cur=current(),dom=dominator(r),fr=facilities(),budget=(scenarioPath().find(p=>p.year===2040)||scenarioPath()[scenarioPath().length-1]).carbon_budget_mtco2,cross=scenarioComparison();
  const gapCost=r.expected_cost_p50_bn_krw_mean-cur.expected_cost_p50_bn_krw_mean,gapRisk=r.tcar_kkrw_per_tco2_mean-cur.tcar_kkrw_per_tco2_mean,residual=emissionsAt(2040,fr),feasible=r.scenario_feasible;
  const drivers=[["기술 CAPEX",r.capex_cost_p50_bn_krw_mean],["전력",r.electricity_cost_p50_bn_krw_mean],["수소",r.hydrogen_cost_p50_bn_krw_mean]].sort((a,b)=>b[1]-a[1]),driver=drivers[0];
  $("logic").innerHTML=
    '<div class="logic-card"><div class="logic-label">공시전략 대비</div><div class="logic-value">'+(gapCost<=0?"비용 절감 ":"비용 증가 ")+fmt(Math.abs(gapCost),0)+'bn</div><div class="logic-copy">TCaR '+(gapRisk<=0?"축소 ":"확대 ")+fmt(Math.abs(gapRisk),1)+"천원/tCO₂ · CAPEX "+signed(r.aligned_capex_bn_krw-cur.aligned_capex_bn_krw,0)+"bn</div></div>"+
    '<div class="logic-card"><div class="logic-label">통합 실행가능성</div><div class="logic-value">'+(feasible?"탄소·자원·공사·실패기준 충족":!r.carbon_budget_feasible?r.first_budget_breach_year+"년 탄소예산 초과":!r.resource_constraints_feasible?r.first_resource_breach_year+"년 공급제약 초과":"공사/실패위험 기준 초과")+'</div><div class="logic-copy">2040 잔여 '+fmt(residual,1)+"Mt / 예산 "+fmt(budget,1)+"Mt · 스크랩 초과 "+fmt(r.max_scrap_supply_excess_mt,1)+"Mt · 수소 초과 "+fmt(r.max_hydrogen_supply_excess_mt,1)+"Mt · 계통 초과 "+fmt(r.max_incremental_grid_excess_twh,1)+"TWh · 동시공사 "+r.max_concurrent_construction_projects+"/"+r.concurrent_construction_limit+" · 실패노출 "+pct(r.portfolio_failure_probability)+".</div></div>"+
    '<div class="logic-card"><div class="logic-label">효율성 판정</div><div class="logic-value">'+(!feasible?"경계 부적격":dom?dom.plan_id+"가 동시 개선":"비지배 대안")+'</div><div class="logic-copy">'+(!feasible?"비용은 계산했지만 탄소예산 미충족으로 추천·효율경계에서 제외됩니다.":dom?"P50과 TCaR 모두 더 낮은 적격 계획이 존재합니다.":"적격안 중 두 판단축을 동시에 더 낮출 수 있는 계획이 없습니다.")+"</div></div>"+
    (cross?'<div class="logic-card"><div class="logic-label">동일 포트폴리오 시나리오 변화</div><div class="logic-value">P50 '+signed(cross.p50,1)+'천원 · TCaR '+signed(cross.tcar,1)+'천원</div><div class="logic-copy">'+scenarioLabel(cross.other)+" 대비 절대 NPV "+signed(cross.npv,0)+"bn, 실제 순현금비용 "+signed(cross.cash,0)+"bn, 탄소회피가치 "+signed(cross.carbon,0)+"bn. CAPEX·설비·연도는 동일합니다.</div></div>":"")+
    '<div class="logic-card"><div class="logic-label">최대 양(+) 비용요인</div><div class="logic-value">'+driver[0]+" · "+fmt(driver[1],0)+'bn</div><div class="logic-copy">실제 순현금비용과 탄소회피가치·정책지원을 분리했습니다. 경제적 순비용이 음수여도 현금수익을 뜻하지 않습니다.</div></div>';
}
function showTip(event,html){
  const tip=$("tip");tip.innerHTML=html;tip.style.display="block";tip.style.left=Math.min(innerWidth-270,event.clientX+14)+"px";tip.style.top=event.clientY+14+"px";
}
function frontierChart(){
  const svg=$("frontier-chart");svg.innerHTML="";
  const rr=rows(),fr=frontier(),sel=selected(),xs=rr.map(r=>r.expected_cost_p50_kkrw_per_tco2_mean),ys=rr.map(r=>r.tcar_kkrw_per_tco2_mean);
  const range=(arr,padding)=>{const a=Math.min(...arr),b=Math.max(...arr),d=Math.max((b-a)*padding,2);return[a-d,b+d]};
  const xr=range(xs,.14),yr=range([0,...ys],.08),xmin=xr[0],xmax=xr[1],ymin=yr[0],ymax=yr[1];
  const L=70,R=28,T=35,B=63,W=940-L-R,H=470-T-B,x=v=>L+(v-xmin)/(xmax-xmin)*W,y=v=>T+(ymax-v)/(ymax-ymin)*H;
  for(let i=0;i<=5;i++){
    const xv=xmin+(xmax-xmin)*i/5,yv=ymin+(ymax-ymin)*i/5;
    svg.append(svgEl("line",{x1:x(xv),y1:T,x2:x(xv),y2:T+H,stroke:"#e7ebf0"}));axisText(svg,x(xv),T+H+22,fmt(xv,0));
    svg.append(svgEl("line",{x1:L,y1:y(yv),x2:L+W,y2:y(yv),stroke:"#e7ebf0"}));axisText(svg,L-9,y(yv)+3,fmt(yv,0),"end");
  }
  if(fr.length>1)svg.append(svgEl("path",{d:fr.map((r,i)=>(i?"L ":"M ")+x(r.expected_cost_p50_kkrw_per_tco2_mean)+" "+y(r.tcar_kkrw_per_tco2_mean)).join(" "),fill:"none",stroke:"#0f7c7b","stroke-width":3}));
  rr.forEach(r=>{
    const X=x(r.expected_cost_p50_kkrw_per_tco2_mean),Y=y(r.tcar_kkrw_per_tco2_mean),isF=fr.some(f=>f.plan_id===r.plan_id),isSel=r.plan_id===plan;
    let shape;
    if(r.is_disclosed_plan)shape=svgEl("polygon",{points:X+","+(Y-9)+" "+(X+9)+","+Y+" "+X+","+(Y+9)+" "+(X-9)+","+Y,fill:"#a6453c"});
    else shape=svgEl("circle",{cx:X,cy:Y,r:isSel?9:7,fill:!r.scenario_feasible?"#c58a2d":isF?"#0f7c7b":"#aab6c2"});
    shape.style.cursor="pointer";
    shape.onclick=()=>{plan=r.plan_id;render()};
    shape.onmousemove=e=>showTip(e,"<strong>"+r.plan_id+" · "+r.plan_name+"</strong><br>P50 "+fmt(r.expected_cost_p50_kkrw_per_tco2_mean,1)+" · TCaR "+fmt(r.tcar_kkrw_per_tco2_mean,1)+"<br>"+(!r.scenario_feasible?"탄소·자원·공사·실패 제약 미충족 · 경계 제외":isF?"효율경계":"지배 대안 존재"));
    shape.onmouseleave=()=>{$("tip").style.display="none"};
    svg.append(shape);
    if(isSel)svg.append(svgEl("circle",{cx:X,cy:Y,r:14,fill:"none",stroke:"#132238","stroke-width":2,"stroke-dasharray":"3 2"}));
    axisText(svg,X+10,Y-10,r.plan_id,"start");
  });
  axisText(svg,L+W/2,462,"Net P50 · 천원/tCO₂");
  svg.append(svgEl("text",{x:18,y:T+H/2,transform:"rotate(-90 18 "+(T+H/2)+")","text-anchor":"middle","font-size":10,fill:"#6b788a"},"TCaR · P90−P50"));
  axisText(svg,L+10,T+13,"← 낮은 비용 · 낮은 위험 방향","start");
  $("selected-plan-head").textContent=sel.plan_id+" · "+sel.plan_name;
}
function planCard(){
  const r=selected(),fr=frontier(),isF=fr.some(f=>f.plan_id===r.plan_id),dom=dominator(r),reco=recommended();
  const status=!r.scenario_feasible?"실행 제약 미충족":r.is_disclosed_plan?"공시전략 프록시":isF?"효율경계 대안":"지배되는 대안",cls=!r.scenario_feasible?"warn":r.is_disclosed_plan?"current":isF?"":"warn";
  $("plan-card").innerHTML=
    '<div class="logic-label">SELECTED PORTFOLIO</div><div class="logic-value">'+r.plan_id+" · "+r.plan_name+'</div><span class="status '+cls+'">'+status+'</span>'+
    '<div class="mini-kpis"><div class="mini"><span>P50 경제적 NPV</span><strong>'+shortBn(r.expected_cost_p50_bn_krw_mean)+'</strong></div><div class="mini"><span>TCaR</span><strong>'+fmt(r.tcar_kkrw_per_tco2_mean,1)+'</strong></div><div class="mini"><span>공통 회피배출 분모</span><strong>'+fmt(r.common_avoided_emissions_mtco2,0)+'Mt</strong></div><div class="mini"><span>경계 반복빈도</span><strong>'+fmt(r.frontier_frequency_pct,0)+'%</strong></div></div><div class="logic-copy">'+r.portfolio_id+" · "+(planInfo().source_note||"")+"</div>";
  const items=[];
  if(!r.scenario_feasible)items.push("이 고정 포트폴리오는 탄소예산 또는 스크랩·수소·계통·동시공사·실패위험 기준을 충족하지 못해 경계와 추천에서 제외됩니다.");
  else if(dom)items.push("<strong>"+dom.plan_id+"</strong>는 P50을 "+fmt(r.expected_cost_p50_kkrw_per_tco2_mean-dom.expected_cost_p50_kkrw_per_tco2_mean,1)+"천원, TCaR을 "+fmt(r.tcar_kkrw_per_tco2_mean-dom.tcar_kkrw_per_tco2_mean,1)+"천원 동시에 낮춥니다.");
  else items.push("이 대안보다 P50과 TCaR을 동시에 낮추는 비교 계획은 없습니다.");
  items.push("현재 위험선호의 추천은 <strong>"+reco.plan_id+"</strong>입니다. 위험선호가 바뀌면 효율경계 위 최적점도 바뀝니다.");
  items.push("경계빈도는 3개 seed에서 효율경계에 포함된 비율입니다. 100%일수록 반복 실행에 안정적입니다.");
  $("frontier-explain").innerHTML=items.map(x=>"<li>"+x+"</li>").join("");
  $("frontier-count").textContent=fr.length+" / "+rows().filter(r=>!r.is_disclosed_plan&&r.scenario_feasible).length+"개 적격안";
}
function candidatePareto(input){
  return input.filter(p=>!input.some(q=>q.candidate_id!==p.candidate_id&&q.expected_cost_p50_kkrw_per_tco2_mean<=p.expected_cost_p50_kkrw_per_tco2_mean&&q.tcar_kkrw_per_tco2_mean<=p.tcar_kkrw_per_tco2_mean&&(q.expected_cost_p50_kkrw_per_tco2_mean<p.expected_cost_p50_kkrw_per_tco2_mean||q.tcar_kkrw_per_tco2_mean<p.tcar_kkrw_per_tco2_mean))).sort((a,b)=>a.expected_cost_p50_kkrw_per_tco2_mean-b.expected_cost_p50_kkrw_per_tco2_mean);
}
function robustChart(){
  const svg=$("robust-chart");svg.innerHTML="";
  const robust=candidateRobustRows(),reco=robustRecommendation(),ranked=[...robust].sort((a,b)=>(Number(b.robust_feasible)-Number(a.robust_feasible))||(a.maximum_regret_p50_kkrw_per_tco2_mean-b.maximum_regret_p50_kkrw_per_tco2_mean)),ids=new Set(ranked.slice(0,28).map(r=>r.candidate_id));
  const rr=candidateScenarioRows().filter(r=>ids.has(r.candidate_id)),xs=rr.map(r=>r.expected_cost_p50_kkrw_per_tco2_mean),ys=rr.map(r=>r.tcar_kkrw_per_tco2_mean);
  if(!rr.length){$("robust-card").innerHTML='<div class="logic-value">후보 결과 없음</div>';return}
  const range=(arr,padding)=>{const a=Math.min(...arr),b=Math.max(...arr),d=Math.max((b-a)*padding,2);return[a-d,b+d]},xr=range(xs,.12),yr=range([0,...ys],.08);
  const L=70,R=28,T=35,B=63,W=940-L-R,H=470-T-B,x=v=>L+(v-xr[0])/(xr[1]-xr[0])*W,y=v=>T+(yr[1]-v)/(yr[1]-yr[0])*H,colors=["#173f6a","#0f7c7b","#a6453c"];
  for(let i=0;i<=5;i++){const xv=xr[0]+(xr[1]-xr[0])*i/5,yv=yr[0]+(yr[1]-yr[0])*i/5;svg.append(svgEl("line",{x1:x(xv),y1:T,x2:x(xv),y2:T+H,stroke:"#e7ebf0"}));axisText(svg,x(xv),T+H+22,fmt(xv,0));svg.append(svgEl("line",{x1:L,y1:y(yv),x2:L+W,y2:y(yv),stroke:"#e7ebf0"}));axisText(svg,L-9,y(yv)+3,fmt(yv,0),"end")}
  ids.forEach(id=>{const pair=rr.filter(r=>r.candidate_id===id).sort((a,b)=>a.scenario_id.localeCompare(b.scenario_id));if(pair.length===2)svg.append(svgEl("line",{x1:x(pair[0].expected_cost_p50_kkrw_per_tco2_mean),y1:y(pair[0].tcar_kkrw_per_tco2_mean),x2:x(pair[1].expected_cost_p50_kkrw_per_tco2_mean),y2:y(pair[1].tcar_kkrw_per_tco2_mean),stroke:id===reco.candidate_id?"#a6453c":"#c8d2dc","stroke-width":id===reco.candidate_id?2.5:1,opacity:id===reco.candidate_id?1:.55}))});
  D.scenarios.forEach((s,index)=>{const points=rr.filter(r=>r.scenario_id===s.scenario_id&&r.scenario_feasible),fr=candidatePareto(points);if(fr.length>1)svg.append(svgEl("path",{d:fr.map((r,i)=>(i?"L ":"M ")+x(r.expected_cost_p50_kkrw_per_tco2_mean)+" "+y(r.tcar_kkrw_per_tco2_mean)).join(" "),fill:"none",stroke:colors[index%colors.length],"stroke-width":3}));});
  rr.forEach(r=>{const X=x(r.expected_cost_p50_kkrw_per_tco2_mean),Y=y(r.tcar_kkrw_per_tco2_mean),scenarioIndex=Math.max(0,D.scenarios.findIndex(s=>s.scenario_id===r.scenario_id)),isReco=r.candidate_id===reco.candidate_id;const dot=svgEl("circle",{cx:X,cy:Y,r:isReco?7:4.5,fill:r.scenario_feasible?colors[scenarioIndex%colors.length]:"#c58a2d",stroke:isReco?"#fff":"none","stroke-width":2});dot.onmousemove=e=>showTip(e,"<strong>"+r.candidate_id+" · "+r.template_plan_id+"</strong><br>"+scenarioLabel(r.scenario_id)+"<br>P50 "+fmt(r.expected_cost_p50_kkrw_per_tco2_mean,1)+" · TCaR "+fmt(r.tcar_kkrw_per_tco2_mean,1)+"<br>후회비용 "+fmt(r.scenario_regret_p50_kkrw_per_tco2_mean,1)+" · "+(r.scenario_feasible?"통합 적격":"제약 미충족"));dot.onmouseleave=()=>{$("tip").style.display="none"};svg.append(dot);if(isReco)axisText(svg,X+9,Y-10,r.candidate_id.slice(5,11),"start")});
  axisText(svg,L+W/2,462,"후보 P50 · 천원/tCO₂");svg.append(svgEl("text",{x:18,y:T+H/2,transform:"rotate(-90 18 "+(T+H/2)+")","text-anchor":"middle","font-size":10,fill:"#6b788a"},"후보 TCaR · P90−P50"));
  $("robust-legend").innerHTML=D.scenarios.map((s,i)=>'<span><i style="background:'+colors[i%colors.length]+'"></i>'+s.label+' 적격 경계</span>').join("")+'<span><i style="background:#c58a2d"></i>실행제약 미충족</span>';
  const eligible=robust.filter(r=>r.robust_feasible),frontier=eligible.filter(r=>r.robust_frontier_frequency_pct>0),top=[...eligible].sort((a,b)=>a.maximum_regret_p50_kkrw_per_tco2_mean-b.maximum_regret_p50_kkrw_per_tco2_mean).slice(0,4);
  $("robust-card").innerHTML='<div class="logic-label">REFINED ROBUST CANDIDATE · λ='+lambdaValue()+'</div><div class="logic-value">'+reco.candidate_id+' · '+reco.template_plan_id+'</div><span class="status '+(reco.robust_feasible?'':'warn')+'">'+(reco.robust_feasible?'모든 활성 시나리오 적격':'최소 위반 대안')+'</span><div class="mini-kpis"><div class="mini"><span>전체 생성</span><strong>'+fmt(D.meta.generated_candidate_count,0)+'개</strong></div><div class="mini"><span>정밀 shortlist</span><strong>'+fmt(D.meta.refined_candidate_count,0)+'개</strong></div><div class="mini"><span>강건 적격</span><strong>'+eligible.length+'개</strong></div><div class="mini"><span>강건 경계</span><strong>'+frontier.length+'개</strong></div><div class="mini"><span>최대후회 P50</span><strong>'+fmt(reco.maximum_regret_p50_kkrw_per_tco2_mean,1)+'</strong></div><div class="mini"><span>최악 TCaR</span><strong>'+fmt(reco.worst_case_tcar_kkrw_per_tco2_mean,1)+'</strong></div></div><div class="candidate-list">'+top.map(r=>'<div class="candidate-row"><span>'+r.candidate_id+' · '+r.template_plan_id+'</span><strong>후회 '+fmt(r.maximum_regret_p50_kkrw_per_tco2_mean,1)+'</strong></div>').join("")+'</div><div class="logic-copy">정밀 shortlist는 seed당 '+fmt(D.meta.refined_candidate_path_count,0)+'경로, 반복 합계 '+fmt(D.meta.effective_refined_candidate_paths,0)+'경로입니다. 최대후회 기준점도 같은 shortlist 안에서 계산합니다.</div>';
}
function robustExecution(){
  const reco=robustRecommendation(),fr=(D.refined_candidate_facility_rows||[]).filter(r=>r.company_id===company&&r.scenario_id===scenario&&r.candidate_id===reco.candidate_id).sort((a,b)=>b.baseline_emissions_mtco2-a.baseline_emissions_mtco2),rp=(D.refined_candidate_resource_rows||[]).filter(r=>r.company_id===company&&r.scenario_id===scenario&&r.candidate_id===reco.candidate_id),metric=candidateScenarioRows().find(r=>r.candidate_id===reco.candidate_id&&r.scenario_id===scenario);
  if(!fr.length||!rp.length||!metric){$("robust-execution-summary").innerHTML='<span>정밀 후보 실행자료 없음</span>';$("robust-facility-body").innerHTML='<tr><td>정밀 시설 결과 없음</td></tr>';$("robust-resource-cards").innerHTML="";$("robust-resource-body").innerHTML="";$("official-benchmarks").innerHTML="";return}
  const eShare=metric.electricity_shapley_variance_share_mean??metric.electricity_variance_share_mean,hShare=metric.hydrogen_shapley_variance_share_mean??metric.hydrogen_variance_share_mean,cShare=metric.capex_shapley_variance_share_mean??metric.capex_variance_share_mean;
  $("robust-execution-summary").innerHTML='<span class="summary-chip"><strong>'+reco.candidate_id+'</strong></span><span class="summary-chip">시나리오 <strong>'+scenarioLabel(scenario)+'</strong></span><span class="summary-chip">정밀 P50 <strong>'+fmt(metric.expected_cost_p50_kkrw_per_tco2_mean,1)+'</strong></span><span class="summary-chip">TCaR <strong>'+fmt(metric.tcar_kkrw_per_tco2_mean,1)+'</strong></span><span class="summary-chip">Shapley 전력/수소/건설 <strong>'+pct(eShare)+' / '+pct(hShare)+' / '+pct(cShare)+'</strong></span>';
  $("robust-facility-body").innerHTML=fr.map(r=>'<tr><td><div class="facility-name"><strong>'+r.facility_name+'</strong><span>'+r.region+' · '+fmt(r.output_mt,2)+'Mt</span></div></td><td><div class="tech-path"><span class="tech-old">'+r.baseline_technology_id+'</span><span class="arrow">→</span><span class="tech-new">'+r.technology_id+'</span></div></td><td>'+r.transition_year+'</td><td>'+fmt(r.aligned_capex_bn_krw,0)+'bn</td><td>'+fmt(r.base_case_net_cash_cost_after_support_bn_krw,0)+'bn</td><td>'+fmt(r.base_case_avoided_carbon_cost_value_bn_krw,0)+'bn</td><td>'+fmt(r.base_case_net_cost_bn_krw,0)+'bn</td><td>'+fmt(r.annual_avoided_emissions_mtco2,1)+'Mt</td></tr>').join("");
  const peak=key=>Math.max(...rp.map(r=>Number(r[key]||0)),0),resources=[["스크랩",peak("scrap_utilization_pct"),"scrap_headroom_mt","Mt"],["수소",peak("hydrogen_utilization_pct"),"hydrogen_headroom_mt","Mt"],["증분계통",peak("incremental_grid_utilization_pct"),"incremental_grid_headroom_twh","TWh"]];
  $("robust-resource-cards").innerHTML=resources.map(x=>{const critical=rp.reduce((a,b)=>Number(a[x[2]])<Number(b[x[2]])?a:b);return '<div class="resource-card"><span>'+x[0]+' 최대 활용률</span><strong class="'+(x[1]>100?'delta bad':'')+'">'+fmt(x[1],0)+'%</strong><small>'+scenarioLabel(scenario)+' · 2026–2040</small><small>최소 여유 '+fmt(critical[x[2]],2)+x[3]+' · '+critical.year+'</small></div>'}).join("");
  $("robust-resource-body").innerHTML=rp.filter(r=>[2030,2035,2040].includes(Number(r.year))).map(r=>'<tr><td>'+r.year+'</td><td>'+fmt(r.scrap_demand_mt,2)+' / '+fmt(r.scrap_supply_mt,2)+'</td><td>'+fmt(r.hydrogen_demand_mt,2)+' / '+fmt(r.hydrogen_supply_mt,2)+'</td><td>'+fmt(r.incremental_grid_demand_twh,2)+' / '+fmt(r.incremental_grid_supply_twh,2)+'</td><td><span class="metric-pill '+(r.resource_feasible?'':'off')+'">'+(r.resource_feasible?'여유 내':'초과')+'</span></td></tr>').join("");
  const benchmarks=(D.resource_benchmarks||[]).filter(r=>r.country_code===companyInfo().country_code);
  $("official-benchmarks").innerHTML=benchmarks.map(r=>'<div class="resource-card"><span>공식 '+r.resource_type+' · '+r.benchmark_year+'</span><strong>'+(r.benchmark_value===null?'정성 정책':fmt(r.benchmark_value,Number(r.benchmark_value)<100?1:0)+' '+r.unit)+'</strong><small>'+r.source_org+' · 회사 한도 아님</small></div>').join("");
}
function facilityTable(){
  const fr=facilities().sort((a,b)=>b.baseline_emissions_mtco2-a.baseline_emissions_mtco2),maxEm=Math.max(...fr.map(r=>r.baseline_emissions_mtco2),1);
  $("facility-body").innerHTML=fr.map(r=>
    '<tr><td><div class="facility-name"><strong>'+r.facility_name+"</strong><span>"+r.region+" · "+fmt(r.output_mt,2)+'Mt 생산</span></div></td>'+
    '<td><div class="em-bar"><div class="em-track"><div class="em-fill" style="width:'+(100*r.baseline_emissions_mtco2/maxEm)+'%"></div></div><strong>'+fmt(r.baseline_emissions_mtco2,1)+'Mt</strong></div></td>'+
    '<td><div class="tech-path"><span class="tech-old">'+r.baseline_technology_id+'</span><span class="arrow">→</span><span class="tech-new">'+r.technology_id+"</span></div></td>"+
    '<td><div class="timeline" style="--pos:'+(100*(r.transition_year-2026)/(2040-2026))+'%"><span>'+r.transition_year+"</span></div></td>"+
    "<td>"+fmt(r.aligned_capex_bn_krw,0)+"bn</td><td>"+fmt(r.base_case_net_cost_bn_krw,0)+"bn</td><td>"+fmt(r.annual_avoided_emissions_mtco2,1)+"Mt</td><td>"+fmt(r.residual_emissions_mtco2,1)+"Mt</td></tr>"
  ).join("");
  $("facility-foot").innerHTML="<tr><td>선택 계획 합계 · "+fr.length+"개 블록</td><td>"+fmt(sum(fr,"baseline_emissions_mtco2"),1)+"Mt</td><td></td><td></td><td>"+fmt(sum(fr,"aligned_capex_bn_krw"),0)+"bn</td><td>"+fmt(sum(fr,"base_case_net_cost_bn_krw"),0)+"bn</td><td>"+fmt(sum(fr,"annual_avoided_emissions_mtco2"),1)+"Mt</td><td>"+fmt(sum(fr,"residual_emissions_mtco2"),1)+"Mt</td></tr>";
  const earliest=Math.min(...fr.map(r=>r.transition_year)),latest=Math.max(...fr.map(r=>r.transition_year));
  $("facility-summary").innerHTML='<span class="summary-chip"><strong>'+fr.length+'</strong>개 블록</span><span class="summary-chip"><strong>'+earliest+"–"+latest+'</strong> 전환</span><span class="summary-chip">기준가격 NPV <strong>'+fmt(sum(fr,"base_case_net_cost_bn_krw"),0)+"bn</strong></span>";
}
function waterfall(){
  const svg=$("waterfall-chart");svg.innerHTML="";const r=selected();
  const items=[
    ["기술 CAPEX",r.capex_cost_p50_bn_krw_mean],["고정 OPEX",r.fixed_opex_cost_p50_bn_krw_mean],["전력",r.electricity_cost_p50_bn_krw_mean],["수소",r.hydrogen_cost_p50_bn_krw_mean],["계약 프리미엄",r.contract_premium_p50_bn_krw_mean],["탄소가치",r.carbon_value_p50_bn_krw_mean],["정책지원",r.policy_support_p50_bn_krw_mean],["중앙값 보정",r.component_reconciliation_p50_bn_krw_mean]
  ];
  let cumulative=0;const steps=items.map(item=>{const start=cumulative;cumulative+=item[1];return{label:item[0],value:item[1],start:start,end:cumulative}});
  const total=r.expected_cost_p50_bn_krw_mean,all=[0,total,...steps.flatMap(s=>[s.start,s.end])],min=Math.min(...all),max=Math.max(...all),pad=Math.max((max-min)*.1,100);
  const L=58,R=24,T=28,B=78,W=940-L-R,H=420-T-B,scale=v=>T+(max+pad-v)/(max-min+2*pad)*H;
  for(let i=0;i<=5;i++){const v=min-pad+(max-min+2*pad)*i/5;svg.append(svgEl("line",{x1:L,y1:scale(v),x2:L+W,y2:scale(v),stroke:"#e6ebf0"}));axisText(svg,L-8,scale(v)+3,fmt(v,0),"end")}
  const gap=W/(steps.length+1),bw=Math.min(58,gap*.62);
  steps.forEach((s,i)=>{
    const X=L+gap*(i+.55),top=Math.min(scale(s.start),scale(s.end)),height=Math.max(2,Math.abs(scale(s.start)-scale(s.end))),positive=s.value>=0;
    svg.append(svgEl("rect",{x:X-bw/2,y:top,width:bw,height:height,rx:3,fill:positive?"#517b9f":"#2d8a71"}));
    if(i<steps.length-1)svg.append(svgEl("line",{x1:X+bw/2,y1:scale(s.end),x2:L+gap*(i+1.55)-bw/2,y2:scale(s.end),stroke:"#aab5c0","stroke-dasharray":"3 3"}));
    axisText(svg,X,T+H+20,s.label);axisText(svg,X,positive?top-7:top+height+13,signed(s.value,0));
  });
  const X=L+gap*(steps.length+.55),top=Math.min(scale(0),scale(total)),height=Math.max(2,Math.abs(scale(0)-scale(total)));
  svg.append(svgEl("rect",{x:X-bw/2,y:top,width:bw,height:height,rx:3,fill:"#102f50"}));axisText(svg,X,T+H+20,"Net P50");axisText(svg,X,top-7,fmt(total,0));axisText(svg,14,T+H/2,"KRW bn","start");
}
function riskAndCoverage(){
  const r=selected(),p=planInfo();
  const factors=[["전력","#0f7c7b",r.electricity_variance_share_mean],["수소입력","#6c58a5",r.hydrogen_variance_share_mean],["건설 CAPEX","#74879b",r.capex_variance_share_mean]];
  $("risk-bars").innerHTML=factors.map(f=>'<div class="risk-row"><strong>'+f[0]+'</strong><div class="risk-track"><div class="risk-fill" style="width:'+(100*f[2])+"%;background:"+f[1]+'"></div></div><span class="risk-num">'+pct(f[2])+" · "+fmt(f[2]*r.tcar_kkrw_per_tco2_mean,1)+"천원</span></div>").join("");
  $("coverages").innerHTML=[["전력 PPA",p.ppa_share],["수소 계약",p.hydrogen_contract_share],["고정 EPC",p.fixed_epc_share],["CCfD 적용",p.ccfd_share]].map(item=>'<div class="coverage"><span>'+item[0]+"</span><strong>"+pct(item[1])+"</strong></div>").join("");
}
function planTable(){
  const fr=frontier(),reco=recommended();
  $("plan-body").innerHTML=rows().map(r=>{
    const isF=fr.some(f=>f.plan_id===r.plan_id);
    const state=!r.scenario_feasible?'<span class="metric-pill off">실행 제약 미충족</span>':r.plan_id===reco.plan_id?'<span class="metric-pill reco">추천</span>':r.is_disclosed_plan?'<span class="metric-pill off">공시 프록시</span>':isF?'<span class="metric-pill">효율경계</span>':'<span class="metric-pill off">지배됨</span>';
    return '<tr class="'+(r.plan_id===plan?"selected ":"")+(r.is_disclosed_plan?"current":"")+'" data-plan="'+r.plan_id+'"><td><div class="table-plan"><strong>'+r.plan_id+" · "+r.plan_name+"</strong><span>"+(planInfo(r.plan_id).source_note||"")+"</span></div></td><td>"+state+"</td><td>"+fmt(r.expected_cost_p50_bn_krw_mean,0)+"bn</td><td>"+fmt(r.expected_cost_p50_kkrw_per_tco2_mean,1)+"</td><td>"+fmt(r.tcar_kkrw_per_tco2_mean,1)+"</td><td>"+fmt(r.p90_cost_to_ebitda_x_mean,2)+"×</td><td>"+fmt(r.aligned_capex_bn_krw,0)+"bn</td><td>"+fmt(r.policy_support_dependence_kkrw_per_tco2_mean,1)+"</td><td>"+fmt(r.frontier_frequency_pct,0)+"%</td></tr>";
  }).join("");
  document.querySelectorAll("[data-plan]").forEach(row=>row.onclick=()=>{plan=row.dataset.plan;render()});
}
function projectEvidence(){
  const projects=(D.transition_projects||[]).filter(p=>p.company_id===company),c=companyInfo();
  const statusLabels={operating:"가동 중",announced_demo:"실증 준비",investment_decided:"투자 결정",feasibility_study:"타당성 검토",completed:"완료",demonstration_completed:"실증 완료"};
  const mappingLabels={unmapped_new_asset:"신규자산·모델 미편입",unmapped_demo_asset:"실증자산·모델 미편입",timing_and_site_anchor:"시설·시점 앵커",unmapped_group_asset:"그룹자산·모델 미편입",hybrid_route_evidence:"혼합경로 증거",direct_historical_anchor:"직접 과거 앵커",technology_performance_anchor:"기술성능 앵커"};
  $("project-count").textContent=projects.length+"건 · 기준일 "+D.meta.evidence_extraction_date;
  $("project-body").innerHTML=projects.map(p=>{
    const evidence=(D.technology_cost_evidence||[]).find(e=>e.project_id===p.project_id),tech=(D.technologies||[]).find(t=>t.technology_id===p.technology_id),modelUnit=tech?tech.capex_bn_krw_per_mtpa*c.capex_cost_index:null;
    const support=p.government_support_pct===null?"미공시":pct(p.government_support_pct,1);
    const disclosed=evidence?fmt(evidence.normalized_capex_bn_krw_per_mtpa,0)+"bn/Mtpa":"—";
    return '<tr><td><div class="table-plan"><strong>'+p.project_name+'</strong><span>'+p.technology_id+' · '+p.confidence_grade+'</span></div></td><td><span class="metric-pill '+(p.model_mapping_status.includes("unmapped")?'off':'')+'">'+(statusLabels[p.project_status]||p.project_status)+'</span><br><small>'+(mappingLabels[p.model_mapping_status]||p.model_mapping_status)+'</small></td><td>'+(p.capacity_mtpa===null?'—':fmt(p.capacity_mtpa,2)+'Mtpa')+'</td><td>'+(p.capex_bn_krw===null?'미공시':fmt(p.capex_bn_krw,0)+'bn')+'</td><td>'+support+'</td><td>'+p.operation_start_label+'</td><td>'+disclosed+'</td><td>'+(modelUnit===null?'—':fmt(modelUnit,0)+'bn/Mtpa')+'</td><td><a href="'+p.source_url+'" target="_blank" rel="noopener">원문 ↗</a></td></tr>';
  }).join("");
  const costRows=(D.technology_cost_evidence||[]).filter(e=>e.company_id===company),units=costRows.map(e=>e.normalized_capex_bn_krw_per_mtpa);
  $("project-evidence-note").innerHTML='<strong>범위 해석.</strong> '+(units.length?'이 회사의 공시 총사업비 원단위는 '+fmt(Math.min(...units),0)+'–'+fmt(Math.max(...units),0)+'bn KRW/Mtpa입니다. ':'공시 총사업비를 용량으로 나눌 수 있는 프로젝트가 아직 없습니다. ')+'모델 원단위는 공통 기술패키지의 스크리닝 값이고, 공시는 부두·물류·전력·후공정 또는 혼합공정을 포함할 수 있습니다. 같은 범위로 bridge하기 전에는 공시값의 단순 평균이나 직접 치환을 금지합니다.';
}
function sources(){
  $("sources").innerHTML=D.companies.map(c=>'<article class="source"><h3>'+c.company_name+" · "+c.base_year+"</h3><p>생산 "+fmt(c.production_mt,2)+"Mt · Scope 1+2 "+fmt(c.scope12_emissions_mtco2,2)+"Mt · 2030 앵커 "+fmt(c.target_2030_mtco2,2)+"Mt</p><p>"+c.source_note+'</p><a href="'+c.source_url+'" target="_blank" rel="noopener">'+c.source_name+" ↗</a></article>").join("");
}
function scenarioProvenance(){
  const s=scenarioInfo(),pending=D.scenario_registry.filter(x=>!x.is_active).map(x=>x.scenario_id).join(", ");
  $("scenario-provenance").innerHTML="<strong>시나리오 출처</strong>"+s.label+" · "+s.data_status+". "+s.source_note+" 비활성 공식 추출 슬롯: "+pending+".";
}
function render(){
  setupControls();decision();kpis();emissionsChart();logic();frontierChart();planCard();robustChart();robustExecution();facilityTable();waterfall();riskAndCoverage();planTable();projectEvidence();sources();scenarioProvenance();
}
$("runs").textContent=D.meta.run_count+"회 반복 · seeds "+D.meta.seeds.join(", ");
$("paths").textContent="계획·시나리오당 "+fmt(D.meta.effective_paths_per_plan,0)+"개 모의경로";
$("years").textContent="분석기간 "+D.meta.year_start+"–"+D.meta.year_end;
$("model-tag").textContent="MODEL v"+D.meta.model_version+" · "+D.meta.data_status;
$("footer").textContent="Capital Allocation Pathway v"+D.meta.model_version+" · 대표 seed "+D.meta.representative_seed+" · 시설 스케줄은 결정론적 최적화, 비용은 반복 Monte Carlo 평균";
render();
'''
