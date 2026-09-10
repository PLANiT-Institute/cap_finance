"""Run an isolated research configuration with input/code/output provenance."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def digest(paths):
    return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):
            hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    args=parser.parse_args()
    from cap import config as C,e1_constraints,e2_milp,e3_prices,e4_revalue,e5_metrics
    cfg=C.load(args.config)
    output=Path(cfg.out_dir);output.mkdir(parents=True,exist_ok=True)
    files=list(C.data_dir(cfg).glob('*.csv'))+list((ROOT/'src/cap').glob('*.py'))+[args.config.resolve(),Path(__file__).resolve()]
    before=digest(files)
    record=dict(started_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                config_path=str(args.config.resolve()),status='running',stages=[],source_sha256=before)
    path=output/'run_manifest.json'
    def save():path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    save()
    try:
        for name,module in [('E1',e1_constraints),('E2',e2_milp),('E3',e3_prices),('E4',e4_revalue),('E5',e5_metrics)]:
            started=time.monotonic();print('START',name,flush=True)
            module.run(cfg)
            record['stages'].append(dict(stage=name,status='completed',elapsed_seconds=time.monotonic()-started))
            save();print('DONE',name,flush=True)
        after=digest(files)
        if after!=before:
            raise RuntimeError('Source or input changed during run; isolate or rerun before publishing this result')
        record.update(status='completed',finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      output_sha256=digest([p for p in output.rglob('*') if p.is_file() and p!=path]))
    except Exception:
        record.update(status='failed',finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      error=traceback.format_exc())
        save();raise
    save()


if __name__=='__main__':main()
