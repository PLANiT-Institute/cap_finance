import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';

const root = path.resolve(import.meta.dirname, '..');
const dest = path.join(root, 'outputs/01a07012-9848-7b02-8b66-346eca06ed4d');
const scratch = path.join(root, 'tmp/tcar_workbook');
// Resolve the documented public package through the task-local runtime symlink.
const runtimeRequire = createRequire(path.join(scratch, 'package.json'));
const { Workbook, SpreadsheetFile } = await import(runtimeRequire.resolve('@oai/artifact-tool'));
const args=process.argv.slice(2);
const option=(name,fallback)=>args.includes(name)?args[args.indexOf(name)+1]:fallback;
const payload = JSON.parse(await fs.readFile(option('--payload',path.join(scratch,'payload_v2.json')),'utf8'));
const outputPath=option('--out',path.join(dest,'TCaR_research_control.xlsx'));
const previewDir=option('--preview-dir',path.join(scratch,'previews_v2'));
const letters = n => { let s=''; for(n++;n;n=Math.floor((n-1)/26)) s=String.fromCharCode(65+(n-1)%26)+s; return s; };
const checks=[];
const excelText=value=>String(value).match(/[\s\S]{1,120}/g)?.map(part=>`"${part.replaceAll('"','""')}"`).join('&')??'""';
const changed=(reference,value)=>value===null?`IF(ISBLANK(${reference}),0,1)`:
 typeof value==='number'?`IF(ISNUMBER(${reference}),IF(${reference}=${value},0,1),1)`:
 typeof value==='boolean'?`IF(${reference}=${value?'TRUE':'FALSE'},0,1)`:
 `IF(EXACT(${reference},(${excelText(value)})),0,1)`;
for(const def of payload.sheets.filter(x=>x.editable_columns!==undefined)){
 checks.push([def.name,'column_headers','='+def.columns.map((field,i)=>changed(`'${def.name}'!${letters(i)}5`,field)).join('+')]);
 for(let j=0;j<def.rows.length;j++){
  const expressions=def.columns.filter((field,i)=>typeof def.rows[j][i]!=='string'||def.rows[j][i].length<=120).map(field=>{
   const i=def.columns.indexOf(field);return changed(`'${def.name}'!${letters(i)}${j+6}`,def.rows[j][i]);
  });
  checks.push([def.name,String(def.rows[j][0]),'='+expressions.join('+')]);
 }
}
payload.sheets.splice(4,0,{name:'Input checks',title:'마지막 실행 이후의 입력 변경',
 note:'수치·ID·단위의 변경을 표시합니다. 긴 출처 문장과 입력 수식의 검사는 실행 전 검증기가 수행합니다.',
 columns:['sheet','record','changed_input_cells'],rows:checks.map(r=>[r[0],r[1],null]),checkFormulas:checks.map(r=>[r[2]])});
const wb = Workbook.create();
const cover = wb.worksheets.add('Overview');
for(const def of payload.sheets) wb.worksheets.add(def.name);
const previews=[];

