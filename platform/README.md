# TCaR transition-finance web platform

Production: https://tcar-transition-finance.vercel.app/

PLANiT's K-ETS Outlook design language, Next.js 16 / React 19 / Recharts, and the
existing Python FIN calculators. Next.js is patched to 16.3.4; the reference site
was inspected at 16.2.6. Only this folder is sent to Vercel.

## What runs

- Corporate research: 450 company-level contract candidates from the completed
  2026-09-05 research run; read-only snapshot, no remote corporate MILP rerun.
- Joint prices / partial operating costs: original `ncc_joint_control.evaluate`.
- NCC capital and operating cash: original `ncc_cash_workbook_control.evaluate`.
- Timing qualification / costs / frontier: original `timing_workbook_control.evaluate`.
- 14 public dataframes, searchable and downloadable, with provenance and scope.

The three reference models preserve separate scopes, defaults, currency years,
seeds and risk levels. Missing/infeasible costs are not converted to zero.

## Rebuild data and engine (repository root)

```sh
.venv/bin/python scripts/build_web_platform.py
.venv/bin/python scripts/build_web_defaults.py
```

The explicit allowlist never copies raw/private PDFs, facility inputs, workbooks,
or run folders. Company results are checked against their historical run's output
hashes. Facility D1/D7 rows are aggregated before publication. `engine/` is generated;
edit the originals under `src/cap` / `scripts`, then rebuild. Each execution checks
the byte-identical generated engine and selected source files.

## Local development

```sh
# From repository root
.venv/bin/python platform/api/simulate.py
# In another terminal, from platform/
npm install
npm run dev -- --port 3000
```

The development server proxies `/api/*` to port 8532. Vercel serves the Python
function at `/api/simulate` directly. Public production data use no external API
credentials. The API accepts at most 10,000 paths and 16 KB per request; individual
instances serialize their heavy calculation work. This is an alpha research tool,
not a calibrated investment advice or corporate underwriting product.

## Verify and deploy

```sh
# Repository root
.venv/bin/pytest platform/tests -q
# platform/
npm run build
vercel --prod
```

The 23 contract tests cover exact original FIN parity, fractional-tail statistics,
infeasibility, zero production, malformed input, seed reproducibility, histogram
mass, snapshot identities, public-file hashes and absence of private inputs.

The page feature-detects optional WebMCP and exposes the same simulator action.
No supported WebMCP validation context was available during initial delivery;
the optional integration is not claimed as verified. No browser UI test was
requested; validation uses the production compiler and actual local/deployed API.
