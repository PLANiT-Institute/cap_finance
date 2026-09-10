"""Validate research Excel inputs, export isolated cases, run, and prepare refreshed results."""
from pathlib import Path
import argparse
from collections import Counter
import copy
import csv
from datetime import datetime, timezone
import hashlib
import io
from importlib import metadata
import json
import os
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from research_control_contract import (CONTROLS, decode_contract, get_nested,
                                      numeric, set_nested, validate_control)
from xlsx_table_reader import WorkbookInputError, literal, read_cells


def key_of(row, columns, keys):
    return tuple(row[columns.index(k)] for k in keys)


def validate_input_values(name, columns, rows, baseline_rows=None):
    """Check model domains in addition to literal numeric types and locked references."""
    for i, values in enumerate(rows):
        row = dict(zip(columns, values))
        def check(field, lower=None, upper=None, integer=False, positive=False):
            if field not in row:
                return
            originally_missing = baseline_rows is not None and baseline_rows[i][columns.index(field)] is None
            value = numeric(row[field], f'{name} row {i+6}, {field}', blank=originally_missing)
            if value is None:
                return
            if ((lower is not None and value<lower) or (upper is not None and value>upper)
                    or (positive and value<=0) or (integer and value!=int(value))):
                raise WorkbookInputError(f'{name} row {i+6}, {field}: invalid domain value {value}')
        if name=='D1a':
            for f in ['capacity','reinvest_cycle_yr']:check(f,positive=True)
            for f in ['incumbent_capex_unit']:check(f,lower=0)
            for f in ['commissioning_year','last_reline_year','reinvest_cycle_yr','next_reinvest_year']:check(f,integer=True)
            if row['commissioning_year'] is not None and row['last_reline_year']<row['commissioning_year']:
                raise WorkbookInputError(f'{name} row {i+6}: campaign precedes commissioning')
        elif name=='D1b':
            for f in ['production','emissions_s1','emissions_s2','energy_coal','energy_gas','energy_elec','energy_naphtha']:check(f,lower=0)
        elif name=='D2a':check('carbon_budget',lower=0)
        elif name in {'D2b','D4'}:check('value',positive=True)
        elif name=='D3':
            for f in ['capex_unit','opex_fixed','opex_var','elec_intensity','h2_intensity','emission_factor','capex_uncertainty']:check(f,lower=0)
            for f in ['retained_coal_fraction','retained_gas_fraction','retained_grid_fraction','retrofit']:check(f,lower=0,upper=1)
            check('retrofit',integer=True);check('avail_year',integer=True)
            check('build_years',lower=0,integer=True);check('lifetime',positive=True,integer=True)
        elif name=='D3b':
            check('value_low',lower=0);check('value_high',lower=0)
            if row['value_low']>row['value_high']:
                raise WorkbookInputError(f'{name} row {i+6}: lower bound exceeds upper bound')
        elif name=='D5':
            check('value',lower=0)
            if row['unit']=='%':check('value',upper=100)
            if row['unit'] in {'share','fraction'}:check('value',upper=1)
        elif name=='D6':
            for f in ['revenue','capex_total','total_debt','interest_expense','cash']:check(f,lower=0)


