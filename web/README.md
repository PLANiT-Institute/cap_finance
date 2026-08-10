# CAP 정적 배포

`web/`의 모든 페이지는 `scripts/build_site.py` 하나가 만든다 — 랜딩(`index.html`),
진단 보고서(`report.html`), 기술 가이드(`guide.html`, `docs/TECHNICAL_GUIDE.md`를 렌더),
증거·시나리오·메모·변경보고, 그리고 EFF 대시보드 사본.
갱신: `.venv/bin/python scripts/build_site.py` 후 커밋·푸쉬 → Vercel 자동 재배포.

주의: 보고서 §4 시설 단위 표는 설계서 §8-2 비공개 원칙 대상 — 외부 공유 전
Vercel Deployment Protection(비밀번호/SSO) 활성화 권장.
