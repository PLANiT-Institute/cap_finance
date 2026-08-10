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


def test_section9_hand_written_counts_still_hold():
    """§9는 생성 블록 밖의 산문에 두 개의 수를 박아 두었다 — 그 둘이 이 절의 논지다.

    ① 공시 12행 중 **2행**만 강제 결정이 되고, 그래서 회사당 확약이 하나뿐이다(O3).
    ② `out/e5/gap.csv`의 8행은 support 축을 따라 복제된 **4개**의 서로 다른 gap이다(O7).

    둘 다 산문이라 생성기가 갱신하지 않는다. 파이프라인이 바뀌어 수가 달라지면 이 절은
    조용히 거짓이 되므로, 산출물에서 다시 세어 대조한다.
    """
    import csv

    text = GUIDE.read_text(encoding="utf-8")
    gap = ROOT / "out" / "e5" / "gap.csv"
    if not gap.exists():
        pytest.skip("no pipeline run in out/")
    rows = list(csv.DictReader(gap.open()))
    distinct = {(r["company_id"], r["scenario"]) for r in rows}
    assert len(rows) == 8 and len(distinct) == 4, (
        f"§9 O7이 '8행 = 4개 gap의 복제'라고 적었는데 지금은 {len(rows)}행 / {len(distinct)}개다")
    # 회사당 강제된 공시 확약이 하나뿐이라는 O3의 주장
    assert len({c for c, _ in distinct}) == 2, "§9 O3은 좌표를 가진 회사가 둘이라고 적었다"
    assert "**2 become a forced decision**" in text, "§9 O3의 강제 확약 수가 사라졌다"


def test_seed_sweep_staleness_is_described_as_it_is():
    """§6.1이 시드 표를 '한 번 낡았다'고 밝힌다 — 그 판정 자체가 낡을 수 있다.

    `docs/seed_stability.csv`의 정본 시드 행은 NSC에서만 `out/`과 어긋난다(그 회사의
    최소비용 계획이 스윕 이후 바뀌었다). 스윕을 다시 뜨면 어긋남이 사라지고 §6.1의
    단락은 거짓이 되며, 반대로 다른 회사까지 어긋나면 그 단락은 실제보다 약하게 적은
    것이 된다. 어느 쪽이든 산문을 고쳐야 하므로 여기서 잡는다.
    """
    import csv

    m = ROOT / "out" / "e5" / "metrics_company.csv"
    sweep = ROOT / "docs" / "seed_stability.csv"
    if not (m.exists() and sweep.exists()):
        pytest.skip("no pipeline run in out/ or no seed sweep")
    from cap import config as C  # noqa: E402  (src/ is on the path via conftest)
    pinned = str(C.load().seed)
    cur = {r["company_id"]: r for r in csv.DictReader(m.open())
           if r["scenario"] == "NZ15" and r["support"] == "none"}
    drift = set()
    for r in csv.DictReader(sweep.open()):
        if r["seed"] != pinned or r["company_id"] not in cur:
            continue
        if round(float(r["tcar_bnkrw"]), 3) != round(float(cur[r["company_id"]]["tcar_bnkrw"]), 3):
            drift.add(r["company_id"])
    assert drift == {"NSC"}, (
        f"§6.1은 시드 스윕이 NSC에서만 현재 실행과 어긋난다고 적었는데 지금 어긋나는 것은 {drift or '없다'}"
        " — 문단을 고치거나 지워라")


def test_gap_legs_are_clamped_as_the_figure_and_prose_say():
    """§2 그림·§9.1·O4는 "모든 비용 다리가 경계 끝점까지의 거리"라고 적는다.

    이것은 `_gap`의 클램프 분기가 실제로 타지는가에 달린 사실이고, 공시 좌표나 경계가
    움직이면 조용히 거짓이 된다(보간 분기로 넘어가면 gap은 더 이상 하한이 아니다).
    캡션의 수는 생성되지만 §9.1과 O4의 산문은 손으로 쓴 것이므로 여기서 다시 센다.
    """
    import csv

    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if not fp.exists():
        pytest.skip("no pipeline run in out/")
    rows = [r for r in csv.DictReader(fp.open()) if r["support"] == "none"]
    cost_clamped = risk_clamped = n = 0
    for co, sc in {(r["company_id"], r["scenario"]) for r in rows}:
        d = [r for r in rows if r["company_id"] == co and r["scenario"] == sc]
        disc = [r for r in d if r["is_disclosed"] == "True"]
        fr = [r for r in d if r["on_frontier"] == "True"]
        if not disc or not fr:
            continue
        n += 1
        p = disc[0]
        cost_clamped += float(p["tcar"]) > max(float(r["tcar"]) for r in fr)
        risk_clamped += float(p["p50"]) > max(float(r["p50"]) for r in fr)
    assert (n, cost_clamped, risk_clamped) == (4, 4, 3), (
        f"가이드는 gap 4개 중 비용 다리 4개·위험 다리 3개가 끝점 클램프라고 적었는데 "
        f"지금은 {n}개 중 {cost_clamped}·{risk_clamped}다 — §9.1과 O4의 산문을 고쳐라")
    text = GUIDE.read_text(encoding="utf-8")
    assert "It is not a nearest-point distance" in text, "§9.1의 정정 문장이 사라졌다"


