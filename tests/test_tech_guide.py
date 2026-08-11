"""The external technical guide must not carry stale numbers.

`docs/TECHNICAL_GUIDE.md` is the document that goes to people outside the project.
Its prose is hand-written, but its counts, coverage windows, evidence tiers,
configuration and headline results are generated from the live repository. A cycle
that changes the data and forgets the guide would ship last week's numbers to an
external reader with no visible sign that they are old — so staleness is a test
failure, not a housekeeping item.

Run: .venv/bin/pytest tests/test_tech_guide.py -q
"""

import datetime as _dt
import os
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


def test_stamp_is_a_content_digest_not_a_commit_sha():
    """스탬프가 커밋 SHA면 그 스탬프를 쓴 커밋이 만들어지는 순간 반드시 낡는다.

    F16이 `data/` 아래 파일 하나를 지웠고, F17 시작 시 게이트가 이 이유로 빨갰다.
    SHA를 상태 경로로 좁히는 것으로는 못 막는다 — 상태를 건드리는 커밋마다 재발한다.
    내용 다이제스트는 커밋 전에 알 수 있으므로 자기 자신을 낡게 만들지 않는다.
    """
    import re
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_tech_guide as btg

    m = re.search(r"hash to `([0-9a-f]{12})`", GUIDE.read_text(encoding="utf-8"))
    assert m, "상태 스탬프가 사라졌거나 다이제스트 형식이 아니다"
    assert m.group(1) == btg.state_digest(), "스탬프가 현재 상태와 다르다 — 빌더를 다시 돌려라"
    resolved = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{m.group(1)}^{{commit}}"],
                              cwd=ROOT, capture_output=True, text=True)
    assert resolved.returncode != 0, "스탬프가 커밋으로 해석된다 — SHA 스탬프로 되돌아갔다"


