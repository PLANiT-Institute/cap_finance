import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..'),req=createRequire(path.join(root,'tmp/ncc_joint_workbook/package.json'));
const {FileBlob,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const [payloadPath,out]=process.argv.slice(2),preview=!process.argv.includes('--no-preview');
const p=JSON.parse(await fs.readFile(payloadPath,'utf8')),c=p.controls,N=c.paths,last=N+4,dir=path.dirname(payloadPath);
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p.input_workbook));
if(process.argv.includes('--review-only')){
 for(const [name,range,suffix]of [['NCC paths','H13:I18','hashes'],['NCC annual','T4:AA9','source_snapshot'],['Control','A1:D37','old_control']]){
  const blob=await wb.render({sheetName:name,range,scale:1});await fs.writeFile(path.join(dir,suffix+'.png'),new Uint8Array(await blob.arrayBuffer()));
 }
 process.exit(0);
}
const before=await wb.inspect({kind:'sheet',include:'id,name',maxChars:2500});
await fs.writeFile(path.join(dir,'input_sheets.json'),JSON.stringify(before));
function sheet(name){let s;try{s=wb.worksheets.getItem(name);s.getUsedRange().clear({applyTo:'all'});}catch{s=wb.worksheets.add(name);}return s;}
const control=sheet('NCC cash'),annual=sheet('NCC annual'),draw=sheet('NCC paths');
const money='#,##0.000;(#,##0.000);"–"';
function base(s,rows,widths,title){s.showGridLines=false;const r=s.getRangeByIndexes(0,0,rows,widths.length);r.format.font={name:'Helvetica Neue',size:11,color:'#172432'};r.format.rowHeightPx=28;r.format.verticalAlignment='center';widths.forEach((w,i)=>s.getRangeByIndexes(0,i,rows,1).format.columnWidthPx=w);s.getRange('A2').values=[[title]];s.getRange('A2').format.font={size:17,bold:true,color:'#163b58'};s.getRange('A2').format.rowHeightPx=38;s.freezePanes.freezeRows(4);}
function header(s,r){s.getRange(r).format={fill:'#234e72',font:{bold:true,color:'#ffffff'},rowHeightPx:32};}
base(control,42,[290,240,420,30,290,240],'NCC 신규 설비의 조건부 현금비용');
control.getRange('A4:C10').values=[['전기화 − 기존 방식','백만 EUR2019 가정','할인 기준: 2027년'],['평균',null,'가격 표본의 평균'],['중앙값',null,'가격 표본의 중앙값'],['상위 분위 비용',null,'선택한 α 분위수'],['TCaR',null,'상위 분위수 − 중앙값'],['ES',null,'상위 (1−α) 질량의 평균'],['모형의 기대비용',null,'중심 가격의 선형 원장. 미래 관측값 아님']];header(control,'A4:C4');
control.getRange('A11:C11').values=[['입력 항목','편집 값','단위와 해석']];header(control,'A11:C11');
control.getRange('A12:C29').values=p.fields.map(([k,l,u])=>[l,c[k],u]);
control.getRange('B12:B29').format.fill='#fff2ca';control.getRange('B12:B29').format.font={color:'#0056b3'};
control.getRange('B12:B29').setNumberFormat('#,##0.000');
for(const row of [13,14,15,18,19,20])control.getRange(`B${row}`).setNumberFormat('#,##0');
for(const row of [16,17,22,23,28,29])control.getRange(`B${row}`).setNumberFormat('0.0%');
control.getRange('E11:F11').values=[['실행된 입력','저장된 값']];header(control,'E11:F11');
control.getRange('E12:F29').values=p.fields.map(([k,l])=>[l,c[k]]);
control.getRange('F12:F29').setNumberFormat('#,##0.000');
for(const row of [13,14,15,18,19,20])control.getRange(`F${row}`).setNumberFormat('#,##0');
for(const row of [16,17,22,23,28,29])control.getRange(`F${row}`).setNumberFormat('0.0%');
control.getRange('B12').dataValidation={rule:{type:'list',values:['CPS','STEPS','NZE']}};
control.getRange('B24').dataValidation={rule:{type:'list',values:['none','straight_line_proxy']}};
control.getRange('A31').values=[['입력과 실행 결과']];
const equal=p.fields.map((_,i)=>`B${i+12}=F${i+12}`).join(',');
control.getRange('B31').formulas=[[`=IF(AND(COUNT(B12:B29)=16,${equal},COUNT('NCC reference'!C10:C48)=39,COUNT('NCC reference'!B64:C70)=14,COUNT('Scenario source'!C5:E85)=243,COUNTIF('NCC annual'!Z5:Z43,"일치")=39,COUNTIF('NCC annual'!AA47:AA127,"일치")=81,COUNTIF('NCC annual'!X131:X137,"일치")=7),"최신 계산","재계산 필요")`]];
control.getRange('B31').conditionalFormats.add('containsText',{text:'재계산',format:{fill:'#fbe5e5',font:{color:'#a00000',bold:true}}});
for(let row=5;row<=9;row++)control.getRange(`B${row}`).formulas=[[`=IF($B$31="최신 계산",'NCC paths'!I${row},"재계산 필요")`]];
control.getRange('B10').formulas=[['=IF($B$31="최신 계산",\'NCC annual\'!R55-\'NCC annual\'!R54,"재계산 필요")']];control.getRange('B5:B10').setNumberFormat(money);
const notes=[['계산 범위','2027–2029 투자, 2030–2050 가동. 생산능력 115t/h, 원문 Table 1·3 참조.'],['사용 방법','노란 셀 편집 후 저장하고 재계산을 요청합니다. 새 파일에서 변경 가정과 비용 경로를 확인합니다.'],['공정 가정','증기 압력 계통을 하나의 열 서비스로 집계합니다. 보일러는 추가 설비이며 교체 중 정지는 0입니다.'],['비용 범위','원료·전력·메탄·설비 투자·유지비 포함. 탄소·노무·운전자본·조세·금융·기타 부산물 판매 제외.'],['가격 분포','IEA 중심 경로에 과거 공동 월별 블록 충격을 적용합니다. 12개월 산술 평균, 이론적 기대배율 1 보정.'],['해석 경계','가격·수명·증기 이용률은 가정입니다. 실제 회사 개조비나 최적 frontier로 해석하지 않습니다.'],['원문 위치','NCC reference의 원문 수치·단위·출처와 Scenario source의 중심 경로를 사용합니다.'],['통합 파일','Control은 기존 Layritz 부분 모형입니다. NCC cash는 Tiggeloven 신규 설비 가정으로 별도 재계산합니다.']];
control.getRange('A34:A41').values=notes.map(x=>[x[0]]);control.getRange('B34:B41').values=notes.map(x=>[x[1]]);
control.getRange('B34:F41').format.wrapText=false;control.getRange('A34:F41').format.rowHeightPx=30;