def test_figure_is_built_and_referenced():
    fig = ROOT / "docs" / "figures" / "frontier_gap.svg"
    assert fig.exists(), "§2 그림 파일이 없다 — scripts/build_tech_guide.py 를 돌려라"
    assert "figures/frontier_gap.svg" in GUIDE.read_text(encoding="utf-8")
    assert fig.read_text(encoding="utf-8").startswith("<svg")


def test_no_facility_carries_a_measured_emission():
    """§8 주장 1은 "실측 시설 배출은 하나도 없다"고 단정한다 — 손으로 쓴 단정이다.

    F11 이전의 문장은 "일본은 이제 실측이다"였고 이것이 틀렸다. 사업소 실측(EEGS)은
    NSC의 배분 분포로만 들어가고 MCI 2기는 두 사업소 모두 실측 행이 있는데도
    상향식 추정이다. 실측 시설 배출이 D1b에 들어오면 이 테스트가 실패해야 하고,
    그때 §8 주장 1은 다시 써야 한다.
    """
    import csv

    prep = ROOT / "data" / "prepared"
    d1b = list(csv.DictReader((prep / "D1b_facility_panel.csv").open()))
    assert {r["source_id"] for r in d1b} <= {"PREP_ALLOC", "PREP_BOTTOMUP"}, (
        "D1b에 배분·상향식이 아닌 출처가 생겼다 — 실측이면 §8 주장 1을 다시 써라")
    keys = {r["site_key"] for r in csv.DictReader(
        (ROOT / "data" / "raw" / "jp_site_emissions.csv").open())}
    bottomup = {r["facility_id"] for r in d1b if r["source_id"] == "PREP_BOTTOMUP"}
    unused = {f for f in bottomup if f.split("_")[1] in keys}
    assert unused == {"MCI_ICH_CR", "MCI_OSK_CR"}, (
        f"사업소 실측이 있는데 상향식으로 남은 시설이 {sorted(unused)}로 바뀌었다 "
        "— §8 주장 1의 마지막 문장을 고쳐라")


def test_frontier_is_one_schedule_per_bundle():
    """O11·P1은 "8묶음 전부에서 경계 점들이 한 기술계획의 계약 변형"이라고 단정한다.

    F12가 찾은 사실이다. 경계에 두 번째 base_plan_id가 생기면 그 단정이 거짓이 되고,
    §9.1 생성문·O11·P1 상태칸을 다시 써야 한다. CCfD를 서명한 경계 점이 생겨도 같다.
    """
    import csv

    rows = [r for r in csv.DictReader((ROOT / "out" / "e5" / "frontier_points.csv").open())
            if r["support"] == "none" and r["on_frontier"] == "True"
            and r["is_disclosed"] != "True"]
    bundles = {(r["company_id"], r["scenario"]) for r in rows}
    for co, sc in bundles:
        base = {r["base_plan_id"] for r in rows
                if r["company_id"] == co and r["scenario"] == sc}
        assert len(base) == 1, (
            f"{co} {sc} 경계에 기술계획이 {len(base)}개다 — O11·P1의 '한 계획'이 거짓이다")
    assert len(bundles) == 8, f"묶음이 8개가 아니라 {len(bundles)}개다 — §9.1 표를 다시 읽어라"
    assert {r["ccfd"] for r in rows} == {"0"}, "경계 점이 CCfD를 서명했다 — O11 문장을 고쳐라"


def test_base_is_not_counted_as_an_assumption_bundle():
    """§4.3·§6·O8의 '열한 개'와 '열여섯 칸'은 base를 빼고 센 수다 (F12).

    F12 이전에는 생성기가 base를 포함해 12로 세었고, 그 12가 §4.3과 O8에 복사되어
    "twelve sensitivity axes"라는 틀린 문장이 되었다.
    """
    import csv

    rows = list(csv.DictReader((ROOT / "out" / "scenarios" / "summary.csv").open()))
    bundles = {r["bundle"] for r in rows} - {"base"}
    cells = sum(r["bundle"] == "base" for r in rows)
    assert (len(bundles), cells) == (11, 16), (
        f"가정 묶음 {len(bundles)}개 · 칸 {cells}개로 바뀌었다 — §4.3·O8의 손으로 쓴 수를 고쳐라")
    text = GUIDE.read_text(encoding="utf-8")
    assert "twelve sensitivity axes" not in text and "twelve firm × scenario" not in text


