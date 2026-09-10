"""Read typed XLSX cells without Excel, macros, or formula evaluation.

This module is deliberately read-only. Workbook authoring uses Artifact Tool.
"""
from pathlib import PurePosixPath
import posixpath
import re
from zipfile import ZipFile
from xml.etree import ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


class WorkbookInputError(ValueError):
    pass


def column_index(address):
    match = re.fullmatch(r'([A-Z]+)([1-9][0-9]*)', address)
    if not match:
        raise WorkbookInputError(f'Invalid cell address: {address}')
    col = 0
    for letter in match[1]:
        col = col * 26 + ord(letter) - 64
    return int(match[2]), col


def read_cells(path):
    """Return sheet->(one-based row,column)->{value,formula,error}."""
    with ZipFile(path) as z:
        if any(i.file_size > 100_000_000 for i in z.infolist()):
            raise WorkbookInputError('Workbook part is too large for this control importer')
        if any('vbaProject' in name or name.startswith('xl/externalLinks/') for name in z.namelist()):
            raise WorkbookInputError('Use a local .xlsx without macros or external workbook links')
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for node in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
                strings.append(''.join(t.text or '' for t in node.iter('{'+NS['m']+'}t')))
        relationships = {}
        for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')):
            target = r.get('Target', '')
            if r.get('TargetMode') == 'External':
                continue
            resolved = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            if '..' in PurePosixPath(resolved).parts:
                raise WorkbookInputError('Invalid workbook relationship target')
            relationships[r.get('Id')] = resolved
        result = {}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
            cells = {}
            for c in ET.fromstring(z.read(relationships[sheet.get(RID)])).findall('.//m:sheetData/m:row/m:c', NS):
                t = c.get('t'); v = c.find('m:v', NS); f = c.find('m:f', NS)
                raw = v.text if v is not None else None
                if t == 's':
                    value = strings[int(raw)]
                elif t == 'inlineStr':
                    value = ''.join(n.text or '' for n in c.findall('.//m:t', NS))
                elif t == 'b':
                    value = raw == '1'
                elif t in {'str', 'e', 'd'}:
                    value = raw
                elif raw is None:
                    value = None
                else:
                    value = float(raw)
                    if value.is_integer():
                        value = int(value)
                cells[column_index(c.get('r'))] = dict(value=value, formula=None if f is None else f.text or '', error=t=='e')
            result[sheet.get('name')] = cells
        return result


def literal(cells, row, col, location):
    cell = cells.get((row, col), {})
    if cell.get('formula') is not None or cell.get('error'):
        raise WorkbookInputError(f'{location}: input must be a literal value, not a formula or Excel error')
    return cell.get('value')
