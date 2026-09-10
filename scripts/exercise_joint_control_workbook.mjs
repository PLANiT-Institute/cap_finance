import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..'),scratch=path.join(root,'tmp/ncc_joint_workbook');
const req=createRequire(path.join(scratch,'package.json'));
const {SpreadsheetFile,FileBlob}=await import(req.resolve('@oai/artifact-tool'));
const input=process.argv[2],out=process.argv[3]||path.join(scratch,'exercises');await fs.mkdir(out,{recursive:true});
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const control=wb.worksheets.getItem('Control'),source=wb.worksheets.getItem('Scenario source');
const original=control.getRange('B12:B26').values,checks=[];
async function save(name,changes,extra){
 control.getRange('B12:B26').values=original;
 for(const[cell,value]of Object.entries(changes))control.getRange(cell).values=[[value]];
 if(extra)extra();wb.recalculate();
 const state=control.getRange('B29').values[0][0],metric=control.getRange('B5').values[0][0];
 if(state!=='재계산 필요'||metric!=='재계산 필요')throw Error(name+': stale values exposed');
 const output=path.join(out,name+'.xlsx');await(await SpreadsheetFile.exportXlsx(wb)).save(output);
 checks.push({name,state,metric,annualNPV:control.getRange('B30').values[0][0],output});
}
await save('changed_scenario_and_fractional_tail',{B12:'NZE',B20:0,B24:.95327,B25:101});
await save('zero_production',{B16:0,B25:101});
await save('blank_production',{B16:null});
await save('changed_source',{},()=>source.getRange('D5').values=[[999]]);
source.getRange('D5').values=[[79]];
await save('changed_technology',{},()=>wb.worksheets.getItem('Technology DB').getRange('B7').values=[[3.59]]);
if(process.argv.includes('--reference')){
 control.getRange('B12:B26').values=original;
 wb.worksheets.getItem('Technology DB').getRange('B7').values=[[3.58]];
 const ref=wb.worksheets.getItem('NCC reference');
 for(const[name,cell,value]of [['changed_reference_yield','C23',.31],['changed_reference_coproduct','C66',400.]]){
  const old=ref.getRange(cell).values;ref.getRange(cell).values=[[value]];wb.recalculate();
  if(control.getRange('B29').values[0][0]!=='최신 계산')throw Error('Inactive reference changed active MC status');
  const output=path.join(out,name+'.xlsx');await(await SpreadsheetFile.exportXlsx(wb)).save(output);
  checks.push({name,output,activeMCUnchanged:true,referenceDerived:ref.getRange('B52:B56').values});
  ref.getRange(cell).values=old;
 }
}
await fs.writeFile(path.join(out,'checks.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify(checks));
