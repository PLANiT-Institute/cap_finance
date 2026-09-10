"""Explicit assumption controls for the conditional NCC capital/energy ledger."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, math
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.reference_ncc import NCCConditions,build_ncc_reference
from cap.plancost import simulate_cost
from cap.reference_delivery import validate_ncc_delivery_pair
from cap.risk_metrics import loss_summary
from cap import config as C
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from research_block_price_paths import block_paths
from joint_workbook_control import read_controls as read_original,reference_data,sources,NODE
from xlsx_table_reader import read_cells,literal,WorkbookInputError

FIELDS=[
 ('scenario','IEA 시나리오','CPS / STEPS / NZE'),
 ('block','공동 블록 길이','개월: 1 / 6 / 12 / 24'),
 ('seed','난수 시드','0 이상의 정수'),
 ('paths','경로 수','2–10,000'),
 ('alpha','꼬리 분위수','0.5 초과, 1 미만'),
 ('recovery','유효 증기 이용률','압력 계통 집계 가정, 0–1'),
 ('hours','연간 가동시간','시간/년, 0 초과 8,760 이하'),
 ('base_life','기존 방식 신규 설비 수명','년, 1–100'),
 ('electric_life','전기화 신규 설비 수명','년, 1–100'),
 ('maintenance_scale','원문 유지비 비율 해석','1: 소수 비율 / 0.01: 문자 그대로 %'),
 ('annuity_rate','유지비 환산 연율','연간 환산 투자비 기준'),
 ('discount','현금흐름 할인율','실질 연율, 0–100%'),
 ('terminal','잔존가치 가정','none / straight_line_proxy'),
 ('power','기준 전력 가격','EUR2019 가정/MWh'),
 ('methane','기준 메탄 가격','EUR2019 가정/원문 에너지 MWh'),
 ('naphtha','기준 나프타 가격','EUR2019 가정/t'),
 ('beta','전력의 LNG 연동 비중','0–1, 고정 성분과 혼합'),
 ('sale','잉여 메탄 판매비율','0–1, 미판매는 경계 밖 무상 이전')]
DEFAULTS=dict(scenario='STEPS',block=12,seed=20260913,paths=5000,alpha=.95,recovery=1.,hours=8000.,
 base_life=30,electric_life=20,maintenance_scale=1.,annuity_rate=.05,discount=.05,terminal='none',power=100.,methane=40.,naphtha=600.,beta=.5,sale=1.)

def validate(c):
 if set(c)!=set(DEFAULTS):raise WorkbookInputError('Required NCC cash controls changed')
 if c['scenario'] not in ('CPS','STEPS','NZE') or c['terminal'] not in ('none','straight_line_proxy'):raise WorkbookInputError('Unknown scenario or terminal rule')
 for k in set(c)-{'scenario','terminal'}:
  if isinstance(c[k],bool) or not isinstance(c[k],(int,float)) or not math.isfinite(c[k]):raise WorkbookInputError('Finite numeric input required: '+k)
 for k,lo,hi in [('block',1,24),('seed',0,2**32-1),('paths',2,10000),('base_life',1,100),('electric_life',1,100)]:
  if c[k]!=int(c[k]) or not lo<=c[k]<=hi:raise WorkbookInputError('Integer input range: '+k)
  c[k]=int(c[k])
 if c['block'] not in (1,6,12,24) or c['maintenance_scale'] not in (.01,1.):raise WorkbookInputError('Unsupported block or maintenance interpretation')
 if not .5<c['alpha']<1 or not 0<c['hours']<=8760:raise WorkbookInputError('Invalid alpha or hours')
 for k in ('recovery','annuity_rate','discount','beta','sale'):
  if not 0<=c[k]<=1:raise WorkbookInputError('Fraction range: '+k)
 for k in ('power','methane','naphtha'):
  if c[k]<0:raise WorkbookInputError('Nonnegative purchase price required: '+k)
 return c

def read_input(path):
 try:read_original(path) # Shared source packages and original model controls remain validated.
 except WorkbookInputError as exc:
  raise WorkbookInputError(str(exc).replace('This reference is not an active FIN specification.', 'The conditional cash mode requires a reviewed source package.')) from exc
 sheets=read_cells(path)
 if 'NCC cash' not in sheets:
  if {'NCC annual','NCC paths'} & set(sheets):raise WorkbookInputError('NCC cash input sheet missing')
  return DEFAULTS.copy()
 sh=sheets['NCC cash'];c={}
 for row,(key,label,_) in enumerate(FIELDS,12):
  if literal(sh,row,1,f'NCC cash!A{row}')!=label:raise WorkbookInputError('NCC input labels changed')
  c[key]=literal(sh,row,2,f'NCC cash!B{row}')
 return validate(c)

def evaluate(c):
 c=validate(c.copy());years=tuple(range(2027,2051));T=len(years);N=c['paths'];fx=1000.
 source=ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv'
 sm=json.loads((source.parent/'manifest.json').read_text())
 if hashlib.sha256(source.read_bytes()).hexdigest()!=sm['sha256'][str(source.relative_to(ROOT))]:raise WorkbookInputError('NCC source hash differs')
 obs=pd.read_csv(source).to_dict('records')
 values={(r['case'],r['item']):float(r['value']) for r in obs}
 capacity=np.where(np.array(years)>=2030,values['both','reference_capacity']*8760.,0.)
 required=np.where(np.array(years)>=2030,values['both','reference_capacity']*c['hours'],0.)
 references={}
 for case,life,psi in [('conventional',c['base_life'],.04),('electric',c['electric_life'],.02)]:
  cond=NCCConditions(c['recovery'],c['hours'],life,psi*c['maintenance_scale'],.04*c['maintenance_scale'],c['annuity_rate'],c['sale'],c['terminal'])
  references[case]=build_ncc_reference(obs,case,years,cond,numerical_KRW_per_EUR=fx)
 delivery=validate_ncc_delivery_pair(references,years=years,required_output_t=required,capacity_t=capacity,
  ethylene_yields={case:values[case,'ethylene_yield'] for case in references})
 delivery['implementation_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/cap/reference_delivery.py',ROOT/'src/cap/supply_network.py']}
 histfile=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
 if hashlib.sha256(histfile.read_bytes()).hexdigest()!=json.loads((ROOT/'data/research_v2/block_price_paths/manifest.json').read_text())['source_sha256']:raise WorkbookInputError('History hash differs')
 hist=pd.read_csv(histfile).set_index('period');curvefile=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
 curves=[ScenarioPriceCurve(**x) for x in json.loads(curvefile.read_text())]
 def ratio(commodity,region=None):
  curve=next(x for x in curves if x.scenario==c['scenario'] and x.commodity==commodity and (region is None or x.region==region))
  return np.array(interpolate_curve(curve,years,method='linear').values)/curve.values[0]
 gr=ratio('natural_gas','Japan');orr=ratio('crude_oil')
 monthly,_,_=block_paths(hist.to_numpy(),T*12,N,c['block'],c['seed'])
 annual=monthly.reshape(N,T,12,len(hist.columns)).mean(axis=2);del monthly
 gas=annual[:,:,hist.columns.get_loc('japan_lng')];oil=annual[:,:,hist.columns.get_loc('brent')]
 cp=c['power']*(1-c['beta']+c['beta']*gr);cg=c['methane']*gr;cn=c['naphtha']*orr
 power=c['power']*(1-c['beta']+c['beta']*gr*gas);methane=cg*gas;naphtha=cn*oil
 sh={k:np.ones((N,T)) for k in ('elec','h2','capex')}
 sh.update(elec=np.divide(power,cp,out=np.ones_like(power),where=cp!=0),methane=gas,naphtha=oil)
 px={k:np.zeros(T) for k in ('elec','re','h2','co2','coal','gas')};px.update(elec=cp*fx,methane=cg*fx,naphtha=cn*fx)
 cfg=C.load(discount_rate=c['discount'],carbon_accounting_mode='gross_obligation_proxy');cfg['years']={'start':2027,'end':2050}
 disc=(1.+c['discount'])**-np.arange(T);costs=[];rows=[];means=[];errors=[]
 for case in ('conventional','electric'):
  r=references[case];p=r['profile'];cap=r['capital']
  fixed=cap.net_cash_payments+r['maintenance_EUR'];feed=p.additional_commodity_flows[0].quantity
  buy=p.additional_commodity_flows[1].quantity;sell=p.additional_commodity_flows[2].quantity
  cost=simulate_cost(p,px,sh,{'subsidy':{}},cfg,freeze='capex')*1000/fx
  hand=((fixed+p.grid_mwh*power+feed*naphtha+(buy+sell)*methane)*disc).sum(axis=1)/1e6
  np.testing.assert_allclose(cost,hand,rtol=1e-12,atol=1e-7);costs.append(cost);errors.append(float(abs(cost-hand).max()))
  means.append(float(((fixed+p.grid_mwh*cp+feed*cn+(buy+sell)*cg)*disc).sum()/1e6))
  for i,y in enumerate(years):
   rows.append([case,y,float(r['output_t'][i]),float(cap.cash_payments[i]),float(cap.terminal_receipt.sum(axis=0)[i]),float(r['maintenance_EUR'][i]),float(p.grid_mwh[i]),float(feed[i]),float(buy[i]),float(sell[i]),float(cp[i]),float(cn[i]),float(cg[i]),float(disc[i])])
 delta=costs[1]-costs[0]
 return dict(controls=c,fields=FIELDS,metrics=loss_summary(delta,c['alpha']),analytic_mean=means[1]-means[0],
  max_FIN_error=max(errors),FIN_checks=2*N,annual=rows,delivery_contract=delivery,
  draws=[[i+1,float(b),float(e)] for i,(b,e) in enumerate(zip(*costs))],reference=reference_data(),scenarios=sources(),
  source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,histfile,curvefile,ROOT/'src/cap/reference_ncc.py',Path(__file__)]},
  corporate_full_cost=False,incumbent_retrofit=False,native_Excel_tested=False)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--scratch',type=Path,required=True);ap.add_argument('--no-preview',action='store_true');a=ap.parse_args()
 if a.input.resolve()==a.output.resolve():ap.error('Preserve the edited input; use a distinct output path')
 c=read_input(a.input);p=evaluate(c);a.scratch.mkdir(parents=True,exist_ok=True)
 p['input_workbook']=str(a.input.resolve());payload=a.scratch.resolve()/'payload.json';payload.write_text(json.dumps(p,ensure_ascii=False)+'\n')
 cmd=[str(NODE),str(ROOT/'scripts/build_ncc_cash_workbook.mjs'),str(payload),str(a.output.resolve())]
 if a.no_preview:cmd.append('--no-preview')
 subprocess.run(cmd,check=True,cwd=ROOT)

if __name__=='__main__':main()
