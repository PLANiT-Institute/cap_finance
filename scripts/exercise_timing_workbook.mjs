import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..'),req=createRequire(path.join(root,'tmp/ncc_joint_workbook/package.json'));
const {FileBlob,SpreadsheetFile}=await import(req.resolve('@oai/artifact-tool'));
const [input,folder]=process.argv.slice(2);await fs.mkdir(folder,{recursive:true});
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));const s=wb.worksheets.getItem('Timing');
let staleChecks=0;
for(let row=14;row<=27;row++){
 const r=s.getRange(`B${row}`),old=r.values[0][0];
 r.values=[[row===14?'NZE':row===24?'연도별 선형':old+0.01]];wb.recalculate();
 if(s.getRange('B30').values[0][0]!=='재계산 필요')throw Error('Stale control not detected '+row);
 if(s.getRange('E6').values[0][0]!=='재계산 필요')throw Error('Old result not withheld');
 r.values=[[old]];wb.recalculate();staleChecks++;
}
const source=wb.worksheets.getItem('NCC reference').getRange('C10'),oldSource=source.values[0][0];source.values=[[oldSource+.001]];wb.recalculate();
if(s.getRange('B30').values[0][0]!=='재계산 필요')throw Error('Changed source not detected');source.values=[[oldSource]];wb.recalculate();staleChecks++;
const original=s.getRange('B14:B27').values;
async function write(name,changes){s.getRange('B14:B27').values=original;for(const [row,v]of Object.entries(changes))s.getRange(`B${row}`).values=[[v]];wb.recalculate();await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(folder,name+'.xlsx'));}
await write('changed',{14:'NZE',15:103,16:20260918,18:.93,22:1,25:.08,26:3,27:1.2});
await write('empty',{15:207,21:.05});
await write('annual',{15:101,24:'연도별 선형'});
await write('invalid_blank',{19:null});
await write('invalid_fraction',{22:1.1});
s.getRange('B14:B27').values=original;s.getRange('B19').formulas=[['=0.2']];wb.recalculate();await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(folder,'invalid_formula.xlsx'));
await fs.writeFile(path.join(folder,'stale_checks.json'),JSON.stringify({changed_controls:14,source_edits:1,total:staleChecks,result_withheld:true},null,2));
console.log({staleChecks});