def validate(workbook):
    sheets=read_cells(workbook);contract=decode_contract(sheets)
    config=copy.deepcopy(contract['config']);changes=[];inputs={}
    for name, definition in contract.get('reference_tables',{}).items():
        if name not in sheets:raise WorkbookInputError(f'Missing reference sheet: {name}')
        cells=sheets[name];columns=definition['columns']
        if [literal(cells,5,c+1,name) for c in range(len(columns))]!=columns:
            raise WorkbookInputError(f'{name}: reference header changed')
        rows=[]
        for r in range(6,max(row for row,col in cells)+1):
            values=tuple(literal(cells,r,c+1,f'{name} reference') for c in range(len(columns)))
            if any(v is not None for v in values):rows.append(values)
        if Counter(rows)!=Counter(tuple(row) for row in definition['rows']):
            raise WorkbookInputError(f'{name}: reference or result values changed; update through a verified source/run refresh')
    for name, definition in contract['sheets'].items():
        if name not in sheets:
            raise WorkbookInputError(f'Missing required input sheet: {name}')
        cells=sheets[name];columns=definition['columns'];width=len(columns)
        header=[literal(cells,5,c+1,f'{name} header') for c in range(width)]
        if header!=columns:
            raise WorkbookInputError(f'{name}: header names or order differ from the control template')
        for (r,c), cell in cells.items():
            if r>=5 and c>width and cell['value'] is not None:
                raise WorkbookInputError(f'{name}: unexpected data column {c}; use the fixed input schema')
        rows=[]
        for r in range(6,max(row for row,col in cells)+1):
            values=[literal(cells,r,c+1,f'{name} row {r}, {field}') for c,field in enumerate(columns)]
            if any(v is not None for v in values):rows.append(values)
        expected=definition['rows']
        if len(rows)!=len(expected):
            raise WorkbookInputError(f'{name}: expected {len(expected)} input records, found {len(rows)}')
        baseline={key_of(r,columns,definition['keys']):r for r in expected}
        actual={key_of(r,columns,definition['keys']):r for r in rows}
        if len(actual)!=len(rows) or set(actual)!=set(baseline):
            raise WorkbookInputError(f'{name}: missing, duplicated or altered record ID; only value fields are editable')
        # Restore canonical ordering so Excel sorting cannot perturb a run.
        ordered=[]
        for key, old in baseline.items():
            new=actual[key];ordered.append(new)
            for j,field in enumerate(columns):
                if field in definition['editable_columns']:
                    numeric(new[j],f'{name} {key}, {field}',blank=old[j] is None)
                if new[j]!=old[j]:
                    if field not in definition['editable_columns']:
                        raise WorkbookInputError(f'{name} {key}: {field} is a reference field; revise its evidence outside this fixed template')
                    changes.append(dict(sheet=name,record=list(key),field=field,old=old[j],new=new[j],status='user_assumption_override'))
        validate_input_values(name,columns,ordered,expected)
        inputs[name]=dict(definition,rows=ordered)
    if 'Settings' not in sheets:
        raise WorkbookInputError('Missing Settings sheet')
    cells=sheets['Settings'];found=set()
    for row in range(6,max(r for r,c in cells)+1):
        key=literal(cells,row,1,'Settings')
        if key is None:continue
        if key not in CONTROLS or key in found:
            raise WorkbookInputError(f'Settings: unexpected or duplicate parameter {key}')
        found.add(key);value=validate_control(key,literal(cells,row,2,f'Settings {key}'))
        old=get_nested(config,key)
        if value!=old:
            changes.append(dict(sheet='Settings',record=[key],field='value',old=old,new=value,status='user_assumption_override'))
        set_nested(config,key,value)
    if found!=set(CONTROLS):raise WorkbookInputError('Settings: required parameter is missing')
    if config['simulation']['n_sims_flex']>config['simulation']['n_sims']:
        raise WorkbookInputError('Settings: n_sims_flex cannot exceed n_sims')
    # Preserve the declared information boundary, even after changing campaign years.
    start=config['years']['start']
    for row in inputs['D1a']['rows']:
        d=dict(zip(inputs['D1a']['columns'],row))
        if d['last_reline_year']>start:
            raise WorkbookInputError(f'D1a {d["facility_id"]}: future campaign is not an observed starting state')
    return dict(contract=contract,config=config,inputs=inputs,changes=changes,
                workbook_sha256=hashlib.sha256(workbook.read_bytes()).hexdigest())


def save_json(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2)+'\n')


