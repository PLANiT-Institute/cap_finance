"""Regenerate web examples using the exact bundled live API; never hardcode results."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'platform/api'))
from simulate import catalog,solve,DEFAULTS

def build():
    public=ROOT/'platform/public/data'
    (public/'catalog.json').write_text(json.dumps(catalog(),ensure_ascii=False,allow_nan=False)+'\n')
    for model,controls in DEFAULTS.items():
        result=solve(dict(model=model,controls=controls))
        (public/f'default-{model}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False)+'\n')
        print(f'{model}: {len(result["summaries"])} comparisons; {result["audit"]["checks"]} independent cash checks')

if __name__=='__main__':build()
