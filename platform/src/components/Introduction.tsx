'use client';

import {useEffect, useId, useState, useSyncExternalStore} from 'react';
import research from '@/lib/research.json';
import {fmt} from '@/lib/format';

// Every plotted point and numerical comparison comes from the published FIN snapshot.
const points=research.candidates.filter(r=>r.company_id==='POSCO'&&r.scenario==='NZ15');
const eligible=points.filter(r=>r.decision_eligible);
const leastCost=[...eligible].sort((a,b)=>a.mean-b.mean)[0];
const leastRisk=[...eligible].sort((a,b)=>a.es_abs-b.es_abs)[0];
const minX=Math.floor(Math.min(...points.map(r=>r.mean))/5000)*5000;
const maxX=Math.ceil(Math.max(...points.map(r=>r.mean))/5000)*5000;
const maxY=Math.ceil(Math.max(...points.map(r=>r.es_abs))/20000)*20000;
const minY=Math.floor(Math.min(...points.map(r=>r.es_abs))/20000)*20000;
const x=(v:number)=>84+(v-minX)/(maxX-minX)*560;
const y=(v:number)=>414-(v-minY)/(maxY-minY)*318;
const chapters=[
 {title:'전환 일정',text:'동일한 생산량과 누적 배출예산을 적용한 투자 일정 후보입니다. 계약 미적용 결과를 표시합니다.'},
 {title:'PPA·EPC 계약',text:'전력 PPA와 건설비 EPC 계약을 적용한 후보입니다. 계약 미적용 후보와 동일한 가격경로로 평가합니다.'},
 {title:'비용–위험 효율경계 (v2)',text:'표본 지배 후보를 뺀 뒤 (평균 증분비용, 계획 자체 ES90)의 비지배 후보를 표시합니다. 위험 축이 계획의 절대 비용분포라서 탄소·연료 노출을 없애는 투자가 위험 감소로 계산됩니다.'},
];
const motionQuery='(prefers-reduced-motion: reduce)';
const subscribe=(callback:()=>void)=>{const q=window.matchMedia(motionQuery);q.addEventListener('change',callback);return()=>q.removeEventListener('change',callback);};

