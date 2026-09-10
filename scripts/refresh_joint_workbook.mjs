// Patch the existing ten-sheet workbook. Both models were executed before import.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const req=createRequire(path.join(root,'tmp/ncc_joint_workbook/package.json'));
const {FileBlob,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const [payloadPath,out]=process.argv.slice(2),preview=!process.argv.includes('--no-preview');
const p=JSON.parse(await fs.readFile(payloadPath,'utf8')),j=p.joint,r=j.result,c=p.cash,dir=path.dirname(payloadPath);
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(p.input_workbook));
const sheet=name=>wb.worksheets.getItem(name);
const mc=sheet('MC summary'),nc=sheet('NCC cash'),nd=sheet('NCC paths');
// Validate original units where the owning input sheet already checks quantities.
const techUnits=['MWh/t 에틸렌','MWh/t 에틸렌','t 나프타/t 에틸렌','t CH4/t 에틸렌'];
sheet('Technology DB').getRange('B11').formulas=[[`=IF(AND(COUNT(B5:B8)=4,B5='MC summary'!D15,B6='MC summary'!D16,B7='MC summary'!D17,B8='MC summary'!D18,${techUnits.map((u,i)=>`C${i+5}="${u}"`).join(',')}),"일치","원자료 변경")`]];
// Source metadata is checked against its existing execution snapshot as well.
sheet('Scenario source').getRange('H5:H85').formulas=j.scenarios.map((_,i)=>{
 const row=i+5,snapshot=i+47;
 return [`=IF(AND(A${row}='MC summary'!H${row},D${row}='MC summary'!I${row},E${row}='MC summary'!J${row},B${row}='NCC annual'!U${snapshot},C${row}='NCC annual'!V${snapshot},F${row}='NCC annual'!Y${snapshot},G${row}='NCC annual'!Z${snapshot}),"일치","원자료 변경")`];
});
const oldJoint=mc.getRange('B28').values[0][0],oldCash=nc.getRange('F15').values[0][0];
for(const n of [oldJoint,oldCash])if(!Number.isInteger(n)||n<2||n>50000)throw Error('Invalid stored path count');

function paths(name,draws,oldCount,boundary,money){
 const sh=sheet(name),N=draws.length,last=N+4;
 sh.getRange(`A5:E${Math.max(N,oldCount)+4}`).clear({applyTo:'contents'});
 if(N>oldCount){
  const added=sh.getRange(`A${oldCount+5}:E${last}`);
  added.format.font={name:'Helvetica Neue',size:11,color:'#172432'};
  added.format.rowHeightPx=name==='Cost paths'?27:28;
  added.format.verticalAlignment='center';
  sh.getRange(`B${oldCount+5}:E${last}`).setNumberFormat(money);
 }
 sh.getRange(`A5:C${last}`).values=draws;
 sh.getRange(`D5:E${last}`).formulas=draws.map((_,i)=>[`=C${i+5}-B${i+5}`,`=MAX(D${i+5}-${boundary},0)`]);
 return last;
}
const jl=paths('Cost paths',j.draws,oldJoint,"'MC summary'!$B$11",'#,##0.00;(#,##0.00);"–"');
mc.getRange('B15:B29').values=j.fields.map(([key])=>[r.controls[key]]);
mc.getRange('B10').values=[[r.theoretical_mean_bnKRW2024]];
mc.getRange('B33:B36').values=[[r.baseline_mean_bnKRW2024],[r.transition_mean_bnKRW2024],[r.mc_mean_standard_error_bnKRW2024],[r.max_independent_formula_error_bnKRW2024]];
const jd=`'Cost paths'!D5:D${jl}`;
mc.getRange('B5:B9').formulas=[[`=AVERAGE(${jd})`],[`=PERCENTILE.INC(${jd},0.5)`],[`=PERCENTILE.INC(${jd},$B$27)`],['=B7-B6'],[`=B11+AVERAGE('Cost paths'!E5:E${jl})/(1-$B$27)`]];
mc.getRange('B11').formulas=[[`=SMALL(${jd},ROUNDUP($B$28*$B$27,0))`]];
mc.getRangeByIndexes(44,0,Object.keys(r.input_sha256).length,2).values=Object.entries(r.input_sha256);

nc.getRange('F12:F29').values=c.fields.map(([key])=>[c.controls[key]]);
sheet('NCC annual').getRange('A5:N52').values=c.annual;
const cl=paths('NCC paths',c.draws,oldCash,'$I$10','#,##0.000;(#,##0.000);"–"');
const cd=`D5:D${cl}`,alpha="'NCC cash'!$F$16",count="'NCC cash'!$F$15";
nd.getRange('I5:I10').formulas=[[`=AVERAGE(${cd})`],[`=PERCENTILE.INC(${cd},0.5)`],[`=PERCENTILE.INC(${cd},${alpha})`],['=I7-I6'],[`=I10+AVERAGE(E5:E${cl})/(1-${alpha})`],[`=SMALL(${cd},ROUNDUP(${count}*${alpha},0))`]];
nd.getRangeByIndexes(13,7,Object.keys(c.source_sha256).length,2).values=Object.entries(c.source_sha256).map(([k,v])=>[path.basename(k),v]);
nc.getRange('B41').values=[['Control과 NCC cash의 가정을 각각 유지하며, 저장한 한 파일에서 두 모형을 함께 재계산합니다.']];
wb.recalculate();
for(const [name,expected,range]of [['Control',r.metrics,'B5:B9'],['NCC cash',c.metrics,'B5:B9']]){
 const actual=sheet(name).getRange(range).values.map(x=>x[0]);
 for(const [i,k]of ['mean','p50','q_alpha','tcar','es_alpha'].entries()){
  if(typeof actual[i]!=='number'||Math.abs(actual[i]-expected[k])>1e-7*Math.max(1,Math.abs(expected[k])))throw Error(`${name} ${k} mismatch`);
 }
}
if(sheet('Control').getRange('B29').values[0][0]!=='최신 계산'||nc.getRange('B31').values[0][0]!=='최신 계산')throw Error('A model remains stale');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'unified refresh errors'});
await fs.writeFile(path.join(dir,'formula_scan.json'),JSON.stringify(errors));
if(preview)for(const [name,range]of [['Control','A1:D37'],['NCC cash','A1:F41'],['MC summary','A1:E36'],['NCC paths','A1:I12'],['Annual cost','A1:H29'],['NCC annual','K1:R12']]){
 const blob=await wb.render({sheetName:name,range,scale:1});
 await fs.writeFile(path.join(dir,name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(out);
console.log(JSON.stringify({staged:out,joint_paths:j.draws.length,cash_paths:c.draws.length}));
