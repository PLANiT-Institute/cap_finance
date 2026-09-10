"""Extract audited native-currency facts; do not overwrite legacy D6 inputs.

Raw public source copies and their SHA256 are registered in data_source_access_audit.
An observation records its exact earnings definition and reporting boundary.
EBITDA proxies are named explicitly and do not become issuer-reported EBITDA.
"""
from __future__ import annotations

import csv
from functools import lru_cache
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/research_cycles/2026-09-05"
SOURCES = {r["name"]: r for r in json.loads((AUDIT / "data_source_access_audit.json").read_text())
           if r["status"] == "downloaded"}
ROWS = []


class TableRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cell = self.row = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr": self.row = []
        if tag in ("td", "th"): self.cell = []

    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            if self.row is not None: self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def source_bytes(name):
    source = SOURCES[name]
    value = (ROOT / source["local_path"]).read_bytes()
    assert hashlib.sha256(value).hexdigest() == source["sha256"], name
    return value


def html_rows(name):
    parser = TableRows()
    # POSCO serves a few non-UTF8 decorative characters despite its UTF-8 meta.
    # Reject replacement characters in every extracted numeric cell below.
    parser.feed(source_bytes(name).decode("utf-8", errors="replace"))
    return parser.rows


@lru_cache(maxsize=8)
def pdf_text(name):
    source_bytes(name)
    path = ROOT / SOURCES[name]["local_path"]
    return subprocess.check_output(["pdftotext", "-layout", str(path), "-"]).decode("utf-8")


def number(cell):
    assert "\ufffd" not in cell, cell
    return float(cell.replace(",", "").replace("▲", "-"))


def add(company, year, metric, value, filename, locator, label, notes="", derivation=""):
    japan = company in ("NSC", "MCI")
    ROWS.append(dict(company_id=company, fiscal_year=year,
        fiscal_period_end=f"{year+1}-03-31" if japan else f"{year}-12-31",
        metric=metric, value_bn_native=value, currency="JPY" if japan else "KRW",
        price_basis="nominal_fiscal_year", reporting_scope="separate_operating_company" if company=="POSCO" else "consolidated_group",
        source_name=filename, source_url=SOURCES[filename]["url"], source_locator=locator,
        source_label=label, source_sha256=SOURCES[filename]["sha256"],
        accessed_at_utc=SOURCES[filename]["accessed_at_utc"],
        derivation=derivation, notes=notes))


def html_series(company, filename, lookup, mapping, years, positions, notes=""):
    rows = html_rows(filename)
    for label, metric in mapping.items():
        row = next(r for r in rows if any(label==v or (lookup=="contains" and label in v) for v in r[:2]))
        for year, pos in zip(years, positions):
            add(company,year,metric,number(row[pos]),filename,
                f"annual table; {year} column",label,notes)


def pdf_pair(company, filename, page, label, metric, divisor=1., notes=""):
    source_bytes(filename)
    txt = pdf_text(filename)
    page_text = txt.split("\f")[page-1]
    label = label.strip()
    matches = [line.strip() for line in page_text.splitlines()
               if re.match(re.escape(label)+r"\s{2,}", line.strip())]
    assert len(matches)==1, (filename,page,label,matches)
    values = re.findall(r"(?<![A-Za-z])[-(]?\d[\d,]*(?:\.\d+)?\)?",matches[0][len(label):])
    assert len(values)>=2,(label,values)
    for year, raw in zip((2023,2024),values[:2]):
        value = float(raw.replace(",", "").replace("(","-").replace(")",""))/divisor
        add(company,year,metric,value,filename,f"PDF page {page}; FY{year} column",label,notes)


def main():
    html_series("POSCO","posco_income.html","exact",
                {"Revenue":"revenue","Operating profit":"operating_profit","EBITDA":"reported_ebitda"},
                [2023,2024,2025],[4,5,6],"2022 spin-off transition year excluded from this verified window")
    html_series("POSCO","posco_balance.html","exact",{"Cash and cash equivalents":"cash"},
                [2023,2024,2025],[3,4,5])
    html_series("POSCO","posco_balance.html","contains",{"Long-term and short-term borrowings":"interest_bearing_debt"},
                [2023,2024,2025],[3,4,5])
    html_series("POSCO","posco_balance.html","exact",{"Net debt":"reported_net_debt"},
                [2023,2024,2025],[2,3,4],"Rounded source values; do not force exact borrowings-minus-cash equality")
    html_series("LOTTE","lotte_financials.html","exact",{"매출액":"revenue","영업이익":"operating_profit"},
                [2023,2024,2025],[1,2,3],"Annual table as of 2026-05-15; vintage differs from earlier releases; EBITDA not supplied here")
    for label, metric in [("Revenue","revenue"),("Operating profit","operating_profit")]:
        pdf_pair("NSC","nippon_fy2024.pdf",17,label,metric,1000.)
    pdf_pair("NSC","nippon_fy2024.pdf",20,"Depreciation and amortization","depreciation_amortization",1000.)
    pdf_pair("NSC","nippon_fy2024.pdf",15,"Cash and cash equivalents","cash",1000.)
    # Table dates, unlike the flows above, identify fiscal year-end balances.
    for label,metric in [("Sales revenue","revenue"),("Operating income before special items","operating_profit_before_special_items"),("Operating income ","operating_profit")]:
        pdf_pair("MCI","mitsui_fy2024.pdf",1,label,metric)
    for label,metric in [("Cash and cash equivalents at the end of period","cash"),
                         ("Depreciation & amortization","depreciation_amortization"),
                         ("Capital expenditures","capital_expenditure"),
                         ("Interest-bearing debt","interest_bearing_debt")]:
        pdf_pair("MCI","mitsui_fy2024.pdf",2,label,metric)
    for co in ("NSC","MCI"):
        for year in (2023,2024):
            get = lambda metric: next(r for r in ROWS if r["company_id"]==co and r["fiscal_year"]==year and r["metric"]==metric)
            op, da = get("operating_profit"), get("depreciation_amortization")
            add(co,year,"ebitda_proxy_op_plus_da",op["value_bn_native"]+da["value_bn_native"],
                op["source_name"],op["source_locator"]+" + "+da["source_locator"],
                "Derived operating profit plus D&A","Not issuer-reported EBITDA; no special-item adjustment",
                "operating_profit + depreciation_amortization")
    assert len({(r['company_id'],r['fiscal_year'],r['metric']) for r in ROWS})==len(ROWS)
    target=AUDIT/"verified_financial_observations.csv"
    with target.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(ROWS[0]));w.writeheader();w.writerows(ROWS)
    manifest=dict(observations=len(ROWS),native_currency=True,fx_conversion_applied=False,
        legacy_inputs_overwritten=False,coverage="POSCO/LOTTE FY2023-25; NSC/MCI FY2023-24 selected metrics only",
        limitation="Issuer summaries and flash reports; not a complete audit of all historical D6 rows or an affordability certification",
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),target)})
    (AUDIT/"verified_financial_observations_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