def test_stamp_covers_the_results_it_claims_to_cover():
    """스탬프가 `out`을 이름으로 대면서 `out`을 세지 않으면 그것은 거짓 그린이다.

    F28까지 `state_digest`는 `git ls-files`만 읽었고 `.gitignore`가 `out/**`를 지운다.
    847개 결과 파일 중 2개(우연히 추적되던 `out/sensitivity/*.csv`)만 세고 있었으므로,
    파이프라인을 다시 돌려 가이드의 모든 수치가 움직여도 스탬프는 그대로였다.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_tech_guide as btg

    counted = set(btg._state_files())
    results = {str(p.relative_to(ROOT)) for p in (ROOT / "out").rglob("*")
               if p.is_file() and not any(s.startswith(".") for s in p.parts)}
    missed = results - counted
    assert not missed, f"결과 {len(missed)}개가 상태 스탬프 밖에 있다, 예: {sorted(missed)[:3]}"

    # 실제로 내용에 반응하는가 — 목록에 있으나 읽지 않는 구현이면 여기서 잡힌다
    victim = ROOT / "out" / "e5" / "gap.csv"
    before, keep, st = btg.state_digest(), victim.read_bytes(), victim.stat()
    try:
        victim.write_bytes(keep + "\n# 스탬프 반응 확인\n".encode())
        assert btg.state_digest() != before, "결과 파일 내용이 바뀌었는데 스탬프가 그대로다"
    finally:
        victim.write_bytes(keep)
        # mtime까지 되돌린다 — 안 되돌리면 이 파일이 out/e5의 최신이 되고
        # 게이트의 곁가지 검사가 아홉 디렉터리를 전부 STALE로 부른다(검사가 base를
        # `_newest("out/e5/*.csv")`로 잡는다). 테스트가 게이트를 붉히면 안 된다.
        os.utime(victim, (st.st_atime, st.st_mtime))
    assert btg.state_digest() == before, "복원 뒤에도 스탬프가 다르다 — 다이제스트가 결정적이지 않다"


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

    `docs/seed_stability.csv`의 정본 시드 행이 `out/`과 어긋나면 §6.1의 변동계수는 지금
    돌아가는 계획 메뉴의 오차범위가 아니다. 스윕을 다시 뜨면 어긋남이 사라지고, 반대로
    파이프라인만 다시 돌면 어긋남이 생긴다 — 어느 쪽이든 산문이 뒤집힌다.

    **F26까지 이 테스트는 어긋나는 회사가 정확히 {NSC}라고 못박고 있었다.** 스윕을
    17초에 다시 돌리자 어긋남이 사라졌고 테스트가 붉어졌다 — 실패가 아니라 사실이
    바뀐 것이었다. 이제는 방향을 못박지 않고, 가이드의 주장과 실제 어긋남이 **같은
    방향인가**만 본다.
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
    text = GUIDE.read_text(encoding="utf-8")
    fresh = "The sweep is **taken on the plan menu now in `out/`**" in text
    assert fresh == (not drift), (
        f"§6.1은 시드 스윕을 {'현행' if fresh else '낡음'}으로 적는데 고정 시드 행이 "
        f"실제로 어긋나는 회사는 {sorted(drift) or '없다'} — 문단을 고치거나 스윕을 다시 떠라")
    if drift:
        assert "**The sweep is older than the current run.**" in text, (
            "고정 시드 행이 어긋나는데 §6.1이 그 사실을 밝히지 않는다")


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


def test_epsilon_diagnostic_counts_are_the_ones_in_6_3():
    """§6.3의 32 / 4 / 25는 파이프라인이 아니라 별도 진단 실행에서 나온다 (F15).

    F15까지 §6.3은 이 세 수를 출처 없이 적고 있었다 — 가이드 머리말이 "모든 정량 주장은
    생성되었거나 그것을 만드는 파일을 가리킨다"고 약속한 바로 그 규칙을 §6.3이 어기고 있었고,
    수를 만드는 `out/m8/summary.csv`는 가이드 어디에도 이름이 없었다. 게다가 비지배 4개가
    **한 묶음에 몰려 있다**는 사실(나머지 일곱에서는 0개)이 §1 P1과 §6.3 어디에도 없었다.
    진단을 다시 돌리면 이 테스트가 세 수와 묶음 분포를 다시 대조한다.
    """
    import csv

    s = ROOT / "out" / "m8" / "summary.csv"
    if not s.exists():
        pytest.skip("M8 진단 미실행 — scripts/frontier_tech_epsilon.py")
    rows = list(csv.DictReader(s.open(encoding="utf-8")))
    caps = sum(int(r["caps_tried"]) for r in rows)
    head = [int(r["nondominated_headline"]) for r in rows]
    l2 = [int(r["nondominated_l2"]) for r in rows]
    text = " ".join(GUIDE.read_text(encoding="utf-8").split())   # 줄바꿈에 걸리지 않게

    assert f"all {caps} caps are feasible" in text, f"§6.3의 강제 상한 수가 {caps}와 다르다"
    assert f"{sum(l2)} of the same {caps}" in text, f"§6.3의 L2 비지배 수가 {sum(l2)}와 다르다"
    assert f"technology axis returns in {sum(v > 0 for v in l2)} of {len(rows)}" in text
    assert f"the other **{sum(v == 0 for v in head)} of {len(rows)}** bundles" in text, (
        "§6.3이 '나머지 묶음에서는 0개'를 더 이상 정확히 세지 않는다")
    assert sum(head) == 4 and sum(v > 0 for v in head) == 1, (
        f"헤드라인 비지배가 {sum(head)}개·{sum(v > 0 for v in head)}묶음으로 바뀌었다 "
        "— §1 P1과 §6.3의 '4개가 전부 한 묶음'을 다시 써라")
    assert "out/m8/summary.csv" in text, "§6.3이 수를 만드는 파일을 더 이상 가리키지 않는다"


def test_hydrogen_share_in_the_ledger_is_reproducible():
    """A-05의 임팩트 값은 METHODOLOGY(정본)와 가이드 §4.1이 공유하는데 재현되지 않았다 (F15).

    양쪽이 "TCaR 30~42%"라고 적고 있었다. 현행 `out/e5/variance_decomp.csv` 어느 절단으로도
    그 구간이 나오지 않고, 애초에 TCaR은 분위수 차이라 요인별로 가법 분해되지 않는다
    (`docs/uncertainty_propagation.md` §1이 같은 이유로 상호작용 잔차를 남긴다). 지금은 양쪽이
    NZ15 비용최소 계획의 분산 몫을 적는다 — 그 계획이 바뀌면 이 테스트가 먼저 실패한다.
    """
    import csv

    vd = ROOT / "out" / "e5" / "variance_decomp.csv"
    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if not (vd.exists() and fp.exists()):
        pytest.skip("파이프라인 미실행")

    elig = [r for r in csv.DictReader(fp.open(encoding="utf-8"))
            if r["scenario"] == "NZ15" and r["support"] == "none"
            and r["is_disclosed"] in ("False", "0") and r["budget_ok"] in ("True", "1")]
    cheapest = {}
    for r in elig:
        c = r["company_id"]
        if c not in cheapest or float(r["p50"]) < float(cheapest[c]["p50"]):
            cheapest[c] = r
    want = {(c, r["plan_id"]) for c, r in cheapest.items()}
    share = [float(v["variance_share"]) for v in csv.DictReader(vd.open(encoding="utf-8"))
             if v["factor"] == "h2" and v["scenario"] == "NZ15" and v["support"] == "none"
             and (v["company_id"], v["plan_id"]) in want]
    assert len(share) == len(want) == 4, "비용최소 계획을 기업마다 하나씩 찾지 못했다"

    lo, hi = f"{min(share):.0%}", f"{max(share):.0%}"
    for path in (GUIDE, ROOT / "METHODOLOGY.md"):
        text = " ".join(path.read_text(encoding="utf-8").split())
        assert "30–42% of TCaR" not in text and "TCaR 30~42%" not in text, (
            f"{path.name}에 재현되지 않는 A-05 임팩트가 되살아났다")
        anchor = next(a for a in ("Hydrogen is procured externally", "수소 = 외부 조달")
                      if a in text)
        row = text[text.index(anchor):][:900]          # A-05 행 하나만 본다
        assert lo in row and hi in row, (
            f"{path.name}의 A-05 수소 분산 몫이 실제 {lo}–{hi}와 다르다")


def test_section_7_backtest_matches_the_backtest_record():
    """§7이 하지 않은 검증을 했다고 적고 있었다 (F16).

    두 가지였다. (1) "reproduction error on actual emissions **and energy cost**" —
    `docs/validation_backtest.md` §3이 에너지 원단위도 비용도 재현하지 못했다고 명시한다.
    (2) 후향 검증의 판정 자체가 없었다 — NSC가 ±10% 기준을 초과하고 석화 2사는 생산량
    미공시로 대조가 성립하지 않는데, §7은 "오차를 보고한다"까지만 적었다.
    이 테스트는 §7이 실제 판정과 어긋나면 실패한다.
    """
    import csv

    bt = ROOT / "docs" / "validation_backtest.csv"
    if not bt.exists():
        pytest.skip("후향 검증 미실행 — scripts/validate_backtest.py")
    err = {}
    for r in csv.DictReader(bt.open(encoding="utf-8")):
        if r["err_pct"]:
            err.setdefault(r["company_id"], []).append(float(r["err_pct"]))
    assert set(err) == {"POSCO", "NSC"}, f"대조 가능한 기업이 {sorted(err)}로 바뀌었다"

    text = " ".join(GUIDE.read_text(encoding="utf-8").split())
    for firm, sign in (("POSCO", "+"), ("NSC", "+")):
        v = err[firm]
        mean, worst = sum(v) / len(v), max(abs(x) for x in v)
        assert f"mean {sign}{mean:.1f}%" in text, (
            f"§7의 {firm} 평균 오차가 실제 {mean:+.1f}%와 다르다")
        assert f"{worst:.1f}%" in text, f"§7의 {firm} 최대 오차가 실제 {worst:.1f}%와 다르다"

    assert "and energy cost reported" not in text, (
        "§7이 다시 에너지 비용을 후향 검증했다고 주장한다 — validation_backtest.md §3은 "
        "비용 재현이 없다고 적는다")
    assert "has not been compared against published hydrogen-DRI LCOA" in text, (
        "§7이 문헌 LCOA 대조의 공백을 더 이상 밝히지 않는다 — validation_external.md §5는 "
        "그 대조를 '아직 하지 않음'으로 기록한다")
    for rec in ("docs/validation_external.md", "docs/validation_backtest.md",
                "docs/cross_model_check.md", "tests/test_consistency.py"):
        assert rec in text, f"§7이 {rec}를 가리키지 않는다 — 검증 층의 기록을 찾을 수 없다"


def test_section_4_5_band_coverage_is_the_inventory_not_a_story():
    """§4.5가 팔던 그림이 데이터와 달랐다 (F17).

    "가장 좋은 출처를 가진 파라미터가 밴드 없는 것들"은 T1(3행 중 2행이 밴드 보유)에서
    성립하지 않고, 실제 사실은 그것보다 단순하다 — **415행 중 21행만 밴드를 가진다.**
    그리고 T5 규약("범위 필수")은 155행 중 139행에서 지켜지지 않는다. 이 테스트는 §4.5의
    수가 `docs/parameter_inventory.csv`에서 다시 계산되지 않으면 실패한다.
    """
    import pandas as pd

    inv = ROOT / "docs" / "parameter_inventory.csv"
    if not inv.exists():
        pytest.skip("파라미터 인벤토리 미생성 — scripts/build_parameter_inventory.py")
    d = pd.read_csv(inv)
    band = d.value_low.notna() & d.value_high.notna()
    text = " ".join(GUIDE.read_text(encoding="utf-8").split())

    assert f"{band.sum()} of {len(d)} parameters" in text, (
        f"§4.5의 밴드 보유 수가 실제 {band.sum()}/{len(d)}와 다르다")
    t5 = d.evidence_tier == "T5"
    assert f"{(t5 & ~band).sum()} of the {t5.sum()} T5 parameters carry no range" in text, (
        f"§4.5의 T5 무밴드 수가 실제 {(t5 & ~band).sum()}/{t5.sum()}와 다르다")
    cover = " ".join(f"T{i} {int((band & (d.evidence_tier == f'T{i}')).sum())}/"
                     f"{int((d.evidence_tier == f'T{i}').sum())}" for i in range(1, 6))
    assert cover.replace("T1", "T1", 1) in text.replace(",", ""), (
        f"§4.5의 등급별 밴드 보유율이 실제 '{cover}'와 다르다")
    # 밴드가 있는 T5는 우리가 고른 수(model_choice·policy_assumption·prep_injection)뿐이라는
    # 것이 §4.5의 논지다 — 물리·비용 쪽에 하나라도 붙으면 그 문장을 다시 써야 한다.
    physical = {"technology", "facility", "price_path"}
    assert not set(d[t5 & band].group) & physical, (
        "T5 물리·비용 파라미터에 밴드가 붙었다 — §4.5의 'Not one T5 technology, facility or "
        "price_path parameter carries a range'가 더 이상 참이 아니다")


def test_section_7_audit_tally_is_the_audit_not_a_memory():
    """§7이 감사 결과를 기억으로 적고 있었다 (F18).

    두 가지였다. (1) `D6.capex_total`을 `PARTIAL`(=일부만 채워졌지만 소비된다)로 적었는데
    엔진은 이 열을 읽지 않는다 — 감사가 E5 산출의 동명 필드(`best.capex_total`)에 걸려
    `UNUSED`를 놓쳤다. (2) 게이트가 "unused or unsourced columns"에서 실패한다고 적었는데
    `audit_data.py`의 치명 조건은 합성 데이터 유출과 입력 파일 부재뿐이고, 지금도 UNSOURCED
    경고 4건이 선 채로 게이트가 초록이다. 이 테스트는 §7이 감사 파일과 어긋나면 실패한다.
    """
    import pandas as pd

    audit = ROOT / "docs" / "data_audit.csv"
    if not audit.exists():
        pytest.skip("감사 미실행 — scripts/audit_data.py")
    d = pd.read_csv(audit)
    tally = d.verdict.value_counts()
    text = " ".join(GUIDE.read_text(encoding="utf-8").split())

    assert f"{len(d)} columns across the {d.file.nunique()} input files" in text, (
        f"§7의 컬럼·파일 수가 실제 {len(d)}/{d.file.nunique()}와 다르다")
    stated = (f"{tally.get('ok', 0)} `ok`, {tally.get('PARTIAL', 0)} `PARTIAL`, "
              f"{tally.get('UNUSED', 0)} `UNUSED`, {tally.get('설계상 정상', 0)} "
              "empty-or-unread by design")
    assert stated in text, f"§7의 감사 판정 집계가 실제와 다르다 — 실제는 '{stated}'"

    unused = set(d[d.verdict == "UNUSED"].file + "." + d[d.verdict == "UNUSED"].column)
    assert unused == {"D6_company_financials.capex_total"}, (
        f"UNUSED 집합이 {sorted(unused)}로 바뀌었다 — §7이 이 열을 이름으로 적는다")
    row = d[(d.file == "D6_company_financials") & (d.column == "capex_total")].iloc[0]
    assert f"collected for {row.filled} of {row.rows} firm-years" in text, (
        f"§7의 채움 수가 실제 {row.filled}/{row.rows}와 다르다")

    # 게이트의 이빨을 과장하면 심사자가 한 번의 실행으로 잡는다
    assert "no unused or" not in text, (
        "§7이 다시 게이트가 미사용·미출처 컬럼에서 실패한다고 주장한다 — "
        "audit_data.py의 치명 조건은 SYNTHETIC LEAK / MISSING INPUT뿐이다")


def test_section_6_1_seed_sweep_matches_the_stability_record():
    """§6.1이 잰 것과 재지 않은 것을 구분하지 않았다 (F18).

    (1) "it is a lower bound, so more simulation buys nothing" — CV는 표본오차이므로
    n_sims를 올리면 줄어든다. `docs/seed_stability.md`가 바로 그 둘(자릿수 축소 또는
    n_sims 상향)을 남은 선택지로 적는다. (2) 시드는 가격 경로만 바꾸고 계획 메뉴는 고정이라
    **계획 선택의 안정성은 이 스윕이 재지 않는다** — §6.1은 그 사실을 밝혀야 한다.

    **F26에서 셋째 검사를 뺐다.** 이 테스트는 §6.1이 인용하던 NSC 수치(고정 시드 ② 165.4,
    계획 변경 −5.9%)를 대조하고 있었는데, 스윕을 다시 뜨자 그 수치가 어느 파일에도 남지
    않았다 — 가이드의 모든 수치는 살아 있는 파일에서 나와야 하므로 문장과 함께 지웠다.
    잰 것과 재지 않은 것을 구분하라는 F18의 요구는 아래 두 문장 검사로 남는다.
    """
    sweep = ROOT / "docs" / "seed_stability.csv"
    live = ROOT / "out" / "e5" / "metrics_company.csv"
    if not (sweep.exists() and live.exists()):
        pytest.skip("시드 스윕 또는 E5 산출 부재")

    text = " ".join(GUIDE.read_text(encoding="utf-8").split())
    assert "more simulation buys nothing" not in text, (
        "§6.1이 다시 표본오차를 줄일 수 없다고 주장한다 — seed_stability.md는 n_sims 상향을 "
        "남은 두 선택지 중 하나로 적는다")
    assert "the stability of plan selection is not measured by this sweep" in text, (
        "§6.1이 이 스윕이 재지 않는 채널을 더 이상 밝히지 않는다")


def test_ccus_is_described_as_excluded_wherever_a10_is_stated():
    """A-10이 파이프라인이 하는 일의 반대를 적고 있었다 (F19).

    `prepare_raw.py:303`은 raw 17행에서 CCUS 2행을 떨어뜨린다 — 어떤 설비도 어떤 가격에도
    포집을 채택할 수 없다. 그런데 가이드 §4.2와 METHODOLOGY §A-10은 둘 다 "CCUS·효율은
    리트로핏"이라고 적고 있었고, 같은 두 문서의 §6.4는 "LOTTE의 공시 수단이 CCUS인데
    우리가 제외했다"고 적고 있었다. 한 문서 안에서 서로를 부정하고 있었던 것이다.
    이 테스트는 (a) 실제로 제외돼 있는지, (b) 두 문서가 그렇게 적는지 둘 다 본다.
    """
    import pandas as pd

    raw = pd.read_csv(ROOT / "data" / "raw" / "tech_options.csv")
    prep = pd.read_csv(ROOT / "data" / "prepared" / "D3_tech_options.csv")
    ccus_raw = set(raw[raw.tech_id.str.contains("ccus")].tech_id)
    assert ccus_raw, "raw에 CCUS 행이 없다 — 이 테스트의 전제가 사라졌으니 문장을 다시 써라"
    assert not any("ccus" in t for t in prep.tech_id), (
        "CCUS가 D3에 들어왔다 — A-10과 §3.4를 다시 써라")

    for doc in (GUIDE, ROOT / "METHODOLOGY.md"):
        text = " ".join(doc.read_text(encoding="utf-8").split())
        a10 = [ln for ln in doc.read_text(encoding="utf-8").splitlines() if "A-10" in ln and "|" in ln]
        assert a10, f"{doc.name}에서 A-10 줄을 못 찾았다"
        assert any("ccus" in ln.lower() for ln in a10), f"{doc.name}의 A-10이 CCUS를 언급하지 않는다"
        assert "CCUS and efficiency are retrofits" not in text and "CCUS·효율은 리트로핏" not in text, (
            f"{doc.name}이 다시 CCUS를 리트로핏 수단으로 적는다 — prepare_raw.py:303이 떨어뜨린다")
        assert "prepare_raw.py:303" in text, (
            f"{doc.name}이 CCUS 제외 지점을 파일:행으로 적지 않는다")


def test_section_3_4_excluded_rows_are_counted_not_typed():
    """§3.4가 "13 rows in total"만 적어 4행이 왜 사라졌는지 말하지 않았다 (F19).

    양쪽 수가 데이터이므로 생성 블록으로 옮겼다. 이 테스트는 그 블록의 수·이름을
    raw ↔ prepared에서 다시 세고, `steel_eaf` 240의 위치 주장(6건 중 최저·유일한
    partial_scope)도 EFF 증거 파일에서 다시 확인한다.
    """
    import pandas as pd

    raw = pd.read_csv(ROOT / "data" / "raw" / "tech_options.csv")
    prep = pd.read_csv(ROOT / "data" / "prepared" / "D3_tech_options.csv")
    text = " ".join(GUIDE.read_text(encoding="utf-8").split())
    assert f"sees {len(prep)} of the {len(raw)} rows" in text, (
        f"§3.4의 행 수가 실제 {len(prep)}/{len(raw)}와 다르다")
    for tid in set(raw.tech_id) - set(prep.tech_id):
        assert f"`{tid}`" in text, f"§3.4가 탈락 행 {tid}을 이름으로 적지 않는다"

    ev = ROOT / "cap-efficient" / "data" / "technology_cost_evidence.csv"
    if not ev.exists():
        pytest.skip("EFF 증거 파일 부재")
    e = pd.read_csv(ev)
    e = e[e.technology_id == "SCRAP_EAF"]
    v = e.normalized_capex_bn_krw_per_mtpa.astype(float)
    lo = e.loc[v.idxmin()]
    assert abs(float(lo.normalized_capex_bn_krw_per_mtpa) - 240) < 0.5, (
        "6건 중 최저가 더 이상 광양 240이 아니다 — §3.4의 '가장 낮다' 주장을 다시 써라")
    assert lo.comparability.startswith("partial"), (
        "광양 행의 comparability가 바뀌었다 — §3.4의 partial-scope 주장을 다시 써라")
    rest = v.drop(v.idxmin())
    assert f"{rest.min():,.0f}–{rest.max():,.0f} thousand KRW/t" in text, (
        f"§3.4의 나머지 5건 범위가 실제 {rest.min():,.0f}–{rest.max():,.0f}와 다르다")

    # 이 표를 정합의 근거로 쓰던 두 칸이 model_estimate 위에 서 있었다
    tech = pd.read_csv(ROOT / "cap-efficient" / "data" / "technologies.csv")
    for tid in ("SCRAP_EAF", "H2_DRI_EAF"):
        row = tech[tech.technology_id == tid].iloc[0]
        assert row.data_status == "model_estimate", (
            f"EFF {tid}에 출처가 붙었다 — §7과 tech_cost_reconciliation.md의 F19 정정을 갱신하라")


def test_diagnostic_drift_block_measures_the_real_gap():
    """§6.2가 인용하는 곁가지 산출물이 헤드라인 실행보다 오래된 것을 숨기지 않는가 (F20).

    `out/process/*`는 `_link_shared`로 E1·E2를 base에 심볼릭 링크한다. base가 다시
    풀리면 링크가 가리키는 계획집합이 바뀌지만 이미 계산된 E3–E5는 그대로 남는다 —
    디스크 위에서 자기 입력과 어긋난 트리가 된다. F20에서 실제로 그랬다: 명목상
    헤드라인과 같은 설정인 `gbm` 팔이 NSC에 대해 ② +6.3%, ③ +4.6% 어긋나 있었다.

    이 테스트는 그 어긋남을 out/에서 다시 계산해 생성 블록의 수와 맞춘다. 팔을 다시
    돌리면 블록은 저절로 "모두 최신"으로 바뀌고 이 테스트는 그 쪽을 검사한다.
    """
    import pandas as pd

    base = ROOT / "out" / "e5" / "metrics_company.csv"
    proc = ROOT / "out" / "process" / "gbm" / "e5" / "metrics_company.csv"
    if not (base.exists() and proc.exists()):
        pytest.skip("base 또는 process 팔 미실행")

    text = " ".join(GUIDE.read_text(encoding="utf-8").split())

    def nz(p):
        m = pd.read_csv(p).query("scenario=='NZ15' and support=='none'")
        return {r.company_id: (r.cost_per_tco2_thkrw, r.tcar_bnkrw) for r in m.itertuples()}

    cur, arm = nz(base), nz(proc)
    d2 = {k: 100 * (arm[k][0] / cur[k][0] - 1) for k in cur if k in arm}
    worst = max(d2, key=lambda k: abs(d2[k]))

    # F26: 낡음 판정은 팔 하나가 아니라 **모든 팔**을 본다. `out/process`의 arm 중 하나만
    # 다시 돌아도 gbm 통제군은 새것이 되므로, 통제군 시각만으로는 디렉터리를 판정할 수 없다.
    arms = [d / "e5" / "metrics_company.csv" for d in sorted((ROOT / "out" / "process").iterdir())
            if (d / "e5" / "metrics_company.csv").exists()]
    behind = sum(1 for a in arms if a.stat().st_mtime < base.stat().st_mtime)
    if not behind:
        assert abs(d2[worst]) < 0.05, (
            f"process 팔이 base보다 새로운데 gbm 통제군이 헤드라인과 {d2[worst]:+.2f}% "
            "어긋난다 — 같은 설정이면 같은 수가 나와야 한다")
        assert f"| 0 of {len(arms)} | `gbm` |" in text, (
            "`out/process`의 팔이 전부 최신인데 §6.2의 'Arms behind base' 칸이 0이 아니다")
        return

    assert "at least one arm that predates it" in text, (
        "process/scenarios 팔이 base보다 오래됐는데 §6.2가 그 사실을 적지 않는다")
    assert f"{d2[worst]:+.2f}%" in text, (
        f"§6.2의 ② 최대 어긋남이 실제 {d2[worst]:+.2f}%와 다르다 — 블록을 다시 생성하라")


def test_cross_model_causes_name_the_price_process():
    """H4 요인 목록이 확률과정을 빠뜨리고 있었다 (F20).

    두 문서 모두 TCaR 수준 비교 불가의 이유로 '분모가 다르다'만 적었다. 분모를 맞춰도
    남는 요인이 하나 더 있다 — FIN은 GBM, EFF는 OU다. 가이드 자신의 §6.2가 그 크기를
    41~48%로 재어 두었으므로, 목록에서 빠진 것은 사소한 누락이 아니라 목록에 있는 어떤
    요인보다 큰 항목이었다. EFF가 GBM으로 바꾸거나 반감기가 달라지면 실패한다.
    """
    import json
    import math

    p = ROOT / "cap-efficient" / "data" / "price_process.json"
    if not p.exists():
        pytest.skip("EFF price_process.json 부재")
    e = json.loads(p.read_text(encoding="utf-8"))
    kappa = e.get("mean_reversion", {}).get("electricity")
    assert kappa, "EFF가 더 이상 평균회귀를 쓰지 않는다 — §7과 cross_model_check.py를 다시 써라"
    hl = math.log(2) / kappa

    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
    assert f"{hl:.1f}-year half-life" in guide, (
        f"§7이 EFF 전력 반감기 {hl:.1f}년을 적지 않는다")
    assert "equalising the denominator would not make them comparable" in guide, (
        "§7이 이 교란을 분모 문제의 각주로 되돌려 적는다")

    cmc = ROOT / "docs" / "cross_model_check.md"
    if not cmc.exists():
        pytest.skip("cross_model_check.md 미생성")
    body = " ".join(cmc.read_text(encoding="utf-8").split())
    assert "확률과정·변동성·요인상관" in body, (
        "cross_model_check.md §4의 설명되는 차이 목록에 확률과정이 없다")
    assert f"반감기 {hl:.1f}년" in body, "cross_model_check.md의 EFF 반감기가 실제와 다르다"


def test_reline_verdict_uses_every_anchor_not_the_binding_one():
    """A-13의 판정이 단일 관측 위에 서 있었다 (F21).

    가이드는 §4.1과 §7 두 곳에서 "외부 검증 실패 — 공시 실적의 4.2배"라고 적었다.
    그 판정은 고베 1건에 기댄 것이고, `docs/validation_external.md` §1-1이 L1 문헌
    지도(2026-08-10) 이후 이미 철회했다 — 앵커가 셋이면 우리 200은 앞의 둘보다 크지만
    셋째 대역 **안**이다. 이 테스트는 세 앵커를 출처에서 다시 계산해 가이드와 맞추고,
    '4.2배'가 다시 최종 판정 자리로 돌아가면 실패한다.
    """
    import pandas as pd
    sys.path.insert(0, str(ROOT / "scripts"))
    from validate_external import (ACCR_RELINE_USD_M, EURKRW, NATCOMM_RELINE_EUR_T,
                                   USDKRW)

    ev = None
    for base in (pathlib.Path.home() / "Documents" / "cap-efficient", ROOT / "cap-efficient"):
        p = base / "data" / "technology_cost_evidence.csv"
        if p.exists():
            ev = p
            break
    if ev is None:
        pytest.skip("EFF technology_cost_evidence.csv 부재")
    rl = pd.read_csv(ev).query("technology_id == 'BF_RELINE'")
    kobe = float(rl.normalized_capex_bn_krw_per_mtpa.iloc[0])

    d1a = pd.read_csv(ROOT / "data" / "prepared" / "D1a_facility_static.csv")
    bf = d1a[d1a.unit_type == "BF"]
    ours = float(bf.incumbent_capex_unit.median())
    cap = float(bf.capacity.median()) / 1e6
    natcomm = NATCOMM_RELINE_EUR_T * EURKRW / 1000
    lo, hi = (v * USDKRW / 1e3 / cap for v in ACCR_RELINE_USD_M)

    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
    for v in (kobe, natcomm, lo, hi, ours):
        assert f"{v:,.0f}" in guide, f"§7의 개수 앵커 표에 {v:,.0f} 천원/t가 없다"

    assert lo <= ours <= hi, (
        f"우리 {ours:,.0f}이 더 이상 ACCR 대역 [{lo:,.0f}, {hi:,.0f}] 안이 아니다 "
        "— §7의 'inside this band'와 §4.1의 판정을 다시 써라")
    assert "**ours is inside this band**" in guide
    assert "not a point error in ours" in guide, (
        "가이드가 단일 관측 판정('외부 검증 실패')으로 되돌아갔다")
    # 약한 근거는 같은 문장에서 밝힌다 — ACCR의 통화가 USD 가정이라는 것과, AUD였다면
    # 우리 값이 대역 위로 나간다는 것.
    assert f"[{lo * 0.65:,.0f}, {hi * 0.65:,.0f}]" in guide, (
        "AUD 해석에서 대역이 어디로 내려가는지 적지 않는다 — 'inside the band'가 무조건적으로 읽힌다")


def test_reline_cheap_is_not_sold_as_a_completed_check():
    """`reline_cheap`이 "not needed"로 찍히고 있었다 (F21).

    `incumbent_capex_scale`은 `plancost.py`에서 좌초비용에 곱해지고 그 값은 E2 계획
    탐색이 읽는다 — 즉 이 축의 본 효과는 채택 시점 이동이고, 계획 메뉴를 공유한 채
    돌린 2.0% / 0.3%는 하한이다. `build_scenario_page.py`가 이미 그렇게 적고 있었으므로
    목록을 두 벌 두지 않고 그쪽을 읽는다. 이 테스트는 그 연결이 끊기면 실패한다.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_scenario_page import PARTIAL_EFFECT
    from run_scenarios import BUNDLES, REPLAN_REQUIRED

    assert "reline_cheap" in PARTIAL_EFFECT, (
        "시나리오 페이지가 reline_cheap을 부분효과 목록에서 뺐다 — 가이드 §4.3도 같이 고쳐라")
    assert "reline_cheap" not in REPLAN_REQUIRED, (
        "reline_cheap이 --replan 강제 목록에 들어갔다 — 이제 표의 표기는 "
        "'**no — required**'여야 하고 §4.3 산문의 '여섯 번째' 문장은 틀린다")
    assert "incumbent_capex_scale" in str(BUNDLES["reline_cheap"][1]), (
        "reline_cheap이 더 이상 개수 재조달가를 흔들지 않는다")

    src = (ROOT / "src" / "cap" / "plancost.py").read_text(encoding="utf-8")
    assert "incumbent_capex_scale" in src, (
        "좌초비용이 더 이상 이 배수를 읽지 않는다 — 그렇다면 '하한'이라는 서술의 근거가 없다")

    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
    assert "| **no — lower bound** |" in guide, (
        "§4.3 표가 reline_cheap을 다시 'not needed'로 찍는다")
    assert "pull adoption years forward" in guide