base(annual,138,[150,90,150,...Array(15).fill(170),30,150,365,165,255,90,390,160,160],'NCC 연간 물량과 현금 지급');
annual.getRange('A3').values=[['실행 시나리오']];annual.getRange('B3').formulas=[['=\'NCC cash\'!F12']];
annual.getRange('A4:R4').values=[['공정','연도','에틸렌 t','투자비 EUR','잔존수입 EUR','유지비 EUR','전력 MWh','나프타 t','메탄 구매 MWh','메탄 판매 −MWh','전력 EUR/MWh','나프타 EUR/t','메탄 EUR/MWh','할인계수','전력비 EUR','원료비 EUR','메탄 순비용 EUR','현재가치 백만 EUR']];header(annual,'A4:R4');annual.getRange('A4:R4').format.wrapText=true;annual.getRange('A4:R4').format.rowHeightPx=52;
annual.getRange('A5:N52').values=p.annual;
annual.getRange('O5:R52').formulas=p.annual.map((_,i)=>{const r=i+5;return [`=G${r}*K${r}`,`=H${r}*L${r}`,`=(I${r}+J${r})*M${r}`,`=(D${r}-E${r}+F${r}+O${r}+P${r}+Q${r})*N${r}/1E6`];});
annual.getRange('C5:R55').setNumberFormat(money);annual.getRange('B5:B52').setNumberFormat('0');annual.getRange('N5:N52').setNumberFormat('0.0000');
annual.getRange('Q54:Q55').values=[['기존 방식 합계'],['전기화 합계']];annual.getRange('R54:R55').formulas=[['=SUM(R5:R28)'],['=SUM(R29:R52)']];
annual.getRange('A58').values=[['아래 우측 원문은 실행 시점에 사용한 값입니다. 현재 원문과 비교하여 출처 변경 시 재계산을 표시합니다.']];
annual.getRange('T4:Z4').values=[['공정','원문 항목','원문 수치','단위','쪽','해석','현재 입력과 일치']];header(annual,'T4:Z4');
annual.getRange('T5:Y43').values=p.reference.observations;
annual.getRange('Z5:Z43').formulas=p.reference.observations.map((row,i)=>[`=IF(AND(${row.map((_,j)=>`${String.fromCharCode(84+j)}${i+5}='NCC reference'!${String.fromCharCode(65+j)}${i+10}`).join(',')}),"일치","변경")`]);
annual.getRange('T46:AA46').values=[['조회 키','시나리오','연도','원유 가격','LNG 가격','생성','출처','현재 입력과 일치']];header(annual,'T46:AA46');
annual.getRange('T47:Z127').values=p.scenarios;
annual.getRange('AA47:AA127').formulas=p.scenarios.map((row,i)=>[`=IF(AND(${row.map((_,j)=>`${String.fromCharCode(84+j)}${i+47}='Scenario source'!${String.fromCharCode(65+j)}${i+5}`).join(',')}),"일치","변경")`]);
annual.getRange('T130:X130').values=[['부산물','수율','가격','원문 근거','현재 입력과 일치']];header(annual,'T130:X130');annual.getRange('T131:W137').values=p.reference.coproducts;
annual.getRange('X131:X137').formulas=p.reference.coproducts.map((row,i)=>[`=IF(AND(${row.map((_,j)=>`${String.fromCharCode(84+j)}${i+131}='NCC reference'!${String.fromCharCode(65+j)}${i+64}`).join(',')}),"일치","변경")`]);
annual.freezePanes.freezeColumns(2);

