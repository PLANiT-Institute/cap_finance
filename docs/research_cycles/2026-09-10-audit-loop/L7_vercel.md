# L7 · Vercel 완성 (2026-09-11 10:38 KST)

관점: 웹 도구가 정본(v2.3)을 정확히 보여 주고, 실시간 참조 API가 살아 있으며, 그 두 사실을 기계가 검사하게 한다.

## 운영 API

`GET /api/simulate`는 이 회차에도 500(정적 `/500` 페이지)이다. 사용자 재배포는 아직 없다. 원인은 로그 없이 확정할 수 없지만, Vercel 문서(2026-08-12 판)와 대조하면 설정 한 줄이 의심된다. `/api` 파일 기반 파이썬 함수의 `functions` 항목에는 `maxDuration`·`includeFiles`·`excludeFiles`만 쓰고 `runtime` 키는 커뮤니티 런타임용인데, 기존 `vercel.json`은 `"runtime": "@vercel/python@4.3.0"`을 지정하고 있었다. 이를 제거하고 글로브를 `api/**/*.py`로, `excludeFiles`에 tests·캐시를 넣었으며, `.python-version`으로 3.12(기본값)를 고정했다. requirements의 pandas 3.0.5·numpy 2.5.1·PyYAML 6.0.3은 PyPI에 cp312 manylinux x86_64 휠이 있다(확인). 기본값 JSON은 Python 3.14.6로 생성됐고 Vercel은 3.14도 지원하지만, 휠 안정성 기준으로 3.12를 택했다. 확인은 재배포 후 `python scripts/smoke_deploy.py`로 한다(엔진 해시가 catalog.json과 같은 JSON을 받으면 0, 아니면 1).

## UI 문구

α 표기를 "95.00%"에서 "0.95"로, 데이터 탐색기의 `value`/`unit` 라벨을 "원문 값/원문 단위"에서 "값(원문·환산·EST 혼재; source_id로 구분)/단위(상태 열 참조)"로 바꿨다 — D2b는 환산·EST가 섞여 있어 "원문"이 틀린 말이었다. joint 모형의 경로 수 힌트 "2–50,000"을 웹 API 상한 10,000에 맞췄다(로컬 실행 상한 50,000은 병기). 섹션 번호를 내비게이션 순서(연구 01 → 데이터 02 → 모형 03 → 참조 실험 04)에 맞췄다. D4의 WB_CMO_*·KRX 행과 D5의 free_allocation_rule 행은 빌드 스크립트가 v2 데이터 폴더에서 복사하므로 데이터 탐색기에 그대로 나온다(L2·L3 빌드에서 확인).

## 검사

`platform/tests/test_simulator.py`에 네 계약을 더했다. 모든 판본에서 표본 지배 후보가 경계 플래그를 가지면 실패(B3 회귀), 공개 CSV와 정본 JSON의 후보 집합 일치, catalog 힌트 ≤ API 상한, 판본별 메타데이터에 헤지 기준·경계 축·탄소 포함·결과 해시가 있을 것. `scripts/smoke_deploy.py`는 배포 후 실행하는 1분짜리 검사다.

## 없어서 못 한 것

배포 자체는 Mac에서 `cd platform && vercel --prod`로 해야 한다(VM·컨테이너에 인증 없음). 재배포 후에도 500이면 Vercel 대시보드의 함수 로그가 필요하다. 브라우저 렌더링 테스트는 없다(tsc만). 배출 방향 확장 결과는 L8에서 합친다.