def test_crossmodel_band_reads_the_committed_eff_copy():
    """교차대조의 유일한 수준(level) 검사가 저장소 밖 파일에 걸려 있었다 (F22).

    EFF는 두 벌로 존재하고 `outputs/candidate_scenario_metrics.csv`가 두 트리에서
    다르다. F20까지 `cross_model_check.py`는 저장소 밖 사본을 읽었고, 그 사본에서는
    NSC가 EFF 실행가능 대역 **안**, 커밋된 사본에서는 **밖**이다 — 즉 이 저장소만으로
    재현하면 판정이 뒤집힌다. 이 테스트는 (a) 읽는 사본이 커밋된 쪽인지, (b) 가이드
    §7의 대역 표가 그 사본에서 다시 계산한 값과 맞는지, (c) 대역이 EFF 자신의 선택값을
    하단으로 삼는다는(=한쪽으로만 실패하는) 서술이 남아 있는지를 본다.
    """
    pd = pytest.importorskip("pandas")
    if not (ROOT / "out" / "e5" / "metrics_company.csv").exists():
        pytest.skip("out/ 없음")
    sys.path.insert(0, str(ROOT / "scripts"))
    from cross_model_check import CAND, PAIR, cost_band, eff_file

    src = eff_file(CAND)
    assert src is not None, f"EFF 후보 지표가 두 트리 어디에도 없다: {CAND}"
    assert ROOT in src.parents, (
        f"교차대조가 저장소 밖 사본을 읽는다 ({src}) — 이 저장소만으로 재현되지 않고, "
        "NSC의 대역 안/밖 판정이 어느 트리를 읽느냐로 뒤집힌다")

    band = cost_band(src)
    m = pd.read_csv(ROOT / "out" / "e5" / "metrics_company.csv").query(
        "scenario=='NZ15' and support=='none'").set_index("company_id")
    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())

    for fin, eff in PAIR.items():
        if fin not in m.index or eff not in band.index:
            continue
        ours = float(m.loc[fin, "cost_per_tco2_thkrw"])
        lo, hi = float(band.loc[eff, "min"]), float(band.loc[eff, "max"])
        assert f"{lo:,.1f}" in guide and f"{hi:,.1f}" in guide, (
            f"§7의 대역 표에 {fin}의 [{lo:,.1f}, {hi:,.1f}]가 없다 — 생성기를 다시 돌려라")
        assert ours >= lo, (
            f"{fin}: 우리 {ours:,.0f}이 EFF 채택값 {lo:,.1f} 아래다 — 대역 하단이 EFF "
            "자신의 선택값이라는 §7의 서술이 더 이상 참이 아니다")

    assert "the band's lower edge is EFF's own answer" in guide, (
        "§7이 대역 검사를 대칭적인 검사처럼 되돌려 팔고 있다 — 이 검사는 위쪽으로만 실패한다")
    assert "not tree-invariant" in guide, (
        "§7이 두 EFF 트리가 이 판정을 갈라놓는다는 사실을 더 이상 적지 않는다")


