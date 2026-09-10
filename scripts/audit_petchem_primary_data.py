"""Extract selected primary petrochemical facts without treating plant totals as cracker data."""
from pathlib import Path
import csv
import hashlib
import html
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'tmp/pdfs/tcar_petchem_sources'
OUT = ROOT / 'docs/research_cycles/2026-09-05/petchem_data'


def clean(text):
    text = re.sub(r'<(?:script|style)\b[^>]*>.*?</(?:script|style)>', '', text, flags=re.S | re.I)
    return ' '.join(html.unescape(re.sub('<[^>]+>', ' ', text)).split())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    access = json.loads((RAW / 'access_preparation.json').read_text())
    sources = {Path(r['file']).name: r for r in access if r['status'] == 'downloaded'}
    facts = []

    def body(file, page=None):
        p = RAW / file
        assert hashlib.sha256(p.read_bytes()).hexdigest() == sources[file]['sha256']
        if page is not None:
            return subprocess.check_output(['/opt/homebrew/bin/pdftotext', '-f', str(page), '-l', str(page),
                                             '-layout', str(p), '-'], text=True)
        return clean(p.read_text())

    def add(file, location, company, boundary, metric, year, value, unit, note=''):
        facts.append(dict(observation_id=f'PC{len(facts)+1:03}', company_id=company,
                          boundary=boundary, metric=metric, year=year, value=value, unit=unit,
                          source_url=sources[file]['url'], source_sha256=sources[file]['sha256'],
                          source_file=file, source_location=location, interpretation_limit=note))

    file = 'lotte_esg_2025.pdf'
    text = body(file, 117)
    assert re.search(r'2025\s+2024\s+2023', text)
    blocks = {
        'scope1': text.split('직접 온실가스(Scope 1) 배출량 - 사업장별', 1)[1].split('직접 온실가스(Scope 1) 배출량 - 고정연소별', 1)[0],
        'scope2': text.split('간접 온실가스(Scope 2) 배출량', 1)[1].split('직접/간접 온실가스', 1)[0],
    }
    sites = {'여수공장(기초)': 'LOTTE_YEO1_TOTAL', '여수공장(첨단)': 'LOTTE_YEO2_TOTAL',
             '대산공장': 'LOTTE_DAE_TOTAL', '울산공장': 'LOTTE_ULS_TOTAL', '기타': 'LOTTE_OTH_TOTAL', '합계': 'LOTTE_TOTAL'}
    for metric, block in blocks.items():
        for label, boundary in sites.items():
            lines = [s for s in block.splitlines() if label in s and 'tCO2eq' in s]
            assert len(lines) == 1, (metric, label, lines)
            values = re.findall(r'\d[\d,]*', lines[0].split('tCO2eq', 1)[1])[:3]
            assert len(values) == 3
            for year, value in zip([2025, 2024, 2023], values):
                add(file, 'PDF/printed p117; site GHG table', 'LOTTE', boundary, metric, year,
                    int(value.replace(',', '')), 'tCO2e',
                    'Whole site/company, not cracker;2023/24 final submissions;2025 first submission;rounded printed cells')
    total_line = next(s for s in text.splitlines() if '총합계' in s and 'tCO2eq' in s)
    for year, value in zip([2025, 2024, 2023], re.findall(r'\d[\d,]*', total_line.split('tCO2eq')[1])[:3]):
        add(file, 'PDF/printed p117; total GHG', 'LOTTE', 'LOTTE_TOTAL', 'reported_scope1_scope2_total', year,
            int(value.replace(',', '')), 'tCO2e', 'Sum of truncated site totals; do not force equality with rounded Scope1+2')
    assurance = body(file, 145)
    for metric, value in [('scope1_assurance', 3594672.358), ('scope2_assurance', 1776106.527)]:
        assert f'{value:,.3f}' in assurance
        add(file, 'PDF/printed p145; KFQ assurance 2026-05-29', 'LOTTE', 'operational_control_except_advanced_Daegu',
            metric, 2025, value, 'tCO2e', 'Different precision from p117 rounded cells; annual final certification may differ')
    target = body(file, 13)
    assert '2018년 배출량 대비 ▲20%' in target and '국내 Scope 1&2 기준' in target
    add(file, 'PDF/printed p13 footnotes1,2', 'LOTTE', 'domestic_scope1_scope2', 'reduction_target_pct', 2030, 20, '%',
        'Base year2018; replaces current-use interpretation of 2022 announcement (25% vs2019), not historical quote')
    add(file, 'PDF/printed p13 footnote2', 'LOTTE', 'domestic_scope1_scope2', 'target_base_year', 2030, 2018, 'year')

    file = 'mci_esg_environment.html';body(file)
    html_rows = re.findall(r'<tr\b[^>]*>(.*?)</tr>', (RAW / file).read_text(), flags=re.S | re.I)
    current = None
    boundaries = {'Mitsui Chemicals, Inc.': 'MITSUI_TOTAL', 'Domestic subsidiaries and affiliates': 'domestic_subsidiaries_affiliates',
                  'Overseas subsidiaries and affiliates': 'overseas_subsidiaries_affiliates', 'Mitsui Chemicals Group': 'MITSUI_GROUP'}
    for row in html_rows:
        row = re.sub(r'<sup\b[^>]*>.*?</sup>', '', row, flags=re.S | re.I)
        cells = [clean(s).replace('★', '') for s in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', row, flags=re.S | re.I)]
        joined = ' '.join(cells)
        if 'GHG emissions (Scope1)' in joined:
            current = 'scope1'
        elif 'GHG emissions (Scope2)' in joined:
            current = 'scope2'
        elif 'GHG emissions(Scopes 1 and 2)' in joined:
            current = None
        if current:
            match = [label for label in boundaries if label in cells]
            if not match:
                continue
            vals = cells[-4:]
            assert all(re.fullmatch(r'[\d,]+', v) for v in vals), vals
            for year, value in zip([2021, 2022, 2023, 2024], vals):
                add(file, 'GHG table; FY2021–FY2024', 'MCI', boundaries[match[0]], current, year,
                    int(value.replace(',', '')) * 1000, 'tCO2e', 'Original unit thousand tonnes; fiscal year ends following March; scope follows issuer methodology')
    assert len([r for r in facts if r['source_file'] == file]) == 32

    file = 'jpca_capacity_2024.html';text = body(file)
    for label, boundary, value in [('大阪石油化学', 'MCI_OSK_CR', 455), ('三井化学', 'MCI_ICH_CR', 553)]:
        assert re.search(re.escape(label) + r'\s+' + str(value) + r'\b', text)
        add(file, 'Ethylene year-end2024 capacity table and footnotes1,2', 'MCI', boundary, 'ethylene_capacity', 2024,
            value * 1000, 't_ethylene_per_year', 'Annual capacity with maintenance turnaround; not actual output or no-turnaround maximum')

    file = 'mci_osaka_cn_2023.pdf';text = body(file, 1) + body(file, 2)
    for metric, value, needle in [('planned_furnace_ammonia_reduction', 700000, '70 万㌧'), ('site_scope1_scope2_approx', 1600000, '160 万㌧')]:
        assert needle in text
        add(file, 'PDFpp1–2; Osaka CN concept and site definition', 'MCI', 'Osaka_entire_works', metric, 2023,
            value, 'tCO2_per_year', 'Ammonia fuel, not purchased hydrogen; projected full-furnace conversion around2030, not achieved reduction')

    # Exact selected facts; totals and ceilings retain the announcement perimeter.
    projects = [
        ('mci_west_japan_2026.html','MCI','three_company_multi_site_project','gross_project_investment',2026,21.2,'bn_JPY','21.2 billion','Structural changes plus initial Revolefin facility; not Osaka ammonia-only capex'),
        ('mci_west_japan_2026.html','MCI','three_company_multi_site_project','subsidy_application_ceiling',2026,10.4,'bn_JPY','10.4 billion','Maximum requested subsidy; not cash received or certain net investment'),
        ('mci_west_japan_2026.html','MCI','Osaka_and_Mizushima_structural_transition','planned_scope1_scope2_reduction',2030,506000,'tCO2_per_year','506,000','Relative to FY2023 Osaka/FY2024 Mizushima; not a standalone fuel-switch saving'),
        ('mci_west_japan_2026.html','MCI','AMEC_plus_OPC','ethylene_capacity_before',2026,951000,'t_ethylene_per_year','951,000','Maintenance turnaround basis; jointly operated facilities'),
        ('mci_west_japan_2026.html','MCI','OPC_consolidated_operation','ethylene_capacity_after',2030,455000,'t_ethylene_per_year','455,000','FY2030 target; closure occurs at AMEC, not Osaka'),
        ('basf_ecracker_2024.html','BASF','two_demonstration_furnaces','electric_input',2024,6,'MW','6 megawatts','Demonstration with renewable power; not commercial fleet capacity'),
        ('basf_ecracker_2024.html','BASF','two_demonstration_furnaces','hydrocarbon_feedstock_rate',2024,4,'t_feedstock_per_hour','4 tons','Feedstock tonnes, not ethylene tonnes; needs product yield for per-ethylene normalization'),
        ('basf_ecracker_2024.html','BASF','two_demonstration_furnaces','grant',2024,14.8,'million_EUR','14.8 million','Government grant, not total plant capex'),
        ('basf_ecracker_2024.html','BASF','electric_furnace_process','potential_reduction_lower_bound_pct',2024,90,'%','at least 90%','Conditional potential with renewable electricity, not measured company-wide reduction'),
        ('lotte_ccu_2021.html','LOTTE','Daesan_capture_and_liquefaction','planned_investment',2021,60,'bn_KRW','600억','Announced after economic review; not evidence of commissioning'),
        ('lotte_ccu_2021.html','LOTTE','Daesan_capture_and_liquefaction','planned_capture_capacity',2023,200000,'tCO2_per_year','20만','Capture/use capacity; permanent net CO2 avoidance is not established'),
        ('lotte_ccu_2021.html','LOTTE','expanded_CCUS_concept','planned_capture_use_capacity',2030,500000,'tCO2_per_year','50만','Includes future expansion; not achieved or permanent storage'),
        ('lotte_lpg_2021.html','LOTTE','Yeosu_and_Daesan_feedstock_modification','planned_investment',2021,140,'bn_KRW','1,400억','Feedstock LPG flexibility, not external fuel consumption'),
        ('fsc_daesan_2026.html','LOTTE','LOTTE_DAE_NCC','approved_shutdown_capacity',2026,1100000,'t_ethylene_per_year','110만톤','Approved restructuring; exact shutdown date not established by approval'),
        ('fsc_daesan_2026.html','LOTTE','two_parent_integrated_entity','announced_equity_injection_total',2026,1200,'bn_KRW','1.2조원','Two parents combined, 600bn each; financing flow not capex'),
        ('fsc_yeosu_2026.html','LOTTE','Yeocheon_NCC_two_units','approved_shutdown_capacity',2026,1390000,'t_ethylene_per_year','139만톤','Yeocheon assets over3year restructuring; not shutdown of LOTTE Yeosu cracker'),
    ]
    for file,company,boundary,metric,year,value,unit,needle,note in projects:
        assert needle in body(file), (file,needle)
        add(file,'Selected announcement body/project table',company,boundary,metric,year,value,unit,note)

    with (OUT / 'verified_primary_observations.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(facts[0]));writer.writeheader();writer.writerows(facts)
    raw = list(csv.DictReader((ROOT / 'data/raw/facility_panel.csv').open(encoding='utf-8-sig')))
    comparisons = []
    for fact in facts:
        if fact['metric'] not in ('scope1', 'scope2'):
            continue
        candidates = [r for r in raw if r['facility_id'] == fact['boundary'] and int(r['year']) == fact['year']]
        field = 'emissions_s1' if fact['metric'] == 'scope1' else 'emissions_s2'
        val = float(candidates[0][field]) if candidates and candidates[0][field] else None
        comparisons.append(dict(observation_id=fact['observation_id'], boundary=fact['boundary'], year=fact['year'],
                                metric=fact['metric'], primary_value=fact['value'], legacy_value=val,
                                status='absent' if val is None else 'match' if val == fact['value'] else 'different'))
    with (OUT / 'legacy_observation_comparison.csv').open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(comparisons[0]));writer.writeheader();writer.writerows(comparisons)
    result = {'selected_primary_observations': len(facts), 'legacy_comparisons': len(comparisons),
              'comparison_counts': {s: sum(r['status'] == s for r in comparisons) for s in ['match','absent','different']},
              'scope': 'Selected primary GHG, target and capacity facts; no automatic allocation to cracker or production input replacement'}
    (OUT / 'primary_observation_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
