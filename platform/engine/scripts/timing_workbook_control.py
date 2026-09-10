"""Refresh only the timing extension of the integrated research workbook."""
from pathlib import Path
import argparse,hashlib,json,math,os,shutil,subprocess,sys,tempfile
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.reference_timing import timing_menu,emission_qualification
from cap.risk_metrics import loss_summary,pareto_mask
from cap.plancost import simulate_cost
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from cap import config as C
from research_block_price_paths import block_paths
from xlsx_table_reader import read_cells,literal,WorkbookInputError
from ncc_cash_workbook_control import read_input as validate_shared_sources

NODE=Path('/Users/jinsu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
FIELDS=[('scenario','가격 시나리오','IEA2025 조건부 경로'),('paths','표본 경로 수','2–10000'),('seed','난수 시드','다른 값은 독립 표본'),('block','월별 블록 길이','1 / 6 / 12 / 24개월'),('alpha','상위 위험 분위','0.5 초과, 1 미만'),('grid_start','2027년 전력계수','tCO2/MWh · 가정'),('grid_end','2050년 전력계수','tCO2/MWh · 선형 연결'),('residual','공통 잔여배출','tCO2/t 나프타 · 가정'),('cum_fraction','누적 배출예산 비율','동일 조건 기존 유지 누적배출 대비'),('terminal_fraction','2050년 배출 상한 비율','2027년 기존 유지 배출 대비'),('constraint','적용할 배출 제약','누적+말기 또는 연도별 선형'),('discount','할인율','2027년 현재가치'),('remaining_years','기존 설비 남은 수명','1–25년 · 공통 가정'),('replacement_scale','기존 교체비 배율','신규 재래식 참조비 대비')]
DEFAULTS=dict(scenario='STEPS',paths=5000,seed=20260917,block=12,alpha=.95,grid_start=.2,grid_end=0.,residual=0.,cum_fraction=.75,terminal_fraction=0.,constraint='cumulative_terminal',discount=.05,remaining_years=8,replacement_scale=1.)
NEW_SHEETS={'Timing','Timing annual','Timing paths'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def validate(values):
 c=values.copy()
 if set(c)!=set(DEFAULTS):raise WorkbookInputError('Timing controls missing or unknown')
 if c['scenario'] not in ['CPS','STEPS','NZE'] or c['constraint'] not in ['cumulative_terminal','annual_linear']:raise WorkbookInputError('Unknown scenario or emissions constraint')
 for k in set(c)-{'scenario','constraint'}:
  if isinstance(c[k],bool) or not isinstance(c[k],(int,float)) or not math.isfinite(c[k]):raise WorkbookInputError('Finite literal number required: '+k)
 for k,lo,hi in [('paths',2,10000),('seed',0,2**32-1),('block',1,24),('remaining_years',1,25)]:
  if c[k]!=int(c[k]) or not lo<=c[k]<=hi:raise WorkbookInputError('Integer range: '+k)
  c[k]=int(c[k])
 if c['block'] not in [1,6,12,24] or not .5<c['alpha']<1:raise WorkbookInputError('Block or risk alpha invalid')
 for k,hi in [('grid_start',2),('grid_end',2),('residual',2),('cum_fraction',1),('terminal_fraction',1),('discount',1),('replacement_scale',5)]:
  if not 0<=c[k]<=hi:raise WorkbookInputError('Supported control range: '+k)
 return c

def read_input(path):
 validate_shared_sources(path)
 s=read_cells(path)
 if 'Timing' not in s:
  if NEW_SHEETS&set(s):raise WorkbookInputError('Timing control sheet missing')
  return DEFAULTS.copy()
 c={}
 for row,(key,label,unit) in enumerate(FIELDS,14):
  if literal(s['Timing'],row,1,f'Timing!A{row}')!=label or literal(s['Timing'],row,3,f'Timing!C{row}')!=unit:raise WorkbookInputError('Timing labels or units changed')
  c[key]=literal(s['Timing'],row,2,f'Timing!B{row}')
 c['constraint']={'누적+말기':'cumulative_terminal','연도별 선형':'annual_linear'}.get(c['constraint'],c['constraint'])
 return validate(c)

def evaluate(c):
 c=validate(c);yy=np.arange(2027,2051);T=len(yy);N=c['paths'];disc=(1+c['discount'])**-np.arange(T)
 src=ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv';histfile=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv';curvefile=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
 if sha(src)!=json.loads((src.parent/'manifest.json').read_text())['sha256'][str(src.relative_to(ROOT))]:raise WorkbookInputError('Source package changed')
 if sha(histfile)!=json.loads((ROOT/'data/research_v2/block_price_paths/manifest.json').read_text())['source_sha256']:raise WorkbookInputError('History changed')
 emission_source=ROOT/'data/research_v2/ncc_emissions_context/direct_emissions_observations.csv'
 if sha(emission_source)!=json.loads((emission_source.parent/'manifest.json').read_text())['artifact_sha256'][str(emission_source.relative_to(ROOT))]:raise WorkbookInputError('Direct emission source changed')
 direct=pd.read_csv(emission_source).set_index('case');direct_c=float(direct.loc['conventional','value']);direct_e=float(direct.loc['electric','value'])
 if not (direct.unit=='kgCO2/kg_naphtha').all():raise WorkbookInputError('Direct emission source units differ')
 obs=pd.read_csv(src).to_dict('records');menu=timing_menu(obs,[2030,2035,2040,2045],remaining_years=c['remaining_years'],replacement_cost_scale=c['replacement_scale'],numerical_KRW_per_EUR=1000.)
 grid=np.linspace(c['grid_start'],c['grid_end'],T);feed=menu['baseline'].additional_commodity_flows[0].quantity
 base_emissions=feed*(direct_c+c['residual'])+menu['baseline'].grid_mwh*grid;terminal=base_emissions[0]*c['terminal_fraction'];caps=np.linspace(base_emissions[0],terminal,T);budget=float(c['cum_fraction']*base_emissions.sum())
 qual=[];emissions={};eligible=[]
 for name,r in menu['candidates'].items():
  emissions[name]=np.where(r['electric_active'],direct_e,direct_c)*feed+r['profile'].grid_mwh*grid+c['residual']*feed
  q=emission_qualification(emissions[name],annual_caps=caps,cumulative_cap=budget,terminal_cap=float(terminal))
  passed=q['annual_feasible'] if c['constraint']=='annual_linear' else q['cumulative_feasible'] and q['terminal_feasible']
  if passed:eligible.append(name)
  qual.append(dict(candidate=name,year=r['commission_year'],eligible=bool(passed),cumulative_ratio=float(emissions[name].sum()/base_emissions.sum()),terminal=float(emissions[name][-1]),**q))
 # No price draws if the feasible set is empty. An empty set is not zero cost.
 curves=[ScenarioPriceCurve(**x) for x in json.loads(curvefile.read_text())]
 def ratio(item,region=None):
  curve=next(x for x in curves if x.scenario==c['scenario'] and x.commodity==item and (region is None or x.region==region))
  return np.array(interpolate_curve(curve,yy,method='linear').values)/curve.values[0]
 gr=ratio('natural_gas','Japan');orr=ratio('crude_oil');cp=100*(.5+.5*gr);cg=40*gr;cn=600*orr
 def manual(p,fixed,pe,pg,pn):
  f=p.additional_commodity_flows
  return ((fixed+p.grid_mwh*pe+f[0].quantity*pn+(f[1].quantity+f[2].quantity)*pg)*disc).sum(axis=-1)/1e6
 base_mean=float(manual(menu['baseline'],menu['baseline_fixed_cash_EUR'],cp,cg,cn))
 metrics={};draws=[];checks=0;errors=[]
 if eligible:
  hist=pd.read_csv(histfile).set_index('period');monthly,_,_=block_paths(hist.to_numpy(),T*12,N,c['block'],c['seed'])
  annual=monthly.reshape(N,T,12,len(hist.columns)).mean(axis=2);del monthly
  gas=annual[:,:,hist.columns.get_loc('japan_lng')];oil=annual[:,:,hist.columns.get_loc('brent')];pe=100*(.5+.5*gr*gas);pg=cg*gas;pn=cn*oil
  prices={k:np.zeros(T) for k in ['elec','re','h2','co2','coal','gas']};prices.update(elec=cp*1000,methane=cg*1000,naphtha=cn*1000)
  shocks={k:np.ones((N,T)) for k in ['elec','h2','capex']};shocks.update(elec=pe/cp,methane=gas,naphtha=oil)
  cfg=C.load(discount_rate=c['discount'],carbon_accounting_mode='gross_obligation_proxy');cfg['years']={'start':2027,'end':2050}
  totals={}
  for name in ['baseline']+eligible:
   p=menu['baseline'] if name=='baseline' else menu['candidates'][name]['profile'];fixed=menu['baseline_fixed_cash_EUR'] if name=='baseline' else menu['candidates'][name]['fixed_cash_EUR']
   totals[name]=simulate_cost(p,prices,shocks,{'subsidy':{}},cfg,freeze='capex');expected=manual(p,fixed,pe,pg,pn)
   np.testing.assert_allclose(totals[name],expected,rtol=1e-12,atol=1e-7);checks+=N;errors.append(float(np.max(abs(totals[name]-expected))))
  for name in eligible:
   r=menu['candidates'][name];metrics[name]=dict(**loss_summary(totals[name]-totals['baseline'],c['alpha']),analytic_mean=float(manual(r['profile'],r['fixed_cash_EUR'],cp,cg,cn))-base_mean)
  mask=pareto_mask([metrics[n]['analytic_mean'] for n in eligible],[metrics[n]['es_alpha'] for n in eligible])
  for name,keep in zip(eligible,mask):metrics[name]['frontier']=bool(keep)
  draws=[[i+1,float(totals['baseline'][i])]+[float(totals[n][i]-totals['baseline'][i]) if n in totals else None for n in menu['candidates']] for i in range(N)]
 annual=[]
 for name in ['baseline']+list(menu['candidates']):
  p=menu['baseline'] if name=='baseline' else menu['candidates'][name]['profile'];fixed=menu['baseline_fixed_cash_EUR'] if name=='baseline' else menu['candidates'][name]['fixed_cash_EUR'];e=base_emissions if name=='baseline' else emissions[name]
  for i,y in enumerate(yy):annual.append([name,int(y),920000.,float(grid[i]),float(e[i]),float(caps[i]),float(fixed[i]),float(p.grid_mwh[i]),float(feed[i]),float(sum(f.quantity[i] for f in p.additional_commodity_flows[1:])),float(cp[i]),float(cn[i]),float(cg[i]),float(disc[i])])
 inputs=[src,histfile,curvefile,emission_source,ROOT/'src/cap/reference_timing.py',ROOT/'src/cap/reference_ncc.py',ROOT/'src/cap/reference_incumbent.py',ROOT/'src/cap/component_capital.py',ROOT/'src/cap/capital_ledger.py',ROOT/'src/cap/plancost.py',ROOT/'src/cap/risk_metrics.py',ROOT/'scripts/research_block_price_paths.py',Path(__file__)]
 return dict(controls=c,fields=FIELDS,qualification=qual,metrics=metrics,draws=draws,annual=annual,cumulative_budget=budget,terminal_budget=float(terminal),FIN_checks=checks,max_FIN_error=max(errors,default=0.),MC_executed=bool(eligible),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},corporate_calibration=False,scope='Reference timing only; same 920kt/year; fixed price mapping; carbon and other nonmodeled costs excluded')

def verify_saved(path,p):
 s=read_cells(path);main=s['Timing'];before=read_cells(p['input_workbook'])
 for name,cells in before.items():
  if name in NEW_SHEETS:continue
  assert cells==s[name],f'Existing sheet changed: {name}'
 assert main[30,2]['value']=='최신 계산'
 raw=s['Timing paths'];count=sum(1 for (r,c),v in raw.items() if r>=5 and c==1 and isinstance(v['value'],(int,float)))
 assert count==len(p['draws']), 'Stale or missing cost paths'
 # Independent saved-file cash arithmetic and fractional empirical tail mass.
 annual=s['Timing annual'];npv=[]
 for row in range(5,125):
  v=[annual[row,col]['value'] for col in range(1,16)]
  expected=(v[6]+v[7]*v[10]+v[8]*v[11]+v[9]*v[12])*v[13]/1e6
  np.testing.assert_allclose(v[14],expected,rtol=1e-12,atol=1e-7);npv.append(expected)
 for i,q in enumerate(p['qualification'],6):
  assert main[i,2]['value']==('적격' if q['eligible'] else '불가')
  np.testing.assert_allclose([main[i,3]['value'],main[i,4]['value']],[q['cumulative_ratio'],q['terminal']],rtol=1e-12,atol=1e-7)
  if q['eligible']:
   m=p['metrics'][q['candidate']]
   for j,k in enumerate(['analytic_mean','mean','es_alpha','tcar'],5):np.testing.assert_allclose(main[i,j]['value'],m[k],rtol=1e-12,atol=1e-7)
   cost_col=i-3;x=np.array([raw[r,cost_col]['value'] for r in range(5,count+5)]);ordered=np.sort(x);mass=count*(1-p['controls']['alpha']);whole=int(mass)
   es=(ordered[-whole:].sum() if whole else 0.)+(mass-whole)*ordered[-whole-1];es/=mass
   np.testing.assert_allclose([main[i,6]['value'],main[i,7]['value'],main[i,8]['value']],[x.mean(),es,np.quantile(x,p['controls']['alpha'])-np.median(x)],rtol=1e-12,atol=1e-7)
   offset=(i-5)*24;np.testing.assert_allclose(main[i,5]['value'],sum(npv[offset:offset+24])-sum(npv[:24]),rtol=1e-12,atol=1e-7)
   assert main[i,9]['value']==('경계' if m['frontier'] else '지배됨')
  else:assert all(main[i,j]['value']=='불가' for j in range(5,10))
 errors=[(name,cell) for name,cells in s.items() for cell in cells.values() if cell['error']]
 assert not errors,errors[:3]
 return dict(candidates_checked=4,risk_values_checked=len(p['metrics'])*4,annual_cash_formulas_checked=120,saved_path_rows_checked=count,existing_sheets_preserved=len(before.keys()-NEW_SHEETS),native_Excel_tested=False)

def refresh(input_path,output_path,scratch,preview=True,*,integrated_refresh=False):
 input_path,output_path,scratch=map(lambda x:Path(x).resolve(),[input_path,output_path,scratch])
 if output_path.exists() or input_path==output_path:raise WorkbookInputError('Distinct unused output path required')
 if scratch.exists() and any(scratch.iterdir()):raise WorkbookInputError('Empty run directory required')
 scratch.mkdir(parents=True,exist_ok=True);h=sha(input_path);snapshot=scratch/'input.xlsx';shutil.copyfile(input_path,snapshot)
 if sha(snapshot)!=h:raise WorkbookInputError('Input changed during snapshot')
 c=read_input(snapshot);p=evaluate(c);p['input_workbook']=str(snapshot);p['integrated_refresh']=integrated_refresh;payload=scratch/'payload.json';payload.write_text(json.dumps(p,ensure_ascii=False,allow_nan=False)+'\n')
 output_path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(dir=output_path.parent,prefix='.timing-') as stage:
  candidate=Path(stage)/'result.xlsx';cmd=[str(NODE),str(ROOT/'scripts/build_timing_workbook.mjs'),str(payload),str(candidate)]
  if not preview:cmd.append('--no-preview')
  subprocess.run(cmd,check=True,cwd=ROOT);report=verify_saved(candidate,p)
  if sha(input_path)!=h:raise WorkbookInputError('Input changed during run')
  report.update(input_sha256=h,output_sha256=sha(candidate),FIN_checks=p['FIN_checks'],MC_executed=p['MC_executed'],input_preserved=True)
  (scratch/'verification.json').write_text(json.dumps(report,indent=2)+'\n');os.link(candidate,output_path)
 return report

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',required=True);ap.add_argument('--output',required=True);ap.add_argument('--scratch',required=True);ap.add_argument('--no-preview',action='store_true');a=ap.parse_args()
 print(refresh(a.input,a.output,a.scratch,not a.no_preview))