for(const def of payload.sheets){
  const sh=wb.worksheets.getItem(def.name);
  const cols=def.columns.length, end=def.rows.length+5;
  sh.showGridLines=false;
  const all=sh.getRangeByIndexes(0,0,end,cols);
  all.format.font={name:'Helvetica Neue',size:11,color:'#172033'};
  all.format.verticalAlignment='top';
  sh.getRange('A1').values=[[def.title]];
  sh.getRange('A1').format.font={size:16,bold:true};
  sh.getRangeByIndexes(0,0,1,cols).format.rowHeightPx=34;
  sh.getRange('A3').values=[[def.note]];
  sh.getRange('A3').format.font={size:10,color:'#586174'};
  const noteEnd=letters(Math.min(cols-1,6));
  sh.mergeCells(`A3:${noteEnd}3`);
  sh.getRange(`A3:${noteEnd}3`).format.wrapText=true;
  sh.getRange(`A3:${noteEnd}3`).format.rowHeightPx=42;
  sh.getRangeByIndexes(4,0,1,cols).values=[def.columns];
  sh.getRangeByIndexes(4,0,1,cols).format={fill:'#25354A',font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:46};
  if(def.rows.length) sh.getRangeByIndexes(5,0,def.rows.length,cols).values=def.rows;
  const widths=def.columns.map((c,i)=> {
    if(['quality_note','claim_supported','limits','required_resolution','finding','note','derivation','interpretation_limit','interpretation','interval_scope','unit_or_description'].includes(c)) return 420;
    if(c==='content') return 700;
    if(c.includes('url')) return 410;
    if(['title','used_in','location','evidence'].includes(c)) return 310;
    if(c==='param_id') return 320;
    if(c.includes('source')) return 240;
    if(c.includes('gap')) return 160;
    if(c==='field') return 170;
    return 145;
  }).map((w,i)=>Math.max(w,def.columns[i].length*8.5+22));
  for(let i=0;i<cols;i++){
    sh.getRangeByIndexes(0,i,end,1).format.columnWidthPx=widths[i];
    const r=sh.getRangeByIndexes(5,i,def.rows.length,1);
    r.format.wrapText=true;
    if(def.rows.some(row=>typeof row[i]==='number')) r.setNumberFormat('#,##0.00;[Red](#,##0.00);0.00');
    if(def.columns[i].includes('year')||['priority','changed_input_cells','valid_from','valid_to'].includes(def.columns[i])) r.setNumberFormat('0');
    if(def.name==='Sensitivity'&&i>0) r.setNumberFormat('0');
    if(def.editable_columns?.includes(def.columns[i])) r.format.fill='#FFF6D5';
  }
  for(let j=0;j<def.rows.length;j++){
    const lines=Math.max(...def.rows[j].map((v,i)=>String(v??'').split('\n').reduce((sum,s)=>sum+Math.max(1,Math.ceil([...s].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?2:1),0)/(widths[i]/8.5))),0)));
    sh.getRangeByIndexes(j+5,0,1,cols).format.rowHeightPx=Math.max(34,Math.min(480,lines*20+14));
  }
  sh.freezePanes.freezeRows(5);
  sh.freezePanes.freezeColumns(1);
  sh.tables.add(`A5:${letters(cols-1)}${end}`,true,'T_'+def.name.replaceAll(/[^A-Za-z0-9]/g,''));
  if(def.checkFormulas) sh.getRange(`C6:C${end}`).formulas=def.checkFormulas;
  if(def.name==='Control schema') sh.getRange('B6').setNumberFormat('0');
  if(def.name==='Settings'){
    for(let j=0;j<def.rows.length;j++){
      const value=def.rows[j][1];
      const cell=sh.getRange(`B${j+6}`);
      if(typeof value==='number') cell.setNumberFormat(Number.isInteger(value)?'0':'0.0000');
      if(typeof value==='string') cell.dataValidation={rule:{type:'list',values:def.rows[j][3].split(', ')}};
    }
  }
  if(def.name==='Parameters'){
    sh.getRange('O5').values=[['bounds_present']];
    sh.getRange('O5').format={fill:'#25354A',font:{color:'#FFFFFF',bold:true},wrapText:true};
    sh.getRange('O6').formulas=[['=IF(AND(ISNUMBER(I6),ISNUMBER(J6)),1,0)']];
    sh.getRange(`O6:O${end}`).fillDown();
    sh.getRange(`O1:O${end}`).format.columnWidthPx=140;
  }
  previews.push({name:def.name,range:`A1:${letters(Math.min(cols-1,6))}${Math.min(end,def.name==='Control schema'?7:8)}`});
}

