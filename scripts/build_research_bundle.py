"""Create a private local research bundle with an explicit allowlist and SHA256 inventory.

No uploads, git mutations, raw source PDFs, secrets, or bundled third-party runtimes.
"""
from pathlib import Path
import argparse,hashlib,json,zipfile
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'docs/research_cycles/2026-09-05'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workbook',type=Path,required=True);p.add_argument('--pdf',type=Path,required=True)
    p.add_argument('--replace',action='store_true');args=p.parse_args()
    if args.out.exists() and not args.replace:raise FileExistsError('Use a new bundle path or --replace')
    files={}
    def add(path,name=None):
        assert path.is_file() and not path.is_symlink(),path
        name=name or str(path.relative_to(ROOT))
        assert not name.startswith('/') and '..' not in Path(name).parts
        if name in files:raise ValueError(f'Duplicate archive entry: {name}')
        files[name]=path.read_bytes()
    for name in ['pyproject.toml','README.md','docs/RESEARCH_CONTROL.md','docs/parameter_inventory.csv',
                 'docs/TECHNICAL_GUIDE.md','docs/LEGACY_WORKFLOW.md','docs/figures/frontier_gap.svg']:
        add(ROOT/name)
    for directory,patterns in [(ROOT/'src/cap',['*.py']),(ROOT/'scripts',['*.py','*.mjs']),
                               (ROOT/'paper/methodology',['*.md']),(ROOT/'paper/methodology/figures',['*.png','*.pdf','*.svg','*.json'])]:
        for pattern in patterns:
            for path in sorted(directory.glob(pattern)):add(path)
    # Selected source observations and audits, not full publisher source documents.
    for path in sorted(AUDIT.rglob('*')):
        if path.is_file() and path.suffix.lower() in {'.csv','.json','.md','.log','.txt','.py'}:add(path)
    for path in sorted((ROOT/'tmp/research_case_expanded/run').rglob('*')):
        if path.is_file():add(path,'reference_run/'+str(path.relative_to(ROOT/'tmp/research_case_expanded/run')))
    for path in sorted((ROOT/'tmp/research_case_v3/data').glob('*.csv')):add(path,'reference_inputs/'+path.name)
    add(args.workbook,'TCaR_research_control.xlsx');add(args.pdf,'TCaR_methodology.pdf')
    # Embedded workbook exporter relocates data/out paths and creates a fresh provenance chain.
    files['START_HERE.md']='''# 비공개 TCaR 재현 묶음

시설별 추정 입력이 들어 있는 로컬 연구 묶음이다. 공개 저장소에 통째로 올리는 배포물이 아니다. 원문 선택 수치와 출처 링크는 포함하고 출판사 원문 PDF나 외부 런타임은 포함하지 않았다.

1. Python 3.11 이상에서 새 가상환경을 만들고 `pip install -e .`로 설치한다.
2. `python scripts/research_control.py doctor`로 패키지·CBC와 선택적 Excel 런타임을 확인한다.
3. `python scripts/research_control.py validate --workbook TCaR_research_control.xlsx`로 입력을 검사한다.
4. `python scripts/research_control.py run --workbook TCaR_research_control.xlsx --out-root runs/reproduction`으로 새 입력·설정·결과를 만든다.
5. `python scripts/verify_research_case.py --config runs/reproduction/expanded/config.yaml --out runs/reproduction/audit`로 본문과 같은 누적예산 사례를 검증한다.
6. Excel 재수입은 `python scripts/research_control.py refresh --run-root runs/reproduction --out TCaR_reproduced.xlsx`를 사용한다. Codex Node/Artifact Tool 런타임이 별도로 필요하다.

`reference_run/`은 기존 결과와 원래 실행 해시를 보존한 사본이다. 내부 절대 경로는 원래 감사 이력이며 현재 컴퓨터의 실행 경로가 아니다. 재실행에는 반드시 워크북을 내보내어 새 경로를 생성한다. `reference_inputs/`는 원문 관측과 가정을 구별한 입력 스냅샷이다.

모든 파일의 SHA256은 BUNDLE_MANIFEST.json에 있다. 환경 버전은 docs/research_cycles/2026-09-05/runtime_environment.json을 따른다. 다른 솔버 버전·제한시간·운영체제에서는 같은 일정 ID의 재현이 보장되지 않는다. 모형 결과와 실제 기업의 완전한 자산·에너지 수지 검증은 다르다.
'''.encode()
    report=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),classification='PRIVATE local research reproduction; facility inputs included; no upload performed',
                scope='Source code, manuscript, integrated workbook, selected evidence and fixed reference run; no raw publisher PDFs or runtimes',
                files={name:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for name,raw in sorted(files.items())})
    files['BUNDLE_MANIFEST.json']=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,raw in sorted(files.items()):z.writestr(name,raw)
    with zipfile.ZipFile(args.out) as z:
        assert z.testzip() is None
        for name,item in report['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==item['sha256']
    check=dict(bundle=str(args.out.resolve()),sha256=hashlib.sha256(args.out.read_bytes()).hexdigest(),file_count=len(files),bytes=args.out.stat().st_size,all_member_hashes_verified=True)
    args.out.with_suffix('.validation.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check,indent=2))

if __name__=='__main__':main()
