"""Preserve a pinned public technology dataset; no FIN input or distribution fit.

POSTED v0.4.0 data: CC-BY4.0, Verpoort et al., doi:10.5281/zenodo.18155305.
Original publication keys and curator notes remain attached to every row.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'tmp/pdfs/tcar_research_v2'
OUT = ROOT / 'data/research_v2/posted_reference'
TECHS = ['Iron Direct Reduction', 'Electric Arc Furnace', 'Naphtha Steam Cracking',
         'Steel Casting', 'Steel Hot Rolling', 'Blast Furnace and Basic Oxygen Furnace with CC']


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((RAW / 'posted_v040_download.json').read_text())
    blob = (RAW / 'posted_v040.zip').read_bytes()
    assert hashlib.sha256(blob).hexdigest() == metadata['sha256']
    rows, members = [], []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for tech in TECHS:
            names = [n for n in z.namelist() if n.endswith('/tedfs/Tech/' + tech + '.csv')]
            assert len(names) == 1, tech
            native = z.read(names[0])
            sha = hashlib.sha256(native).hexdigest()
            members.append(dict(member=names[0], sha256=sha))
            for row_no, r in enumerate(csv.DictReader(io.StringIO(native.decode('utf-8-sig'))), 2):
                flags = []
                note = r.get('comment', '')
                if 'misquoted' in note:
                    flags.append('curator_reports_upstream_misquotation')
                if 'exchange with the author' in note:
                    flags.append('private_author_correspondence_not_independently_accessed')
                if 'assum' in note.lower() or 'read off' in note:
                    flags.append('curator_assumption_or_digitization')
                if tech == 'Iron Direct Reduction' and r['source'] == 'Vogl18' and r['variable'] == 'Input|Iron Ore':
                    assert float(r['reference_value']) == 1.1 and '1.08' in note
                    flags.append('BLOCKED_reference_value_1.1_conflicts_with_comment_1.08')
                if r.get('uncertainty'):
                    flags.append('uncertainty_semantics_not_verified_do_not_treat_as_SD')
                rows.append(dict(technology=tech, native_row=row_no, **r,
                    member=names[0], member_sha256=sha,
                    archive_sha256=metadata['sha256'], version='0.4.0',
                    dataset_doi='10.5281/zenodo.18155305', dataset_license='CC-BY-4.0',
                    audit_flags=';'.join(flags),
                    original_publication_independently_verified=False,
                    use_status='curated_reference_pending_source_and_boundary_validation',
                    distribution_fit_allowed=False, FIN_import_allowed=False))
        bib = next(n for n in z.namelist() if n.endswith('/database/sources.bib'))
        (OUT / 'upstream_sources.bib').write_bytes(z.read(bib))
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (OUT / 'native_technology_rows.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    manifest = dict(archive=metadata, members=members, rows=len(rows),
        native_sources=len(set(r['source'] for r in rows)),
        flagged_rows=sum(bool(r['audit_flags']) for r in rows),
        denominator_conflicts=sum('BLOCKED' in r['audit_flags'] for r in rows),
        source_dependence='Repeated or derived literature values are not independent observations',
        latest_version_claimed=False, FIN_imported_rows=0)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (OUT / 'ATTRIBUTION.md').write_text(
        '# POSTED reference extract\n\n'
        'Source: Philipp C. Verpoort and POSTED contributors, POSTED v0.4.0, '
        '[version DOI](https://doi.org/10.5281/zenodo.18155305). '
        'Data license: [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).\n\n'
        'Changes: selected six technology tables; appended provenance and audit fields. '
        'Native values, units, source identifiers and curator comments are preserved. '
        'Consult upstream_sources.bib and cite the original publications as well. '
        'These rows have not all been independently checked against original publications. '
        'This pinned version is not asserted to be the latest release.\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('members','archive')}, indent=2))


if __name__ == '__main__':
    main()
