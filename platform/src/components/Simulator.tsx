'use client';
import {useEffect,useRef,useState} from 'react';
import {ResponsiveContainer,LineChart,Line,BarChart,Bar,XAxis,YAxis,CartesianGrid,Tooltip,ReferenceLine,Legend,ScatterChart,Scatter} from 'recharts';
import {Kpi} from './Research';
import {fmt,csvDownload,download,type Row} from '@/lib/format';
import catalogData from '../../public/data/catalog.json';
import jointDefault from '../../public/data/default-joint.json';
import cashDefault from '../../public/data/default-cash.json';
import timingDefault from '../../public/data/default-timing.json';
type Model='joint'|'cash'|'timing';
type Controls=Record<string,string|number>;
type Summary={id:string;label:string;eligible:boolean;frontier?:boolean;mean?:number;p50?:number;q_alpha?:number;tcar?:number;es_alpha?:number;analytic_mean?:number};
type Result={model:Model;controls:Controls;unit:string;summaries:Summary[];qualification:Row[];annual:Row[];chart:Row[];distributions:Record<string,{cost:number;lower:number;upper:number;count:number}[]>;scope:string;audit:Record<string,string|number|boolean>;engine_version:string;request_id:string;elapsed_seconds:number;source_sha256:Record<string,string>};
const CATALOG=catalogData as {engine_version:string;models:Record<Model,{defaults:Controls;fields:string[][];unit:string}>};
const INITIAL={joint:jointDefault,cash:cashDefault,timing:timingDefault} as unknown as Record<Model,Result>;
const INFO:Record<Model,{title:string;subtitle:string;number:string;question:string}>={
 joint:{title:'공동 가격·운영비',subtitle:'Control · EUR2024 → KRW2024',number:'01',question:'전력 구매·메탄 판매의 증분 운영비'},
 cash:{title:'NCC 현금비용',subtitle:'Cash · EUR2019 가정',number:'02',question:'재래식·전기식 NCC의 건설·갱신·운영비'},
 timing:{title:'전환 시점',subtitle:'Timing · EUR2019 가정',number:'03',question:'전환 연도별 배출 적격성·비용·위험'},
};
const OPTIONS:Record<string,[string,string][]>= {
 scenario:[['CPS','CPS · 현행 정책'],['STEPS','STEPS · 명시 정책'],['NZE','NZE · 2050 순배출 제로']],
 shock_model:[['empirical_block_12','12개월 공동 블록'],['empirical_block_1','1개월 공동 블록'],['empirical_block_6','6개월 공동 블록'],['empirical_block_24','24개월 공동 블록'],['iid_gaussian','독립 월 · 공동 정규 충격']],
 block:[['1','1개월'],['6','6개월'],['12','12개월'],['24','24개월']],
 constraint:[['cumulative_terminal','누적 + 말기 상한'],['annual_linear','연도별 선형 상한']],
 terminal:[['none','잔존수입 없음'],['straight_line_proxy','남은 수명 비례 대용치']],
 maintenance_scale:[['1','1 · 원문 4%·2%를 문자 그대로 %로 적용 (논문 표 16 기본)'],['0.01','0.01 · 원문 표기를 소수(0.04%·0.02%)로 읽음']],
};
const INTEGER=new Set(['paths','seed','start_year','end_year','block','base_life','electric_life','remaining_years']);
const FRACTION=new Set(['discount_rate','discount','power_indexed_share','methane_sale_fraction','recovery','annuity_rate','beta','sale','cum_fraction','terminal_fraction']);
function limits(key:string):{min?:number;max?:number;step:string|number} {
 if(key==='paths')return {min:2,max:10000,step:1};
 if(key==='seed')return {min:0,max:4294967295,step:1};
 if(key==='alpha')return {min:.500001,max:.999999,step:'any'};
 if(key==='start_year'||key==='end_year')return {min:2024,max:2050,step:1};
 if(key==='hours')return {min:.001,max:8760,step:'any'};
 if(key==='remaining_years')return {min:1,max:25,step:1};
 if(key.endsWith('_life'))return {min:1,max:100,step:1};
 if(FRACTION.has(key))return {min:0,max:1,step:'any'};
 if(['grid_start','grid_end','residual'].includes(key))return {min:0,max:2,step:'any'};
 if(key==='replacement_scale')return {min:0,max:5,step:'any'};
 if(key==='KRW2024_per_EUR2024')return {min:.000001,max:1e10,step:'any'};
 return {min:key==='methane_EUR2024_t'?-1e10:0,max:1e10,step:INTEGER.has(key)?1:'any'};
}
function strings(c:Controls){return Object.fromEntries(Object.entries(c).map(([k,v])=>[k,String(v)]));}
function controlsFromDraft(model:Model,draft:Record<string,string>):Controls{
 return Object.fromEntries(Object.entries(draft).map(([k,v])=>{
  if(v.trim()==='')throw new Error('빈칸이 있습니다. 0을 뜻하는 경우에는 숫자 0을 입력하세요.');
  const value=typeof CATALOG.models[model].defaults[k]==='string'?v:Number(v);
  if(typeof value==='number'&&!Number.isFinite(value))throw new Error('유효한 숫자를 입력하세요.');
  return [k,value];
 }));
}
function same(a:Controls,b:Controls){return Object.keys(b).every(k=>a[k]===b[k]);}
export default function Simulator(){
 const [model,setModel]=useState<Model>('timing');
 const [drafts,setDrafts]=useState<Record<Model,Record<string,string>>>(()=>({joint:strings(CATALOG.models.joint.defaults),cash:strings(CATALOG.models.cash.defaults),timing:strings(CATALOG.models.timing.defaults)}));
 const [results,setResults]=useState(INITIAL);const [fresh,setFresh]=useState<Record<string,boolean>>({});
 const [selected,setSelected]=useState('replace_2040');const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 const [api,setApi]=useState<'checking'|'online'|'offline'>('checking');
 useEffect(()=>{const c=new AbortController();fetch('/api/simulate',{signal:c.signal}).then(r=>r.ok?r.json():Promise.reject(r.status)).then(j=>setApi(j&&j.engine_version?'online':'offline')).catch(()=>setApi('offline'));return()=>c.abort();},[]);
 const inFlight=useRef(false);const abort=useRef<AbortController|null>(null);
 useEffect(()=>()=>abort.current?.abort(),[]);
 const draft=drafts[model];const result=results[model];let dirty=true;
 try{dirty=!same(controlsFromDraft(model,draft),result.controls);}catch{}
 const candidates=result.summaries.filter(s=>s.eligible);
 const summary=candidates.find(s=>s.id===selected)??[...candidates].sort((a,b)=>(a.analytic_mean??Infinity)-(b.analytic_mean??Infinity))[0];
 const alpha=Number(result.controls.alpha)*100; const alphaLabel=fmt(alpha,Number.isInteger(alpha)?0:2);
 const distribution=summary?result.distributions[summary.id]:[];
 async function run(which:Model,controls:Controls){
  if(inFlight.current)throw new Error('진행 중인 계산이 끝난 뒤 실행하세요.');
  inFlight.current=true;setBusy(true);setError('');
  const controller=new AbortController();abort.current=controller;
  const timeout=setTimeout(()=>controller.abort(),65000);
  try{
   const response=await fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:which,controls}),signal:controller.signal});
   if(!response.headers.get('content-type')?.includes('application/json'))throw new Error('계산 서버가 응답하지 않았습니다. 잠시 후 다시 실행하세요.');
   const body=await response.json();if(!response.ok)throw new Error(body.error??'계산에 실패했습니다.');
   const next=body as Result;
   if(next.model!==which||!same(next.controls,controls))throw new Error('응답의 모형 또는 입력이 요청과 다릅니다.');
   setResults(previous=>({...previous,[which]:next}));setFresh(previous=>({...previous,[which]:true}));
   const choice=next.summaries.filter(s=>s.eligible).sort((a,b)=>(a.analytic_mean??Infinity)-(b.analytic_mean??Infinity))[0];
   setSelected(choice?.id??'');
   return {request_id:next.request_id,model:next.model,unit:next.unit,summaries:next.summaries};
  }catch(e){const message=e instanceof Error?(e.name==='AbortError'?'응답 시간이 초과되었습니다. 경로 수를 줄여 다시 실행하세요.':e.message):'계산에 실패했습니다.';setError(message);throw new Error(message);}
  finally{clearTimeout(timeout);inFlight.current=false;setBusy(false);}
 }
 useEffect(()=>{
  const context=(document as Document & {modelContext?:{registerTool:(tool:object,options:object)=>void|Promise<void>}}).modelContext;
  if(!context?.registerTool)return;const lifecycle=new AbortController();
  const tool={name:'run_tcar_reference_simulation',description:'Run the same reference simulator shown on this page. Updates model, controls, and results. Model scopes and currency years remain separate.',inputSchema:{type:'object',properties:{model:{type:'string',enum:['joint','cash','timing']},controls:{type:'object',description:'Complete controls object for the selected model.'}},required:['model','controls'],additionalProperties:false},annotations:{readOnlyHint:false},execute:async(input:unknown)=>{
   const value=input as {model:Model;controls:Controls};
   if(!value||!Object.hasOwn(CATALOG.models,value.model)||!value.controls||typeof value.controls!=='object'||Array.isArray(value.controls))throw new Error('Invalid model or controls.');
   const defaults=CATALOG.models[value.model].defaults;
   if(Object.keys(value.controls).length!==Object.keys(defaults).length||Object.keys(defaults).some(k=>typeof value.controls[k]!==typeof defaults[k]))throw new Error('Provide every control with its documented type.');
   if(inFlight.current)throw new Error('Calculation in progress.');
   const outcome=await run(value.model,value.controls);
   setModel(value.model);setDrafts(prev=>({...prev,[value.model]:strings(value.controls)}));
   await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));return outcome;
  }};
  try{void Promise.resolve(context.registerTool(tool,{signal:lifecycle.signal})).catch(()=>{});}catch{}
  return ()=>lifecycle.abort();
 // The registered action uses functional state updates and the in-flight ref.
 // eslint-disable-next-line react-hooks/exhaustive-deps
 },[]);
 return <>
 <div className="section-heading"><div><span className="eyebrow">04 / REFERENCE SIMULATORS · {api==='online'?'LIVE':api==='checking'?'…':'계산 서버 오프라인'}</span><h1>가격·현금흐름 참조 실험 <small style={{fontSize:'0.5em',fontWeight:400,opacity:.7}}>부속 · 기업 경계 결과와 무관</small></h1><p>공동 가격·부분 운영비, NCC 현금비용, 전환 시점의 세 참조 모형입니다. 모형별 입력에 따라 가격경로와 비용 분포를 재계산합니다. 위 기업 후보 결과와 범위·통화연도·시드·α가 다른 별도 공정 모형입니다.</p>{api==='offline'&&<p className="notice compact"><span className="notice-index">안내</span>계산 서버가 응답하지 않아 저장된 기본 실행만 표시합니다. 재계산은 서버 복구 후 가능합니다.</p>}</div><span className="status">보조 분석 · 공정 참조 모형</span></div>
 <div className="model-tabs" role="tablist" aria-label="참조 모형">{(Object.keys(INFO) as Model[]).map(id=><button disabled={busy} key={id} role="tab" aria-selected={model===id} aria-controls="simulator-workspace" onClick={()=>{setModel(id);setSelected('');setError('');}} className={model===id?'active':''}><span>{INFO[id].number}</span><div><strong>{INFO[id].title}</strong><small>{INFO[id].subtitle}</small></div><span>↗</span></button>)}</div>
 <div className="notice">세 모형은 공정·비용 범위·가격연도가 다릅니다. 결과를 서로 더하거나 기업 후보 450개의 새로운 최적화 결과로 해석하지 않습니다.</div>
 <div className="sim-grid" id="simulator-workspace" role="tabpanel">
 <form className="assumptions" onSubmit={e=>{e.preventDefault();try{void run(model,controlsFromDraft(model,draft)).catch(()=>{});}catch(err){setError((err as Error).message);}}}>
 <div className="form-heading"><h2>입력 가정</h2><button disabled={busy} type="button" className="text-button" onClick={()=>{setDrafts(prev=>({...prev,[model]:strings(CATALOG.models[model].defaults)}));setError('');}}>기본값 복원 ↺</button></div>
 <p className="caption">가격·기술 가정은 기업의 관측 조달조건이 아닙니다. 비율 0.05 = 5%.</p>
 <fieldset disabled={busy}>{CATALOG.models[model].fields.map(([key,label,unit,hint])=><label key={key}>{label}
  {OPTIONS[key]?<select value={draft[key]} onChange={e=>setDrafts(prev=>({...prev,[model]:{...prev[model],[key]:e.target.value}}))}>{OPTIONS[key].map(([v,name])=><option value={v} key={v}>{name}</option>)}</select>:<input required type="number" value={draft[key]} {...limits(key)} onChange={e=>setDrafts(prev=>({...prev,[model]:{...prev[model],[key]:e.target.value}}))}/>}
  <small>{key==='paths'?'웹 실행: 2–10,000개 · 꼬리 정밀도는 별도 확인':unit}</small>{hint&&<span className="input-hint">{hint}</span>}
 </label>)}</fieldset>
 <div className="run-actions"><button type="submit" disabled={busy} className="button">{busy?'가격경로·현금비용 계산 중…':'시뮬레이션 실행'} <span aria-hidden="true">→</span></button><span>같은 입력·시드·엔진 버전으로 재현</span></div>
 </form>
 <div className="sim-results" aria-live="polite" aria-busy={busy}><div className="panel-head"><div><span className="eyebrow">{INFO[model].subtitle}</span><h2>{INFO[model].question}</h2></div></div>
 {error&&<div className="error" role="alert">{error}</div>}
 {dirty?<div className="empty-state"><span className="eyebrow">INPUTS CHANGED</span><h2>입력 변경 · 재계산 필요</h2><p>변경된 입력의 계산 결과가 없습니다. 재계산을 실행하면 결과가 표시됩니다.</p><button className="button" disabled={busy} onClick={()=>{try{void run(model,controlsFromDraft(model,draft)).catch(()=>{});}catch(e){setError((e as Error).message);}}}>{busy?'계산 중…':'재계산 →'}</button></div>:<>
 <div className="result-status"><span><i className="dot"/> {fresh[model]?'현재 입력으로 계산 완료':'동일 엔진의 저장된 기본 실행'}</span><span>{String(result.controls.scenario)} · N={fmt(result.controls.paths,0)} · α={fmt(alpha/100,Number.isInteger(alpha)?2:4)} · {result.unit}</span></div>
 {!candidates.length?<div className="empty-state"><span className="eyebrow">NO FEASIBLE CANDIDATE</span><h2>적격 후보 없음</h2><p>현재 배출 제약을 만족하는 전환 일정이 없어 비용과 위험을 계산하지 않았습니다. 가격경로도 새로 생성하지 않았습니다.</p></div>:<>
 {model==='timing'&&<div className="result-picker"><label>결과 표시 후보<select value={summary?.id} onChange={e=>setSelected(e.target.value)}>{candidates.map(s=><option key={s.id} value={s.id}>{s.label}{s.frontier?' · 평균–ES 비지배':''}</option>)}</select></label><span>비용 단위: {result.unit}</span></div>}
 {summary&&<div className="kpis sim-kpis"><Kpi label="표본 평균" value={summary.mean!} note={result.unit}/><Kpi label="중앙값 · P50" value={summary.p50!} note={result.unit}/><Kpi label={`TCaR${alphaLabel}`} value={summary.tcar!} note={`P${alphaLabel} − P50`}/><Kpi label={`ES${alphaLabel}`} value={summary.es_alpha!} note={`상위 ${fmt(100-alpha,Number.isInteger(alpha)?0:2)}% 질량 평균`}/></div>}
 <section className="panel"><div className="panel-head"><div><h2>증분 비용의 분포</h2><p>{summary?.label} · 같은 가격경로에서 기준 비용을 차감</p></div><span className="unit">{result.unit}</span></div><div className="chart distribution" role="img" aria-label="증분 비용 히스토그램. 분위수와 평균은 아래 표로도 제공됩니다."><ResponsiveContainer width="100%" height="100%"><BarChart data={distribution} margin={{left:4,right:16,bottom:10,top:10}}><CartesianGrid vertical={false} stroke="#e2e7ee"/><XAxis dataKey="cost" tickFormatter={v=>fmt(v,0)} minTickGap={45} tickLine={false} axisLine={false}/><YAxis tickLine={false} axisLine={false} width={44}/><Tooltip content={({active,payload})=>{const r=payload?.[0]?.payload;return active&&r?<div className="chart-tooltip">{fmt(r.lower)} ~ {fmt(r.upper)}<p>{fmt(r.count,0)}개 경로</p></div>:null;}}/><Bar dataKey="count" name="경로 수" fill="#446eb7" isAnimationActive={false}/></BarChart></ResponsiveContainer></div><p className="caption">40개 구간별 표본 경로 수입니다. 비용분포는 과거 벤치마크와 선택한 가격생성법에 따른 조건부 추정치입니다.</p></section>
 </>}
 <section className="panel"><div className="panel-head"><div><h2>{model==='timing'?'전환 시점별 배출 경로':'연도별 중심 가격의 증분 현금비용'}</h2><p>{model==='timing'?'기준선, 각 전환 후보와 연간 선형 상한 · tCO2':'중심 가격을 적용한 할인 비용. 표본 평균과 차이가 날 수 있습니다.'}</p></div></div><div className="chart" role="img" aria-label={model==='timing'?'연도별 배출경로. 아래 원장에서 연간 수치를 확인할 수 있습니다.':'연도별 중심 가격 할인 증분 현금비용.'}><ResponsiveContainer width="100%" height="100%"><LineChart data={result.chart} margin={{left:16,right:15,top:10,bottom:5}}><CartesianGrid stroke="#e2e7ee" strokeDasharray="3 4"/><XAxis dataKey="year" minTickGap={25} tickLine={false} axisLine={false}/><YAxis width={66} tickFormatter={v=>Math.abs(v)>=1e6?`${fmt(v/1e6,1)}M`:fmt(v,0)} tickLine={false} axisLine={false}/><Tooltip formatter={v=>fmt(Number(v))}/><Legend/>{model==='timing'?<><Line dataKey="baseline" name="기존 유지" stroke="#92a0b2" dot={false} strokeDasharray="5 4" isAnimationActive={false}/><Line dataKey="cap" name="연간 선형 상한" stroke="#9c7156" dot={false} strokeDasharray="2 4" isAnimationActive={false}/>{['2030','2035','2040','2045'].map((year,i)=><Line key={year} dataKey={`replace_${year}`} name={`${year} 전환`} stroke={['#2859be','#267d75','#94775b','#9ba9c2'][i]} strokeWidth={2} dot={false} isAnimationActive={false}/>)}</>:<><ReferenceLine y={0} stroke="#96a3b6"/><Line dataKey="incremental" name="할인 증분비용" stroke="#2859be" strokeWidth={2} dot={false} isAnimationActive={false}/></>}</LineChart></ResponsiveContainer></div>{model==='timing'&&<p className="caption">누적+말기 모드에서는 점선의 연간 상한 통과가 선택 조건이 아닙니다. 누적예산 {fmt(result.audit.cumulative_budget,0)} tCO2, 말기 상한 {fmt(result.audit.terminal_budget,0)} tCO2를 각각 검사합니다.</p>}</section>
 {model==='timing'&&<section className="panel"><div className="panel-head"><div><h2>배출 적격성 및 평균–ES 후보 경계</h2><p>불가 후보에 가상 비용을 부여하지 않습니다. 연간·누적·말기 충족 여부를 구분합니다.</p></div></div><div className="table-wrap"><table><thead><tr>{['전환','종합','누적','말기','연간','평균 기대비용','ES','TCaR','비지배'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{result.qualification.map(q=>{const s=result.summaries.find(s=>s.id===q.candidate);return <tr key={String(q.candidate)}><td>{String(q.year)}</td><td><span className={`badge ${q.eligible?'blue':''}`}>{q.eligible?'적격':'불가'}</span></td><td>{q.cumulative_feasible?'충족':'초과'}</td><td>{q.terminal_feasible?'충족':'초과'}</td><td>{q.annual_feasible?'충족':'초과'}</td><td>{fmt(s?.analytic_mean)}</td><td>{fmt(s?.es_alpha)}</td><td>{fmt(s?.tcar)}</td><td>{s?.frontier?'●':'—'}</td></tr>;})}</tbody></table></div>{candidates.length>0&&<div className="chart small-chart" role="img" aria-label="적격 전환 후보의 기대비용–ES 산점도"><ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{left:25,right:30,bottom:25,top:20}}><CartesianGrid stroke="#e2e7ee"/><XAxis type="number" dataKey="analytic_mean" name="평균 기대비용" label={{value:'평균 기대비용 →',position:'bottom'}} tickFormatter={v=>fmt(v,0)}/><YAxis type="number" dataKey="es_alpha" name="ES" tickFormatter={v=>fmt(v,0)}/><Tooltip formatter={v=>fmt(Number(v))}/><Scatter data={candidates.filter(c=>!c.frontier)} fill="#b6c2d3" name="적격 후보" isAnimationActive={false}/><Scatter data={candidates.filter(c=>c.frontier)} fill="#2859be" name="비지배 후보" isAnimationActive={false}/></ScatterChart></ResponsiveContainer></div>}</section>}
 {candidates.length>0&&<div className="table-wrap"><table><thead><tr>{['비교','중심 가격 기대비용','표본 평균','P50',`P${alphaLabel}`,`TCaR${alphaLabel}`,`ES${alphaLabel}`].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{candidates.map(s=><tr key={s.id}><td>{s.label}</td><td>{fmt(s.analytic_mean)}</td><td>{fmt(s.mean)}</td><td>{fmt(s.p50)}</td><td>{fmt(s.q_alpha)}</td><td>{fmt(s.tcar)}</td><td>{fmt(s.es_alpha)}</td></tr>)}</tbody></table></div>}
 <div className="result-actions"><button className="button secondary" onClick={()=>csvDownload(`${model}-annual.csv`,result.annual)}>연간 원장 CSV ↓</button><button className="button secondary" onClick={()=>download(`TCaR-${model}-${result.request_id.slice(0,8)}.json`,JSON.stringify(result,null,2))}>입력·결과·근거 JSON ↓</button></div>
 <details className="details"><summary>연간 데이터 원장 · {result.annual.length}행</summary><div className="table-wrap ledger-table"><table><thead><tr>{Object.keys(result.annual[0]??{}).map(k=><th key={k}>{k}</th>)}</tr></thead><tbody>{result.annual.map((r,i)=><tr key={i}>{Object.values(r).map((v,j)=><td key={j}>{typeof v==='number'?fmt(v,2):String(v??'—')}</td>)}</tr>)}</tbody></table></div></details>
 <details className="details"><summary>계산 범위·검증 기록</summary><p>{result.scope}</p><dl className="audit-grid"><dt>독립 현금식 대조</dt><dd>{fmt(result.audit.checks,0)}개 · 최대 오차 {Number(result.audit.max_error).toExponential(2)} {result.unit}</dd><dt>엔진 버전</dt><dd className="mono">{result.engine_version}</dd><dt>입력·버전 실행 지문</dt><dd className="mono">{result.request_id}</dd><dt>실행 시간</dt><dd>{fmt(result.elapsed_seconds,3)}초</dd></dl><p>대조는 계산식의 일치를 확인합니다. 기업의 실측 조달조건·미래 분포·모든 비용의 외부 타당성을 검증했다는 뜻은 아닙니다.</p></details>
 </>}
 </div></div></>;
}
