"""Shared page chrome for the generated HTML pages (evidence, scenarios).

One copy of the design tokens and base elements. build_report.py keeps its own
richer stylesheet — it is the primary artefact and not worth the regression risk.
"""

DOCTYPE = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>')

CSS = r""":root{--surface:#FBFBF9;--panel:#fff;--panel2:#F4F4F0;--ink:#191C24;--ink2:#565B66;--ink3:#8B909C;
  --line:#E4E4DE;--line2:#EEEEE8;--accent:#2a78d6;--warn-bg:#FBF3E2;--warn-line:#E5C878;--danger:#e34948}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){
  --surface:#15171C;--panel:#1C1F26;--panel2:#22252D;--ink:#EDEEF0;--ink2:#A8ADB8;--ink3:#747A87;
  --line:#2E323B;--line2:#262A32;--accent:#3987e5;--warn-bg:#2A2517;--warn-line:#6B5A2A;--danger:#e66767}}
:root[data-theme="dark"]{--surface:#15171C;--panel:#1C1F26;--panel2:#22252D;--ink:#EDEEF0;
  --ink2:#A8ADB8;--ink3:#747A87;--line:#2E323B;--line2:#262A32;--accent:#3987e5;
  --warn-bg:#2A2517;--warn-line:#6B5A2A;--danger:#e66767}
*{box-sizing:border-box}
body{margin:0;background:var(--surface);color:var(--ink);line-height:1.62;font-size:15px;
  font-family:"Apple SD Gothic Neo",Pretendard,"Noto Sans KR",system-ui,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:56px 30px 90px}
.eyebrow{font-size:11.5px;letter-spacing:.15em;color:var(--accent);font-weight:700;text-transform:uppercase}
h1{font-size:31px;line-height:1.22;margin:8px 0 8px;font-weight:800;letter-spacing:-.015em;text-wrap:balance}
.lede{color:var(--ink2);max-width:74ch;margin:0;font-size:14.5px}
h2{font-size:19px;margin:0 0 4px;font-weight:760}
section{margin-top:56px}
.secno{color:var(--ink3);font-weight:600;margin-right:8px}
.secnote{color:var(--ink2);font-size:13.5px;margin:0 0 20px;max-width:80ch}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
svg{display:block;width:100%;height:auto}
.axis{font-size:10.5px;fill:var(--ink3)}
.axislab{font-size:11px;fill:var(--ink2);font-weight:600}
.gridline{stroke:var(--line2);stroke-width:1}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--ink2);margin:10px 0 16px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:11px;height:11px;border-radius:3px;display:inline-block}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:13.5px}
th{font-size:11.5px;color:var(--ink2);font-weight:650;text-align:right;padding:9px 10px;border-bottom:1.5px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
td{padding:7.5px 10px;border-bottom:1px solid var(--line2);text-align:right;white-space:nowrap}
.tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel);padding:8px 12px}
.chip{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:999px;font-weight:700;color:#fff}
.callout{background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:12px;padding:16px 20px;font-size:13.5px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-top:22px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px 17px}
.kpi .l{font-size:12px;color:var(--ink2);font-weight:600}
.kpi .v{font-size:25px;font-weight:800;margin-top:3px;font-variant-numeric:tabular-nums}
.kpi .d{font-size:12px;color:var(--ink3);margin-top:3px}
.tip{position:fixed;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:9px;
  padding:8px 11px;font-size:12px;box-shadow:0 6px 18px rgba(0,0,0,.14);opacity:0;transition:opacity .1s;z-index:9;max-width:290px}
ul.tight{margin:8px 0 0;padding-left:18px} ul.tight li{margin:5px 0;font-size:13.5px;color:var(--ink2)}
ul.tight li b{color:var(--ink)}
.footer{margin-top:64px;padding-top:18px;border-top:1px solid var(--line);font-size:12.5px;color:var(--ink3)}
a{color:var(--accent)}
"""
