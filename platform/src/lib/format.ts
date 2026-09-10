export type Cell = string | number | boolean | null;
export type Row = Record<string, Cell>;
export const fmt = (value: unknown, digits=1): string => typeof value === 'number' && Number.isFinite(value) ? value.toLocaleString('ko-KR', {maximumFractionDigits:digits, minimumFractionDigits:digits}) : '—';
export function download(name:string, content:string, type='application/json') {
  const url=URL.createObjectURL(new Blob([content], {type: `${type};charset=utf-8`}));
  const a=document.createElement('a'); a.href=url; a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function csvDownload(name:string, rows:Row[]) {
  if (!rows.length) return;
  const cols=Object.keys(rows[0]);
  const cell=(v:unknown)=>'"'+String(v??'').replace(/^[=+@\t\r]/,"' $&").replaceAll('"','""')+'"';
  download(name,'\uFEFF'+[cols,...rows.map(r=>cols.map(k=>r[k]))].map(r=>r.map(cell).join(',')).join('\r\n'),'text/csv');
}
