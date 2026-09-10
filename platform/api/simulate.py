"""Vercel and local HTTP adapter; all financial arithmetic uses the FIN originals."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import hashlib
import json
import logging
import sys
import threading
import time
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'
sys.path.insert(0,str(ENGINE/'scripts'))
sys.path.insert(0,str(ENGINE/'src'))
import ncc_joint_control as joint
import joint_workbook_control as joint_schema
import ncc_cash_workbook_control as cash
import timing_workbook_control as timing

MANIFEST=json.loads((ENGINE/'bundle-manifest.json').read_text())
for relative,expected in MANIFEST.items():
    if hashlib.sha256((ENGINE/relative).read_bytes()).hexdigest()!=expected:
        raise RuntimeError('Engine bundle differs from reviewed source: '+relative)
RELEASE=dict(engine=MANIFEST,adapter=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    requirements=hashlib.sha256((ROOT/'requirements.txt').read_bytes()).hexdigest())
VERSION=hashlib.sha256(json.dumps(RELEASE,sort_keys=True).encode()).hexdigest()
LOCK=threading.Lock()
DEFAULTS={'joint':joint.DEFAULTS,'cash':cash.DEFAULTS,'timing':timing.DEFAULTS}
FIELDS={'joint':joint_schema.FIELDS,'cash':cash.FIELDS,'timing':timing.FIELDS}
UNITS={'joint':'십억 KRW2024','cash':'백만 EUR2019 가정','timing':'백만 EUR2019 가정'}

def catalog():
    return dict(engine_version=VERSION,models={key:dict(defaults=value,fields=FIELDS[key],unit=UNITS[key]) for key,value in DEFAULTS.items()})

def validate_request(payload):
    if not isinstance(payload,dict) or set(payload)!={'model','controls'}:
        raise ValueError('model과 controls를 포함한 요청이 필요합니다.')
    model=payload['model']; controls=payload['controls']
    if not isinstance(model,str) or model not in DEFAULTS or not isinstance(controls,dict):
        raise ValueError('지원하지 않는 모형 또는 입력입니다.')
    if set(controls)!=set(DEFAULTS[model]):
        raise ValueError('입력 항목이 누락되었거나 알 수 없는 항목이 있습니다.')
    for key,value in controls.items():
        if isinstance(DEFAULTS[model][key],str):
            if not isinstance(value,str): raise ValueError('문자 선택값이 필요합니다: '+key)
        elif isinstance(value,bool) or not isinstance(value,(int,float)) or not np.isfinite(value):
            raise ValueError('빈칸 대신 유효한 숫자를 입력하세요: '+key)
        elif abs(value)>1e10:
            raise ValueError('지원 범위를 벗어난 숫자입니다: '+key)
    if not 2<=controls['paths']<=10000: raise ValueError('웹 계산은 2–10,000개 경로를 지원합니다.')
    if not 0<=controls['seed']<=2**32-1: raise ValueError('시드 범위는 0–4,294,967,295입니다.')
    if model=='joint':
        if not 0<=controls['discount_rate']<=1: raise ValueError('웹 할인율 범위는 0–1입니다.')
        joint.validate_controls(controls)
    elif model=='cash': cash.validate(controls)
    else: timing.validate(controls)
    return model,controls

def histogram(values):
    count,edges=np.histogram(np.asarray(values),bins=40)
    return [dict(cost=float((a+b)/2),lower=float(a),upper=float(b),count=int(n)) for a,b,n in zip(edges[:-1],edges[1:],count)]

def solve(payload):
    model,c=validate_request(payload)
    started=time.perf_counter()
    charts=[]; distributions={}; summaries=[]; qualification=[];audit={}
    if model=='joint':
        result,draws=joint.evaluate(c)
        summaries=[dict(id='electric',label='전기화 − 재래식 부분 운영비',eligible=True,frontier=False,analytic_mean=result['theoretical_mean_bnKRW2024'],**result['metrics'])]
        annual=result['annual']
        charts=[dict(year=r['year'],incremental=r['discounted_incremental_bnKRW2024']) for r in annual]
        distributions['electric']=histogram(draws['incremental'])
        audit=dict(checks=c['paths'],max_error=result['max_independent_formula_error_bnKRW2024'],sample_id=result['sample_id'])
        source_hashes=result['input_sha256']
        scope='전력·나프타·메탄 판매의 부분 운영비. CAPEX·탄소·기타 OPEX·제품 매출·환율 충격 제외. EUR2024 기준가격과 고정 환산율은 가정.'
    elif model=='cash':
        result=cash.evaluate(c)
        summaries=[dict(id='electric',label='전기식 신설 − 재래식 신설',eligible=True,frontier=False,analytic_mean=result['analytic_mean'],**result['metrics'])]
        cols=['공정','연도','에틸렌_t','자본지출_EUR','잔존수입_EUR','유지비_EUR','전력_MWh','나프타_t','구매메탄_MWh','판매메탄_MWh','전력_EUR_MWh','나프타_EUR_t','메탄_EUR_MWh','할인계수']
        annual=[dict(zip(cols,r)) for r in result['annual']]
        byyear={}
        for r in result['annual']:
            # Display the independently checked annual cash identity from the source adapter.
            value=(r[3]-r[4]+r[5]+r[6]*r[10]+r[7]*r[11]+(r[8]+r[9])*r[12])*r[13]/1e6
            byyear.setdefault(r[1],dict(year=r[1]))[r[0]]=value
        charts=[dict(**r,incremental=r['electric']-r['conventional']) for r in byyear.values()]
        distributions['electric']=histogram([e-b for _,b,e in result['draws']])
        audit=dict(checks=result['FIN_checks'],max_error=result['max_FIN_error'],delivery_checked=True)
        source_hashes=result['source_sha256']
        scope='두 신규 NCC 설비의 건설·갱신·유지비·전력·나프타·메탄 순비용 비교. 기존 기업 개조 견적 아님. 탄소·노무·세금·운전자본·금융비용·기타 공동제품 매출 제외.'
    else:
        result=timing.evaluate(c)
        qualification=result['qualification']
        for q in qualification:
            key=q['candidate']; m=result['metrics'].get(key)
            summaries.append(dict(id=key,label=f"{q['year']}년 전환",eligible=q['eligible'],**(m or {})))
        cols=['후보','연도','에틸렌_t','전력계수_tCO2_MWh','배출_tCO2','연간상한_tCO2','고정현금_EUR','전력_MWh','나프타_t','순메탄_MWh','전력_EUR_MWh','나프타_EUR_t','메탄_EUR_MWh','할인계수']
        annual=[dict(zip(cols,r)) for r in result['annual']]
        byyear={}
        for r in result['annual']:
            byyear.setdefault(r[1],dict(year=r[1],cap=r[5]))[r[0]]=r[4]
        charts=list(byyear.values())
        for i,q in enumerate(qualification):
            if q['eligible']: distributions[q['candidate']]=histogram([r[i+2] for r in result['draws']])
        audit=dict(checks=result['FIN_checks'],max_error=result['max_FIN_error'],mc_executed=result['MC_executed'],cumulative_budget=result['cumulative_budget'],terminal_budget=result['terminal_budget'])
        source_hashes=result['source_sha256']
        scope='既存 설비 유지 대비 2030·2035·2040·2045 전환 후보. 연간 에틸렌 92만 t·생산 차질 0·건설 3년·말기 잔존수입 0. Scope 1+구매전력 CO2 참조 경계, 기업 전체 또는 전과정 아님. 탄소지출 등 비모형 비용 제외.'.replace('既存','기존')
    request_id=hashlib.sha256((VERSION+json.dumps(payload,sort_keys=True)).encode()).hexdigest()
    return dict(model=model,controls=c,unit=UNITS[model],summaries=summaries,qualification=qualification,
       annual=annual,chart=charts,distributions=distributions,scope=scope,audit=audit,
       source_sha256=source_hashes,engine_version=VERSION,request_id=request_id,
       runtime=dict(python=sys.version.split()[0],numpy=np.__version__,pandas=pd.__version__,pyyaml=yaml.__version__),
       elapsed_seconds=round(time.perf_counter()-started,3))

class handler(BaseHTTPRequestHandler):
    def respond(self,status,value):
        body=json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers();self.wfile.write(body)
    def do_GET(self): self.respond(200,catalog())
    def do_POST(self):
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<=0 or length>16384: return self.respond(413,dict(error='입력 크기가 허용 범위를 벗어났습니다.'))
            if self.headers.get('Content-Type','').split(';')[0]!='application/json': return self.respond(415,dict(error='JSON 입력이 필요합니다.'))
            def invalid_constant(value): raise ValueError('유한한 숫자를 입력하세요.')
            payload=json.loads(self.rfile.read(length),parse_constant=invalid_constant)
            validate_request(payload)
            if not LOCK.acquire(blocking=False): return self.respond(429,dict(error='다른 계산이 진행 중입니다. 잠시 후 다시 실행하세요.'))
            try: result=solve(payload)
            finally: LOCK.release()
            self.respond(200,result)
        except (ValueError,TypeError,KeyError,OverflowError) as exc:
            self.respond(400,dict(error=str(exc)))
        except Exception:
            logging.exception('TCaR calculation failed')
            self.respond(500,dict(error='계산 또는 원문 검증을 완료하지 못했습니다. 입력을 확인하거나 잠시 후 다시 시도하세요. 이전 결과는 새 결과로 사용하지 않습니다.'))

if __name__=='__main__':
    print('TCaR API: http://127.0.0.1:8532/api/simulate',flush=True)
    HTTPServer(('127.0.0.1',8532),handler).serve_forever()
