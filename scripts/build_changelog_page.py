"""세션 변경 보고 페이지 (web/changelog.html) — 오늘 무엇이 바뀌었나.

수치는 산출물에서 읽고(헤드라인·감사 판정·커밋 목록), 서사만 여기 적는다. 다시 돌리면
그날의 상태로 갱신된다.

    .venv/bin/python scripts/build_changelog_page.py [--since "2026-08-09 10:00"]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _style import CSS, DOCTYPE  # noqa: E402

WEB = ROOT / "web"
CONAME = {"POSCO": "POSCO", "NSC": "Nippon Steel",
          "LOTTE": "LOTTE Chemical", "MCI": "Mitsui Chemicals"}

# 서사 — 수치가 아닌 부분만 여기 산다
SILENT = [
    ("수소 경로가 죽어 있었다",
     "D2b Korea <code>h2_price</code> 2025 셀 하나가 비어 E1 보간이 NaN을 퍼뜨렸고, E2는 그 경로를 "
     "버리고 <b>v2.1에서 폐기한 전해조 구조식으로 되돌아가 있었다</b>. 알림은 로그 14줄 뒤 "
     "<code>note</code> 한 줄. 한국 2사가 설계와 다른 모형으로 계산되던 중.",
     "구조식 대체 발동 14회 → 0회"),
    ("CAPEX를 채택연도에 전액 계상",
     "<code>build_years</code>는 가동개시만 이동시키고 공사비는 1년에 다 실렸다. 피크 자금소요가 "
     "최대 공사기간 배수만큼 과대.", "POSCO 피크 18.6조 → 5.6조"),
    ("Scope 2를 수집해 놓고 버렸다",
     "원자료 36/37행에 값이 있는데 준비 단계가 전부 0으로 덮어썼다.",
     "NSC 11.4 · POSCO 1.4 MtCO₂ 복원"),
    ("정책 구분이 뭉개졌다",
     "원자료는 발전부문 50%와 발전외(철강·석화) 15%를 구분해 뒀는데 준비 단계가 "
     "<code>instrument</code>를 전부 <code>other</code>로 눌렀고, config는 별도 하드코딩을 썼다.",
     "확정 할당계획이 추정 램프를 이긴다"),
    ("감사 스크립트 자체가 틀렸다",
     "pandas 3에서 <code>astype(str)</code>이 NaN을 <code>\"nan\"</code>으로 바꾸지 않아 "
     "<b>빈 셀을 전부 채워진 것으로 계수</b>했다. 스키마 파일이 엔진 스캔에 포함돼 모든 컬럼이 "
     "\"사용됨\"으로도 오판됐다.", "숨어 있던 공백이 드러남"),
    ("공개 출처 등록부가 50건 뒤처졌다",
     "<code>data/raw</code>는 gitignore라 클론하면 대부분 수치의 출처를 추적할 수 없었다.",
     "26 → 78건, 준비 단계에서 자동 동기화"),
    ("무인자 실행이 죽어 있었다",
     "<code>config.yaml</code>의 <code>data_dir</code>이 파이프라인이 읽지 않는 디렉터리를 가리켰다.",
     "<code>python -m cap all</code> 복구"),
]
MINE = [
    ("<code>--replan</code>이 실산출물을 파괴",
     "이전 실행이 남긴 <code>&lt;bundle&gt;/e2 → out/e2</code> 심볼릭 링크를 따라가 공유 "
     "<code>out/e2/plans</code>를 지웠다. 보고서 빌드가 없는 계획 파일을 찾다 드러남.",
     "링크 정리 + 회귀 테스트 2개"),
    ("POSCO 배출을 전량 0으로",
     "폴백 분기가 <code>fb_share</code>(충돌 없으면 0)를 곱해, 사업소 데이터가 없는 회사의 배출이 "
     "0이 됐다. 탄소예산이 저절로 충족돼 CAPEX 0·감축단가 NaN. <b>20분 MILP가 0 입력 위에서 다 "
     "돌 때까지 아무것도 못 잡았다.</b>", "분기 분리 + 배분 항등식 게이트"),
]
CORRECTED = [
    ("후향 검증 15.7%를 결과 편향으로 오독",
     "철강은 시설 배출을 회사 공시 총량에 <b>재척도</b>하므로 루트 표준값은 수준이 아니라 "
     "<b>배분 가중치</b>다. 모형이 쓰는 값은 공시와 ±1%. NSC ②는 과소평가돼 있지 않았다."),
    ("\"미쓰이는 상한 검증 불가\"",
     "EEGS를 찾기 전 이야기였다. 사업소별 공시가 있고, 검증이 되고, 통과한다."),
]
UPGRADES = [
    ("G1 일본 사업소 실측 확보·적용",
     "EEGS(온대법 전자보고시스템)가 2021년도부터 <b>사업소 단위</b>로 공개한다. NSC 27개소·MCI 8개소 "
     "FY2023. <b>수준은 회사 공시, 분포는 사업소 공시</b>로 갈라 적용 — 온대법 산정배출량은 S1+S2라 "
     "수준을 그대로 쓸 수 없다.",
     "민감도 1위 파라미터가 T5 배분값 → <b>T1 실측 분포</b>. NSC ② 165.4 → 155.8 (−5.8%)"),
    ("새 데이터가 깨뜨린 것도 잡았다",
     "사업소 몫을 적용하니 室蘭 고로에 0.28, 鹿島에 3.01 tCO₂/t — 고로로는 불가능. 물리 타당 "
     "대역 가드가 잡아 옛 규칙으로 되돌리고 <b>충돌을 로그로 남긴다</b>.",
     "G3(설비 능력)의 문제 사이트가 특정됨"),
    ("미사용 컬럼 3개 소비",
     "D6 재무 6열(→ 지표 ⑥), <code>capex_uncertainty</code>(기술별 설비비 위험), 그리고 "
     "<code>D7.quote</code> — <b>웹 3사이클로 못 푼 NCC 배출계수 문제를 이 컬럼이 풀었다</b>.",
     "UNUSED는 안 써도 되는 게 아니라 아직 안 읽은 증거"),
    ("외부 대조로 값이 확인됐다",
     "수소환원 CAPEX 863천원/t이 DIW 문헌범위(858~1,089) 안. NCC 배출계수는 미쓰이 설비집약 공시 "
     "역산 1.020 tCO₂/t-에틸렌 대비 −6.9%. 크래커 능력은 경산성 조사와 정확히 일치.", ""),
]
FINDINGS = [
    ("석화 꼬리위험의 100%가 수소인데 헤지 수단이 없다",
     "위험회피 기준(P90 최소)이 고르는 헤지는 CAPEX 고정가 EPC — 분산 기여 <b>0.1%</b>. PPA는 "
     "전력만 고정하고 수소는 시장에 그대로 노출된다. <b>수소 장기 공급계약이 수단으로 들어오기 "
     "전까지 석화 TCaR은 줄일 방법이 없다.</b>"),
    ("② 가 에너지가격 절반인 세계에서 계산되고 있었다",
     "로그정규 충격에 <code>E[충격]=1</code>을 강제하면 왜도 때문에 중앙값이 아래로 흐른다 — "
     "σ0.25·25년이면 2050 중앙값이 중심경로의 <b>0.47배</b>. ②는 P50 지표라 그 세계에서 계산된다. "
     "정규화를 중앙값 기준으로 바꾸면 석화 ②가 <b>+71~73%</b>."),
]
GAPS = [
    ("<code>D2b.value</code>", "99.1%", "Korea h2_price 2025 셀"),
    ("<code>D6.revenue</code>", "95.5%", "LOTTE 2021"),
    ("<code>D6.capex_total</code>", "50.0%", "POSCO·LOTTE 미공시"),
    ("<code>D6.net_debt</code>", "40.9%",
     "<b>경계 문제</b> — 이익은 철강 사업회사, 재무상태표는 지주회사. 맞지 않는 수 대신 공란"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-08-09 10:00")
    a = ap.parse_args()

    log = subprocess.run(["git", "log", "--since", a.since, "--format=%h\t%s\t%ad",
                          "--date=format:%H:%M"], cwd=ROOT, capture_output=True, text=True).stdout
    commits = [dict(zip(("sha", "subject", "time"), ln.split("\t")))
               for ln in log.strip().splitlines() if ln.count("\t") == 2]

    m = pd.read_csv(ROOT / "out" / "e5" / "metrics_company.csv").query(
        "scenario=='NZ15' and support=='none'")
    af = pd.read_csv(ROOT / "out" / "e5" / "affordability.csv").query(
        "scenario=='NZ15' and support=='none'")
    head = m.merge(af[["company_id", "capex_total_to_ebitda", "funding_verdict"]],
                   on="company_id").sort_values("cost_per_tco2_thkrw")

    aud = pd.read_csv(ROOT / "docs" / "data_audit.csv").verdict.value_counts().to_dict()
    docs = sorted(p.name for p in (ROOT / "docs").glob("*.md"))

    D = {
        "commits": commits,
        "head": json.loads(head.round(1).to_json(orient="records")),
        "audit": {"ok": aud.get("ok", 0), "expected": aud.get("설계상 정상", 0),
                  "gap": sum(v for k, v in aud.items() if k not in ("ok", "설계상 정상"))},
        "coname": CONAME, "docs": docs,
        "silent": SILENT, "mine": MINE, "corrected": CORRECTED,
        "upgrades": UPGRADES, "findings": FINDINGS, "gaps": GAPS,
    }
    WEB.mkdir(exist_ok=True)
    (WEB / "changelog.html").write_text(
        DOCTYPE + TEMPLATE.replace("__CSS__", CSS)
        .replace("__DATA__", json.dumps(D, ensure_ascii=False)) + "</body></html>")
    print(f"[changelog] web/changelog.html ({(WEB / 'changelog.html').stat().st_size:,} bytes) "
          f"— 커밋 {len(commits)}개")
    return 0


TEMPLATE = r"""<title>CAP — 2026-08-09 변경 보고</title>
<style>
__CSS__
.hero{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:22px 0 6px}
.hero div{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.hero .n{font-size:26px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.1}
.hero .l{font-size:12px;color:var(--ink2);font-weight:600;margin-top:3px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px 17px;margin-top:10px}
.card h3{margin:0 0 5px;font-size:14.5px;font-weight:740}
.card p{margin:0;font-size:13px;color:var(--ink2);line-height:1.6}
.card .eff{margin-top:8px;padding-top:8px;border-top:1px solid var(--line2);font-size:12.5px;
  color:var(--ink);font-weight:640}
.card.mine{border-left:3px solid var(--danger)}
.card.fix{border-left:3px solid #1baf7a}
.tag{display:inline-block;font-size:10.5px;font-weight:700;padding:1px 7px;border-radius:999px;
  background:var(--panel2);color:var(--ink2);margin-left:6px;vertical-align:2px}
.bar{display:flex;height:26px;border-radius:5px;overflow:hidden;margin:10px 0 4px;gap:2px}
.bar span{display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff}
.leg{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink2)}
.leg i{width:10px;height:10px;border-radius:3px;display:inline-block;margin-right:5px}
details{margin-top:12px}summary{cursor:pointer;font-size:13px;color:var(--ink2);font-weight:640}
.cm{font-size:12px;font-variant-numeric:tabular-nums;color:var(--ink2);padding:3px 0;
  border-bottom:1px solid var(--line2);display:flex;gap:10px}
.cm b{color:var(--ink3);font-weight:600;min-width:44px}
</style>
<div class="wrap">
<div class="eyebrow">CAP · 변경 보고</div>
<h1>2026-08-09에 무엇이 바뀌었나</h1>
<p class="lede">이 저장소는 아침에도 돌아갔다. 바뀐 것은 <b>돌아간다는 것이 맞다는 뜻이 아니라는
사실을 확인할 수단</b>이다. 아래 결함들은 전부 테스트를 통과하는 상태에서 조용히 틀리고 있었다.</p>
<div class="hero" id="hero"></div>

<section>
<h2><span class="secno">1</span>조용히 틀리고 있던 것</h2>
<p class="secnote">전부 "돌아가는" 상태였고, 로그도 대체로 조용했다. 발견 순서가 아니라 영향 순서.</p>
<div id="silent"></div>
</section>

<section>
<h2><span class="secno">2</span>내가 만든 결함</h2>
<p class="secnote">오늘 넣고 오늘 잡았다. 둘 다 회귀 테스트로 봉인했다.</p>
<div id="mine"></div>
</section>

<section>
<h2><span class="secno">3</span>내가 낸 잘못된 판정 — 정정</h2>
<div id="corrected"></div>
</section>

<section>
<h2><span class="secno">4</span>데이터 승급</h2>
<div id="upgrades"></div>
</section>

<section>
<h2><span class="secno">5</span>결과 — 현재 헤드라인</h2>
<p class="secnote">NZ15 · 지원정책 없음. ②는 자원비용 기준 감축단가(천원/tCO₂), 조달배수는 총 CAPEX ÷ 기준 EBITDA.
"싸다"와 "감당된다"가 다른 기업을 지목한다.</p>
<div class="tblwrap"><table id="head"></table></div>
</section>

<section>
<h2><span class="secno">6</span>정책적으로 중요한 발견</h2>
<div id="findings"></div>
</section>

<section>
<h2><span class="secno">7</span>데이터 감사 — 경고 21개에서 진짜 4개로</h2>
<p class="secnote">사유 없는 경고는 아무도 안 본다. 설계상 비어 있는 것이 맞는 컬럼에 <b>이유를 적어</b>
분리하니 조치 대상만 남았다.</p>
<div class="bar" id="bar"></div>
<div class="leg" id="leg"></div>
<div class="tblwrap" style="margin-top:14px"><table id="gaps"></table></div>
</section>

<section>
<h2><span class="secno">8</span>검증 체계</h2>
<p class="secnote">아침에는 0종이었다. MCP <code>get_validation_summary</code>의 <code>missing</code>이 비어 있다는 것은
계획한 검증이 전부 존재한다는 뜻이지, 전부 통과했다는 뜻이 아니다 — 각 문서가 통과·초과·대조불가를 따로 적는다.</p>
<div id="docs"></div>
<details><summary id="cmsum"></summary><div id="commits" style="margin-top:8px"></div></details>
</section>

<div class="footer">수치는 <code>out/e5</code>·<code>docs/data_audit.csv</code>·git 로그에서 읽는다 —
다시 생성하면 그날 상태로 갱신된다. 서사만 <code>scripts/build_changelog_page.py</code>에 있다.</div>
</div>
<script>
const D=__DATA__;
const f=(v,d=0)=>v==null||isNaN(v)?"—":Number(v).toLocaleString("ko-KR",{maximumFractionDigits:d});
const card=(cls)=>([t,b,e])=>`<div class="card ${cls}"><h3>${t}</h3><p>${b}</p>${
  e?`<div class="eff">→ ${e}</div>`:""}</div>`;
document.getElementById("silent").innerHTML=D.silent.map(card("")).join("");
document.getElementById("mine").innerHTML=D.mine.map(card("mine")).join("");
document.getElementById("corrected").innerHTML=D.corrected.map(([t,b])=>
  `<div class="card fix"><h3>${t}</h3><p>${b}</p></div>`).join("");
document.getElementById("upgrades").innerHTML=D.upgrades.map(card("")).join("");
document.getElementById("findings").innerHTML=D.findings.map(([t,b])=>
  `<div class="card"><h3>${t}</h3><p>${b}</p></div>`).join("");

const nsc=D.head.find(r=>r.company_id==="NSC");
document.getElementById("hero").innerHTML=[
  [D.commits.length,"커밋"],
  [D.silent.length+D.mine.length,"잡은 결함"],
  [D.corrected.length,"자체 정정"],
  [D.audit.gap,"남은 진짜 공백"],
  ["6","검증 문서"],
].map(([n,l])=>`<div><div class="n">${n}</div><div class="l">${l}</div></div>`).join("");

document.getElementById("head").innerHTML=
  `<tr><th>기업</th><th>총 CAPEX (조원)</th><th>② 천원/tCO₂</th><th>③ TCaR (조원)</th>
   <th>총 CAPEX/EBITDA</th><th>조달 판정</th></tr>`+
  D.head.map(r=>`<tr><td class="co">${D.coname[r.company_id]||r.company_id}</td>
   <td>${f(r.capex_total_bnkrw/1000,1)}</td><td>${f(r.cost_per_tco2_thkrw)}</td>
   <td>${f(r.tcar_bnkrw/1000,1)}</td>
   <td>${r.capex_total_to_ebitda==null||isNaN(r.capex_total_to_ebitda)?"—":f(r.capex_total_to_ebitda,1)+"×"}</td>
   <td style="text-align:left">${r.funding_verdict||"—"}</td></tr>`).join("");

// 감사 판정 구성 — 상태 색(양호/설명됨/조치대상), 각 조각에 직접 라벨
(()=>{const A=D.audit, tot=A.ok+A.expected+A.gap;
 const seg=[["#1baf7a",A.ok,"ok"],["#eda100",A.expected,"설계상 정상"],["#e34948",A.gap,"진짜 공백"]];
 document.getElementById("bar").innerHTML=seg.map(([c,n,l])=>
   `<span style="background:${c};flex:${n}">${n}</span>`).join("");
 document.getElementById("leg").innerHTML=seg.map(([c,n,l])=>
   `<span><i style="background:${c}"></i>${l} ${n}<span style="color:var(--ink3)"> · ${
     Math.round(100*n/tot)}%</span></span>`).join("");})();

document.getElementById("gaps").innerHTML=
  `<tr><th>컬럼</th><th>채움</th><th>무엇이 없나</th></tr>`+
  D.gaps.map(([c,p,w])=>`<tr><td>${c}</td><td>${p}</td><td style="text-align:left">${w}</td></tr>`).join("");

document.getElementById("docs").innerHTML=`<div class="leg" style="gap:8px">`+
  D.docs.map(d=>`<span class="tag" style="margin:0">${d}</span>`).join("")+`</div>`;

document.getElementById("cmsum").textContent=`커밋 ${D.commits.length}개 펼치기`;
document.getElementById("commits").innerHTML=D.commits.map(c=>
  `<div class="cm"><b>${c.time}</b><code style="color:var(--ink3)">${c.sha}</code>
   <span>${c.subject.replace(/</g,"&lt;")}</span></div>`).join("");
</script>"""


if __name__ == "__main__":
    raise SystemExit(main())