def export(workbook, output):
    checked=validate(workbook)
    output=output.resolve()
    if output.exists():raise WorkbookInputError(f'Output already exists: {output}; choose a new run folder')
    output.mkdir(parents=True);data=output/'data';data.mkdir()
    for filename,entry in checked['contract']['input_files'].items():
        if Path(filename).name!=filename or not filename.endswith('.csv'):
            raise WorkbookInputError('Invalid embedded input filename')
        (data/filename).write_bytes(entry['csv'].encode())
    changed_sheets={r['sheet'] for r in checked['changes'] if r['sheet']!='Settings'}
    for name in changed_sheets:
        definition=checked['inputs'][name]
        columns=list(definition['columns']);rows=copy.deepcopy(definition['rows'])
        changed_keys={tuple(r['record']) for r in checked['changes'] if r['sheet']==name}
        # Keep the original source reference, but explicitly invalidate its value verification.
        if 'input_edit_status' not in columns:columns.append('input_edit_status')
        for row in rows:
            is_changed=key_of(row,definition['columns'],definition['keys']) in changed_keys
            if len(row)<len(columns):row.append('unchanged_baseline')
            if is_changed:
                row[columns.index('input_edit_status')]='user_assumption_override'
                if 'verification_status' in columns:row[columns.index('verification_status')]='user_assumption_override'
        with (data/definition['filename']).open('w',newline='') as f:
            writer=csv.writer(f);writer.writerow(columns);writer.writerows(rows)
    retention_changes=[r for r in checked['changes'] if r['sheet']=='D3' and r['field'].startswith('retained_')]
    if retention_changes:
        path=data/'energy_retention_assumptions.csv'
        with path.open() as f:
            reader=csv.DictReader(f);fields=reader.fieldnames;records=list(reader)
        for item in records:
            for change in retention_changes:
                if item['tech_id']==change['record'][0] and item['field']==change['field']:
                    item['value']=change['new'];item['evidence_status']='user_assumption_override'
                    item['limit']+='; value edited in control workbook; not verified by original source context'
        with path.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(records)
    config=checked['config'];config['data_dir']=str(data);config['out_dir']=str(output/'run')
    config.pop('root',None)
    (output/'config.yaml').write_text(yaml.safe_dump(config,allow_unicode=True,sort_keys=False))
    record=dict(status='exported',created_at_utc=datetime.now(timezone.utc).isoformat(),
                workbook_sha256=checked['workbook_sha256'],source_run_manifest_sha256=checked['contract']['run_manifest_sha256'],
                changes=checked['changes'],input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(data.glob('*.csv'))},
                config_sha256=hashlib.sha256((output/'config.yaml').read_bytes()).hexdigest(),
                interpretation='Changed cells are user assumptions; original source observations remain unchanged.')
    save_json(output/'control_manifest.json',record)
    return record