cover.showGridLines=false;
cover.getRange('A1:G37').format.font={name:'Helvetica Neue',size:11,color:'#172033'};
cover.getRange('A1:A37').format.columnWidthPx=235;
cover.getRange('B1:G37').format.columnWidthPx=150;
cover.getRange('A1:G37').format.rowHeightPx=28;
cover.getRange('A1').values=[['TCaR 연구 통합 관리']];
cover.getRange('A1').format.font={size:18,bold:true};
cover.getRange('A3:B5').values=[['분석 기간',`${payload.config.years.start}–${payload.config.years.end} · 정보 기준일 ${payload.config.information_cutoff}`],['마지막 실행 UTC',payload.run_finished_at_utc],['입력 수정 상태',null]];
cover.getRange('B4').setNumberFormat('yyyy-mm-dd hh:mm');
cover.getRange('B5').formulas=[[`=IF(SUM('Input checks'!C6:C${checks.length+5})=0,"마지막 실행의 입력과 동일","입력 변경됨 — 재실행 필요")`]];
cover.getRange('A7:B11').values=[['항목','건수'],['평가 후보',null],['원문 선택 관측',null],['기존 등록 모수',null],['범위 없는 T5 모수',null]];
const pEnd=payload.sheets.find(x=>x.name==='Parameters').rows.length+5;
const rEnd=payload.sheets.find(x=>x.name==='Risk measures').rows.length+5;
const oEnd=payload.sheets.find(x=>x.name==='Primary observations').rows.length+5;
cover.getRange('B8:B11').formulas=[
 [`=COUNTA('Risk measures'!A6:A${rEnd})`],
 [`=COUNTA('Primary observations'!A6:A${oEnd})`],
 [`=COUNTA('Parameters'!A6:A${pEnd})`],
 [`=COUNTIFS('Parameters'!H6:H${pEnd},"T5",'Parameters'!O6:O${pEnd},0)`]
];
cover.getRange('A13:G13').values=[[payload.config.plan_selection_criterion==='mean'?'평균 최소 후보':'중앙값 최소 후보','시나리오','P50','평균','TCaR90','ES90','선택 계획']];
const cases=payload.sheets.find(x=>x.name==='Case results');
for(let i=0;i<cases.rows.length;i++){
 const source=i+6,target=i+14;
 cover.getRange(`A${target}:G${target}`).formulas=[['A','B','D','E','F','G','C'].map(col=>`='Case results'!${col}${source}`)];
}
cover.getRange('C14:F21').setNumberFormat('#,##0.0;[Red](#,##0.0);0.0');
cover.getRange('A23:B33').values=[
 ['단위','십억원. 선언된2025년 원화 기준 대용치이며 원천 환산의 경험적 검증은 불완전합니다.'],
 ['TCaR','P90−P50의 간격입니다. 평균·ES90와 함께 해석합니다.'],
 ['감축 제약',payload.config.budget_mode==='cumulative_hard'?'누적 Scope1 상한입니다. 연간 상한 준수와 다릅니다.':'연간 Scope1 상한입니다.'],
 ['공시 비교','현재 정확한 공시 비교군이 없어 기업별 개선 간격은 미산출입니다.'],
 ['입력 수정','Settings 및 D1a–D6의 노란 셀을 수정하고 저장합니다.'],
 ['검증과 실행','research_control.py의 validate → run → refresh를 사용합니다.'],
 ['계산 방식','Excel 수식은 변경과 표시를 계산합니다. 정수계획·가격경로는 Python 엔진이 실행합니다.'],
 ['원문 수치','Primary observations의 단위·범위·원문 위치를 먼저 확인합니다.'],
 ['가정과 근거','D3의 잔존 에너지는 가정입니다. Parameters는 기존FIN·EFF 등록부입니다.'],
 ['실행 기록','입력·코드 해시, 변경 셀, 성공·실패와 단계별 로그를 별도 실행 폴더에 저장합니다.'],
 ['사용 설명','동봉한 연구 통제 설명서의 실행 명령과 결과 해석을 따릅니다.']
];
cover.getRange('B23:B33').format.font={size:10};
cover.getRange('A23:G33').format.rowHeightPx=34;
for(const range of ['A7:B7','A13:G13']) cover.getRange(range).format={fill:'#25354A',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:34};
previews.unshift({name:'Overview',range:'A1:G33'});

await fs.mkdir(dest,{recursive:true});
await fs.mkdir(previewDir,{recursive:true});
console.log((await wb.inspect({kind:'table',range:'Overview!A5:G21',include:'values,formulas',tableMaxRows:15,tableMaxCols:6,maxChars:4500})).ndjson);
const errs=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'formula errors',maxChars:1500});
console.log(errs.ndjson);
await fs.writeFile(path.join(scratch,'formula_scan.json'),JSON.stringify(errs,null,2));
for(const [i,view] of previews.entries()){
 if(args.includes('--preview-only')&&view.name!==option('--preview-only','')) continue;
 const blob=await wb.render({sheetName:view.name,range:view.range,scale:1,format:'png'});
 await fs.writeFile(path.join(previewDir,`${String(i).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 console.log(`Rendered ${view.name}`);
}
await fs.writeFile(path.join(previewDir,'index.json'),JSON.stringify(previews,null,2));
const output=await SpreadsheetFile.exportXlsx(wb);
await fs.mkdir(path.dirname(outputPath),{recursive:true});
await output.save(outputPath);
console.log(`Saved ${previews.length} sheets`);