def test_gate_check_count_is_read_off_gate_not_hand_written():
    """가이드가 게이트 항목 수를 손으로 세고 있었고, 그 수가 틀려 있었다 (F23).

    F22가 `sidecars`를 아홉 번째 항목으로 넣었으나 §7은 "Eight checks … Five of the
    eight are hard"를 그대로 들고 있었다 — 외부 독자에게 검사 하나를 숨긴 셈이다.
    이제 그 문장은 `gate.CHECKS`/`gate.HARD`에서 생성된다. 이 테스트는 (a) 생성된
    수가 실제 항목 수와 맞는지, (b) 손으로 센 옛 문장이 되살아나지 않았는지를 본다.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from gate import CHECKS, HARD

    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
    hard = [k for k, _, _ in CHECKS if k in HARD]

    assert f"**{len(CHECKS)} checks.**" in guide, (
        f"§7이 게이트 항목 수를 {len(CHECKS)}로 적지 않는다 — 생성기를 다시 돌려라")
    assert f"{len(hard)} are hard" in guide, (
        f"§7의 hard 항목 수가 gate.HARD({len(hard)}개)와 다르다")
    for key, _, _ in CHECKS:
        assert f"`{key}`" in guide, f"§7이 게이트 항목 `{key}`를 이름으로 싣지 않는다"
    assert "Eight checks" not in guide, (
        "손으로 센 항목 수가 §7에 되살아났다 — 검사가 하나 늘면 다시 틀린다")


def test_criterion_swap_carries_the_tail_not_just_the_ranking():
    """결정 기준을 바꾸는 축이 §6.2에 없었다 (F23).

    §6.2는 할인율·가격과정·충격 정규화·시나리오 묶음을 흔들어 순위가 불변임을 보이지만,
    그 넷은 전부 **입력**을 흔들고 목적함수는 그대로 둔다. `robustness_structural.md`가
    I2 이래 목적함수 자체를 흔든 결과(P90 최소화)를 들고 있었고 가이드는 §1 P2 행에서
    그 문서를 한 번 인용할 뿐 표를 싣지 않았다. 이 테스트는 (a) 각 기업의 꼬리 배수가
    `out/e5`에서 다시 계산한 값과 맞는지, (b) 순위 불변 진술이 실제 재계산과 맞는지,
    (c) 두 약점(A-17 사전값 의존, 재계획이 아닌 재선택)이 같은 자리에 남아 있는지를 본다.
    """
    pd = pytest.importorskip("pandas")
    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if not fp.exists():
        pytest.skip("out/ 없음")
    sys.path.insert(0, str(ROOT / "scripts"))
    from robustness_structural import CONAME, pick

    fr = pd.read_csv(fp).query("scenario=='NZ15' and support=='none'")
    g = fr[~fr.is_disclosed & fr.budget_ok]
    assert not g.empty, "예산 정합 계획이 없다 — e5 먼저 실행"
    p50, p90 = pick(g, "p50"), pick(g, "p90")
    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())

    for c in p50.index:
        if c not in p90.index:
            continue
        a, b = float(p50.loc[c, "lcoa"]), float(p90.loc[c, "lcoa"])
        assert f"{b:,.0f}" in guide, (
            f"§6.2에 {CONAME[c]}의 P90 기준 단가 {b:,.0f}가 없다 — 생성기를 다시 돌려라")
        assert f"×{b / a:.1f}" in guide, (
            f"§6.2에 {CONAME[c]}의 꼬리 배수 ×{b / a:.1f}가 없다")

    order = lambda d: list(d.sort_values("lcoa").index)  # noqa: E731
    same = order(p50) == order(p90)
    assert ("The ordering is **unchanged**" in guide) == same, (
        "§6.2의 순위 불변 진술이 재계산과 어긋난다 — 기준을 바꾸면 순위가 "
        f"{'바뀌지 않는다' if same else '바뀐다'}")

    assert "P90 is our own\nsimulation's P90".replace("\n", " ") in guide, (
        "§6.2가 꼬리 배수의 절대값이 A-17 사전 변동성에 걸려 있다는 사실을 더 이상 적지 않는다")
    assert "re-selection, not a re-solve" in guide, (
        "§6.2가 이것이 재계획이 아니라 재선택이라는 한계를 더 이상 적지 않는다 — "
        "E2가 만들지 않은 계획은 어느 기준으로도 고를 수 없다")


def test_guide_does_not_say_the_gate_ignores_the_side_diagnostics():
    """F22가 `sidecars` 검사를 넣은 뒤에도 §6.2는 게이트가 out/e5만 본다고 적고 있었다 (F23).

    낡은 곁가지 산출물이 §6.2에 인용되는 것이 이 문단의 주제이므로, 그것을 게이트가
    이제 이름으로 말한다는 사실이 빠지면 문단이 실제보다 어두운 그림을 판다.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from gate import CHECKS

    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
    assert "checks staleness for `out/e5` only" not in guide, (
        "§6.2가 게이트에 곁가지 낡음 검사가 없다고 적는다 — gate.CHECKS에 있다")
    if any(k == "sidecars" for k, _, _ in CHECKS):
        assert "`sidecars`" in guide, "§6.2가 게이트의 sidecars 검사를 이름으로 적지 않는다"