def run_case(workbook, output):
    record=export(workbook,output);output=output.resolve();record['status']='running'
    save_json(output/'control_manifest.json',record)
    def command(arguments, logfile):
        with (output/logfile).open('w') as f:
            subprocess.run([sys.executable,*arguments],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    try:
        command(['scripts/run_research_case.py','--config',str(output/'config.yaml')],'pipeline.log')
        config=yaml.safe_load((output/'config.yaml').read_text())
        points=config.get('candidate_expansion_emissions_points',0)
        result_config=output/'config.yaml'
        if points:
            command(['scripts/expand_research_candidates.py','--base-config',str(result_config),
                     '--out-root',str(output/'expanded'),'--emissions-points',str(points)],'expansion.log')
            result_config=output/'expanded/config.yaml'
        record.update(status='completed',result_config=str(result_config),finished_at_utc=datetime.now(timezone.utc).isoformat())
    except Exception as error:
        record.update(status='failed',error=str(error),finished_at_utc=datetime.now(timezone.utc).isoformat())
        save_json(output/'control_manifest.json',record)
        raise
    save_json(output/'control_manifest.json',record)
    return record


def refresh(run_root, workbook_output, node=None, replace=False):
    """Rebuild the integrated workbook from a completed run using Artifact Tool."""
    if workbook_output.exists() and not replace:
        raise WorkbookInputError('Workbook output exists; choose a new path or pass --replace')
    manifest=json.loads((run_root/'control_manifest.json').read_text())
    if manifest['status']!='completed':raise WorkbookInputError('Cannot refresh from a failed or unfinished run')
    from research_workbook_payload import build
    payload=run_root/'workbook_payload.json';build(Path(manifest['result_config']),payload)
    runtime=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
    executable=Path(node or os.environ.get('TCAR_NODE',str(runtime/'bin/node')))
    modules=Path(os.environ.get('TCAR_NODE_MODULES',str(runtime/'node_modules')))
    if not executable.exists() or not (modules/'@oai/artifact-tool').exists():
        raise WorkbookInputError('Excel refresh requires the bundled Node/Artifact Tool runtime. Set TCAR_NODE and TCAR_NODE_MODULES; CSV results remain available.')
    local=ROOT/'tmp/tcar_workbook';local.mkdir(parents=True,exist_ok=True)
    link=local/'node_modules'
    if not link.exists():link.symlink_to(modules,target_is_directory=True)
    with (run_root/'workbook_refresh.log').open('w') as log:
        subprocess.run([str(executable),str(ROOT/'scripts/build_research_workbook.mjs'),
                        '--payload',str(payload.resolve()),'--out',str(workbook_output.resolve()),
                        '--preview-dir',str((run_root/'workbook_previews').resolve())],
                       cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/verify_research_workbook.py'),
                    '--workbook',str(workbook_output.resolve()),'--payload',str(payload.resolve()),
                    '--out',str((run_root/'workbook_validation.json').resolve())],cwd=ROOT,check=True)
    return dict(workbook=str(workbook_output.resolve()),validation=str((run_root/'workbook_validation.json').resolve()))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    commands=ap.add_subparsers(dest='command',required=True)
    commands.add_parser('doctor',help='Report Python, solver and optional Excel runtime availability')
    for name in ['validate','export','run']:
        parser=commands.add_parser(name);parser.add_argument('--workbook',type=Path,required=True)
        if name!='validate':parser.add_argument('--out-root',type=Path,required=True)
    parser=commands.add_parser('refresh-payload');parser.add_argument('--run-root',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser=commands.add_parser('refresh');parser.add_argument('--run-root',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--node',type=Path);parser.add_argument('--replace',action='store_true')
    args=ap.parse_args()
    if args.command=='doctor':
        required=['numpy','pandas','pulp','pyyaml','pyarrow','matplotlib']
        versions={}
        for name in required:
            try:versions[name]=metadata.version(name)
            except metadata.PackageNotFoundError:versions[name]=None
        try:
            import pulp
            solver=pulp.PULP_CBC_CMD(msg=False).available()
        except ImportError:solver=False
        runtime=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
        node=Path(os.environ.get('TCAR_NODE',str(runtime/'bin/node')))
        modules=Path(os.environ.get('TCAR_NODE_MODULES',str(runtime/'node_modules')))
        report=dict(python=sys.version,packages=versions,cbc_available=bool(solver),
                    cbc_path=str(solver) if solver else None,
                    optional_excel_runtime_available=node.exists() and (modules/'@oai/artifact-tool').exists(),
                    explanation='CSV calculation needs Python packages and CBC; Excel refresh additionally requires Node/Artifact Tool')
        print(json.dumps(report,indent=2))
        if not all(versions.values()) or not solver:raise SystemExit(1)
    elif args.command=='validate':
        r=validate(args.workbook);print(json.dumps(dict(valid=True,changed_cells=len(r['changes']),changes=r['changes'],workbook_sha256=r['workbook_sha256']),ensure_ascii=False,indent=2))
    elif args.command in {'export','run'}:
        r=(export if args.command=='export' else run_case)(args.workbook,args.out_root);print(json.dumps(r,ensure_ascii=False,indent=2))
    elif args.command=='refresh':
        print(json.dumps(refresh(args.run_root,args.out,args.node,args.replace),ensure_ascii=False,indent=2))
    else:
        manifest=json.loads((args.run_root/'control_manifest.json').read_text())
        if manifest['status']!='completed':raise WorkbookInputError('Cannot refresh from a failed or unfinished run')
        from research_workbook_payload import build
        build(Path(manifest['result_config']),args.out)


if __name__=='__main__':main()