base(draw,N+4,[100,205,205,205,220,30,30,270,230],'NCC 공동 가격 경로의 비용 분포');
draw.getRange('A3').values=[['단위: 백만 EUR2019 가정, 2027년 현재가치']];
draw.getRange('A4:E4').values=[['경로','기존 방식','전기화','증분비용','ES 경계 초과분']];header(draw,'A4:E4');
draw.getRange(`A5:C${last}`).values=p.draws;
draw.getRange(`D5:E${last}`).formulas=p.draws.map((_,i)=>{const r=i+5;return [`=C${r}-B${r}`,`=MAX(D${r}-$I$10,0)`];});draw.getRange(`B5:E${last}`).setNumberFormat(money);
draw.getRange('H4:I10').values=[['독립 Excel 계산','백만 EUR2019 가정'],['평균',null],['중앙값',null],['상위 분위 비용',null],['TCaR',null],['ES',null],['ES 경계 순서통계량',null]];header(draw,'H4:I4');
const costs=`D5:D${last}`,alpha="'NCC cash'!$F$16",paths="'NCC cash'!$F$15";
draw.getRange('I5:I10').formulas=[[`=AVERAGE(${costs})`],[`=PERCENTILE.INC(${costs},0.5)`],[`=PERCENTILE.INC(${costs},${alpha})`],['=I7-I6'],[`=I10+AVERAGE(E5:E${last})/(1-${alpha})`],[`=SMALL(${costs},ROUNDUP(${paths}*${alpha},0))`]];draw.getRange('I5:I10').setNumberFormat(money);
draw.getRange('H13:I13').values=[['실행 근거 파일','SHA256']];header(draw,'H13:I13');
const hashes=Object.entries(p.source_sha256).map(([k,v])=>[path.basename(k),v]);
draw.getRangeByIndexes(13,7,hashes.length,2).values=hashes;
draw.getRange(`H14:I${13+hashes.length}`).format.wrapText=true;draw.getRange(`H14:I${13+hashes.length}`).format.font={size:10,color:'#607080'};draw.getRange(`H14:I${13+hashes.length}`).format.rowHeightPx=70;
wb.recalculate();
const expected=['mean','p50','q_alpha','tcar','es_alpha'].map(k=>p.metrics[k]),actual=control.getRange('B5:B9').values.map(x=>x[0]);
for(let i=0;i<5;i++)if(typeof actual[i]!=='number'||Math.abs(actual[i]-expected[i])>1e-7*Math.max(1,Math.abs(expected[i])))throw Error(`NCC metric differs ${i}: ${actual[i]} vs ${expected[i]}`);
const theory=control.getRange('B10').values[0][0];if(Math.abs(theory-p.analytic_mean)>1e-7)throw Error('Annual cash formula differs');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'formula errors'});
await fs.writeFile(path.join(dir,'formula_errors.json'),JSON.stringify(errors));
if(preview)for(const [name,range,suffix]of [['NCC cash','A1:F41','control'],['NCC annual','A1:J12','quantities'],['NCC annual','K1:R12','annual_cost'],['NCC paths','A1:I12','paths']]){const blob=await wb.render({sheetName:name,range,scale:1});await fs.writeFile(path.join(dir,suffix+'.png'),new Uint8Array(await blob.arrayBuffer()));}
await fs.mkdir(path.dirname(out),{recursive:true});await(await SpreadsheetFile.exportXlsx(wb)).save(out);
await fs.writeFile(path.join(dir,'verification.json'),JSON.stringify({metrics:actual,expected,analytic_mean:theory,paths:N,FIN_checks:p.FIN_checks,max_FIN_error:p.max_FIN_error,native_Excel_tested:false},null,2));
console.log(JSON.stringify({out,paths:N,metrics:actual,analytic_mean:theory}));