def test_ccfd_cannot_reach_the_frontier():
    """§1 P2·§9.1·O11은 "CCfD는 기각된 것이 아니라 시험된 적이 없다"고 단정한다 (F13).

    F13 이전에는 세 문서 모두 "현행 실행의 경계 점 중 CCfD를 서명한 것은 없다"고 적어
    관측처럼 읽혔다. 실제로는 두 겹의 구성이다 — E5의 계약 격자가 모든 비공시 후보에
    ccfd=0을 강제하고(e5_metrics.py:200), D5에 ccfd 행이 없어 행사가가 정의되지 않는다
    (plancost.py:258). 둘 중 하나라도 바뀌면 P2·O11·§9.1 생성문을 다시 써야 한다.
    """
    import csv
    import re

    src = (ROOT / "src" / "cap" / "e5_metrics.py").read_text(encoding="utf-8")
    assert re.search(r"replace\(prof0,\s*ppa=ppa_v,\s*epc=epc_v,\s*ccfd=0\)", src), (
        "E5의 계약 격자가 더 이상 ccfd=0을 강제하지 않는다 — P2·O11·§9.1을 다시 써라")
    grid = re.search(r"CONTRACT_GRID = \[\(ppa, epc\) for ppa in \(([^)]*)\) "
                     r"for epc in \(([^)]*)\)\]", src)
    assert grid and len(grid.group(1).split(",")) * len(grid.group(2).split(",")) == 10, (
        "계약 격자의 크기가 바뀌었다 — §10 용어집과 §6.3 생성문의 격자 서술을 고쳐라")

    d5 = list(csv.DictReader((ROOT / "data" / "prepared" / "D5_policy_support.csv").open()))
    assert not [r for r in d5 if r["instrument"] == "ccfd"], (
        "D5에 CCfD 행사가 행이 생겼다 — CCfD가 비활성이라는 §9.1 문장이 거짓이 된다")

    plans = list(csv.DictReader((ROOT / "out" / "e2" / "plan_index.csv").open()))
    assert any(r["ccfd"] == "1" for r in plans), (
        "E2가 더 이상 CCfD를 서명하지 않는다 — '대리만 서명한다'는 대비가 사라졌다")


def test_repo_front_door_reaches_the_guide_and_agrees_with_config():
    """README는 저장소의 첫 화면이고, F14까지 가이드로 가는 링크가 한 줄도 없었다.

    링크가 없으면 외부 독자는 우리가 가장 공들인 문서에 도달하지 못하고, 그 대신 README의
    요약을 읽는다 — 그래서 그 요약이 정본과 어긋나면 안 된다. README는 몬테카를로 표본 수를
    N=5,000으로 적고 있었는데 `config.yaml`은 10,000이다(수렴 검사 이탈로 상향한 값). 링크와
    표본 수 둘 다 조용히 낡을 수 있으므로 여기서 잡는다.
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/TECHNICAL_GUIDE.md" in readme, "README에서 기술 가이드로 가는 링크가 사라졌다"

    from cap import config as C  # noqa: E402  (src/ is on the path via conftest)
    n = int(C.load().simulation["n_sims"])
    assert f"N={n:,}" in readme, (
        f"README의 몬테카를로 표본 수가 config.yaml의 {n:,}과 다르다 — 방법 요약 2번을 고쳐라")


def test_landing_card_counts_are_counted_not_typed():
    """랜딩 카드의 두 수는 손으로 박혀 있었고 둘 다 틀렸다 (F14).

    가이드 장 수는 §10 용어집이 붙은 뒤에도 "8장"이었고, 시나리오 묶음 수는 `base`를 묶음으로
    세어 12종이었다 — F12가 가이드에서 고친 것과 같은 오류의 다섯 번째 사본이다. 지금은 둘 다
    세어서 쓰므로, 이 테스트는 누군가 다시 상수로 되돌리면 실패한다.
    """
    import csv
    import re

    idx = ROOT / "web" / "index.html"
    if not idx.exists():
        pytest.skip("사이트 미빌드 — scripts/build_site.py")
    html = idx.read_text(encoding="utf-8")
    n_ch = sum(1 for ln in GUIDE.read_text(encoding="utf-8").splitlines() if ln.startswith("## "))
    assert re.search(rf"· {n_ch}장", html), f"가이드 카드의 장 수가 실제 {n_ch}장과 다르다"

    summary = ROOT / "out" / "scenarios" / "summary.csv"
    if not summary.exists():
        return
    bundles = {r["bundle"] for r in csv.DictReader(summary.open(encoding="utf-8"))} - {"base"}
    assert f"묶음 {len(bundles)}종" in html, (
        f"시나리오 카드가 가정 묶음을 {len(bundles)}종으로 세지 않는다 — base를 세고 있지 않은가")