def test_capacity_estimate_count_separates_estimated_from_all_blast_furnaces():
    """§3.1이 추정 행을 "16 of the 23 rows, all blast furnaces"로 적고 있었다 (F24).

    같은 문서 §4.1의 A-13은 고로를 **17기**로 센다. 두 수를 나란히 읽은 독자는 어느
    쪽이 맞는지 알 수 없고, 실제로는 둘 다 맞다 — 추정된 16기는 고로 17기 중 16기다.
    빠진 한 기(`POSCO_GWY_BF1`)가 곱수를 맞춘 **바로 그 교정점**이므로, 추정값을
    공표값과 대조할 수 있는 행은 하나도 없다. 이 테스트는 (a) 세 수가 D1a와 맞는지,
    (b) 교정점이 이름으로 실려 있는지, (c) 대조 불가 진술이 지워지지 않았는지를 본다.
    """
    pd = pytest.importorskip("pandas")
    p = ROOT / "data" / "prepared" / "D1a_facility_static.csv"
    if not p.exists():
        pytest.skip("D1a 없음")
    d = pd.read_csv(p)
    est = d.capacity_unit.astype(str).str.contains("추정")
    bf = d.unit_type.astype(str).eq("BF")
    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())

    assert f"{int(est.sum())} of the {len(d)} rows are estimated" in guide, (
        f"§3.1의 추정 행 수가 D1a({int(est.sum())}/{len(d)})와 다르다 — 생성기를 다시 돌려라")
    assert f"that is {int((est & bf).sum())} of the {int(bf.sum())} blast furnaces" in guide, (
        f"§3.1이 추정 행을 고로 {int(bf.sum())}기 중 {int((est & bf).sum())}기로 적지 않는다 — "
        "A-13의 고로 수와 어긋난 채로 남는다")
    for t in d[bf & ~est].itertuples():
        assert f"`{t.facility_id}`" in guide, (
            f"§3.1이 공표 용량을 가진 고로 `{t.facility_id}`를 이름으로 싣지 않는다")
    assert "No estimated row can be checked against a published figure" in guide, (
        "교정점이 곧 유일한 공표 고로라는 사실(=표본 외 검증 0건)이 §3.1에서 지워졌다")
    assert "16 of the 23 rows, all blast furnaces" not in guide, (
        "손으로 쓴 옛 문장이 §3.1에 되살아났다 — 고로 수가 바뀌면 다시 어긋난다")


