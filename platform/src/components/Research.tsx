'use client';
import {useMemo,useState} from 'react';
import {ResponsiveContainer,ScatterChart,Scatter,XAxis,YAxis,CartesianGrid,Tooltip,ReferenceDot} from 'recharts';
import research from '@/lib/research.json';
import {fmt,csvDownload} from '@/lib/format';
const COMPANIES:Record<string,string>={POSCO:'POSCO',NSC:'Nippon Steel',LOTTE:'LOTTE Chemical',MCI:'Mitsui Chemicals'};
type Row=Record<string,any>;
// v2 (2026-09-10) is canonical; v1 (2026-09-05) is preserved so the change can be inspected side by side.
const VERSIONS={v23:research as Row,v22:(research as Row).v22 as Row,v21:(research as Row).v21 as Row,v2:(research as Row).v2 as Row,v1:(research as Row).v1 as Row};
const AXES:Record<string,{label:string;flag:string;note:string;v2only:boolean}>={
 es_abs:{label:'ES90 · 계획 자체 비용분포 (v2 정본)',flag:'on_mean_esabs_frontier',note:'계획의 절대 현금비용 상위 10% 평균 · 노출을 없앤 계획은 낮게 나옴',v2only:true},
 tcar_abs:{label:'TCaR90 · 계획 자체 비용분포',flag:'on_mean_tcarabs_frontier',note:'절대 비용의 P90 − P50',v2only:true},
 es_alpha:{label:'ES90 · 증분(기준선 대비)',flag:'on_mean_es_frontier',note:'무전환 기준선 대비 증분비용의 상위 10% 평균 · v1 축',v2only:false},
 tcar:{label:'TCaR90 · 증분(기준선 대비)',flag:'on_mean_tcar_frontier',note:'증분비용의 P90 − P50 · 기준선 추적오차를 재므로 감축이 위험으로 잡힘',v2only:false},
};
export default function Research() {
 const [version,setVersion]=useState<'v23'|'v22'|'v21'|'v2'|'v1'>('v23');
 const [company,setCompany]=useState('POSCO'); const [scenario,setScenario]=useState('NZ15');
 const [axisKey,setAxisKey]=useState<string>('es_abs'); const [criterion,setCriterion]=useState<'mean'|'risk'>('mean');
 const data=VERSIONS[version]; const meta=data.metadata as Row;
 const axis=version==='v1'&&AXES[axisKey].v2only?'es_alpha':axisKey; const ax=AXES[axis];
 const rows=useMemo(()=>(data.candidates as Row[]).filter(r=>r.company_id===company&&r.scenario===scenario),[data,company,scenario]);
 const eligible=rows.filter(r=>r.decision_eligible);
 const chosen=[...eligible].sort((a,b)=>criterion==='mean'?a.mean-b.mean:a[axis]-b[axis])[0];
 const frontier=rows.filter(r=>r[ax.flag]);
 const others=rows.filter(r=>!frontier.includes(r));
 const schedules=new Set(frontier.map(r=>r.base_plan_id)).size;
 const riskLabel=ax.label.split(' · ')[0];
 return <>
  <div className="section-heading"><div><span className="eyebrow">01 / CORPORATE RESEARCH</span><h1>기업 전환계획 비교</h1><p>같은 생산·감축 조건에서 투자 일정과 전력·건설 계약 후보의 비용과 위험을 비교합니다.</p></div><span className="status">{meta.label}</span></div>
  <div className="control-strip"><label>방법론 판본<select value={version} onChange={e=>setVersion(e.target.value as 'v23'|'v22'|'v21'|'v2'|'v1')}><option value="v23">v2.3 · 일정 메뉴 재생성 · 실질 무위험 2.4% (정본)</option><option value="v22">v2.2 · 구조적 수소가·KAU 2026, 구 메뉴 (보존)</option><option value="v21">v2.1 · 순거래 p·(E−A), 정책목표 수소가 (보존)</option><option value="v2">v2.0 · 총의무 p·E (보존)</option><option value="v1">v1 · 2026-09-05 (보존)</option></select></label><label>분석 기업<select value={company} onChange={e=>setCompany(e.target.value)}>{Object.entries(COMPANIES).map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></label><label>감축 시나리오<select value={scenario} onChange={e=>setScenario(e.target.value)}><option value="NZ15">NZ15 · IEA NZE 앵커 (선진국 탄소가·연료가)</option><option value="B20">B20 · IEA STEPS 앵커 (공표정책 — 2°C 정합 아님)</option></select></label><label>위험 지표<select value={axis} onChange={e=>setAxisKey(e.target.value)}>{Object.entries(AXES).filter(([,a])=>version!=='v1'||!a.v2only).map(([k,a])=><option key={k} value={k}>{a.label}</option>)}</select></label><label>후보 선택<select value={criterion} onChange={e=>setCriterion(e.target.value as typeof criterion)}><option value="mean">평균 비용 최소</option><option value="risk">{riskLabel} 최소</option></select></label><button className="button secondary" onClick={()=>csvDownload(`${company}-${scenario}-${version}-candidates.csv`,rows)}>데이터 내려받기 ↓</button></div>
  <div className="notice compact"><span className="notice-index">연구 가정</span>2027–2050 · 누적 Scope 1 예산(연간 상한을 전 기간 충족한 일정은 0개) · 고정 생산 · <b>탄소지출 포함</b>({version==='v21'||version==='v22'||version==='v23'?'순거래 p·(E−A), A = 시나리오 기업 예산경로 (규칙 대용치)':'총의무 p·E, 무상할당 미반영'}) · 시나리오는 IEA GEC 2025 앵커(탄소·연료) + EST 보간(전력·예산)이며 NGFS/GCAM 아님 · {version==='v22'||version==='v23'?'수소 중심가 = 전력가×52 kWh/kg + 전해조 상각(구조적)':'수소 중심가 = 정책목표(3,500원/kg 등)'} · 기업 전체가 아닌 추정 자산 포트폴리오</div>
  {version!=='v1'?<div className="notice compact"><span className="notice-index">v2 변경</span>확률 요인은 검증 계열(KPX SMP·JEPX, KAU, World Bank 석탄·LNG 연간)로만 보정하고 상관을 실제 추정({(meta.correlation?.overlap?.['elec|gas']??'—')}개 연간 겹침) · 수소는 전력에서 구조 파생, 건설비는 결정론 · PPA는 전환이 추가한 전력에만 적용 · 정본 경계는 (평균 증분비용, 계획 자체 ES90)</div>
  :<div className="notice compact"><span className="notice-index">v1 한계</span>h2·capex 변동성은 사전값, 상관은 단위행렬, PPA가 기준선 공통 물량까지 고정, 경계 축은 (P50, 증분 TCaR) — 2026-09-10 외부감사에서 치명으로 분류된 규약입니다. 비교를 위해 보존합니다.</div>}
  {chosen&&<div className="kpis">
   <Kpi label="평균 증분 비용" value={chosen.mean} note="무전환 기준선 대비 할인 현금비용 · 탄소지출 포함"/>
   {version!=='v1'?<Kpi label="탄소지출 차이" value={chosen.carbon_delta} note="증분비용 중 시나리오 탄소가격 항목 (음수 = 회피)"/>:<Kpi label="중앙값 · P50" value={chosen.p50} note="가격경로의 절반에서 이 값 이하"/>}
   <Kpi label={`${riskLabel} · ${axis.includes('abs')?'절대':'증분'}`} value={chosen[axis]} note={ax.note}/>
   {version!=='v1'?<Kpi label="기준선 대비 ES90 변화" value={chosen.es_abs_vs_baseline} note="계획 ES90 − 무전환 ES90 (음수 = 꼬리 노출 감소)"/>:<Kpi label="꼬리 평균 · ES90" value={chosen.es_alpha} note="증분비용 상위 10% 경로의 평균"/>}
  </div>}
  <div className="research-grid">
   <section className="panel chart-panel"><div className="panel-head"><div><h2>기업 내 비용–위험 후보 경계</h2><p>{COMPANIES[company]} / {scenario} · {rows.length}개 계약 후보 · 각 {fmt(rows[0]?.n_draws,0)}개 경로 · 경계 위 기술 일정 {schedules}개</p></div><span className="unit">{meta.unit}</span></div>
   <div className="chart" role="img" aria-label={`${COMPANIES[company]}의 평균비용과 ${riskLabel} 산점도. 아래 표에서 수치를 확인할 수 있습니다.`}><ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{top:15,right:25,bottom:28,left:20}}><CartesianGrid stroke="#e2e7ee" strokeDasharray="3 4"/><XAxis type="number" dataKey="mean" name="평균 비용" tickFormatter={v=>fmt(v,0)} tickLine={false} axisLine={false} label={{value:'평균 증분 비용 →',position:'bottom',offset:8}}/><YAxis type="number" dataKey={axis} name={riskLabel} tickFormatter={v=>fmt(v,0)} tickLine={false} axisLine={false} width={74}/><Tooltip cursor={{strokeDasharray:'3 3'}} content={({active,payload})=>{const r=payload?.[0]?.payload;return active&&r?<div className="chart-tooltip"><strong>{r.plan_id}</strong><p>평균 {fmt(r.mean)}</p><p>{riskLabel} {fmt(r[axis])}</p><p>PPA {fmt(r.ppa_share*100,0)}% · EPC {r.epc?'고정':'미적용'}</p></div>:null;}}/><Scatter name="평가 후보" data={others} fill="#bac5d6" isAnimationActive={false}/><Scatter name="비지배 후보" data={frontier} fill="#2859be" isAnimationActive={false}/>{chosen&&<ReferenceDot x={chosen.mean} y={chosen[axis]} r={8} fill="#172b46" stroke="white" strokeWidth={2}/>}</ScatterChart></ResponsiveContainer></div>
   <div className="legend"><span><i className="dot muted"/>평가 후보</span><span><i className="dot"/>비지배 후보 (표본 지배 후보 제외 후)</span><span><i className="dot navy"/>현재 선택</span></div><p className="caption">점 하나가 실제 평가한 후보입니다. 점 사이를 연결해 실행 가능한 계획으로 해석하지 않습니다. 비지배 표시는 표본 손실 지배로 제외된 후보를 뺀 집합에서 계산합니다.</p></section>
   <aside className="reading-panel"><span className="eyebrow">SELECTED PLAN</span><h2>{criterion==='mean'?'평균 비용 최소 후보':`${riskLabel} 최소 후보`}</h2><dl><div><dt>후보 ID</dt><dd>{chosen?.plan_id??'적격 후보 없음'}</dd></div><div><dt>전력 PPA 비중</dt><dd>{fmt((chosen?.ppa_share??0)*100,0)}% {version!=='v1'?'(전환 증분 전력 기준)':'(전체 구매 전력 기준)'}</dd></div><div><dt>건설비 EPC 계약</dt><dd>{chosen?.epc?'고정 계약':'미적용'}</dd></div><div><dt>표본 손실 지배 제거 후</dt><dd>{eligible.length}개 후보</dd></div><div><dt>표시한 비지배 후보</dt><dd>{frontier.length}개 · 기술 일정 {schedules}개</dd></div></dl><p>선택 기준은 표본 손실 지배 후보를 제외한 집합에 적용합니다. 증분 TCaR는 P90−P50이며 자금요구량이 아닙니다. 가격위험은 D4의 연간 관측(전력 16, 탄소 10, 석탄·가스 15개 수익률)으로 보정한 GBM이며, 독립 표본에서 근접 후보의 순서가 바뀔 수 있습니다.</p><div className="reading-foot">{meta.information_date} 저장 결과입니다. 연구·교육용 알파 도구이며 투자자문이나 기업 인수·여신 심사 자료가 아닙니다. 일본 기업 값은 고정 환율 환산이며 환율 위험을 포함하지 않습니다. 기업 전체의 일정·계약 후보 재계산은 웹에서 지원하지 않습니다.</div></aside>
  </div>
  <section className="panel"><div className="panel-head"><div><h2>후보별 비용과 계약</h2><p>현재 기업·시나리오의 전체 후보. 금액은 {meta.unit}입니다.</p></div></div><div className="table-wrap candidate-table"><table><thead><tr>{['후보','PPA','EPC','평균','P50','증분 TCaR90','증분 ES90',...(version!=='v1'?['절대 ES90','ΔES90 vs 기준선']:[]),'선택 상태'].map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{[...rows].sort((a,b)=>a.mean-b.mean).map(r=><tr className={r.plan_id===chosen?.plan_id?'selected':''} key={r.plan_id}><td className="mono">{r.plan_id}</td><td>{fmt(r.ppa_share*100,0)}%</td><td>{r.epc?'고정':'—'}</td><td>{fmt(r.mean)}</td><td>{fmt(r.p50)}</td><td>{fmt(r.tcar)}</td><td>{fmt(r.es_alpha)}</td>{version!=='v1'&&<><td>{fmt(r.es_abs)}</td><td>{fmt(r.es_abs_vs_baseline)}</td></>}<td><span className={`badge ${r.sampled_statewise_dominated?'':'blue'}`}>{r.sampled_statewise_dominated?'표본 지배로 제외':frontier.includes(r)?'비지배 후보':'평가 후보'}</span></td></tr>)}</tbody></table></div></section>
 </>;
}
export function Kpi({label,value,note}:{label:string;value:number;note:string}) {return <div className="kpi"><span>{label}</span><strong>{fmt(value)}</strong><small>{note}</small></div>;}