export default function Introduction({onNavigate}:{onNavigate:(tab:string)=>void}){
 const [chapter,setChapter]=useState(0);
 const [playing,setPlaying]=useState(true);
 const [replay,setReplay]=useState(0);
 const reducedMotion=useSyncExternalStore(subscribe,()=>window.matchMedia(motionQuery).matches,()=>false);
 const shown=reducedMotion&&playing?2:chapter;
 const svgId=useId().replaceAll(':','');
 useEffect(()=>{
  if(!playing||reducedMotion)return;
  const second=setTimeout(()=>setChapter(1),2600);
  const third=setTimeout(()=>{setChapter(2);setPlaying(false);},5600);
  return()=>{clearTimeout(second);clearTimeout(third);};
 },[playing,replay,reducedMotion]);

 return <div className="tcar-introduction">
  <section className="intro-opening" aria-labelledby="intro-title">
   <div className="intro-kicker"><span>PLANiT ANALYTICAL TOOLS / TRANSITION FINANCE</span><span>{research.metadata.horizon.replace('–','—')}</span></div>
   <div className="intro-copy">
    <div><p className="intro-wordmark">Transition Cost at Risk</p><h1 id="intro-title">기업 전환계획의<br/>비용·위험 분석</h1></div>
    <div className="intro-intent"><p>생산량과 감축목표를 고정하고,<br className="desktop-break"/> 설비 전환 일정·전력구매·건설비 계약에 따른<br className="desktop-break"/> 증분비용과 가격위험을 비교합니다.</p><button className="intro-primary" onClick={()=>onNavigate('research')}>전환계획 비교 <span aria-hidden="true">↗</span></button><button className="intro-secondary" onClick={()=>onNavigate('method')}>모형의 작동 원리 <span aria-hidden="true">→</span></button></div>
   </div>
   <div className="intro-figure-grid">
    <figure className={`intro-scene scene-step-${shown}`}>
     <div className="intro-figure-label"><span>POSCO · NZ15 / 비용–위험 후보 · v2 · 탄소지출 포함</span><span>십억 KRW2025 대용치</span></div>
     <svg viewBox="0 0 730 490" role="img" aria-labelledby={`${svgId}-title ${svgId}-desc`}>
      <title id={`${svgId}-title`}>전환 일정과 계약에 따른 평균 증분비용·계획 ES90</title>
      <desc id={`${svgId}-desc`}>{points.length}개 저장 후보. 평균 최소 후보의 평균 비용은 {fmt(leastCost.mean)}, ES90은 {fmt(leastCost.es_abs)}. ES90 최소 후보의 평균 비용은 {fmt(leastRisk.mean)}, ES90은 {fmt(leastRisk.es_abs)}. 점 사이의 계획은 보간하지 않습니다.</desc>
      <text className="intro-axis-title" x="84" y="58">ES90 · 계획 자체 비용분포의 상위 10% 평균</text>
      {[0,.25,.5,.75,1].map(t=><g key={t} className="intro-chart-grid"><line x1="84" x2="644" y1={y(minY+t*(maxY-minY))} y2={y(minY+t*(maxY-minY))}/><text x="70" y={y(minY+t*(maxY-minY))+5} textAnchor="end">{fmt((minY+t*(maxY-minY))/1000,0)}k</text></g>)}
      {[0,.25,.5,.75,1].map(t=><text className="intro-chart-tick" key={t} x={x(minX+t*(maxX-minX))} y="444" textAnchor="middle">{fmt((minX+t*(maxX-minX))/1000,1)}k</text>)}
      <text className="intro-axis-title" x="644" y="477" textAnchor="end">평균 증분 비용 →</text>
      {points.map(p=>{
       const contracted=p.ppa_share>0||p.epc===1;
       const frontier=shown===2&&p.on_mean_esabs_frontier;
       return <circle key={p.plan_id} className={`intro-point ${contracted?'contracted':''} ${frontier?'frontier':''}`} cx={x(p.mean)} cy={y(p.es_abs)} r={frontier?5:3.5}>
        <title>{p.plan_id}: 평균 {fmt(p.mean)}, ES90 {fmt(p.es_abs)}, PPA {fmt(p.ppa_share*100,0)}%, EPC {p.epc?'고정':'미적용'}</title>
       </circle>;
      })}
      <g className="intro-chart-annotation">
       <circle cx={x(leastCost.mean)} cy={y(leastCost.es_abs)} r="7"/>
       <path d={`M${x(leastCost.mean)},${y(leastCost.es_abs)-10} V${y(leastCost.es_abs)-55} H${x(leastCost.mean)+110}`}/>
       <text x={x(leastCost.mean)+12} y={y(leastCost.es_abs)-64}>평균 비용 최소</text>
       <circle cx={x(leastRisk.mean)} cy={y(leastRisk.es_abs)} r="7"/>
       <path d={`M${x(leastRisk.mean)+10},${y(leastRisk.es_abs)} H${x(leastRisk.mean)+154}`}/>
       <text x={x(leastRisk.mean)+32} y={y(leastRisk.es_abs)-13}>ES90 최소</text>
      </g>
     </svg>
     <figcaption className="intro-legend"><span><i/>계약 없는 일정</span><span className={shown<1?'faded':''}><i className="contract"/>계약 적용 후보</span><span className={shown<2?'faded':''}><i className="frontier"/>비지배 후보</span></figcaption>
    </figure>
    <aside className="intro-reading"><p className="intro-section-index">후보 구성</p><h2>투자 일정·계약별<br/>비용과 ES90</h2><div className="intro-chapters">{chapters.map((c,i)=><button className={shown===i?'active':''} key={c.title} aria-pressed={shown===i} onClick={()=>{setPlaying(false);setChapter(i);}}><span>0{i+1}</span><div><strong>{c.title}</strong><small>{c.text}</small></div></button>)}</div>{!reducedMotion&&<button className="intro-replay" onClick={()=>{if(playing)setPlaying(false);else{setChapter(0);setReplay(n=>n+1);setPlaying(true);}}}>{playing?'일시정지 Ⅱ':'다시 보기 ↺'}</button>}</aside>
   </div>
   <div className="intro-caption"><p>{research.metadata.information_date.replaceAll('-','.')} 기업 연구 결과 (v2) · 누적 Scope 1 예산 · {points.length}개 후보 · 눈금 k = 1천<br/>증분 비용에는 시나리오 탄소지출(총의무 p·E, 무상할당 미반영)이 포함됩니다. POSCO·NZ15의 음의 평균은 이 탄소 회피 항목 때문이며, 탄소가격을 0으로 두면 양수입니다. 시나리오 NZ15·B20은 로컬 EST_v0 대용치입니다. 같은 좌표에 여러 후보가 겹칠 수 있으며, 점 사이의 계획은 보간하지 않습니다.</p><span>조건부 모형 결과</span></div>
  </section>

  <section className="intro-questions" aria-labelledby="questions-title">
   <div><span className="intro-section-index">분석 구성</span><h2 id="questions-title">전환계획 평가</h2><p>기업 내 투자·계약 대안을 비교하는 연구·교육용 알파 도구입니다.<br/>투자자문이나 여신·인수 심사 자료가 아닙니다.</p></div>
   <div className="intro-question-list">
    <button onClick={()=>onNavigate('research')}><span>01</span><div><h3>기업별 투자 일정·계약 비교</h3><p>한국·일본 철강·석유화학 네 기업의 {research.metadata.candidate_count}개 저장 후보에서 평균 증분비용과 계획 자체 ES90·TCaR를 비교합니다 (v1·v2 병기).</p></div><span aria-hidden="true">↗</span></button>
    <button onClick={()=>onNavigate('simulator')}><span>02</span><div><h3>공정 참조 모형 (부속 · 기업 경계 결과와 무관)</h3><p>공동 가격·부분 운영비, NCC 현금비용, 전환 시점의 세 참조 모형을 새 가정으로 계산합니다. 위 기업 후보의 민감도가 아닙니다.</p></div><span aria-hidden="true">↗</span></button>
    <button onClick={()=>onNavigate('data')}><span>03</span><div><h3>입력 데이터와 출처</h3><p>기업·기술·감축예산·가격 데이터의 단위, 출처와 공정 경계를 확인합니다.</p></div><span aria-hidden="true">↗</span></button>
   </div>
  </section>

  <section className="intro-research" aria-labelledby="project-research-title">
   <div className="intro-research-index"><span>PLANiT RESEARCH</span><span>전환금융 연구 프로젝트<br/>방법론 · 조건부 기업 사례 · 참조 실험</span></div>
   <div className="intro-research-body"><p className="intro-section-index">연구 개요</p><h2 id="project-research-title">기후 전환비용의 불확실성과<br/>기업 내 효율경계</h2><p className="intro-english" lang="en">Comparing facility and contract choices with Transition Cost at Risk</p><p>설비 전환은 원료·에너지 구매량과 투자비에, 계약은 가격변동 노출과 비용 부담 주체에 영향을 줍니다. 이 연구는 동일한 생산·배출·회계 조건에서 투자 일정과 계약 후보의 할인 증분비용을 평가합니다.</p><p>비용 수준은 평균·중앙값·ES로, 상위 비용 간격은 TCaR로 평가합니다. 효율경계는 실제 평가한 후보 가운데 비용과 위험을 함께 개선할 다른 후보가 없는 점들의 집합입니다.</p><div className="intro-research-links"><button onClick={()=>onNavigate('method')}>방법론과 해석 범위 →</button><button onClick={()=>onNavigate('research')}>기업 사례 결과 →</button></div><p className="intro-research-note">기업 연구는 저장 결과이며 세 시뮬레이터는 별도의 공정 참조 실험입니다. TCaR를 필요자금·대출한도·기업가치로 해석하지 않습니다.</p></div>
  </section>

  <section className="intro-connection" aria-labelledby="related-tools-title"><div><span className="intro-section-index">PLANiT 분석 도구</span><h2 id="related-tools-title">K-ETS와 TCaR의<br/>분석 범위</h2><p>K-ETS는 배출권 시장의 가격경로를,<br/>TCaR는 기업의 전환계획별 비용분포를 분석합니다.</p></div><div className="intro-tool-comparison"><a href="https://kets-outlook.vercel.app/" target="_blank" rel="noreferrer"><span>01 / CARBON MARKETS</span><h3>K-ETS Outlook <b aria-hidden="true">↗</b></h3><p>배출총량·시장안정화 규칙·감축비용이 배출권 가격과 기술비용 문턱에 미치는 영향을 분석합니다.</p></a><button onClick={()=>onNavigate('research')}><span>02 / TRANSITION FINANCE</span><h3>Transition Cost at Risk <b aria-hidden="true">→</b></h3><p>기업의 설비 일정·에너지 조달·건설 계약이 조건부 현금비용과 상위 비용위험에 미치는 영향을 비교합니다.</p></button><p className="intro-connection-note">현재 두 도구의 계산기는 직접 연결되어 있지 않습니다. K-ETS 가격을 TCaR에 적용하려면 시나리오·가격연도·탄소지출·기업 경계를 먼저 맞춰야 합니다.</p></div></section>

  <section className="intro-source-strip"><div><span className="intro-section-index">데이터와 해석</span><p>자료 출처·가정·적용 범위</p></div><p>결과는 공정 사양·가격 시나리오·계약과 비용 범위에 조건부입니다. 기업 사례의 EST_v0 경로와 참조 모형의 IEA 경로를 구분하고, 시설별 비공개 입력은 기업 수준으로 집계합니다.</p><button onClick={()=>onNavigate('data')}>데이터·출처 ↗</button></section>
 </div>;
}
