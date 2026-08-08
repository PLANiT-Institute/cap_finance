# CAP 보고서 정적 배포

`web/index.html` = 최신 진단 보고서 (scripts/build_report.py 산출).
갱신: `.venv/bin/python scripts/build_report.py web/index.html` 후 커밋·푸쉬 → Vercel 자동 재배포.

주의: 보고서 §4 시설 단위 표는 설계서 §8-2 비공개 원칙 대상 — 외부 공유 전
Vercel Deployment Protection(비밀번호/SSO) 활성화 권장.
