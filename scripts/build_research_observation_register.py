"""Unify selected primary observations without changing their units or boundaries."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'docs/research_cycles/2026-09-05'


def main():
    rows, hashes = [], {}
    def read(relative):
        path = AUDIT / relative
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return list(csv.DictReader(path.open(encoding='utf-8-sig')))
    def add(group, **values):
        rows.append(dict(observation_id=f'{group}{sum(r["group"] == group for r in rows)+1:03}',
                         group=group, **values))
    for r in read('verified_financial_observations.csv'):
        add('FIN', entity=r['company_id'], boundary=r['reporting_scope'], metric=r['metric'],
            period=r['fiscal_period_end'], value=r['value_bn_native'], unit='billion_'+r['currency'],
            price_basis=r['price_basis'], value_status='derived_proxy' if r['derivation'] else 'reported',
            source_url=r['source_url'], source_location=r['source_locator'], source_sha256=r['source_sha256'],
            interpretation_limit='; '.join(filter(None,[r['notes'],r['derivation']])))
    for r in read('steel_data/verified_steel_observations.csv'):
        add('STEEL', entity=r['entity'], boundary=r['boundary'], metric=r['metric'], period=r['year'],
            value=r['value'], unit=r['unit'], price_basis='see_unit_and_source', value_status=r['value_status'],
            source_url=r['source_url'], source_location='PDF p'+r['source_pdf_page'], source_sha256=r['source_sha256'],
            interpretation_limit=r['note'])
    for r in read('petchem_data/verified_primary_observations.csv'):
        add('PETCHEM', entity=r['company_id'], boundary=r['boundary'], metric=r['metric'], period=r['year'],
            value=r['value'], unit=r['unit'], price_basis='see_unit_and_source', value_status='selected_primary_fact',
            source_url=r['source_url'], source_location=r['source_location'], source_sha256=r['source_sha256'],
            interpretation_limit=r['interpretation_limit'])
    for r in read('steel_data/verified_technology_benchmarks.csv'):
        add('TECH', entity=r['technology'], boundary=r['sample'], metric=r['statistic'], period='2022_price_basis',
            value=r['value'], unit=r['unit'], price_basis='EUR_2022', value_status='reported_sample_statistic',
            source_url=r['source_url'], source_location='PDF p'+r['source_pdf_page'], source_sha256=r['source_sha256'],
            interpretation_limit=r['transfer_limit'])
    for r in read('verified_policy_observations.csv'):
        url = r['source_url']
        if r['source_parameters']:
            from urllib.parse import urlencode
            url += ('&' if '?' in url else '?') + urlencode(json.loads(r['source_parameters']))
        add('POLICY', entity=r['jurisdiction'], boundary=r['sector_class'], metric=r['instrument'],
            period=r['valid_from']+'–'+r['valid_to'], value=r['value'], unit=r['unit'], price_basis=r['price_basis'],
            value_status=r['value_status'], source_url=url, source_location=r['source_locator'],
            source_sha256=r['source_sha256'], interpretation_limit=r['interpretation'])
    assert len({r['observation_id'] for r in rows}) == len(rows)
    assert all(r['unit'] and r['source_url'] and r['source_sha256'] and r['boundary'] for r in rows)
    out = AUDIT / 'selected_primary_observation_register.csv'
    with out.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    report = dict(selected_observations=len(rows), groups={g:sum(r['group']==g for r in rows) for g in sorted({r['group'] for r in rows})},
                  input_sha256=hashes, output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                  scope='Selected reported facts and explicitly labelled derived facts; not 238 independently verified model parameters.')
    (AUDIT/'selected_primary_observation_register_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
