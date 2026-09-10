"""Workbook contract for the declared research model; no calculation or file mutation."""
import csv
import hashlib
import io
import json
import math

from xlsx_table_reader import WorkbookInputError, literal

KEYS = {
    'D1a': ['facility_id'], 'D1b': ['facility_id', 'year'],
    'D2a': ['scenario', 'region', 'sector', 'year'],
    'D2b': ['scenario', 'region', 'variable', 'year'],
    'D3': ['tech_id'], 'D3b': ['tech_id', 'field'],
    'D4': ['date', 'series_id'],
    'D5': ['support_scenario', 'instrument', 'tech_id', 'param_type', 'valid_from', 'valid_to'],
    'D6': ['company_id', 'year'],
    'D7': ['company_id', 'item_type', 'facility_id', 'tech_id', 'year_stated'],
}

CONTROLS = {
    'discount_rate': ('number', 0, .30, '연 실질 할인율 가정'),
    'seed': ('integer', 0, 2**32-1, '가격 경로 난수 시드'),
    'price_process': ('choice', ['gbm', 'ou'], None, '양의 승수 가격 과정'),
    'shock_normalisation': ('choice', ['mean', 'median'], None, '중심 경로의 평균 또는 중앙값 해석'),
    'ou_halflife_years': ('number', .1, 100, 'OU 로그 충격 반감기, 년'),
    'budget_mode': ('choice', ['cumulative_hard', 'annual_hard'], None, '누적 또는 연간 Scope1 상한'),
    'terminal_value_rule': ('choice', ['none', 'straight_line_proxy'], None, '종료 수입0 또는 정액 잔존가 대용치'),
    'include_capital_renewals': ('boolean', None, None, '기존 및 전환 설비 갱신 포함'),
    'plan_selection_criterion': ('choice', ['mean', 'p50'], None, '단일 대표 후보의 선택 기준'),
    'simulation.n_sims': ('integer', 100, 100000, '가격 경로 수, 큰 값은 계산시간 증가'),
    'simulation.n_sims_flex': ('integer', 100, 100000, '완전정보 상한 비교 경로 수'),
    'milp.frontier_points': ('integer', 2, 50, 'E2 위험 대용치 방향의 후보 수'),
    'milp.solver_time_limit_s': ('number', 1, 3600, '각 정수계획 계산의 시간 제한, 초'),
    'milp.mip_gap_rel': ('number', 0, .1, '최적성 상대 허용 차이, 실행가능성 오차와 별개'),
    'contracts.ppa_premium_pct': ('number', 0, 2, 'PPA 프리미엄 가정, 비율'),
    'contracts.epc_premium_pct': ('number', 0, 2, 'EPC 초기 공사비 프리미엄 가정, 비율'),
    'candidate_expansion_emissions_points': ('integer', 0, 30, '배출량 방향 추가 후보 수,0은 확장 없음'),
}


def get_nested(config, key):
    item = config
    for part in key.split('.'):
        item = item[part]
    return item


def set_nested(config, key, value):
    item = config
    parts = key.split('.')
    for part in parts[:-1]:
        item = item[part]
    item[parts[-1]] = value


def numeric(value, location, blank=False):
    if value is None or value == '':
        if blank:
            return None
        raise WorkbookInputError(f'{location}: required numeric value is missing')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise WorkbookInputError(f'{location}: enter a finite numeric cell, not text')
    return value


def validate_control(key, value):
    kind, lower, upper, _ = CONTROLS[key]
    if kind == 'choice':
        if value not in lower:
            raise WorkbookInputError(f'Settings {key}: expected one of {lower}')
    elif kind == 'boolean':
        if type(value) is not bool:
            raise WorkbookInputError(f'Settings {key}: enter TRUE or FALSE')
    else:
        numeric(value, key)
        if not lower <= value <= upper or (kind == 'integer' and int(value) != value):
            raise WorkbookInputError(f'Settings {key}: expected {kind} within [{lower}, {upper}]')
    if key=='candidate_expansion_emissions_points' and value==1:
        raise WorkbookInputError('Settings candidate_expansion_emissions_points: use 0 for none, or an integer from 2 to 30')
    return value


def decode_contract(sheets):
    if 'Control schema' not in sheets:
        raise WorkbookInputError('Missing Control schema sheet; use the research control workbook')
    cells = sheets['Control schema']; records = {}
    for row in range(6, max(r for r, c in cells)+1):
        key = literal(cells, row, 1, 'Control schema')
        if key is not None:
            if key in records:
                raise WorkbookInputError('Duplicate Control schema record')
            records[key] = literal(cells, row, 2, 'Control schema')
    chunks = sorted(k for k in records if str(k).startswith('chunk_'))
    raw = ''.join(records[k] for k in chunks)
    if hashlib.sha256(raw.encode()).hexdigest() != records.get('contract_sha256'):
        raise WorkbookInputError('Control schema changed or is incomplete')
    contract = json.loads(raw)
    if contract.get('version') != 2:
        raise WorkbookInputError('Unsupported control workbook version')
    for name, entry in contract['input_files'].items():
        if hashlib.sha256(entry['csv'].encode()).hexdigest() != entry['sha256']:
            raise WorkbookInputError(f'Embedded baseline hash differs: {name}')
    return contract


def csv_rows(text):
    return list(csv.DictReader(io.StringIO(text)))
