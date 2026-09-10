import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..'),scratch=path.join(root,'tmp/tcar_workbook');
const req=createRequire(path.join(scratch,'package.json'));
const {Workbook,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const data=JSON.parse(await fs.readFile(path.join(scratch,'research_v2_register_payload.json'),'utf8'));
const wb=Workbook.create();
const out=path.join(root,'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_research_v2_registers.xlsx');
const previews=path.join(scratch,'research_v2_previews');await fs.mkdir(previews,{recursive:true});
const letters=n=>{let x='';for(n++;n;n=Math.floor((n-1)/26))x=String.fromCharCode(65+(n-1)%26)+x;return x;};
function base(sh,rows,cols){
 sh.showGridLines=false;const a=sh.getRangeByIndexes(0,0,rows,cols);
 a.format.font={name:'Helvetica Neue',size:11,color:'#172432'};
 a.format.verticalAlignment='center';a.format.rowHeightPx=28;
}
const overview=wb.worksheets.add('Research overview'),ledger=wb.worksheets.add('NCC ledger'),source=wb.worksheets.add('NCC source flows');
for(const d of data.sheets)wb.worksheets.add(d.name);
const provenance=wb.worksheets.add('Reproduction');
base(overview,24,2);overview.tabColor='#234e72';
overview.getRange('A1:A24').format.columnWidthPx=235;overview.getRange('B1:B24').format.columnWidthPx=670;
overview.getRange('A2').values=[['TCaR 연구 자료와 계산 예제']];overview.getRange('A2').format.font={size:16,bold:true};
overview.getRange('A4:B10').values=[['항목','현재 사용 범위'],
 ['기술 사양','출처와 경계가 있는 참조 및 미검증 사양. 자동 기업 입력 채택 없음.'],
 ['가격분포','5개 생성법·각 10,000경로의 저장된 벤치마크 결과. 미래 기업위험의 검증 아님.'],
 ['회사 민감도','6개 축소 탐색 실행의 저장 결과. 셀 편집으로 재최적화되지 않음.'],
 ['NCC 원장','노란 입력을 바꾸면 전력비·메탄 판매의 부분 원장이 수식으로 갱신됨.'],
 ['GCAM·KAIST','대응표만 제공. 공식 수치 시나리오를 수령한 것으로 표시하지 않음.'],
 ['전체 계산 통제','v1 연구 통제 워크북과 별도. v2 기술·가격 모듈의 FIN 연결은 미완료.']];
overview.getRange('B5:B10').format.wrapText=true;overview.getRange('A5:B10').format.rowHeightPx=48;
overview.getRange('A13:B16').values=[['해석 수정','근거보다 강한 종전 표현을 수정했습니다.'],
 ['기술 상·하한','문헌 간 사양 차이를 검증된 최솟값·최댓값이나 확률분포로 해석하지 않음.'],
 ['다기간 꼬리','평균을 제거한 로그변화로 비교. 가격수준의 평균회귀는 식별하지 못함.'],
 ['결합 비용 분위수','전력·수소의 같은 경로 비용을 더한 뒤 분위수 산출. 개별 분위수의 합과 다름.']];
overview.getRange('B13:B16').format.wrapText=true;overview.getRange('A13:B16').format.rowHeightPx=46;
base(ledger,27,4);ledger.tabColor='#577c97';
ledger.getRange('A1:A27').format.columnWidthPx=330;ledger.getRange('B1:B27').format.columnWidthPx=175;
ledger.getRange('C1:C27').format.columnWidthPx=220;ledger.getRange('D1:D27').format.columnWidthPx=520;
ledger.getRange('A2').values=[['나프타 전기화의 부분 증분비용']];ledger.getRange('A2').format.font={size:16,bold:true};
ledger.getRange('A4:C6').values=[['결과','값','단위'],['단위 제품당 부분 비용',null,'EUR/t 에틸렌'],['생산량 적용 부분 비용',null,'EUR']];
ledger.getRange('A9:D13').values=[['편집 입력','값','단위','근거'],
 ['전력 가격',100,'EUR/MWh','예시 가정. 실제 조달가격이나 시나리오 전망 아님.'],
 ['메탄 판매 넷백',500,'EUR/t CH4','판매에 필요한 비용 차감 후 가격. 음수 가능. 예시 가정.'],
 ['남는 메탄의 판매 비율',1,'0–1','판매량/발생량. 실제 시장·계약의 검증 필요.'],
 ['에틸렌 생산량',1,'t','예시 가정. 회사 실제 생산량 아님.']];
ledger.getRange('B10:B13').format.fill='#fff2ca';ledger.getRange('B10:B13').setNumberFormat('#,##0.00');ledger.getRange('B12').setNumberFormat('0.0%');
ledger.getRange('B12').dataValidation={rule:{type:'decimal',operator:'between',formula1:0,formula2:1}};
ledger.getRange('A15').values=[['입력 상태']];ledger.getRange('B15').formulas=[['=IF(COUNT(B10:B13)<>4,"입력 필요",IF(OR(B10<0,B12<0,B12>1,B13<0),"범위 확인","계산 가능"))']];
ledger.getRange('A18:C22').values=[['계산','값','단위'],['추가 전력비',null,'EUR/t 에틸렌'],['메탄 판매 크레딧',null,'EUR/t 에틸렌'],['부분 증분비용',null,'EUR/t 에틸렌'],['생산량 적용',null,'EUR']];
ledger.getRange('B19:B22').formulas=[
 ['=IF($B$15="계산 가능",\'NCC source flows\'!B5*$B$10,"입력 확인")'],
 ['=IF($B$15="계산 가능",\'NCC source flows\'!B6*$B$11*$B$12,"입력 확인")'],
 ['=IF($B$15="계산 가능",B19-B20,"입력 확인")'],['=IF($B$15="계산 가능",B21*$B$13,"입력 확인")']];
ledger.getRange('B5:B6').formulas=[['=B21'],['=B22']];ledger.getRange('B19:B22').setNumberFormat('#,##0.00');ledger.getRange('B5:B6').setNumberFormat('#,##0.00');
ledger.getRange('A25').values=[['포함 범위']];ledger.getRange('D25').values=[['추가 전력 구매와 잠재 메탄 판매만 포함. CAPEX·증기·압축·기타 OPEX·탄소·처리비·할인 제외. 총 전환비용 또는 TCaR가 아님.']];
ledger.getRange('D25').format.wrapText=true;ledger.getRange('A25:D25').format.rowHeightPx=60;
base(source,10,5);[360,120,200,530,600].forEach((w,c)=>source.getRangeByIndexes(0,c,10,1).format.columnWidthPx=w);
source.getRange('A2').values=[['Layritz 공정 원장 참조']];source.getRange('A2').format.font={size:16,bold:true};
const url='https://publications.pik-potsdam.de/pubman/item/item_25669_1/component/file_25682/25669_preprint.pdf';
source.getRange('A4:E6').values=[['물량','값','단위','변환·경계','원문'],
 ['추가 구매 전력',data.ledger.added_electricity_MWh_per_t_ethylene,'MWh/t 에틸렌','6.99 총전력 − 0.21 기준 전력. 분해로 전력과 중복 합산 금지.',url],
 ['사용하지 않게 되는 내부 메탄',data.ledger.freed_internal_methane_t_per_t_ethylene,'t CH4/t 에틸렌','기존 내부 연료 0.488t. 구매가스 회피비용 아님. 실제 판매량은 별도.',url]];
source.getRange('B5:B6').setNumberFormat('0.000');source.getRange('D5:E6').format.wrapText=true;source.getRange('A5:E6').format.rowHeightPx=74;
for(const d of data.sheets){
 const sh=wb.worksheets.getItem(d.name),n=d.rows.length,m=d.columns.length;
 base(sh,n+5,m);sh.getRange('A2').values=[[d.name]];sh.getRange('A2').format.font={size:16,bold:true};
 sh.getRangeByIndexes(3,0,1,m).values=[d.columns];sh.getRangeByIndexes(4,0,n,m).values=d.rows;
 const widths=d.columns.map(f=>/note|derivation|source|limitation|scope|condition|boundary|interpret|status|evidence|spec|observation|tech|series|model/.test(f)?360:Math.max(125,Math.min(230,f.length*8+18)));
 for(let c=0;c<m;c++){
  sh.getRangeByIndexes(0,c,n+5,1).format.columnWidthPx=widths[c];sh.getRangeByIndexes(3,c,n+1,1).format.wrapText=true;
  if(d.rows.some(r=>typeof r[c]==='number'))sh.getRangeByIndexes(4,c,n,1).setNumberFormat(/year|paths|n_test|n_windows|length/.test(d.columns[c])?'0':'#,##0.000');
 }
 for(let i=0;i<n;i++){
  const lines=Math.max(...d.rows[i].map((v,c)=>Math.ceil([...String(v??'')].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?2:1),0)/(widths[c]/8))));
  sh.getRangeByIndexes(i+4,0,1,m).format.rowHeightPx=Math.max(42,Math.min(350,lines*19+12));
 }
 sh.getRangeByIndexes(3,0,1,m).format.rowHeightPx=64;sh.freezePanes.freezeRows(4);sh.freezePanes.freezeColumns(1);
 sh.tables.add(`A4:${letters(m-1)}${n+4}`,true,'R_'+d.name.replace(/[^a-zA-Z]/g,''));
 sh.getRangeByIndexes(3,0,1,m).format={fill:'#234e72',font:{color:'#ffffff',bold:true},wrapText:true,rowHeightPx:64};
 for(let i=0;i<n;i++)sh.getRangeByIndexes(i+4,0,1,m).format.fill=i%2?'#ffffff':'#f2f5f7';
}
base(provenance,data.sheets.length+10,4);[235,700,540,100].forEach((w,c)=>provenance.getRangeByIndexes(0,c,30,1).format.columnWidthPx=w);
provenance.getRange('A2').values=[['재생성 및 입력 스냅샷']];provenance.getRange('A2').format.font={size:16,bold:true};
provenance.getRange('A4:D4').values=[['시트','원본 CSV','SHA256','행 수']];provenance.getRangeByIndexes(4,0,data.sheets.length,4).values=data.sheets.map(d=>[d.name,d.source,d.sha256,d.rows.length]);
for(const sh of [overview,ledger,source,provenance]){
 const end=sh===overview?'B':sh===source?'E':sh===provenance?'D':'C';
 sh.getRange(`A4:${end}4`).format.fill='#234e72';sh.getRange(`A4:${end}4`).format.font={bold:true,color:'#ffffff'};
}
wb.recalculate();const checks=[];const get=()=>ledger.getRange('B5').values[0][0];
function expect(x,name){const value=get();if(typeof value!=='number'||Math.abs(value-x)>1e-8)throw Error(name+': '+value+' != '+x);checks.push({name,value});}
expect(434,'base hand calculation');ledger.getRange('B12').values=[[0]];wb.recalculate();expect(678,'no methane sales');
ledger.getRange('B12').values=[[1]];ledger.getRange('B10').values=[[200]];wb.recalculate();expect(1112,'electricity price change');
ledger.getRange('B10').values=[[null]];wb.recalculate();if(typeof get()==='number')throw Error('blank silently treated as zero');checks.push({name:'blank input exposed',value:get()});
ledger.getRange('B10').values=[[100]];wb.recalculate();expect(434,'restored');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'formula scan'});
await fs.writeFile(path.join(previews,'formula_scan.json'),JSON.stringify(errors));
for(const name of ['Research overview','NCC ledger','NCC source flows',...data.sheets.map(d=>d.name),'Reproduction']){
 const range=name==='Research overview'?'A1:B17':name==='NCC ledger'?'A1:D25':name==='NCC source flows'?'A1:E6':'A1:E7';
 const blob=await wb.render({sheetName:name,range,scale:1});await fs.writeFile(path.join(previews,name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir(path.dirname(out),{recursive:true});await (await SpreadsheetFile.exportXlsx(wb)).save(out);
await fs.writeFile(path.join(previews,'verification.json'),JSON.stringify({checks,sheets:data.sheets.length+4,sourceRows:data.sheets.reduce((n,d)=>n+d.rows.length,0),out},null,2));
console.log(JSON.stringify({out,checks,sourceRows:data.sheets.reduce((n,d)=>n+d.rows.length,0)}));