def test_epsilon_sweep_counts_are_read_off_m8_everywhere_they_appear():
    """§6.3과 §1 P1이 ε-스윕 수치를 손으로 들고 있었다 (F24).

    네 수(32 캡 · 헤드라인 비지배 4 · 대체 규약 25 · 8묶음 중 7)는 지금 맞지만
    `out/m8`은 게이트 `sidecars` 검사가 이름으로 부르는 **낡은 부속 산출물**이다.
    최우선 인계인 그 재실행이 끝나는 순간 네 수는 조용히 거짓이 되고, 이전까지
    아무 테스트도 그것을 잡지 못했다. §6.3은 이제 생성되고, §1 P1은 표 안이라
    생성할 수 없으므로 이 테스트가 대신 붙잡는다 — 재실행 후 손으로 고치게 만든다.
    """
    pd = pytest.importorskip("pandas")
    p = ROOT / "out" / "m8" / "summary.csv"
    if not p.exists():
        pytest.skip("out/m8 없음")
    m = pd.read_csv(p)
    tried, nb = int(m.caps_tried.sum()), len(m)
    head, l2 = int(m.nondominated_headline.sum()), int(m.nondominated_l2.sum())
    l2b = int((m.nondominated_l2 > 0).sum())
    hb = m[m.nondominated_headline > 0]
    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())

    assert f"all {tried} caps are feasible" in guide, (
        f"§6.3의 캡 수가 m8({tried})과 다르다 — 생성기를 다시 돌려라")
    assert f"only **{head}** remain non-dominated" in guide, (
        f"§6.3의 헤드라인 비지배 수가 m8({head})과 다르다")
    assert f"{l2} of the same {tried} become non-dominated" in guide, (
        f"§6.3의 대체 규약 비지배 수가 m8({l2}/{tried})과 다르다")
    assert f"technology axis returns in {l2b} of {nb} bundles" in guide, (
        f"§6.3의 기술축 복귀 묶음 수가 m8({l2b}/{nb})과 다르다")

    # §1 P1 — 표 안이라 생성 블록을 넣을 수 없다. 같은 수를 손으로 들고 있으므로 대조한다.
    assert f"only {head} of {tried} forced technology schedules survive" in guide, (
        f"§1 P1의 비지배 수가 m8({head}/{tried})과 다르다 — out/m8을 다시 돌렸다면 "
        "§1 P1 행을 손으로 고쳐라 (§6.3은 자동으로 따라간다)")
    if len(hb) == 1:
        assert f"all {head} sit in one of the {nb} bundles" in guide, (
            f"§1 P1이 비지배 계획이 한 묶음에 몰린 사실을 {nb}묶음 기준으로 적지 않는다")
        assert f"in the other {nb - len(hb)} none survives" in guide, (
            f"§1 P1의 '나머지 묶음' 수가 m8({nb - len(hb)})과 다르다")


def test_sensitivity_ledger_numbers_track_the_screening_output():
    """§4의 A-01·A-02가 3일 낡은 민감도 파일에서 손으로 옮긴 수를 들고 있었다 (F25).

    `scripts/sensitivity_screening.py`는 자기 독스트링과 달리 `outputs/`(존재하지 않는
    디렉터리)에 다른 이름으로 썼고, 소비자 다섯(가이드 §4.3 생성기 · evidence 페이지 ·
    `data_section_table` · MCP `get_sensitivity` · `uncertainty_propagation`)은 전부
    `out/sensitivity/`를 읽었다. 그래서 그 파일들은 G1 배분 수정(08-10) 이전 판에
    얼어붙어 있었고, A-02의 "86%"와 A-01의 "rank 8"은 수정 전 데이터의 값이었다.
    실제 값은 154%와 rank 10이다. 경로를 고쳤으므로 다시 얼어붙지는 않지만, 손으로 적힌
    두 수는 여전히 표 셀 안이라 생성할 수 없다 — 이 테스트가 대신 붙잡는다.

    METHODOLOGY도 같은 두 수를 들고 있으므로 (정본) 같이 본다. 한쪽만 고치면 실패한다.
    """
    pd = pytest.importorskip("pandas")
    p = ROOT / "out" / "sensitivity" / "ranking.csv"
    if not p.exists():
        pytest.skip("out/sensitivity 없음 — scripts/sensitivity_screening.py를 돌려라")
    rk = pd.read_csv(p).reset_index(drop=True)
    top, second = rk.iloc[0], rk.iloc[1]
    cap_rank = int(rk.index[rk.base_param == "fac.capacity"][0]) + 1
    guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
    meth = " ".join((ROOT / "METHODOLOGY.md").read_text(encoding="utf-8").split())

    assert top.base_param == "fac.ef_inc", (
        f"민감도 1위가 `{top.base_param}`로 바뀌었다 — A-02가 여전히 최대 파라미터라는 "
        "§4.1의 주장을 다시 쓰라")
    assert f"up to {top.score:.0f}%" in guide, (
        f"§4.1 A-02의 이동폭이 ranking.csv({top.score:.0f}%)와 다르다")
    assert f"{top.score:.0f}% 움직이는" in meth, (
        f"METHODOLOGY §0의 이동폭이 ranking.csv({top.score:.0f}%)와 다르다")
    ratio = f"{top.score / second.score:.1f}"
    assert f"{ratio}× the next parameter" in guide and f"{ratio}배다" in meth, (
        f"1위/2위 배수가 ranking.csv({ratio}배)와 다르다 — 가이드와 METHODOLOGY 양쪽")
    assert f"Sensitivity rank {cap_rank}." in guide, (
        f"§4.2 A-01의 민감도 순위가 ranking.csv({cap_rank}위)와 다르다")
    assert f"민감도 {cap_rank}위" in meth, (
        f"METHODOLOGY A-01의 민감도 순위가 ranking.csv({cap_rank}위)와 다르다")


def test_screening_writes_where_every_consumer_reads():
    """생산자와 소비자가 다른 경로를 쓰면 낡음은 조용하다 (F25).

    산출 경로를 손으로 바꿔 다시 어긋나게 만들면 이 테스트가 실패한다.
    """
    src = (ROOT / "scripts" / "sensitivity_screening.py").read_text(encoding="utf-8")
    assert 'C.out_dir(cfg, "sensitivity")' in src, (
        "민감도 스크립트가 out/sensitivity 밖으로 쓴다 — 소비자 다섯이 읽는 곳이다")
    assert 'ROOT / "outputs"' not in src, "존재하지 않는 `outputs/`로 되돌아갔다"
    for name in ("screening.csv", "ranking.csv"):
        assert f'"{name}"' in src, f"{name}을 쓰지 않는다"


