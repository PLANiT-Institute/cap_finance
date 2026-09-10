import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..'),req=createRequire(path.join(root,'tmp/ncc_joint_workbook/package.json'));
const {FileBlob,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const [input,dir]=process.argv.slice(2);await fs.mkdir(dir,{recursive:true});
const cases={changed:[['NCC cash','B12','NZE'],['NCC cash','B15',101],['NCC cash','B16',.95327],['NCC cash','B17',.8],['NCC cash','B18',7000],['NCC cash','B19',25],['NCC cash','B20',30],['NCC cash','B21',.01],['NCC cash','B22',0],['NCC cash','B23',0],['NCC cash','B24','straight_line_proxy'],['NCC cash','B25',80],['NCC cash','B26',50],['NCC cash','B27',700],['NCC cash','B28',1],['NCC cash','B29',.5]],
 zero:[['NCC cash','B15',101],['NCC cash','B16',.95327],['NCC cash','B25',0],['NCC cash','B26',0],['NCC cash','B27',0]],
 blank:[['NCC cash','B18',null]],fractional:[['NCC cash','B15',100.5]],alpha:[['NCC cash','B16',1]],
 source_value:[['NCC reference','C10',999]],source_unit:[['NCC reference','D10','wrong unit']],source_blank:[['NCC reference','C10',null]]};
if(process.argv.includes('--unified')){
 for(const key of Object.keys(cases))delete cases[key];
 Object.assign(cases,{
  both_changed:[['Control','B12','NZE'],['Control','B13','iid_gaussian'],['Control','B14',2030],['Control','B15',2040],['Control','B17',80],['Control','B18',-50],['Control','B24',.95327],['Control','B25',101],['NCC cash','B12','CPS'],['NCC cash','B15',103],['NCC cash','B16',.95123],['NCC cash','B18',7000],['NCC cash','B23',0]],
  blank_joint:[['Control','B16',null]],blank_cash:[['NCC cash','B18',null]],
  fractional_cash:[['NCC cash','B15',100.5]],
  technology_unit:[['Technology DB','C5','GJ/t ethylene']],
  scenario_provenance:[['Scenario source','G5','unreviewed source']],
  reference_unit:[['NCC reference','D10','wrong unit']],
 });
}
if(process.argv.includes('--grow-zero')){
 for(const key of Object.keys(cases))delete cases[key];
 cases.grow_zero=[['Control','B16',0],['Control','B25',205],['NCC cash','B15',207],['NCC cash','B25',0],['NCC cash','B26',0],['NCC cash','B27',0]];
}
const report=[];
for(const [name,edits] of Object.entries(cases)){
 const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));
 if(process.argv.includes('--grow-zero')){
  const note=wb.worksheets.add('User notes');note.getRange('A1:B2').values=[['연구자 메모','보존 확인'],['사용자 값',17]];
  note.getRange('B3').formulas=[['=B2*2']];note.getRange('A1:B1').format.fill='#eee6f5';
 }
 for(const [sheet,cell,v]of edits)wb.worksheets.getItem(sheet).getRange(cell).values=[[v]];
 wb.recalculate();const s=wb.worksheets.getItem('NCC cash'),status=s.getRange('B31').values[0][0];
 const jointStatus=wb.worksheets.getItem('Control').getRange('B29').values[0][0];
 if(!process.argv.includes('--unified')&&!process.argv.includes('--grow-zero')){
  if(status!=='재계산 필요'||s.getRange('B5').values[0][0]!=='재계산 필요')throw Error('Stale result not suppressed: '+name);
 }else if(['both_changed','grow_zero'].includes(name)&&[status,jointStatus].some(x=>x!=='재계산 필요'))throw Error('Both changed models must be stale');
 await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,name+'.xlsx'));report.push({name,status,jointStatus});
}
await fs.writeFile(path.join(dir,'stale_checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
