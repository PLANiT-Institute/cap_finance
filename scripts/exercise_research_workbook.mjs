// Temporary workbook edits for the user's requested round-trip and rejection tests.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const require=createRequire(path.join(root,'tmp/tcar_workbook/package.json'));
const {FileBlob,SpreadsheetFile}=await import(require.resolve('@oai/artifact-tool'));
const args=process.argv.slice(2);
const option=name=>args[args.indexOf(name)+1];
const source=option('--source'),manifest=JSON.parse(await fs.readFile(option('--edits'),'utf8'));
await fs.mkdir(manifest.output_directory,{recursive:true});
for(const scenario of manifest.scenarios){
 const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
 for(const edit of scenario.edits){
  const sheet=wb.worksheets.getItem(edit.sheet),range=sheet.getRange(edit.cell);
  if(edit.formula!==undefined) range.formulas=[[edit.formula]];
  else range.values=[[edit.value]];
 }
 const status=await wb.inspect({kind:'table',range:'Overview!A5:B5',include:'values,formulas',tableMaxRows:1,tableMaxCols:2,maxChars:1000});
 console.log(scenario.name,status.ndjson);
 const out=await SpreadsheetFile.exportXlsx(wb);
 await out.save(path.join(manifest.output_directory,scenario.name+'.xlsx'));
 if(scenario.preview){
  const blob=await wb.render({sheetName:'Overview',range:'A1:G6',scale:1,format:'png'});
  await fs.writeFile(path.join(manifest.output_directory,scenario.name+'.png'),new Uint8Array(await blob.arrayBuffer()));
 }
}