def test_gate_sidecar_check_enumerates_out_rather_than_a_hand_written_list():
    """곁가지 목록을 손으로 적으면 목록에 없는 산출물이 낡은 채 인용된다 (F25).

    F22가 네 곳을 이름으로 박았고, 그 목록에 없던 `out/sensitivity`가 base보다 24시간
    낡은 채 §4와 MCP에 인용됐다 — 게이트는 그동안 그린이었다. 이제 base(e1–e5)가 아닌
    `out/` 디렉터리를 전부 센다.

    **F26에서 판정 기준을 가장 새 파일에서 가장 낡은 파일로 바꿨다.** 열거만으로는
    부족했다 — 디렉터리 안 파일 하나만 다시 써도 전체가 최신으로 보였고, 그 상태에서
    `out/scenarios`의 `disc65` 팔이 43시간, `out/uncertainty`의 `decomposition_bands.csv`가
    이틀 낡은 채 게이트는 그린이었다. 후자는 `g2_band_impact.py:44`를 거쳐 가이드 §4.5의
    밴드 열로 인용되고 있었다. 이 테스트도 그때 `_newest`로 기대값을 만들고 있었으므로
    같은 맹점을 공유했다.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import gate

    base = gate._newest("out/e5/*.csv")
    if base is None:
        pytest.skip("out/e5 없음")
    names = [p.name for p in (ROOT / "out").iterdir()
             if p.is_dir() and p.name not in {"e1", "e2", "e3", "e4", "e5"}]
    assert "sensitivity" in names, "out/sensitivity가 없다"
    old = {n: gate._oldest_excluding(f"out/{n}/**/*.csv", "e1_local") for n in names}
    expected = {n for n, o in old.items() if o and o[0] < base[0]}
    ok, msg = gate.check_sidecars()
    for n in expected:
        assert n in msg, f"게이트가 낡은 곁가지 `{n}`를 이름으로 부르지 않는다"
    assert ok == (not expected)
    # 뒤처진 파일을 이름으로 부르지 않으면 재실행할 것을 찾는 데 또 한 사이클이 든다
    for n in expected:
        assert old[n][1].name in msg, (
            f"게이트가 `{n}`의 가장 낡은 파일 `{old[n][1].name}`을 밝히지 않는다")
    # `e1_local`은 out/e1의 mtime 보존 사본이라 지울 수 없는 경고를 만든다 — 세지 않는다
    loc = list(ROOT.glob("out/scenarios/*/e1_local/*.csv"))
    if loc:
        assert "e1_local" not in msg, "게이트가 out/e1의 사본을 낡음으로 보고한다"


def test_freshness_measures_out_by_its_oldest_file_not_its_newest():
    """F27은 곁가지 검사만 고쳤고, 같은 맹점이 `check_freshness`에 F28까지 남아 있었다.

    e5의 아홉 파일 중 하나만 다시 써도 out/ 전체가 입력보다 새것으로 보였다.
    부분 재실행은 실제로 일어난다(F27이 `out/scenarios`에서 실측했다). 여기서는
    파일 하나를 입력보다 낡게 되돌려 게이트가 그것을 보는지 확인한다.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import gate

    src = gate._newest("data/raw/*.csv", "src/cap/*.py", "config.yaml")
    e5 = sorted(ROOT.glob("out/e5/*.csv"))
    if src is None or len(e5) < 2:
        pytest.skip("out/e5 또는 입력 없음")
    assert gate.check_freshness()[0], "전제가 깨졌다 — out/이 이미 입력보다 낡다"

    victim = e5[-1]  # 가장 새 파일 하나로 판정하면 이 파일이 낡아도 그린이다
    st = victim.stat()
    try:
        os.utime(victim, (st.st_atime, src[0] - 3600))
        ok, msg = gate.check_freshness()
        assert not ok, "e5 파일 하나가 입력보다 낡은데 freshness가 그린이다"
        assert victim.name in msg, f"게이트가 뒤처진 파일 `{victim.name}`을 이름으로 부르지 않는다"
    finally:
        os.utime(victim, (st.st_atime, st.st_mtime))
    assert gate.check_freshness()[0], "복원 실패 — mtime을 되돌리지 못했다"


def test_axis_impact_deltas_state_the_cells_they_are_maximised_over():
    """§4.3의 Δ②·Δ③이 어느 칸의 최대인지 가이드가 사실대로 적는가 (F26).

    F26까지 가이드는 "sixteen firm × scenario × support cells (4 × 2 × 2)의 최대"라고
    적었으나, `robustness_section_table.py`는 `SCEN`·`SUPP` 한 칸(기업 4개)만 본다.
    좁은 정의를 넓은 정의로 광고한 것이고, 둘은 멀다 — penalty_none이 5.9% 대 241.8%다.
    이 테스트는 두 수를 `out/`에서 다시 계산해 가이드와 대조한다. 생산자의 필터가
    바뀌거나 옛 문장이 되살아나면 실패한다.
    """
    import pandas as pd

    bm = ROOT / "out" / "m5" / "bundle_matrix.csv"
    if not bm.exists():
        pytest.skip("out/m5 없음")
    sys.path.insert(0, str(ROOT / "scripts"))
    from robustness_section_table import SCEN, SUPP

    guide = GUIDE.read_text(encoding="utf-8")
    b = pd.read_csv(bm)

    s = pd.read_csv(ROOT / "out" / "scenarios" / "summary.csv")
    n_cells = len(s.query("bundle == 'base' and scenario == @SCEN and support == @SUPP"))
    assert f"largest move across the {n_cells} firms in the headline cell " \
           f"(`{SCEN}`, `support={SUPP}`)" in guide, (
        f"§4.3이 Δ의 최대 범위를 {n_cells}개 헤드라인 칸으로 적지 않는다")
    assert "largest\nmove across the **sixteen**" not in guide, (
        "16칸 최대라는 옛 주장이 되살아났다 — 생산자는 헤드라인 한 칸만 본다")

    # 16칸 최대를 요약표에서 직접 다시 계산해 대장 열과 가이드 문장 양쪽에 대조한다
    idx = ["company_id", "scenario", "support"]
    base = s[s.bundle == "base"].set_index(idx)
    for col, ledger in (("cost_per_tco2_thkrw", "d_m2_pct_all"),
                        ("tcar_bnkrw", "d_tcar_pct_all")):
        for n, d in s[s.bundle != "base"].groupby("bundle"):
            x = d.set_index(idx)
            bb = base[col].reindex(x.index)
            m = bb.abs() > 1e-9
            v = round(float(((x[col][m] / bb[m] - 1) * 100).abs().max()), 1)
            assert v == b.set_index("bundle").loc[n, ledger], (
                f"{n}의 {ledger}가 summary.csv에서 다시 센 값({v})과 다르다")
    w = b.loc[b.d_tcar_pct_all.idxmax()]
    assert f"**{b.d_m2_pct_all.max():.1f}%** on ② and " \
           f"**{b.d_tcar_pct_all.max():.1f}%** on ③, both on `{w.bundle}`" in guide, (
        "16칸 최대가 bundle_matrix.csv와 다르다")


def test_guide_never_names_a_pipeline_stage_that_does_not_exist():
    """가이드의 재현 지시가 실행 가능한가 (F26).

    §4.3 대체 문구가 `python -m cap m5`를 시키고 있었다. CLI에는 e1–e5·render·all뿐이고
    m5는 `scripts/robustness_section_table.py`가 쓴다 — 지시대로 하면 아무것도 안 나온다.
    """
    import re

    sys.path.insert(0, str(ROOT / "src"))
    from cap.__main__ import STAGES

    src = (ROOT / "scripts" / "build_tech_guide.py").read_text(encoding="utf-8")
    ok = set(STAGES) | {"all", "--help"}
    for used in re.findall(r"python -m cap ([a-z0-9_]+)", src + GUIDE.read_text("utf-8")):
        assert used in ok, f"`python -m cap {used}`는 없는 단계다. 있는 것: {sorted(ok)}"


def test_diagnostic_drift_dates_each_sidecar_by_its_oldest_arm():
    """§6.2가 곁가지를 **가장 낡은 팔**로 날짜 짓는가 (F26).

    F26까지 이 표는 곁가지를 그 **요약 파일**의 시각으로 날짜 짓고, 드리프트를 그
    **대조 팔 하나**에서만 쟀다. 둘 다 부분 재실행이 다시 쓴다 — 그래서 팔 하나만
    다시 푼 디렉터리가 스스로를 "방금 쓰였고 드리프트 0"으로 보고한다. 2026-08-12
    재계획 캠페인 도중 `out/scenarios`가 정확히 그 상태였다: summary.csv는 06:14,
    대조 팔 base는 새것, 그런데 12개 팔 중 6개가 base 실행보다 낡아 있었다.

    이 테스트는 표의 "Arms behind base" 열을 파일 시각에서 다시 세어 대조한다.
    생성기가 요약 파일 시각으로 돌아가면 실패한다.
    """
    base = ROOT / "out" / "e5" / "metrics_company.csv"
    if not base.exists():
        pytest.skip("파이프라인 미실행")
    guide = GUIDE.read_text(encoding="utf-8")
    t_base = base.stat().st_mtime

    assert "| Diagnostic | Oldest arm written | Arms behind base |" in guide, (
        "§6.2가 곁가지를 요약 파일 시각으로 날짜 짓는 옛 표로 되돌아갔다")

    for label, root in (("out/process", ROOT / "out" / "process"),
                        ("out/scenarios", ROOT / "out" / "scenarios")):
        if not root.exists():
            continue
        arms = [d / "e5" / "metrics_company.csv" for d in sorted(root.iterdir())
                if (d / "e5" / "metrics_company.csv").exists()]
        assert arms, f"{label}에 팔이 하나도 없다"
        behind = sum(1 for a in arms if a.stat().st_mtime < t_base)
        oldest = min(a.stat().st_mtime for a in arms)
        stamp = _dt.datetime.fromtimestamp(oldest).strftime("%Y-%m-%d %H:%M")
        assert f"| {stamp} | {behind} of {len(arms)} |" in guide, (
            f"`{label}`가 표에 '{stamp} | {behind} of {len(arms)}'로 실려 있지 않다 — "
            f"가장 낡은 팔이 아니라 요약 파일로 날짜 지은 것이다")
        # 대조 팔은 새것인데 섭동 팔이 낡은 경우, 0을 증거로 읽지 말라는 경고가 붙는가
        if behind and f"`{label}` bundle matrix | {stamp} | {behind} of" in guide:
            assert f"**`{label}` is part re-run" in guide, (
                f"{label}의 팔 {behind}개가 낡았는데 드리프트 0에 경고가 없다")


