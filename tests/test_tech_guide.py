"""The external technical guide must not carry stale numbers.

`docs/TECHNICAL_GUIDE.md` is the document that goes to people outside the project.
Its prose is hand-written, but its counts, coverage windows, evidence tiers,
configuration and headline results are generated from the live repository. A cycle
that changes the data and forgets the guide would ship last week's numbers to an
external reader with no visible sign that they are old — so staleness is a test
failure, not a housekeeping item.

Run: .venv/bin/pytest tests/test_tech_guide.py -q
"""

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "TECHNICAL_GUIDE.md"
BUILDER = ROOT / "scripts" / "build_tech_guide.py"


def test_generated_blocks_are_current():
    if not (ROOT / "out" / "e5" / "metrics_company.csv").exists():
        pytest.skip("파이프라인 미실행 — 헤드라인 블록을 생성할 수 없다")
    p = subprocess.run([sys.executable, str(BUILDER), "--check"],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, (
        f"{p.stdout.strip()}\n{p.stderr.strip()}\n"
        "→ .venv/bin/python scripts/build_tech_guide.py 를 돌려 갱신하고 같이 커밋하라")


def test_guide_makes_no_claim_it_cannot_source():
    """가장 흔한 사고: 원고에서 문장을 복사해 오면서 근거 파일 링크를 떼는 것.

    약한 근거 위의 수치를 외부 독자에게 줄 때 근거 위치가 같이 가야 한다. 아래 세 파일은
    이 문서가 '못 하는 말'을 적을 때 근거로 지목하는 곳이고, 링크가 끊기면 문서는
    검증 불가능한 주장 모음이 된다.
    """
    text = GUIDE.read_text(encoding="utf-8")
    for target in ("METHODOLOGY.md", "data_gap_registry.md", "mcp_server.md"):
        assert target in text, f"{target} 참조가 사라졌다"
        # 링크 대상이 실제로 존재하는가
        candidates = [ROOT / target, ROOT / "docs" / target]
        assert any(c.exists() for c in candidates), f"{target}를 링크하는데 파일이 없다"


def test_every_generated_marker_is_closed():
    text = GUIDE.read_text(encoding="utf-8")
    opens = text.count("<!-- GEN:")
    closes = text.count("<!-- /GEN:")
    assert opens == closes > 0, f"GEN 마커 짝이 맞지 않는다: {opens} open, {closes} close"


def test_html_render_loses_nothing():
    """웹 판이 md의 부분집합이 되면 안 된다.

    렌더러는 가이드가 실제로 쓰는 마크다운 부분집합만 안다. 원고에 새 구문이 들어오면
    HTML에서 조용히 사라지는 것이 기본 실패 모드이므로, 표 행·코드블록·제목이 전부
    페이지에 도달했는지를 렌더러가 스스로 세게 하고 그 판정을 테스트로 삼는다.
    """
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_guide_page.py"), "--check"],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, f"{p.stdout.strip()}\n{p.stderr.strip()}"


def test_data_dictionary_describes_what_ships():
    """사전은 실린 파일의 실린 열만, 그리고 전부 기술해야 한다.

    이전 사전은 `SCHEMAS`를 그대로 찍어서 패키지에 **없는** 두 파일(시설 단위 D1a·D1b)의
    85개 열을 기술하고, 정작 실린 134개 열 중 73개를 기술하지 않았다. 공개 경계상 나가지
    않는다고 선언한 시설 단위 필드명이 사전에는 실려 있었다는 뜻이기도 하다. 사전이
    가이드 §3에서 파생되는 지금은 정의 없는 열이 빌드를 죽이지만, 사전을 손으로 되돌리는
    사고를 막으려면 산출물 자체를 검사해야 한다.
    """
    import csv
    pkg = ROOT / "data" / "package"
    dic = pkg / "data_dictionary.csv"
    if not dic.exists():
        pytest.skip("패키지 미빌드 — scripts/build_data_package.py")
    rows = list(csv.DictReader(dic.open(encoding="utf-8")))
    described = {(r["file"], r["column"]) for r in rows}
    shipped = set()
    for f in sorted(pkg.glob("*.csv")):
        if f.name == dic.name:
            continue
        shipped |= {(f.stem, c) for c in next(csv.reader(f.open(encoding="utf-8-sig")))}
    assert not shipped - described, f"사전에 없는 실린 열: {sorted(shipped - described)}"
    assert not described - shipped, f"싣지 않는 것을 기술한 행: {sorted(described - shipped)}"
    blank = [(r["file"], r["column"]) for r in rows if not r["definition"].strip()]
    assert not blank, f"정의가 빈 행: {blank}"
