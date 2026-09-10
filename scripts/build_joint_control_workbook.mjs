import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const req=createRequire(path.join(root,'tmp/ncc_joint_workbook/package.json'));
const {Workbook,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const [payloadPath,out]=process.argv.slice(2),preview=!process.argv.includes('--no-preview');
const data=JSON.parse(await fs.readFile(payloadPath,'utf8')),r=data.result,c=r.controls,N=c.paths,last=N+4;
const wb=Workbook.create(),names=['Control','Annual cost','Scenario source','Technology DB','MC summary','Cost paths','NCC reference'];
for(const name of names)wb.worksheets.add(name);
const [control,annual,source,tech,mc,draw]=names.map(n=>wb.worksheets.getItem(n));
const reference=wb.worksheets.getItem('NCC reference'),ref=data.reference;
if(!ref)throw Error('Reviewed NCC reference payload required');
const money='#,##0.00;(#,##0.00);"–"';
function base(sh,rows,widths){
 sh.showGridLines=false;
 const a=sh.getRangeByIndexes(0,0,rows,widths.length);
 a.format.font={name:'Helvetica Neue',size:11,color:'#172432'};a.format.rowHeightPx=27;
 a.format.verticalAlignment='center';
 widths.forEach((w,i)=>sh.getRangeByIndexes(0,i,rows,1).format.columnWidthPx=w);
 sh.freezePanes.freezeRows(4);
}
function title(sh,text){sh.getRange('A2').values=[[text]];sh.getRange('A2').format.font={size:17,bold:true,color:'#163b58'};sh.getRange('A2').format.rowHeightPx=36;}
function header(sh,range){sh.getRange(range).format={fill:'#234e72',font:{color:'#ffffff',bold:true},rowHeightPx:30};}
function fmt(sh,range){sh.getRange(range).setNumberFormat(money);}
base(control,37,[280,220,240,600]);title(control,'NCC 공동 가격 · 비용 위험 통제');
control.getRange('A4:D9').values=[['부분 증분비용 위험','실행 결과','단위','해석'],
 ['평균',null,'십억 KRW2024','전기화 − 기준 공정의 할인된 에너지·원료 부분 비용'],
 ['중앙값',null,'십억 KRW2024','같은 공동 가격 경로를 두 공정에 적용'],
 ['상위 분위 비용',null,'십억 KRW2024','선택한 α 분위수. 총 기업 전환비용이 아님'],
 ['TCaR: 분위수 − 중앙값',null,'십억 KRW2024','중앙값 대비 추가 비용. ES도 함께 비교'],
 ['ES: 상위 꼬리 평균',null,'십억 KRW2024','상위 (1−α) 질량의 평균. 경계 경로는 분할 가중']];
header(control,'A4:D4');fmt(control,'B5:B9');
control.getRange('A11:D11').values=[['입력 항목','편집 값','단위','가정과 적용 경계']];header(control,'A11:D11');
control.getRange('A12:D26').values=data.fields.map(([key,label,unit,note])=>[label,c[key],unit,note]);
control.getRange('B12:B26').format.fill='#fff2ca';control.getRange('B12:B26').format.font={color:'#0056b3'};
fmt(control,'B14:B26');for(const row of [14,15,25,26])control.getRange(`B${row}`).setNumberFormat('0');
for(const row of [20,21,23,24])control.getRange(`B${row}`).setNumberFormat('0.000%');
control.getRange('D12:D26').format.wrapText=true;control.getRange('A12:D26').format.rowHeightPx=35;
control.getRange('B12').dataValidation={rule:{type:'list',values:['CPS','STEPS','NZE']}};
control.getRange('B13').dataValidation={rule:{type:'list',values:['iid_gaussian','empirical_block_1','empirical_block_6','empirical_block_12','empirical_block_24']}};
control.getRange('A28:A30').values=[['입력 유효성'],['현재 결과와 입력 일치'],['중심 가격의 부분 비용 NPV']];
control.getRange('B28').formulas=[['=IF(COUNT(B14:B26)<>13,"입력 확인",IF(AND(OR(B12="CPS",B12="STEPS",B12="NZE"),OR(B13="iid_gaussian",B13="empirical_block_1",B13="empirical_block_6",B13="empirical_block_12",B13="empirical_block_24"),B14=INT(B14),B15=INT(B15),B25=INT(B25),B26=INT(B26),B14>=2024,B15<=2050,B14<=B15,B16>=0,B17>=0,B19>=0,B20>=0,B20<=1,B21>=0,B21<=1,B22>0,B23>-1,B24>0.5,B24<1,B25>=2,B25<=50000,B26>=0),"계산 가능","입력 확인"))']];
const equalInputs=data.fields.map((_,i)=>`B${i+12}='MC summary'!B${i+15}`).join(',');
control.getRange('B29').formulas=[[`=IF(AND(B28="계산 가능",${equalInputs},COUNTIF('Scenario source'!H5:H85,"일치")=81,'Technology DB'!B11="일치"),"최신 계산","재계산 필요")`]];
control.getRange('B30').formulas=[['=IF(B28="계산 가능",\'Annual cost\'!B29,"입력 확인")']];fmt(control,'B30');
control.getRange('C30:D30').values=[['십억 KRW2024','중심 가격 대입 결과. MC 평균과 표본 오차만큼 다를 수 있음']];
for(let i=5;i<=9;i++)control.getRange(`B${i}`).formulas=[[`=IF($B$29="최신 계산",'MC summary'!B${i},"재계산 필요")`]];
control.getRange('A33:D37').merge();control.getRange('A33').values=[['사용: 노란 셀 편집 → 중심 가격 비용은 즉시 갱신 → 공동 분포 결과는 재계산 후 갱신. 편집한 파일로 재계산을 요청하면 입력을 읽어 새 결과 파일을 만듭니다.\n범위: 고정 생산량 NCC 전기화의 전력·나프타·메탄 판매 부분 비용. CAPEX·탄소·그 외 OPEX·제품 매출·생산 조정 제외. 가격과 판매 가정은 실제 기업 계약이 아닙니다. 기술·시나리오 원표의 변경은 출처 갱신과 함께 별도 반영해야 합니다.']];
control.getRange('A33:D37').format.wrapText=true;control.getRange('A33:D37').format.fill='#edf2f6';

base(source,87,[155,100,90,190,215,140,580,140]);title(source,'IEA 2025 중심 가격 · 원자료와 보간');
source.getRange('A4:H4').values=[['조회 키','시나리오','연도','원유 USD2024/bbl','일본 LNG USD2024/MMBtu','생성','출처 · 발열량 HHV/LHV 미지정','실행 시점 비교']];header(source,'A4:H4');
source.getRange('A4:H4').format.wrapText=true;source.getRange('A4:H4').format.rowHeightPx=54;
source.getRange('A5:G85').values=data.scenarios;fmt(source,'D5:E85');
source.getRange('H5:H85').formulas=data.scenarios.map((_,i)=>{let row=i+5;return [`=IF(AND(A${row}='MC summary'!H${row},D${row}='MC summary'!I${row},E${row}='MC summary'!J${row}),"일치","원자료 변경")`];});
source.getRange('G5:G85').format.font={color:'#607080',size:9};
source.freezePanes.freezeColumns(3);

base(tech,15,[330,160,245,670]);title(tech,'NCC 기술 사양 · Layritz 참조 공정');
const techURL='https://publications.pik-potsdam.de/pubman/item/item_25669_1/component/file_25682/25669_preprint.pdf';
tech.getRange('A4:D8').values=[['기술 물량','수량','단위','해석'],
 ['기준 공정 구매 전력',.21,'MWh/t 에틸렌','전기화 공정의 총 전력과 비교'],
 ['전기화 공정 총 전력',6.99,'MWh/t 에틸렌','추가 전력은 6.99 − 0.21 = 6.78'],
 ['기준·전환 공통 나프타',3.58,'t 나프타/t 에틸렌','두 공정의 총 비용에 각각 포함. 증분 비용에서는 상쇄'],
 ['기준 공정 내부 메탄 연료',.488,'t CH4/t 에틸렌','전기화로 남는 양. 구매 가스 회피비용으로 중복 계산 금지']];header(tech,'A4:D4');tech.getRange('B5:B8').setNumberFormat('0.000');tech.getRange('D5:D8').format.wrapText=true;tech.getRange('A5:D8').format.rowHeightPx=48;
tech.getRange('A11').values=[['실행 시점의 물량과 비교']];
tech.getRange('B11').formulas=[['=IF(AND(COUNT(B5:B8)=4,B5=\'MC summary\'!D15,B6=\'MC summary\'!D16,B7=\'MC summary\'!D17,B8=\'MC summary\'!D18),"일치","원자료 변경")']];
tech.getRange('A13').values=[['문헌 원문']];tech.getRange('D13').values=[[techURL]];tech.getRange('D13').format.wrapText=true;tech.getRange('A13:D13').format.rowHeightPx=55;
tech.getRange('A15').values=[['추가 문헌 사양']];tech.getRange('D15').values=[['NCC reference에서 Tiggeloven 사양과 채택 보류 이유를 확인합니다.']];

base(reference,76,[160,365,165,255,90,390]);title(reference,'NCC 추가 문헌과 채택 상태');
reference.getRange('A4').values=[['계산 연결']];reference.getRange('B4').values=[[ref.model_use]];
reference.getRange('B4:F4').merge();reference.getRange('B4').format.wrapText=true;
reference.getRange('A5').values=[['남은 확인']];reference.getRange('B5:F5').merge();reference.getRange('B5').values=[[ref.outstanding]];
reference.getRange('A7').values=[['출판본 원문']];reference.getRange('B7:F7').merge();reference.getRange('B7').values=[[ref.source_main_url]];reference.getRange('B7').format.font={size:9,color:'#607080'};
reference.getRange('A9:F9').values=[['공정','원문 항목','원문 수치','원문 단위','PDF 쪽','해석 및 채택 상태']];header(reference,'A9:F9');
reference.getRange('A10:F48').values=ref.observations;reference.getRange('C10:C48').setNumberFormat('#,##0.0000');
reference.getRange('B10:B48').format.font={size:10};reference.getRange('F10:F48').format.wrapText=true;
reference.getRange('A10:F48').format.rowHeightPx=44;reference.freezePanes.freezeRows(9);
const sourceCell=(c,i)=>{const n=ref.observations.findIndex(x=>x[0]===c&&x[1]===i);if(n<0)throw Error('Missing source key');return `$C$${10+n}`;};
const y=sourceCell('electric','ethylene_yield'),sep=sourceCell('electric','separation_electricity_consumption');
reference.getRange('A51:D51').values=[['단위 변환','계산값','단위','현재 MC 입력 여부']];header(reference,'A51:D51');
reference.getRange('A52:D56').values=[['나프타 투입',null,'t/t 에틸렌','참조 검토 중'],['기존 전력',null,'MWh/t 에틸렌','참조 검토 중'],['전기화 전력',null,'MWh/t 에틸렌','참조 검토 중'],['전력 증가',null,'MWh/t 에틸렌','참조 검토 중'],['115t/h 전체 플랜트 투자비',null,'백만 EUR2019','개조비와 구분']];
reference.getRange('B52:B56').formulas=[[`=1/${y}`],[`=${sourceCell('conventional','separation_electricity_consumption')}/${sourceCell('conventional','ethylene_yield')}`],[`=(${sourceCell('electric','cracker_electricity_consumption')}+${sourceCell('electric','compression_electricity_consumption')}+${sep})/${y}`],['=B54-B53'],[`=(${sourceCell('electric','TOC_slope')}*${sourceCell('both','reference_capacity')}*1000+${sourceCell('electric','TOC_intercept')}*1E6)/1E6`]];
reference.getRange('B52:B56').setNumberFormat('#,##0.000');
reference.getRange('A56').format.wrapText=true;reference.getRange('A56:F56').format.rowHeightPx=44;
reference.getRange('B58:F59').merge();reference.getRange('B58').values=[['위 계산은 원문 단위 변환입니다. 유지비 비율과 수명, 메탄·증기 수지 및 개조비가 확정되지 않아 현재 비용 분포에 자동 적용하지 않습니다. 원문 수치 수정은 출처 검토와 함께 반영해야 합니다.']];reference.getRange('B58').format.wrapText=true;
reference.getRange('A61').values=[['보충자료 원문']];reference.getRange('B61:F61').merge();reference.getRange('B61').values=[[ref.source_si_url]];
reference.getRange('A63:D63').values=[['부산물','수율 t/t 나프타','가격 원문 EUR/t','원문이 인용한 가격 근거']];header(reference,'A63:D63');
reference.getRange('A64:D70').values=ref.coproducts;reference.getRange('B64:B70').setNumberFormat('0.0000');reference.getRange('C64:C70').setNumberFormat('#,##0.0');
reference.getRange('B72:F73').merge();reference.getRange('B72').values=[['Table S6의 비용배분 입력입니다. 순판매 수입·기업 계약가격 또는 공통 실질가격연도로 확정한 값이 아닙니다. 배분 비용에서 부산물 판매액을 다시 차감하면 중복입니다.']];reference.getRange('B72').format.wrapText=true;
reference.getRange('A75').values=[['출판본 SHA256']];reference.getRange('B75:F75').merge();reference.getRange('B75').values=[[ref.source_main_sha256]];
reference.getRange('A76').values=[['보충자료 SHA256']];reference.getRange('B76:F76').merge();reference.getRange('B76').values=[[ref.source_si_sha256]];

base(annual,31,[280,...Array(27).fill(150)]);title(annual,'중심 가격의 연도별 부분 비용');
const letter=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
annual.getRange('B4:AB4').values=[Array.from({length:27},(_,i)=>2024+i)];header(annual,'A4:AB4');
const labels={5:'계산 기간 포함',8:'원유 가격 / 2024 가격',9:'LNG 가격 / 2024 가격',10:'전력 EUR2024/MWh',11:'나프타 EUR2024/t',12:'메탄 넷백 EUR2024/t',14:'추가 전력 MWh',15:'판매 메탄 t',16:'공통 나프타 t',18:'추가 전력비 EUR2024',19:'메탄 판매 크레딧 EUR2024',20:'부분 증분비용 EUR2024',21:'부분 증분비용 십억 KRW2024',22:'할인계수',23:'할인된 부분 증분비용',29:'중심 가격 NPV · 십억 KRW2024'};
for(const [row,text]of Object.entries(labels))annual.getRange(`A${row}`).values=[[text]];
for(let i=1;i<=27;i++){
 const L=letter(i),lookup=col=>`INDEX('Scenario source'!$${col}$5:$${col}$85,MATCH(Control!$B$12&"_"&${L}$4,'Scenario source'!$A$5:$A$85,0))`,baseLookup=col=>`INDEX('Scenario source'!$${col}$5:$${col}$85,MATCH(Control!$B$12&"_2024",'Scenario source'!$A$5:$A$85,0))`;
 const f={5:`IF(Control!$B$28="계산 가능",IF(AND(${L}$4>=Control!$B$14,${L}$4<=Control!$B$15),1,0),0)`,8:`${lookup('D')}/${baseLookup('D')}`,9:`${lookup('E')}/${baseLookup('E')}`,10:`Control!$B$17*(1-Control!$B$20+Control!$B$20*${L}9)`,11:`Control!$B$19*${L}8`,12:`Control!$B$18*${L}9`,14:`('Technology DB'!$B$6-'Technology DB'!$B$5)*Control!$B$16`,15:`'Technology DB'!$B$8*Control!$B$21*Control!$B$16`,16:`'Technology DB'!$B$7*Control!$B$16`,18:`${L}10*${L}14`,19:`${L}12*${L}15`,20:`${L}18-${L}19`,21:`${L}20*Control!$B$22/1E9`,22:`(1+Control!$B$23)^-(${L}$4-Control!$B$14)`,23:`${L}21*${L}22`};
 for(const [row,formula]of Object.entries(f))annual.getRange(`${L}${row}`).formulas=[[row==='5'?`=${formula}`:`=IF(${L}$5=1,${formula},0)`]];
}
annual.getRange('B29').formulas=[['=SUM(B23:AB23)']];fmt(annual,'B8:AB29');annual.getRange('B22:AB22').setNumberFormat('0.0000');annual.freezePanes.freezeColumns(1);

base(mc,87,[290,225,60,180,430,60,60,165,190,200]);title(mc,'공동 경로 분포 · 실행 기록과 독립 수식');
mc.getRange('A4:B11').values=[['통계량 · 십억 KRW2024','독립 Excel 수식'],['평균',null],['중앙값',null],['α 분위 비용',null],['TCaR',null],['ES',null],['중심 가격 NPV',r.theoretical_mean_bnKRW2024],['ES 경계 순서통계량',null]];header(mc,'A4:B4');
const costs=`'Cost paths'!D5:D${last}`;
mc.getRange('B5:B9').formulas=[[`=AVERAGE(${costs})`],[`=PERCENTILE.INC(${costs},0.5)`],[`=PERCENTILE.INC(${costs},$B$27)`],['=B7-B6'],[`=B11+AVERAGE('Cost paths'!E5:E${last})/(1-$B$27)`]];
mc.getRange('B11').formulas=[[`=SMALL(${costs},ROUNDUP($B$28*$B$27,0))`]];fmt(mc,'B5:B11');
mc.getRange('A14:B14').values=[['실행된 입력','고정 스냅샷']];header(mc,'A14:B14');
mc.getRange('A15:B29').values=data.fields.map(([key])=>[key,c[key]]);
mc.getRange('D14:E18').values=[['실행된 기술 물량','설명'],[.21,'기준 전력 MWh/t'],[6.99,'전환 전력 MWh/t'],[3.58,'공통 나프타 t/t'],[.488,'발생 메탄 t/t']];header(mc,'D14:E14');
mc.getRange('H4:J4').values=[['실행 시나리오 키','원유 중심 가격','일본 LNG 중심 가격']];header(mc,'H4:J4');mc.getRange('H5:J85').values=data.scenarios.map(x=>[x[0],x[3],x[4]]);
mc.getRange('A32:B36').values=[['추가 진단','십억 KRW2024'],['기준 공정 평균',r.baseline_mean_bnKRW2024],['전환 공정 평균',r.transition_mean_bnKRW2024],['평균의 MC 표준오차',r.mc_mean_standard_error_bnKRW2024],['독립 FIN 계산 최대 오차',r.max_independent_formula_error_bnKRW2024]];header(mc,'A32:B32');fmt(mc,'B33:B36');mc.getRange('B36').setNumberFormat('0.00E+00');
mc.getRange('A39:E41').merge();mc.getRange('A39').values=[['분포 생성: 평균을 제거한 과거 월별 가격 변화로 공동 충격을 생성합니다. 블록 방식은 같은 역사적 월들을 함께 추출하고, 정규 방식은 추정 공분산을 사용합니다. 가격수준은 양수이며, 각 생성법의 이론적 기대값을 보정한 뒤 연간 12개월을 산술 평균합니다. 시뮬레이션 표본평균으로 나누지 않습니다. IEA 중심 가격에 적용한 조건부 모형이며 미래 예측의 검증은 아닙니다.']];mc.getRange('A39:E41').format.wrapText=true;
mc.getRange('A44:B44').values=[['입력 파일','SHA256']];header(mc,'A44:B44');mc.getRangeByIndexes(44,0,Object.keys(r.input_sha256).length,2).values=Object.entries(r.input_sha256);const hashLast=44+Object.keys(r.input_sha256).length;mc.getRange(`A45:B${hashLast}`).format.font={size:9,color:'#607080'};mc.getRange(`A45:B${hashLast}`).format.wrapText=true;mc.getRange(`A45:B${hashLast}`).format.rowHeightPx=64;

base(draw,N+4,[100,210,210,220,230]);title(draw,'같은 가격 경로 · 공정별 비용과 꼬리');
draw.getRange('B3:E3').merge();draw.getRange('B3').values=[['비용 단위: 십억 KRW2024 · 시작 연도로 할인한 부분 비용 NPV']];draw.getRange('B3').format.font={size:10,color:'#607080'};
draw.getRange('A4:E4').values=[['경로 번호','기준 비용','전환 비용','증분 비용 = 전환 − 기준','ES 경계 초과분']];header(draw,'A4:E4');
draw.getRange(`A5:C${last}`).values=data.draws;
draw.getRange(`D5:E${last}`).formulas=data.draws.map((_,i)=>{let row=i+5;return [`=C${row}-B${row}`,`=MAX(D${row}-'MC summary'!$B$11,0)`];});fmt(draw,`B5:E${last}`);
wb.recalculate();
const derived=reference.getRange('B52:B56').values.map(x=>x[0]);
for(let i=0;i<derived.length;i++)if(Math.abs(derived[i]-ref.derivation_values[i])>1e-9)throw Error('NCC source conversion differs');
const expected=[r.metrics.mean,r.metrics.p50,r.metrics.q_alpha,r.metrics.tcar,r.metrics.es_alpha];
const actual=mc.getRange('B5:B9').values.map(x=>x[0]);
for(let i=0;i<5;i++)if(typeof actual[i]!=='number'||Math.abs(actual[i]-expected[i])>1e-7*Math.max(1,Math.abs(expected[i])))throw Error(`Metric ${i}: ${actual[i]} != ${expected[i]}`);
const npv=annual.getRange('B29').values[0][0];if(Math.abs(npv-r.theoretical_mean_bnKRW2024)>1e-7*Math.max(1,Math.abs(npv)))throw Error('Annual formula differs');
if(control.getRange('B29').values[0][0]!=='최신 계산')throw Error('Fresh result incorrectly marked stale');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'formula errors'});
const dir=path.dirname(payloadPath);await fs.writeFile(path.join(dir,'formula_scan.json'),JSON.stringify(errors));
if(preview)for(const [name,range]of [['Control','A1:D37'],['Annual cost','A1:H29'],['Scenario source','A1:F10'],['Technology DB','A1:D13'],['MC summary','A1:E41'],['Cost paths','A1:E12']]){
 const blob=await wb.render({sheetName:name,range,scale:1});await fs.writeFile(path.join(dir,name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
if(preview)for(const [suffix,range]of [['top','A1:F17'],['capital','A24:F48'],['conversion','A51:F76']]){
 const blob=await wb.render({sheetName:'NCC reference',range,scale:1});await fs.writeFile(path.join(dir,`NCC_reference_${suffix}.png`),new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir(path.dirname(out),{recursive:true});await(await SpreadsheetFile.exportXlsx(wb)).save(out);
await fs.writeFile(path.join(dir,'verification.json'),JSON.stringify({out,paths:N,metrics_actual:actual,metrics_expected:expected,annual_formula_npv:npv,backend_npv:r.theoretical_mean_bnKRW2024,native_Excel_tested:false},null,2));
console.log(JSON.stringify({out,paths:N,metrics:actual,npv}));