def test_seed_cv_table_is_recomputed_from_the_sweep_not_hand_written():
    """§6.1 표본잡음 표가 `docs/seed_stability.csv`에서 다시 나오는가 (F26).

    F26까지 이 표는 손으로 적혀 있었고, 스윕이 base 실행보다 18시간 낡은 채로 그 밑에
    "스윕이 현행보다 낡았다"는 단서가 붙어 있었다. 스윕을 다시 돌리자(17초) 세 행이
    전부 틀렸다 — 0.3–0.8 대 0.2–0.8, 1.1–1.8 대 1.1–1.9, 3–9 대 2.0–9.2. 곁가지를
    다시 돌릴 때마다 손으로 고쳐야 하는 표는 생성기의 것이다.
    """
    import pandas as pd

    p = ROOT / "docs" / "seed_stability.csv"
    cur_p = ROOT / "out" / "e5" / "metrics_company.csv"
    if not (p.exists() and cur_p.exists()):
        pytest.skip("시드 스윕 또는 파이프라인 미실행")
    guide = GUIDE.read_text(encoding="utf-8")
    d = pd.read_csv(p)

    for label, col in [("② P50 / abatement cost", "cost_per_tco2_thkrw"),
                       ("③ TCaR", "tcar_bnkrw"),
                       ("⑤ Flexibility", "flex_value_bnkrw")]:
        g = d.groupby("company_id")[col].agg(
            lambda x: 100 * x.std(ddof=1) / abs(x.mean()))
        assert f"| {label} | {g.min():.1f}–{g.max():.1f}% |" in guide, (
            f"§6.1의 {label} 변동계수가 seed_stability.csv에서 다시 센 값과 다르다")
    # 신선도 판정 자체는 test_seed_sweep_staleness_is_described_as_it_is가 본다.


def test_band_vs_convention_numbers_come_from_the_band_comparison():
    """§4.5의 밴드-대-규약 문장이 `out/g2`에서 나오는가 (F26).

    F26까지 이 문장은 손으로 적혀 있었고, NSC의 규약 기준 파라미터 몫을 23%로 적고
    있었다 — `out/g2/f3_compare.csv`는 21.4%다. 곁가지를 다시 돌릴 때마다 손으로 따라
    고쳐야 하는 수치는 생성기의 것이다. `tech.capex` 승수는 밴드가 붙은 기술 행이 둘이라
    그 **포락선**(min low, max high)이 주장이고, 마지막 행이 아니다.
    """
    import pandas as pd

    b, f = ROOT / "out" / "g2" / "bands.csv", ROOT / "out" / "g2" / "f3_compare.csv"
    if not (b.exists() and f.exists()):
        pytest.skip("out/g2 없음")
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_tech_guide import COMPANY_NAME

    guide = GUIDE.read_text(encoding="utf-8")
    bd, fc = pd.read_csv(b), pd.read_csv(f)
    d = fc[fc.width == 0.15].set_index("company_id")

    cap = bd[bd.field == "capex_unit"]
    assert f"`tech.capex` at [{cap.mult_low.min():.2f}, {cap.mult_high.max():.2f}]×" in guide, (
        "§4.5의 tech.capex 승수 구간이 bands.csv의 포락선과 다르다")
    for co in ("POSCO", "NSC"):
        if co not in d.index:
            continue
        assert (f"{d.loc[co, 'param_share_pct_conv']:.0f}% to "
                f"{d.loc[co, 'param_share_pct_band']:.0f}% "
                f"({COMPANY_NAME[co]})") in guide, (
            f"§4.5의 {co} 파라미터 몫이 f3_compare.csv에서 다시 읽은 값과 다르다")

    # 밴드 치환이 아무것도 안 움직일 때, 그것을 "규약은 무해하다"로 읽히게 두지 않는가.
    # 2026-08-12에 실제로 그렇게 됐다: 민감도 화면을 다시 돌리자 `tech.capex`가 추첨
    # 상위 10에서 13위로 밀려났고, 밴드가 넓은 유일한 파라미터가 검정에서 빠졌다.
    worst = max(abs(d.param_share_pct_band - d.param_share_pct_conv))
    dec = ROOT / "out" / "uncertainty" / "decomposition_bands.csv"
    rk = ROOT / "out" / "sensitivity" / "ranking.csv"
    if worst >= 0.5 or not (dec.exists() and rk.exists()):
        return
    dc = pd.read_csv(dec).iloc[0]
    assert "params" in dc.index, (
        "decomposition_bands.csv가 추첨 파라미터 목록을 남기지 않는다 — "
        "밴드 비교가 0인 이유를 가이드가 출처 있게 말할 수 없다")
    drawn = str(dc.params).split("|")
    assert "**That is not evidence that the convention is harmless.**" in guide, (
        "§4.5가 0을 규약의 무해함으로 읽히게 둔다")
    if "tech.capex" not in drawn:
        r = pd.read_csv(rk).reset_index(drop=True)
        rank = list(r.base_param).index("tech.capex") + 1
        assert f"it ranks {rank} of {len(r)} in the screen" in guide, (
            f"§4.5가 tech.capex의 화면 순위를 실제({rank}/{len(r)})와 다르게 적는다")


def test_availability_is_described_as_scenario_dependent_only_if_it_is():
    """§3.8 test 5가 "가용 연도는 시나리오마다 다르다"고 적고 있었다 (F29).

    C4의 식은 `max(D3.avail_year, 시나리오 가용연도)`이고 코드도 그렇게 계산한다.
    그러나 시나리오 항은 `out/e1/tech_availability.csv`에서 오고, D2b에는
    `tech_avail_*` 경로가 한 줄도 없어 그 파일은 헤더뿐이다 — 판정은 절대
    시나리오마다 갈리지 못한다. 가이드는 갈릴 수 있다고 적고 있었고, **같은 절의
    생성 블록은 "두 시나리오에서 판정이 동일하다"고 적고 있었다.** 한 절이 자기를
    부정했다.

    이 테스트는 양방향이다: 표가 비어 있으면 가이드가 그 사실을 말해야 하고,
    표가 채워지면 "never binds"라고 적힌 채로 남아 있으면 안 된다.
    """
    import pandas as pd

    d2b = pd.read_csv(ROOT / "data" / "prepared" / "D2b_scenario_prices.csv")
    avail = pd.read_csv(ROOT / "out" / "e1" / "tech_availability.csv")
    guide = GUIDE.read_text(encoding="utf-8")
    lines = guide.splitlines()
    i = next(n for n, ln in enumerate(lines) if ln.startswith("5. The technology is available"))
    test5 = " ".join(" ".join(lines[i:]).split()[:200])

    if len(avail):
        assert "never binds" not in guide and "it cannot, on this data" not in test5, (
            f"시나리오 가용성 표가 {len(avail)}행으로 채워졌는데 가이드는 여전히 "
            "그 항이 무의미하다고 적는다 — §3.8 test 5와 생성 블록을 다시 써라")
        return

    assert not any(v.startswith("tech_avail_") for v in d2b.variable), (
        "D2b에 tech_avail_* 경로가 생겼는데 E1의 표는 비어 있다 — E1을 다시 돌려라")
    assert "availability years are scenario-dependent" not in guide, (
        "가이드가 가용 연도를 시나리오 의존이라고 적는다 — "
        "out/e1/tech_availability.csv는 헤더뿐이라 그럴 수 없다")
    for var in sorted(d2b.variable.unique()):
        assert f"`{var}`" in test5, (
            f"§3.8 test 5가 D2b 변수 목록을 적으면서 {var}를 빠뜨린다")
    assert f"has {len(avail)} rows" in guide, (
        "생성 블록이 시나리오 가용성 표의 행 수를 세지 않는다 — "
        "판정이 시나리오마다 같은 *이유*가 출처 없이 남는다")

    # 그리고 그 사실이 실제로 코드에서 그렇게 쓰이는가: NSC 킴 commitment의 2030은
    # D3의 정적 avail_year이지 시나리오 값이 아니다.
    d3 = pd.read_csv(ROOT / "data" / "prepared" / "D3_tech_options.csv").set_index("tech_id")
    h2 = d3.loc["steel_h2dri"]
    assert f"an `avail_year` of {int(h2.avail_year)}" in guide, (
        f"§3.8이 steel_h2dri의 avail_year를 D3의 {int(h2.avail_year)}와 다르게 적는다")
    assert f"adopt {int(h2.avail_year)} (operational {int(h2.avail_year + h2.build_years)})" in guide, (
        "§3.8의 D7 표가 D3의 avail_year + build_years와 어긋난다")
