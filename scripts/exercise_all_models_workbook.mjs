// Disposable saved inputs for all-model refresh verification; no delivered variants.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const req=createRequire(path.join(root,'tmp/ncc_joint_workbook/package.json'));
const {FileBlob,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const [input,folder]=process.argv.slice(2);
await fs.mkdir(folder,{recursive:true});
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const changes={
 'Control':{B12:'NZE',B17:130,B24:.93,B25:103,B26:20260920},
 'NCC cash':{B12:'CPS',B14:20260921,B15:107,B16:.91,B23:.08,B25:120},
 'Timing':{B14:'STEPS',B15:109,B16:20260922,B18:.97,B22:1,B25:.07},
};
for(const [name,cells]of Object.entries(changes)){
 const sheet=wb.worksheets.getItem(name);
 for(const [cell,value]of Object.entries(cells))sheet.getRange(cell).values=[[value]];
}
wb.recalculate();
for(const [name,cell]of [['Control','B29'],['NCC cash','B31'],['Timing','B30']]){
 if(wb.worksheets.getItem(name).getRange(cell).values[0][0]!=='재계산 필요')throw Error('Stale model not withheld: '+name);
}
async function save(name){wb.recalculate();await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(folder,name+'.xlsx'));}
await save('changed');
const timing=wb.worksheets.getItem('Timing');
timing.getRange('B21').values=[[.05]];
await save('empty_timing');
timing.getRange('B21').values=[[0]];
timing.getRange('B19').formulas=[['=0.2']];
await save('invalid_timing_formula');
timing.getRange('B19').values=[[.2]];
const source=wb.worksheets.getItem('NCC reference').getRange('C10');
source.values=[[source.values[0][0]+.001]];
await save('invalid_source');
await fs.writeFile(path.join(folder,'edited_controls.json'),JSON.stringify({changes,all_three_stale:true},null,2));
console.log({three_models_withheld:true,temporary_inputs:4});
