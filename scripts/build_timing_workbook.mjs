import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const req=createRequire(path.join(root,'tmp/ncc_joint_workbook/package.json'));
const {FileBlob,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const [payloadPath,out]=process.argv.slice(2),p=JSON.parse(await fs.readFile(payloadPath,'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p.input_workbook));
const preview=!process.argv.includes('--no-preview'),dir=path.dirname(payloadPath);
function sheet(name){let s;try{s=wb.worksheets.getItem(name);s.getUsedRange().clear({applyTo:'all'});}catch{s=wb.worksheets.add(name);}return s;}
const main=sheet('Timing'),annual=sheet('Timing annual'),draw=sheet('Timing paths');
const money='#,##0.00;(#,##0.00);"–"';
function setup(s,n,widths,title){s.showGridLines=false;const r=s.getRangeByIndexes(0,0,n,widths.length);r.format.font={name:'Helvetica Neue',size:11,color:'#172432'};r.format.rowHeightPx=28;r.format.verticalAlignment='center';widths.forEach((w,i)=>s.getRangeByIndexes(0,i,n,1).format.columnWidthPx=w);s.getRange('A2').values=[[title]];s.getRange('A2').format.font={size:17,bold:true,color:'#163b58'};s.getRange('A2').format.rowHeightPx=38;}
function header(s,r){s.getRange(r).format={fill:'#234e72',font:{bold:true,color:'#ffffff'},rowHeightPx:38,wrapText:true};}
setup(main,58,[270,145,185,175,175,175,175,195,160],'전환 시점별 배출 자격과 비용 비교');
main.getRange('A3').values=[['비용: 백만 EUR2019 가정 · 2027년 현재가치 · 동일 생산 92만t/년']];
main.getRange('A5:I5').values=[['가동 시작','배출 자격','누적 배출 비율','2050 배출 tCO2','해석적 평균','표본 평균','ES','TCaR','평균·ES 경계']];header(main,'A5:I5');
main.getRange('A6:A9').values=p.qualification.map(q=>[q.year]);
main.getRange('A13:C13').values=[['입력 항목','편집 값','단위와 해석']];header(main,'A13:C13');
const displayValue=k=>k==='constraint'?(p.controls[k]==='annual_linear'?'연도별 선형':'누적+말기'):p.controls[k];
main.getRange('A14:C27').values=p.fields.map(([k,label,unit])=>[label,displayValue(k),unit]);
main.getRange('B14:B27').format.fill='#fff2ca';main.getRange('B14:B27').format.font={color:'#0056b3'};
main.getRange('B15:B17').setNumberFormat('#,##0');main.getRange('B18:B23').setNumberFormat('0.000');main.getRange('B25:B27').setNumberFormat('0.000');
for(const r of [18,22,23,25])main.getRange(`B${r}`).setNumberFormat('0.0%');main.getRange('B26').setNumberFormat('0');
main.getRange('B14').dataValidation={rule:{type:'list',values:['CPS','STEPS','NZE']}};
main.getRange('B24').dataValidation={rule:{type:'list',values:['누적+말기','연도별 선형']}};
main.getRange('H13:I13').values=[['실행된 입력','저장된 값']];header(main,'H13:I13');
main.getRange('H14:I27').values=p.fields.map(([k,label])=>[label,displayValue(k)]);
main.getRange('I15:I17').setNumberFormat('0');main.getRange('I18:I23').setNumberFormat('0.000');main.getRange('I25:I27').setNumberFormat('0.000');
main.getRange('A30').values=[['입력과 실행 결과']];
const equal=p.fields.map((_,i)=>`B${i+14}=I${i+14}`).join(',');
main.getRange('B30').formulas=[[`=IF(AND(COUNT(B14:B27)=12,${equal},COUNTIFS('NCC annual'!Z5:Z43,"일치")=39,COUNTIFS('NCC annual'!AA47:AA127,"일치")=81,COUNTIFS('NCC annual'!X131:X137,"일치")=7),"최신 계산","재계산 필요")`]];
// Clearing cell contents/formats does not remove imported conditional rules.
// Replace this owned status rule so repeated refreshes do not accumulate it.
main.getRange('B30').conditionalFormats.deleteAll();
main.getRange('B30').conditionalFormats.add('containsText',{text:'재계산',format:{fill:'#fbe5e5',font:{color:'#a00000',bold:true}}});
const notes=[['재계산 방법','노란 셀을 편집하고 저장한 뒤 Timing 재계산을 요청합니다. 편집 중에는 이전 결과를 최신으로 표시하지 않습니다.'],['배출 제약','누적+말기는 두 상한을 함께 검사합니다. 연도별 선형은 2027 기준배출에서 말기 상한까지의 매년 경로입니다.'],['모형 경계','가동 시작 2030/2035/2040/2045 · 건설 3년 · 신규 수명 20년 · 생산 차질·말기 잔존수입 0 가정.'],['가격·비용','전력 100의 절반이 LNG 연동, 메탄 40·나프타 600 기준가격 가정. 탄소·노무·세금·금융비용 등 제외.'],['해석','적격 후보가 없으면 비용은 불가로 표시합니다. 표본 경계이며 실제 회사 최적 시점·국가 전력경로가 아닙니다.'],['통합 파일','이번 실행은 Timing만 갱신합니다. Control과 NCC cash의 독립 계산·통화 경계는 각 기존 도구를 따릅니다.'],['공정 출처','Tiggeloven et al. 2023, Table1·3·직접배출 본문. NCC reference의 원문과 동일한 고정 공정 패키지입니다.'],['가격 출처','IEA2025 STEPS/CPS/NZE 조건부 비율 + World Bank 월별 공동 블록 충격. Scenario source 참조.']];
if(p.integrated_refresh){
 notes[0][1]='노란 셀을 편집·저장한 뒤 전체 재계산을 요청합니다. 세 모형 검증 후 새 파일로 받습니다.';
 notes[5][1]='Control·NCC cash·Timing을 한 번에 갱신했습니다. 각 입력·통화·공정 경계는 독립이며 결과를 합산하지 않습니다.';
}
main.getRange('A33:B40').values=notes;
main.getRange('A43:B43').values=[['실행 근거','SHA256']];header(main,'A43:B43');
main.getRangeByIndexes(43,0,Object.keys(p.source_sha256).length,2).values=Object.entries(p.source_sha256).map(([k,v])=>[path.basename(k),v]);
main.getRange('A44:B55').format.font={size:10,color:'#607080'};

setup(annual,128,[165,80,130,130,155,155,165,165,165,165,135,135,135,115,170,110,25,25,25,25,165,180,180,130,130,185],'전환 일정의 연간 배출·물량·현금');
annual.getRange('A3').values=[['실행 시나리오']];annual.getRange('B3').formulas=[["='Timing'!I14"]];
annual.getRange('A4:P4').values=[['후보','연도','생산 t','전력 tCO2/MWh','배출 tCO2','선형 상한 tCO2','고정 현금 EUR','전력 MWh','나프타 t','메탄 순구매 MWh','전력 EUR/MWh','나프타 EUR/t','메탄 EUR/MWh','할인계수','현재가치 백만 EUR','선형 충족']];header(annual,'A4:P4');annual.getRange('A4:P4').format.rowHeightPx=54;
annual.getRange('A5:N124').values=p.annual;
annual.getRange('O5:P124').formulas=p.annual.map((_,i)=>{const r=i+5;return [`=(G${r}+H${r}*K${r}+I${r}*L${r}+J${r}*M${r})*N${r}/1E6`,`=E${r}<=F${r}+0.0000001`];});
annual.getRange('C5:O124').setNumberFormat(money);annual.getRange('D5:D124').setNumberFormat('0.0000');annual.getRange('N5:N124').setNumberFormat('0.0000');
annual.getRange('U4:Z4').values=[['후보','누적배출 tCO2','말기배출 tCO2','매년 선형 충족','적격','현재가치 합계']];header(annual,'U4:Z4');
for(let i=0;i<5;i++){
 const r=i+5,a=5+i*24,b=a+23;
 annual.getRange(`U${r}`).values=[[i===0?'baseline':p.qualification[i-1].candidate]];
 annual.getRange(`V${r}:Z${r}`).formulas=[[`=SUM(E${a}:E${b})`,`=E${b}`,`=COUNTIFS(P${a}:P${b},TRUE)=24`,i===0?'=FALSE':`=IF('Timing'!$I$24="연도별 선형",X${r},AND(V${r}<=$V$12+0.0000001,W${r}<=$V$13+0.0000001))`,`=SUM(O${a}:O${b})`]];
}
annual.getRange('U12:U13').values=[['누적 예산 tCO2'],['말기 상한 tCO2']];annual.getRange('V12:V13').formulas=[["=V5*'Timing'!I22"],["=E5*'Timing'!I23"]];
annual.getRange('V5:W13').setNumberFormat(money);annual.getRange('Z5:Z9').setNumberFormat(money);annual.freezePanes.freezeRows(4);annual.freezePanes.freezeColumns(2);

const N=p.draws.length,last=N+4;
setup(draw,Math.max(N+4,15),[80,160,160,160,160,160,25,160,160,160,160,190,180,180,180,180],'공동 가격 표본과 Excel 위험 계산');
draw.getRange('A3').values=[[N?'기준안 총비용과 각 적격 후보의 증분비용 · 백만 EUR2019 가정':'적격 후보 없음: 가격 표본 생성과 비용 계산을 수행하지 않았습니다.']];
draw.getRange('A4:K4').values=[['경로','기준안 총비용','2030 증분','2035 증분','2040 증분','2045 증분',null,'2030 초과분','2035 초과분','2040 초과분','2045 초과분']];header(draw,'A4:F4');header(draw,'H4:K4');
if(N)draw.getRange(`A5:F${last}`).values=p.draws;
draw.getRange('L4:P4').values=[['독립 Excel 계산',2030,2035,2040,2045]];header(draw,'L4:P4');
draw.getRange('L5:L10').values=[['표본 평균'],['중앙값'],['상위 분위 비용'],['TCaR'],['ES'],['ES 경계 순서통계량']];
for(let j=0;j<4;j++){
 const q=p.qualification[j],col=String.fromCharCode(67+j),helper=String.fromCharCode(72+j),summary=String.fromCharCode(77+j),range=`${col}5:${col}${last}`;
 if(q.eligible){
  draw.getRange(`${helper}5:${helper}${last}`).formulas=p.draws.map((_,i)=>[`=MAX(${col}${i+5}-$${summary}$10,0)`]);
  draw.getRange(`${summary}5:${summary}10`).formulas=[[`=AVERAGE(${range})`],[`=PERCENTILE.INC(${range},0.5)`],[`=PERCENTILE.INC(${range},'Timing'!$I$18)`],[`=${summary}7-${summary}6`],[`=${summary}10+AVERAGE(${helper}5:${helper}${last})/(1-'Timing'!$I$18)`],[`=SMALL(${range},ROUNDUP('Timing'!$I$15*'Timing'!$I$18,0))`]];
 }else draw.getRange(`${summary}5:${summary}10`).values=[['불가'],['불가'],['불가'],['불가'],['불가'],['불가']];
 const r=j+6,ar=j+6;
 main.getRange(`B${r}:D${r}`).formulas=[[`=IF($B$30<>"최신 계산","재계산 필요",IF('Timing annual'!Y${ar},"적격","불가"))`,`=IF($B$30="최신 계산",'Timing annual'!V${ar}/'Timing annual'!$V$5,"재계산 필요")`,`=IF($B$30="최신 계산",'Timing annual'!W${ar},"재계산 필요")`]];
 main.getRange(`E${r}:H${r}`).formulas=[[`=IF(B${r}="적격",'Timing annual'!Z${ar}-'Timing annual'!$Z$5,B${r})`,`=IF(B${r}="적격",'Timing paths'!${summary}5,B${r})`,`=IF(B${r}="적격",'Timing paths'!${summary}9,B${r})`,`=IF(B${r}="적격",'Timing paths'!${summary}8,B${r})`]];
 main.getRange(`I${r}`).formulas=[[`=IF(B${r}<>"적격",B${r},IF(COUNTIFS($B$6:$B$9,"적격",$E$6:$E$9,"<="&E${r},$G$6:$G$9,"<"&G${r})+COUNTIFS($B$6:$B$9,"적격",$E$6:$E$9,"<"&E${r},$G$6:$G$9,"<="&G${r})>0,"지배됨","경계"))`]];
}
main.getRange('C6:C9').setNumberFormat('0.00%');main.getRange('D6:H9').setNumberFormat(money);draw.getRange(`B5:K${Math.max(last,5)}`).setNumberFormat(money);draw.getRange('M5:P10').setNumberFormat(money);draw.freezePanes.freezeRows(4);
main.getRange('B6:B9').format.horizontalAlignment='center';main.getRange('E6:H9').format.horizontalAlignment='right';draw.getRange('M5:P10').format.horizontalAlignment='right';
wb.recalculate();
const results=main.getRange('A6:I9').values;
for(let i=0;i<4;i++){
 const q=p.qualification[i],r=results[i];if(r[1]!== (q.eligible?'적격':'불가'))throw Error(`Eligibility differs ${q.candidate}: ${r[1]}`);
 if(q.eligible){const m=p.metrics[q.candidate];for(const [j,k]of [[4,'analytic_mean'],[5,'mean'],[6,'es_alpha'],[7,'tcar']])if(Math.abs(r[j]-m[k])>1e-7)throw Error(`Risk differs ${k}`);if(r[8]!== (m.frontier?'경계':'지배됨'))throw Error('Frontier differs');}
}
await fs.writeFile(path.join(dir,'timing_inspect.json'),JSON.stringify(await wb.inspect({kind:'table',range:'Timing!A5:I9',include:'values,formulas',tableMaxRows:5,tableMaxCols:9,maxChars:6000})));
await fs.writeFile(path.join(dir,'timing_formula_errors.json'),JSON.stringify(await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'final error scan'})));
if(preview)for(const [name,range,file]of [['Timing','A1:I10','result'],['Timing','A13:I40','controls'],['Timing annual','A1:P10','annual'],['Timing annual','U4:Z13','eligibility'],['Timing paths','L4:P10','risk']]){const blob=await wb.render({sheetName:name,range,scale:1});await fs.writeFile(path.join(dir,file+'.png'),new Uint8Array(await blob.arrayBuffer()));}
await fs.mkdir(path.dirname(out),{recursive:true});await(await SpreadsheetFile.exportXlsx(wb)).save(out);
