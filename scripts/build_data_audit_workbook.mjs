import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

process.on("uncaughtException", (error) => {
  console.error(`FATAL: ${error?.message ?? error}`);
  process.exit(1);
});
process.on("unhandledRejection", (error) => {
  console.error(`FATAL: ${error?.message ?? error}`);
  process.exit(1);
});

const root = process.cwd();
const dataDir = path.join(root, "data");
const outputDir = path.join(root, "outputs", "data_audit");
const renderDir = path.join(outputDir, "rendered_workbook");

const inputSheets = [
  ["Companies", "companies.csv"],
  ["Facilities", "facilities.csv"],
  ["Financials", "company_financials.csv"],
  ["Technologies", "technologies.csv"],
  ["Scenarios", "scenario_anchors.csv"],
  ["Scenario_Definitions", "scenario_definitions.csv"],
  ["Plans", "plans.csv"],
  ["Policy", "policy_support.csv"],
  ["Company_Constraints", "company_constraints.csv"],
  ["Tech_Constraints", "technology_constraints.csv"],
  ["Resource_Constraints", "resource_constraints.csv"],
  ["Resource_Benchmarks", "resource_benchmarks.csv"],
  ["Transition_Projects", "transition_projects.csv"],
  ["Technology_Cost_Evidence", "technology_cost_evidence.csv"],
  ["Data_Gaps", "data_gap_registry.csv"],
  ["GCAM_Run_Manifest", "gcam_run_manifest.csv"],
  ["GCAM_Query_Manifest", "gcam_query_manifest.csv"],
];

const auxiliaryFiles = [
  "price_process.json",
  "gcam/policy_target_temperature_1p5.xml",
  "gcam/policy_target_temperature_2p0.xml",
];

const COLORS = {
  navy: "#0B1F33",
  navy2: "#173A5E",
  teal: "#0C7C86",
  blue: "#3B82F6",
  sky: "#DDEBF7",
  pale: "#F3F7FA",
  white: "#FFFFFF",
  ink: "#1F2937",
  gray: "#64748B",
  line: "#CBD5E1",
  green: "#15803D",
  greenFill: "#DCFCE7",
  amber: "#B45309",
  amberFill: "#FEF3C7",
  red: "#B91C1C",
  redFill: "#FEE2E2",
};

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows;
}

function objectsFromCsv(text) {
  const rows = parseCsv(text);
  const header = rows[0];
  return rows.slice(1).filter((r) => r.some((v) => v !== "")).map((r) =>
    Object.fromEntries(header.map((h, i) => [h, r[i] ?? ""])),
  );
}

function coerceCsvValue(value) {
  const trimmed = value.trim();
  if (/^-?\d+(?:\.\d+)?$/.test(trimmed)) return Number(trimmed);
  if (trimmed.toLowerCase() === "true") return true;
  if (trimmed.toLowerCase() === "false") return false;
  return value;
}

function colName(n) {
  let x = n;
  let out = "";
  while (x > 0) {
    x -= 1;
    out = String.fromCharCode(65 + (x % 26)) + out;
    x = Math.floor(x / 26);
  }
  return out;
}

function setWidths(sheet, widths, rows = 200) {
  widths.forEach((width, i) => {
    sheet.getRange(`${colName(i + 1)}1:${colName(i + 1)}${rows}`).format.columnWidth = width;
  });
}

function styleTitle(sheet, range, title, subtitle) {
  range.merge();
  range.values = [[title]];
  range.format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 18 },
    verticalAlignment: "center",
  };
  range.format.rowHeight = 34;
  if (subtitle) {
    const start = range.getBoundingRect ? null : null;
  }
}

function styleHeader(sheet, address) {
  const r = sheet.getRange(address);
  r.format = {
    fill: COLORS.navy2,
    font: { bold: true, color: COLORS.white, size: 10 },
    verticalAlignment: "center",
    wrapText: true,
    borders: { bottom: { color: COLORS.teal, style: "continuous", weight: 2 } },
  };
  r.format.rowHeight = 28;
}

function styleBody(sheet, address) {
  const r = sheet.getRange(address);
  r.format = {
    font: { color: COLORS.ink, size: 9 },
    verticalAlignment: "top",
    wrapText: true,
    borders: { bottom: { color: COLORS.line, style: "continuous", weight: 1 } },
  };
}

function styleStatusCell(cell, status) {
  const good = status === "PASS" || status === "SUITABLE";
  const review = status === "REVIEW" || status === "CONDITIONAL";
  cell.format = {
    fill: good ? COLORS.greenFill : review ? COLORS.amberFill : COLORS.redFill,
    font: { bold: true, color: good ? COLORS.green : review ? COLORS.amber : COLORS.red },
    horizontalAlignment: "center",
  };
}

function sha256(text) {
  return crypto.createHash("sha256").update(text).digest("hex");
}

// Render directory is generated output; clear stale previews so numbering always
// maps one-to-one to the current workbook sheet order.
await fs.rm(renderDir, { recursive: true, force: true });
await fs.mkdir(renderDir, { recursive: true });

const csvTextByFile = {};
const rowsByFile = {};
for (const [, filename] of inputSheets) {
  const text = await fs.readFile(path.join(dataDir, filename), "utf8");
  csvTextByFile[filename] = text;
  rowsByFile[filename] = objectsFromCsv(text);
}
const priceProcessText = await fs.readFile(path.join(dataDir, "price_process.json"), "utf8");
const priceProcess = JSON.parse(priceProcessText);
const auxiliaryTextByFile = {};
for (const filename of auxiliaryFiles) {
  auxiliaryTextByFile[filename] = await fs.readFile(path.join(dataDir, filename), "utf8");
}
const repeatText = await fs.readFile(path.join(root, "outputs", "repeat_plan_summary.csv"), "utf8");
const repeatRows = objectsFromCsv(repeatText);
const comparisonText = await fs.readFile(path.join(root, "outputs", "repeat_scenario_comparison.csv"), "utf8");
const comparisonRows = objectsFromCsv(comparisonText);
const candidateCatalogRows = parseCsv(await fs.readFile(path.join(root, "outputs", "candidate_portfolios.csv"), "utf8"));
const candidateRobustRows = parseCsv(await fs.readFile(path.join(root, "outputs", "repeat_candidate_robust_summary.csv"), "utf8"));
const candidateComparisonRows = parseCsv(await fs.readFile(path.join(root, "outputs", "repeat_candidate_scenario_comparison.csv"), "utf8"));
const refinedMetricText = await fs.readFile(path.join(root, "outputs", "repeat_refined_candidate_scenario_metrics.csv"), "utf8");
const refinedRobustText = await fs.readFile(path.join(root, "outputs", "repeat_refined_candidate_robust_summary.csv"), "utf8");
const refinedComparisonText = await fs.readFile(path.join(root, "outputs", "repeat_refined_candidate_scenario_comparison.csv"), "utf8");
const refinedFacilityText = await fs.readFile(path.join(root, "outputs", "refined_candidate_facility_schedule.csv"), "utf8");
const refinedResourceText = await fs.readFile(path.join(root, "outputs", "refined_candidate_resource_profile.csv"), "utf8");
const refinedMetricRows = parseCsv(refinedMetricText);
const refinedRobustRows = parseCsv(refinedRobustText);
const refinedComparisonRows = parseCsv(refinedComparisonText);
const refinedFacilityRows = parseCsv(refinedFacilityText);
const refinedResourceRows = parseCsv(refinedResourceText);
const refinedMetricObjects = objectsFromCsv(refinedMetricText);
const refinedRobustObjects = objectsFromCsv(refinedRobustText);
const refinedFacilityObjects = objectsFromCsv(refinedFacilityText);
const refinedResourceObjects = objectsFromCsv(refinedResourceText);
let roundtripAudit = { files: {} };
try {
  roundtripAudit = JSON.parse(await fs.readFile(path.join(outputDir, "roundtrip_audit.json"), "utf8"));
} catch {
  // First build happens before the roundtrip exporter has produced an audit.
}

const workbook = Workbook.create();
const cover = workbook.worksheets.add("Cover");
for (const [sheetName, filename] of inputSheets) {
  // Instance CSV import cannot be repeated safely after collaborative edits in
  // artifact-tool 2.8.6, so values are parsed and written as a single block.
  const rows = parseCsv(csvTextByFile[filename]).map((row, rowIndex) =>
    row.map((value) => (rowIndex === 0 ? value : coerceCsvValue(value))),
  );
  const sheet = workbook.worksheets.add(sheetName);
  sheet.getRange(`A1:${colName(rows[0].length)}${rows.length}`).values = rows;
}
const priceSheet = workbook.worksheets.add("Price_Process");
const reconciliation = workbook.worksheets.add("Reconciliation");
const reason = workbook.worksheets.add("Reasonableness");
const results = workbook.worksheets.add("Current_Results");
const comparison = workbook.worksheets.add("Scenario_Comparison");
const candidateCatalog = workbook.worksheets.add("Candidate_Catalog");
const candidateRobust = workbook.worksheets.add("Robust_Candidates");
const candidateComparison = workbook.worksheets.add("Candidate_Comparison");
const refinedDecision = workbook.worksheets.add("Refined_Decision");
const refinedMetrics = workbook.worksheets.add("Refined_Metrics");
const refinedRobust = workbook.worksheets.add("Refined_Robust");
const refinedComparison = workbook.worksheets.add("Refined_Comparison");
const refinedFacilities = workbook.worksheets.add("Refined_Facilities");
const refinedResources = workbook.worksheets.add("Refined_Resources");
const sources = workbook.worksheets.add("Sources");
const manifest = workbook.worksheets.add("CSV_Manifest");

workbook.comments.setSelf({ displayName: "Codex Data Audit" });

// Cover sheet
cover.showGridLines = false;
cover.getRange("A1:H2").merge();
cover.getRange("A1").values = [["한·일 철강 Capital Allocation — 기준데이터 감사본"]];
cover.getRange("A1:H2").format = {
  fill: COLORS.navy,
  font: { bold: true, color: COLORS.white, size: 20 },
  verticalAlignment: "center",
};
cover.getRange("A3:H3").merge();
cover.getRange("A3").values = [["CSV 원천 → Excel 검증 → CSV 재생성 → 모델 재실행 | 2026-08-08"]];
cover.getRange("A3:H3").format = { fill: COLORS.teal, font: { color: COLORS.white, italic: true, size: 10 } };
cover.getRange("A5:B5").merge();
cover.getRange("A5").values = [["검증 결론"]];
cover.getRange("C5:H5").merge();
cover.getRange("C5").formulas = [["=Reasonableness!B14"]];
cover.getRange("A5:B5").format = { fill: COLORS.sky, font: { bold: true, color: COLORS.navy } };
styleStatusCell(cover.getRange("C5:H5"), "CONDITIONAL");
cover.getRange("A7:H7").values = [["원천 CSV", "→", "검증 Excel", "→", "재생성 CSV", "→", "동일성·실행 확인", "→ 보고서"]];
cover.getRange("A7:H7").format = {
  fill: COLORS.pale,
  font: { bold: true, color: COLORS.navy },
  horizontalAlignment: "center",
  borders: { top: { color: COLORS.line, style: "continuous", weight: 1 }, bottom: { color: COLORS.line, style: "continuous", weight: 1 } },
};
cover.getRange("A9:D9").merge();
cover.getRange("A9").values = [["정량 검증"]];
cover.getRange("E9:H9").merge();
cover.getRange("E9").values = [["의사결정 적합성"]];
cover.getRange("A9:H9").format = { fill: COLORS.navy2, font: { bold: true, color: COLORS.white } };
cover.getRange("A10:B13").values = [
  ["회사 수", null],
  ["시설 블록 수", null],
  ["총량 조정 PASS", null],
  ["CSV 파일 수", null],
];
cover.getRange("B10:B13").formulas = [
  ["=COUNTA(Companies!A2:A5)"],
  ["=COUNTA(Facilities!A2:A18)"],
  ["=COUNTIF(Reconciliation!H5:I8,\"PASS\")"],
  [`=COUNTA(CSV_Manifest!A5:A${4 + inputSheets.length + auxiliaryFiles.length})`],
];
cover.getRange("E10:F13").values = [
  ["종합 점수 / 5", null],
  ["경계 비교가능성", "2 / 5"],
  ["시설 현실성", "2 / 5"],
  ["CAPEX 보정", "2 / 5"],
];
cover.getRange("F10").formulas = [["=Reasonableness!B15"]];
cover.getRange("F10").format.numberFormat = "0.0";
cover.getRange("A10:F13").format = { font: { color: COLORS.ink, size: 11 }, borders: { bottom: { color: COLORS.line, style: "continuous", weight: 1 } } };
cover.getRange("A15:H15").merge();
cover.getRange("A15").values = [["해석 원칙"]];
cover.getRange("A15:H15").format = { fill: COLORS.navy2, font: { bold: true, color: COLORS.white } };
cover.getRange("A16:H18").merge();
cover.getRange("A16").values = [["회사 총량과 계산 재현성은 검증 가능하다. 다만 시설별 값은 공식 총량을 맞추기 위한 모델 블록이며, 일본 3사의 환경·재무 경계가 다르다. 현재 결과는 상대 민감도와 데이터 구조 검증에는 사용 가능하지만 투자 승인·기업 순위·기업가치 판단에는 사용하지 않는다."]];
cover.getRange("A16:H18").format = { fill: COLORS.amberFill, font: { color: COLORS.amber, size: 11 }, wrapText: true, verticalAlignment: "center" };
cover.getRange("A20:H20").merge();
cover.getRange("A20").values = [["사용법: 노란 입력·추정치와 Sources를 검토 → Reconciliation/Reasonableness 확인 → export_verified_csv.py 실행 → 모델 재실행"]];
cover.getRange("A20:H20").format = { font: { italic: true, color: COLORS.gray, size: 9 } };
setWidths(cover, [18, 13, 18, 10, 22, 16, 24, 18], 24);
cover.freezePanes.freezeRows(3);

// Imported source sheets: preserve source columns, append formula-driven audit fields.
for (const [sheetName, filename] of inputSheets) {
  const sheet = workbook.worksheets.getItem(sheetName);
  sheet.showGridLines = false;
  const raw = parseCsv(csvTextByFile[filename]);
  const lastRow = raw.length;
  const lastCol = raw[0].length;
  styleHeader(sheet, `A1:${colName(lastCol)}1`);
  if (lastRow > 1) styleBody(sheet, `A2:${colName(lastCol)}${lastRow}`);
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(sheetName === "Facilities" ? 2 : 1);
  const defaultWidths = raw[0].map((h) => {
    if (h.includes("note") || h.includes("boundary") || h.includes("url")) return 34;
    if (h.includes("name")) return 24;
    if (h.includes("id")) return 21;
    return 15;
  });
  setWidths(sheet, defaultWidths, Math.max(lastRow, 25));
}

const companies = workbook.worksheets.getItem("Companies");
companies.getRange("T1:X1").values = [["calc_intensity", "intensity_diff", "2030_slack_mt", "boundary_grade", "audit_status"]];
styleHeader(companies, "T1:X1");
companies.getRange("T2:T5").formulas = [["=H2/G2"]];
companies.getRange("T2:T5").fillDown();
companies.getRange("U2:U5").formulas = [["=T2-I2"]];
companies.getRange("U2:U5").fillDown();
companies.getRange("V2:V5").formulas = [["=K2-H2"]];
companies.getRange("V2:V5").fillDown();
companies.getRange("W2:W5").values = [["HIGH"], ["LOW"], ["LOW"], ["LOW"]];
companies.getRange("X2:X5").formulas = [["=IF(ABS(U2)<=0.01,\"PASS\",\"REVIEW\")"]];
companies.getRange("X2:X5").fillDown();
companies.getRange("T2:V5").format.numberFormat = "0.000";
companies.getRange("T2:X5").format.fill = COLORS.pale;
setWidths(companies, [21, 22, 11, 12, 11, 34, 14, 18, 18, 13, 17, 17, 14, 11, 13, 18, 26, 38, 48, 16, 16, 16, 18, 16], 10);
for (let row = 2; row <= 5; row += 1) {
  const sourceUrl = rowsByFile["companies.csv"][row - 2].source_url;
  workbook.comments.addThread({ cell: companies.getRange(`G${row}`) }, `생산·배출 기준값 출처: ${sourceUrl}`);
  workbook.comments.addThread({ cell: companies.getRange(`H${row}`) }, `Scope 1+2 기준값 출처: ${sourceUrl}`);
}

const facilities = workbook.worksheets.getItem("Facilities");
facilities.getRange("O1:Q1").values = [["calc_output_mt", "calc_emissions_mt", "audit_class"]];
styleHeader(facilities, "O1:Q1");
facilities.getRange("O2:O18").formulas = [["=E2*F2"]];
facilities.getRange("O2:O18").fillDown();
facilities.getRange("P2:P18").formulas = [["=O2*H2"]];
facilities.getRange("P2:P18").fillDown();
facilities.getRange("Q2:Q18").values = Array.from({ length: 17 }, () => ["RECONCILED MODEL BLOCK"]);
facilities.getRange("O2:P18").format.numberFormat = "0.000";
facilities.getRange("O2:Q18").format.fill = COLORS.pale;
setWidths(facilities, [18, 21, 29, 15, 13, 14, 21, 17, 17, 18, 13, 16, 18, 42, 15, 17, 25], 22);

const financials = workbook.worksheets.getItem("Financials");
financials.getRange("J1:K1").values = [["financial_boundary", "comparison_flag"]];
styleHeader(financials, "J1:K1");
financials.getRange("J2:J5").values = [["POSCO standalone"], ["Nippon consolidated"], ["JFE Holdings consolidated"], ["Kobelco consolidated"]];
financials.getRange("K2:K5").values = [["ALIGNED"], ["MISMATCH"], ["MISMATCH"], ["MISMATCH"]];
financials.getRange("C2:E5").format.numberFormat = "#,##0.0";
financials.getRange("J2:K5").format.fill = COLORS.pale;
setWidths(financials, [21, 13, 18, 18, 19, 15, 12, 20, 62, 26, 16], 10);
const financialUrls = {
  POSCO_KR: "https://www.posco.co.kr/homepage/docs/eng7/jsp/ir/s91b6000050l.jsp",
  NIPPON_STEEL_JP: "https://www.nipponsteel.com/en/ir/library/pdf/nsc_en_ir_2025_all.pdf",
  JFE_STEEL_JP: "https://www.jfe-holdings.co.jp/en/common/pdf/investor/library/group-report/2025/all.pdf",
  KOBE_STEEL_JP: "https://www.kobelco.co.jp/english/ir/integrated-reports/pdf/integrated-reports2025_e.pdf",
};
rowsByFile["company_financials.csv"].forEach((r, i) => {
  const row = i + 2;
  workbook.comments.addThread({ cell: financials.getRange(`C${row}`) }, `재무 입력 출처: ${financialUrls[r.company_id]}`);
  workbook.comments.addThread({ cell: financials.getRange(`D${row}`) }, `EBITDA 또는 EBITDA proxy 출처: ${financialUrls[r.company_id]}`);
});

// Price process assumptions flattened from JSON.
priceSheet.showGridLines = false;
priceSheet.getRange("A1:D1").values = [["parameter", "value", "unit", "audit_status"]];
const flattened = [];
function flatten(obj, prefix = "") {
  for (const [key, value] of Object.entries(obj)) {
    const full = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === "object" && !Array.isArray(value)) flatten(value, full);
    else flattened.push([full, Array.isArray(value) ? JSON.stringify(value) : value, "model assumption", "ESTIMATE"]);
  }
}
flatten(priceProcess);
priceSheet.getRange(`A2:D${flattened.length + 1}`).values = flattened;
styleHeader(priceSheet, "A1:D1");
styleBody(priceSheet, `A2:D${flattened.length + 1}`);
priceSheet.getRange(`B2:B${flattened.length + 1}`).format.numberFormat = "0.000";
setWidths(priceSheet, [42, 24, 22, 18], flattened.length + 3);
priceSheet.freezePanes.freezeRows(1);

// Formula reconciliation: official company totals vs model facility blocks.
reconciliation.showGridLines = false;
reconciliation.getRange("A1:I2").merge();
reconciliation.getRange("A1").values = [["총량 조정 검증 — 공식 회사값과 시설 블록 합계"]];
reconciliation.getRange("A1:I2").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 17 }, verticalAlignment: "center" };
reconciliation.getRange("A4:I4").values = [["company_id", "official production", "facility production", "difference", "official emissions", "facility emissions", "difference", "production", "emissions"]];
styleHeader(reconciliation, "A4:I4");
reconciliation.getRange("A5:A8").values = [["POSCO_KR"], ["NIPPON_STEEL_JP"], ["JFE_STEEL_JP"], ["KOBE_STEEL_JP"]];
const companyRows = [2, 3, 4, 5];
companyRows.forEach((companyRow, idx) => {
  const row = idx + 5;
  reconciliation.getRange(`B${row}`).formulas = [[`=Companies!G${companyRow}`]];
  reconciliation.getRange(`C${row}`).formulas = [[`=SUMIF(Facilities!$B$2:$B$18,A${row},Facilities!$O$2:$O$18)`]];
  reconciliation.getRange(`D${row}`).formulas = [[`=C${row}-B${row}`]];
  reconciliation.getRange(`E${row}`).formulas = [[`=Companies!H${companyRow}`]];
  reconciliation.getRange(`F${row}`).formulas = [[`=SUMIF(Facilities!$B$2:$B$18,A${row},Facilities!$P$2:$P$18)`]];
  reconciliation.getRange(`G${row}`).formulas = [[`=F${row}-E${row}`]];
  reconciliation.getRange(`H${row}`).formulas = [[`=IF(ABS(D${row})<=0.001,\"PASS\",\"REVIEW\")`]];
  reconciliation.getRange(`I${row}`).formulas = [[`=IF(ABS(G${row})<=0.001,\"PASS\",\"REVIEW\")`]];
});
styleBody(reconciliation, "A5:I8");
reconciliation.getRange("B5:G8").format.numberFormat = "0.000";
reconciliation.getRange("A10:I10").merge();
reconciliation.getRange("A10").values = [["허용오차 ±0.001Mt. PASS는 산술적 일치만 의미하며, 시설별 공개 데이터의 정확성을 의미하지 않는다."]];
reconciliation.getRange("A10:I10").format = { fill: COLORS.amberFill, font: { color: COLORS.amber, italic: true }, wrapText: true };
setWidths(reconciliation, [23, 18, 18, 15, 18, 18, 15, 14, 14], 14);
reconciliation.freezePanes.freezeRows(4);

// Reasonableness assessment and public EAF benchmark calibration.
reason.showGridLines = false;
reason.getRange("A1:H2").merge();
reason.getRange("A1").values = [["말이 되는가? — 모델 타당성 판정"]];
reason.getRange("A1:H2").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 17 }, verticalAlignment: "center" };
reason.getRange("A4:E4").values = [["검증 차원", "점수/5", "판정", "근거", "의미"]];
styleHeader(reason, "A4:E4");
reason.getRange("A5:E12").values = [
  ["공식값 추적성", 4, "GOOD", "생산·배출·재무 총량에 공식 URL과 경계 메모 존재", "회사 총량 재검증 가능"],
  ["산술 조정", 5, "PASS", "시설 블록 합계가 공식 생산·배출 총량과 허용오차 내 일치", "계산 구조는 일관"],
  ["회사 간 경계", 2, "WEAK", "일본 3사는 환경값과 연결 재무의 경계 불일치", "스트레스 배수 직접 비교 금지"],
  ["시설 현실성", 2, "CONDITIONAL", "설비 블록에 스크랩·수소·계통·동시공사·실패 제약을 추가했으나 한도값은 추정", "위치·시점 의사결정 전 공식 검증 필요"],
  ["기술 CAPEX", 2, "WEAK", "일본 대형 EAF 공시 프로젝트 대비 모델 원단위가 낮음", "현재 비용은 하방 편향 가능"],
  ["시나리오", 3, "CONDITIONAL", "GCAM 9.1 실행·query·hash 매니페스트와 1.5°C/2.0°C 온도 target 입력을 고정; Java 부재로 수치 실행은 pending", "활성화 게이트는 검증되나 공식 실행결과 전 조건부"],
  ["확률 계산", 4, "GOOD", "seed 반복과 P50/P90·TCaR 집계가 재현 가능", "분포 계산은 검증 가능"],
  ["투자결정 준비도", 2, "CONDITIONAL", "경계·시설·CAPEX 보정 전", "승인용이 아닌 진단용"],
];
styleBody(reason, "A5:E12");
reason.getRange("B5:B12").format.numberFormat = "0.0";
reason.getRange("A14").values = [["종합 판정"]];
reason.getRange("B14").values = [["CONDITIONAL — 구조 검증용 적합 / 투자 의사결정용 부적합"]];
reason.getRange("A15").values = [["평균 점수"]];
reason.getRange("B15").formulas = [["=AVERAGE(B5:B12)"]];
reason.getRange("B15").format.numberFormat = "0.0";
reason.getRange("A14:A15").format = { fill: COLORS.sky, font: { bold: true, color: COLORS.navy } };
reason.getRange("B14:E14").merge();
styleStatusCell(reason.getRange("B14:E14"), "CONDITIONAL");
reason.getRange("B15:E15").merge();
reason.getRange("B15:E15").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy } };
reason.getRange("B15").format.numberFormat = "0.0";
reason.getRange("A18:H18").values = [["benchmark", "model tech", "project capex (bn JPY)", "capacity (Mtpa)", "FX JPY→KRW", "public full-scope cost", "model/public", "required multiplier"]];
styleHeader(reason, "A18:H18");
reason.getRange("A19:E20").values = [
  ["JFE Kurashiki 2025", "SCRAP_EAF", 329.4, 2.0, 9.2],
  ["Nippon 3 EAFs 2025", "SCRAP_EAF", 868.7, 2.9, 9.2],
];
reason.getRange("F19:F20").formulas = [["=C19/D19*E19"], ["=C20/D20*E20"]];
reason.getRange("G19:G20").formulas = [["=(Technologies!C5*Companies!O4)/F19"], ["=(Technologies!C5*Companies!O3)/F20"]];
reason.getRange("H19:H20").formulas = [["=1/G19"], ["=1/G20"]];
styleBody(reason, "A19:H20");
reason.getRange("C19:F20").format.numberFormat = "#,##0.0";
reason.getRange("G19:G20").format.numberFormat = "0.0%";
reason.getRange("H19:H20").format.numberFormat = "0.00x";
reason.getRange("A22:H23").merge();
reason.getRange("A22").values = [["공시 프로젝트는 전기로 외 전력계통·물류·부대설비를 포함할 수 있어 완전한 동등 비교는 아니다. 그럼에도 모델의 일본 SCRAP_EAF 비용(616bn KRW/Mtpa)은 JFE 공시 환산 원단위의 약 41%, Nippon Steel의 약 22%로, 최소한 low/base/high 범위 재보정이 필요하다."]];
reason.getRange("A22:H23").format = { fill: COLORS.amberFill, font: { color: COLORS.amber, size: 10 }, wrapText: true, verticalAlignment: "center" };
workbook.comments.addThread({ cell: reason.getRange("C19") }, "JFE official release: https://www.jfe-steel.co.jp/en/release/2025/04/250410.html");
workbook.comments.addThread({ cell: reason.getRange("C20") }, "Nippon Steel official release: https://www.nipponsteel.com/common/secure/en/news/20250530_200.pdf");
setWidths(reason, [24, 16, 20, 18, 15, 22, 15, 18], 28);
reason.freezePanes.freezeRows(4);

// Current disclosed-strategy proxies, accelerated pathway, three-seed mean.
results.showGridLines = false;
results.getRange("A1:H2").merge();
results.getRange("A1").values = [["고정 공시경로 포트폴리오 재평가 — ACCELERATED_15C / 3 seeds × 1,000 paths"]];
results.getRange("A1:H2").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 16 }, verticalAlignment: "center" };
results.getRange("A4:H4").values = [["company", "P50 economic cost (천원/tCO₂)", "TCaR (천원/tCO₂)", "aligned CAPEX (십억원)", "P90 absolute NPV (십억원)", "NPV / annual EBITDA", "P50 seed std", "interpretation"]];
styleHeader(results, "A4:H4");
const current = repeatRows.filter((r) => r.scenario_id === "ACCELERATED_15C" && r.plan_id === "CURRENT");
const currentMatrix = current.map((r) => [
  r.company_name,
  Number(r.expected_cost_p50_kkrw_per_tco2_mean),
  Number(r.tcar_kkrw_per_tco2_mean),
  Number(r.aligned_capex_bn_krw),
  Number(r.p90_net_cost_bn_krw_mean),
  Number(r.p90_cost_to_ebitda_x_mean),
  Number(r.expected_cost_p50_kkrw_per_tco2_std),
  r.scenario_feasible === "True"
    ? "목표경로 적합; 방향성 지표·기업 순위 금지"
    : "통합 실행 제약 미충족; 효율경계 제외·기업 순위 금지",
]);
results.getRange(`A5:H${4 + currentMatrix.length}`).values = currentMatrix;
styleBody(results, `A5:H${4 + currentMatrix.length}`);
results.getRange(`B5:C${4 + currentMatrix.length}`).format.numberFormat = "0.0";
results.getRange(`D5:E${4 + currentMatrix.length}`).format.numberFormat = "#,##0";
results.getRange(`F5:F${4 + currentMatrix.length}`).format.numberFormat = "0.00x";
results.getRange(`G5:G${4 + currentMatrix.length}`).format.numberFormat = "0.000";
results.getRange("A11:H12").merge();
results.getRange("A11").values = [["P90 absolute NPV / annual EBITDA는 15년 누적 순현재비용을 1년 EBITDA로 나눈 스트레스 배수다. 통상적 부채상환·커버리지 비율이 아니며, 환경·재무 경계가 다른 회사 간 직접 비교는 금지한다."]];
results.getRange("A11:H12").format = { fill: COLORS.amberFill, font: { color: COLORS.amber }, wrapText: true };
setWidths(results, [20, 17, 14, 18, 20, 20, 16, 36], 16);
results.freezePanes.freezeRows(4);

// Signed scenario deltas for the exact same physical portfolio.
comparison.showGridLines = false;
comparison.getRange("A1:P2").merge();
comparison.getRange("A1").values = [["동일 물리 포트폴리오 시나리오 비교 — to scenario − from scenario"]];
comparison.getRange("A1:P2").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 16 }, verticalAlignment: "center" };
comparison.getRange("A4:H4").values = [["비교행", null, "동일 포트폴리오", null, "CAPEX 불변", null, "목표경로 적합", null]];
comparison.getRange("B4").formulas = [[`=COUNTA(A10:A${9 + comparisonRows.length})`]];
comparison.getRange("D4").formulas = [[`=COUNTIF(H10:H${9 + comparisonRows.length},"PASS")`]];
comparison.getRange("F4").formulas = [[`=COUNTIF(P10:P${9 + comparisonRows.length},0)`]];
comparison.getRange("H4").formulas = [[`=COUNTIF(G10:G${9 + comparisonRows.length},"PASS")`]];
comparison.getRange("A4:H4").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy }, horizontalAlignment: "center" };
comparison.getRange("A6:P7").merge();
comparison.getRange("A6").values = [["모든 Δ는 signed 값이다. 경제적 비용은 실제 순현금비용에서 회피 탄소비용 가치를 차감한 값이며, 탄소가치와 정책지원은 실제 현금지출과 분리해 읽는다. 목표경로에 부적합한 포트폴리오는 효율경계에서 제외한다."]];
comparison.getRange("A6:P7").format = { fill: COLORS.amberFill, font: { color: COLORS.amber }, wrapText: true, verticalAlignment: "center" };
comparison.getRange("A9:P9").values = [[
  "company", "plan", "portfolio_id", "from", "to", "from feasible", "to feasible", "same portfolio",
  "common avoided Mt", "ΔP50 common", "ΔTCaR", "Δabsolute NPV P50", "Δnet cash P50", "Δavoided carbon value", "Δpolicy support", "Δaligned CAPEX",
]];
styleHeader(comparison, "A9:P9");
const comparisonMatrix = comparisonRows.map((r) => [
  r.company_name,
  r.plan_name,
  r.portfolio_id,
  r.from_scenario_id,
  r.to_scenario_id,
  r.from_scenario_feasible === "True" ? "PASS" : "FAIL",
  r.to_scenario_feasible === "True" ? "PASS" : "FAIL",
  r.same_physical_portfolio === "True" ? "PASS" : "FAIL",
  Number(r.common_avoided_emissions_mtco2),
  Number(r.delta_p50_common_kkrw_per_tco2_mean),
  Number(r.delta_tcar_kkrw_per_tco2_mean),
  Number(r.delta_absolute_npv_p50_bn_krw_mean),
  Number(r.delta_net_cash_cost_p50_bn_krw_mean),
  Number(r.delta_avoided_carbon_value_p50_bn_krw_mean),
  Number(r.delta_policy_support_value_p50_bn_krw_mean),
  Number(r.delta_aligned_capex_bn_krw_mean),
]);
comparison.getRange(`A10:P${9 + comparisonMatrix.length}`).values = comparisonMatrix;
styleBody(comparison, `A10:P${9 + comparisonMatrix.length}`);
comparison.getRange(`I10:K${9 + comparisonMatrix.length}`).format.numberFormat = "0.000";
comparison.getRange(`L10:P${9 + comparisonMatrix.length}`).format.numberFormat = "#,##0.0;[Red](#,##0.0);-";
setWidths(comparison, [20, 24, 21, 20, 22, 15, 15, 16, 17, 17, 15, 21, 19, 22, 19, 18], 46);
comparison.freezePanes.freezeRows(9);
comparison.freezePanes.freezeColumns(3);

// Generated candidate outputs are model results, not canonical input tabs.
for (const [sheet, rows] of [
  [candidateCatalog, candidateCatalogRows],
  [candidateRobust, candidateRobustRows],
  [candidateComparison, candidateComparisonRows],
]) {
  sheet.showGridLines = false;
  sheet.getRange(`A1:${colName(rows[0].length)}${rows.length}`).values = rows.map((row, rowIndex) =>
    row.map((value) => (rowIndex === 0 ? value : coerceCsvValue(value))),
  );
  styleHeader(sheet, `A1:${colName(rows[0].length)}1`);
  styleBody(sheet, `A2:${colName(rows[0].length)}${rows.length}`);
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(3);
}
setWidths(candidateCatalog, [23, 22, 20, 16, 25, 22, 22, 17, 18, 18, 19, 19, 20, 22, 14, 20, 16, 14, 18, 22, 70, 25, 58], Math.min(candidateCatalogRows.length, 920));
setWidths(candidateRobust, Array.from({ length: candidateRobustRows[0].length }, (_, i) => i < 5 ? 22 : 20), Math.min(candidateRobustRows.length, 230));
setWidths(candidateComparison, Array.from({ length: candidateComparisonRows[0].length }, (_, i) => i < 5 ? 22 : 20), Math.min(candidateComparisonRows.length, 230));

// Full-path refined shortlist: decision summary plus raw, auditable result tables.
refinedDecision.showGridLines = false;
refinedDecision.getRange("A1:P2").merge();
refinedDecision.getRange("A1").values = [["정밀 강건후보 의사결정 요약 — 고정 shortlist / 3 seeds × 요청 전체 경로"]];
refinedDecision.getRange("A1:P2").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 17 }, verticalAlignment: "center" };
refinedDecision.getRange("A4:P5").merge();
refinedDecision.getRange("A4").values = [["λ=1 추천빈도가 가장 높은 후보를 표시한다. 최대후회 기준점은 전체 910개가 아니라 중앙가격으로 고정한 정밀 shortlist 안의 시나리오별 최저 적격안이다. 요인비중은 같은 공통난수로 모든 8개 요인부분집합을 평가한 정확한 3요인 Shapley 분산배분이며 총비용 구성비가 아니다."]];
refinedDecision.getRange("A4:P5").format = { fill: COLORS.amberFill, font: { color: COLORS.amber, size: 10 }, wrapText: true, verticalAlignment: "center" };
refinedDecision.getRange("A7:P7").values = [[
  "company", "λ=1 candidate", "template", "λ=1 frequency", "max regret", "worst TCaR", "worst scenario", "scenario P50", "scenario TCaR", "electricity risk", "H₂-input risk", "construction risk", "facility blocks", "aligned CAPEX bn", "annual abatement Mt", "peak scrap / H₂ / grid",
]];
styleHeader(refinedDecision, "A7:P7");
const refinedDecisionRows = [...new Set(refinedRobustObjects.map((r) => r.company_id))].map((companyId) => {
  const robustChoices = refinedRobustObjects
    .filter((r) => r.company_id === companyId && r.robust_feasible === "True")
    .sort((a, b) =>
      Number(b.lambda_1_optimal_frequency_pct) - Number(a.lambda_1_optimal_frequency_pct)
      || (Number(a.maximum_regret_p50_kkrw_per_tco2_mean) + Number(a.worst_case_tcar_kkrw_per_tco2_mean))
      - (Number(b.maximum_regret_p50_kkrw_per_tco2_mean) + Number(b.worst_case_tcar_kkrw_per_tco2_mean)),
    );
  const reco = robustChoices[0];
  const metrics = refinedMetricObjects
    .filter((r) => r.company_id === companyId && r.candidate_id === reco.candidate_id)
    .sort((a, b) => Number(b.tcar_kkrw_per_tco2_mean) - Number(a.tcar_kkrw_per_tco2_mean));
  const worst = metrics[0];
  const facilitiesForScenario = refinedFacilityObjects.filter((r) =>
    r.company_id === companyId && r.candidate_id === reco.candidate_id && r.scenario_id === worst.scenario_id,
  );
  const resourcesForScenario = refinedResourceObjects.filter((r) =>
    r.company_id === companyId && r.candidate_id === reco.candidate_id && r.scenario_id === worst.scenario_id,
  );
  const peak = (field) => Math.max(...resourcesForScenario.map((r) => Number(r[field])), 0);
  return [
    reco.company_name, reco.candidate_id, reco.template_plan_id, Number(reco.lambda_1_optimal_frequency_pct) / 100,
    Number(reco.maximum_regret_p50_kkrw_per_tco2_mean), Number(reco.worst_case_tcar_kkrw_per_tco2_mean), worst.scenario_id,
    Number(worst.expected_cost_p50_kkrw_per_tco2_mean), Number(worst.tcar_kkrw_per_tco2_mean),
    Number(worst.electricity_shapley_variance_share_mean), Number(worst.hydrogen_shapley_variance_share_mean), Number(worst.capex_shapley_variance_share_mean),
    facilitiesForScenario.length,
    facilitiesForScenario.reduce((sum, r) => sum + Number(r.aligned_capex_bn_krw), 0),
    facilitiesForScenario.reduce((sum, r) => sum + Number(r.annual_avoided_emissions_mtco2), 0),
    `${peak("scrap_utilization_pct").toFixed(0)}% / ${peak("hydrogen_utilization_pct").toFixed(0)}% / ${peak("incremental_grid_utilization_pct").toFixed(0)}%`,
  ];
});
refinedDecision.getRange(`A8:P${7 + refinedDecisionRows.length}`).values = refinedDecisionRows;
styleBody(refinedDecision, `A8:P${7 + refinedDecisionRows.length}`);
refinedDecision.getRange(`D8:D${7 + refinedDecisionRows.length}`).format.numberFormat = "0%";
refinedDecision.getRange(`E8:F${7 + refinedDecisionRows.length}`).format.numberFormat = "0.0";
refinedDecision.getRange(`H8:I${7 + refinedDecisionRows.length}`).format.numberFormat = "0.0";
refinedDecision.getRange(`J8:L${7 + refinedDecisionRows.length}`).format.numberFormat = "0.0%";
refinedDecision.getRange(`N8:O${7 + refinedDecisionRows.length}`).format.numberFormat = "#,##0.0";
setWidths(refinedDecision, [20, 24, 12, 16, 16, 15, 21, 15, 15, 17, 17, 18, 15, 19, 20, 24], 14);
refinedDecision.freezePanes.freezeRows(7);
refinedDecision.freezePanes.freezeColumns(2);

for (const [sheet, rows] of [
  [refinedMetrics, refinedMetricRows],
  [refinedRobust, refinedRobustRows],
  [refinedComparison, refinedComparisonRows],
  [refinedFacilities, refinedFacilityRows],
  [refinedResources, refinedResourceRows],
]) {
  sheet.showGridLines = false;
  sheet.getRange(`A1:${colName(rows[0].length)}${rows.length}`).values = rows.map((row, rowIndex) =>
    row.map((value) => (rowIndex === 0 ? value : coerceCsvValue(value))),
  );
  styleHeader(sheet, `A1:${colName(rows[0].length)}1`);
  styleBody(sheet, `A2:${colName(rows[0].length)}${rows.length}`);
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(3);
  setWidths(sheet, Array.from({ length: rows[0].length }, (_, i) => i < 7 ? 21 : 16), Math.min(rows.length, 1120));
}

// Source register.
sources.showGridLines = false;
sources.getRange("A1:G2").merge();
sources.getRange("A1").values = [["공식 출처·경계 레지스터"]];
sources.getRange("A1:G2").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 17 }, verticalAlignment: "center" };
sources.getRange("A4:G4").values = [["source_id", "company", "topic", "official_url", "accessed", "values used", "boundary / caution"]];
styleHeader(sources, "A4:G4");
const sourceRows = [
  ["P-ENV", "POSCO", "Scope 1+2", "https://sustainability.posco.com/S91/S91F10/eng/cmspage.do?mmcd=2682093497003371", "2026-08-06", "2025 69.84605Mt", "국내 사업장"],
  ["P-PROD", "POSCO", "production/revenue", "https://sustainability.posco.com/S91/S91F10/eng/cmspage.do?mmcd=2682093474001805", "2026-08-06", "34.537Mt; 35,010.837bn KRW", "국내 생산·별도 매출"],
  ["P-CLIM", "POSCO", "targets/projects", "https://sustainability.posco.com/S91/S91F10/eng/cmspage.do?mmcd=2648825310001953", "2026-08-06", "2030 -10%; 2040 -50%; EAF 2.5Mt", "2017–2019 baseline 78.8Mt"],
  ["P-FIN", "POSCO", "financials", "https://www.posco.co.kr/homepage/docs/eng7/jsp/ir/s91b6000050l.jsp", "2026-08-06", "revenue 35,011; EBITDA 4,230", "standalone"],
  ["N-IR", "Nippon Steel", "integrated report", "https://www.nipponsteel.com/en/ir/library/pdf/nsc_en_ir_2025_all.pdf", "2026-08-06", "34.30Mt; 72.6Mt; financials", "parent environment vs consolidated finance"],
  ["N-EAF", "Nippon Steel", "EAF project", "https://www.nipponsteel.com/common/secure/en/news/20250530_200.pdf", "2026-08-06", "868.7bn JPY / 2.9Mt", "three-project full program"],
  ["J-IR", "JFE", "integrated report", "https://www.jfe-holdings.co.jp/en/common/pdf/investor/library/group-report/2025/all.pdf", "2026-08-06", "21.95Mt; 45.3Mt; financials", "JFE Steel environment vs Holdings finance"],
  ["J-EAF", "JFE", "Kurashiki EAF", "https://www.jfe-steel.co.jp/en/release/2025/04/250410.html", "2026-08-06", "329.4bn JPY / 2.0Mt", "project scope broader than furnace only"],
  ["J-RISK", "JFE", "capacity", "https://www.jfe-holdings.co.jp/en/investor/management/risk/", "2026-08-06", "21Mt target by FY2027", "group planning disclosure"],
  ["K-IR", "Kobe Steel", "integrated report", "https://www.kobelco.co.jp/english/ir/integrated-reports/pdf/integrated-reports2025_e.pdf", "2026-08-06", "5.96Mt; 14.3Mt; financials", "target boundary includes major subsidiaries"],
  ["GCAM-POL", "JGCRI", "climate constraints", "https://jgcri.github.io/gcam-doc/policies.html", "2026-08-07", "carbon/GHG price and climate constraints", "공식 프레임워크 문서이며 수치 시나리오 export는 아님"],
  ["GCAM-HEC", "JGCRI", "temperature model", "https://jgcri.github.io/gcam-doc/hector.html", "2026-08-07", "GCAM emissions → Hector temperature", "온도 출력·제약 설명; 회사별 데이터가 아님"],
  ["GCAM-STL", "JGCRI", "iron and steel", "https://jgcri.github.io/gcam-doc/demand_energy.html", "2026-08-07", "BOF, scrap EAF, DRI-EAF; steel in Mt", "지역 산업모형이며 회사별 설비 배분이 아님"],
  ["GCAM-EXT", "JGCRI", "database extraction", "https://jgcri.github.io/gcam-doc/dev-guide/analysis.html", "2026-08-07", "ModelInterface / rgcam / gcam_reader", "정확한 DB 버전·query XML·추출 hash가 필요"],
  ["GCAM-REL", "JGCRI", "official release", "https://github.com/JGCRI/gcam-core/releases/tag/gcam-v9.1", "2026-08-07", "GCAM 9.1; Mac asset SHA256 b009e58a…d0868a", "공식 binary를 검증했으나 프로젝트 target run은 아직 실행 전"],
  ["GCAM-TGT", "JGCRI", "target finder", "https://jgcri.github.io/gcam-doc/user-guide.html", "2026-08-07", "target-type=temperature; target-value/tolerance", "프로젝트 XML은 공식 schema를 사용한 입력이지 JGCRI 발표 결과가 아님"],
  ["KR-H2", "Korea", "clean hydrogen", "https://www.pcccr.go.kr/base/board/read?boardManagementNo=10&boardNo=124&menuLevel=2&menuNo=18&page=2", "2026-08-07", "2030 domestic clean H2 1 Mt/year", "국가 목표이며 철강·기업 배분이 아님"],
  ["KR-GRID", "Korea", "national grid", "https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/170183/view", "2026-08-07", "2038 target demand 129.3 GW; new capacity need 10.3 GW", "전력량 TWh 또는 회사 접속한도가 아님"],
  ["KR-SCRAP", "Korea", "steel scrap policy", "https://www.2050cnc.go.kr/storage/board/base/2023/02/17/BOARD_ATTACH_1676595021015.pdf", "2026-08-07", "circular-resource recognition and statistics policy", "검증된 정량 공급치는 없음"],
  ["JP-H2", "Japan", "hydrogen strategy", "https://www.meti.go.jp/policy/energy_environment/global_warming/transition/jcr_climate_transition_bond_framework_spo_eng.pdf", "2026-08-07", "3/12/20 MtH2-eq in 2030/2040/2050", "암모니아의 수소환산량 포함; 기업 배분 아님"],
  ["JP-GRID", "Japan", "transmission plans", "https://www.occto.or.jp/assets/en/information_disclosure/annual_report/files/2023_annualreport_240131.pdf", "2026-08-07", "30,163 MVA transformers; 1,200 MW converters", "FY2032까지 국가·광역 개발계획; 회사 한도 아님"],
  ["JP-SCRAP", "Japan", "steel scrap", "https://www.env.go.jp/content/000315009.pdf", "2026-08-07", "2022 generation 43.16 Mt/year", "JISF 기반 국가발생량; 회사 조달량 아님"],
  ["JP-SCRAP-HG", "Japan", "high-grade scrap", "https://www.env.go.jp/policy/hakusyo/r08/html/hj26010401.html", "2026-08-07", "2030 additional processing capacity 2 Mt/year", "추가 가공능력이며 발생량·회사 배분 아님"],
];
sources.getRange(`A5:G${4 + sourceRows.length}`).values = sourceRows;
styleBody(sources, `A5:G${4 + sourceRows.length}`);
setWidths(sources, [14, 18, 22, 58, 15, 34, 43], 18);
sources.freezePanes.freezeRows(4);

// Manifest ties canonical files to source sheets and hashes.
manifest.showGridLines = false;
manifest.getRange("A1:F2").merge();
manifest.getRange("A1").values = [["CSV 왕복 검증 매니페스트"]];
manifest.getRange("A1:F2").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 17 }, verticalAlignment: "center" };
manifest.getRange("A4:F4").values = [["file", "sheet", "data rows", "source SHA256", "export columns", "status"]];
styleHeader(manifest, "A4:F4");
const manifestRows = inputSheets.map(([sheetName, filename]) => {
  const parsed = parseCsv(csvTextByFile[filename]);
  return [filename, sheetName, parsed.length - 1, sha256(csvTextByFile[filename]), parsed[0].join(", "), roundtripAudit.files?.[filename]?.status ?? "PENDING ROUNDTRIP"];
});
manifestRows.push(["price_process.json", "Price_Process", flattened.length, sha256(priceProcessText), "JSON copied unchanged", roundtripAudit.files?.["price_process.json"]?.status ?? "PENDING ROUNDTRIP"]);
for (const filename of auxiliaryFiles.filter((name) => name !== "price_process.json")) {
  manifestRows.push([filename, "GCAM_Run_Manifest", 1, sha256(auxiliaryTextByFile[filename]), "XML support file copied unchanged", roundtripAudit.files?.[filename]?.status ?? "PENDING ROUNDTRIP"]);
}
manifest.getRange(`A5:F${4 + manifestRows.length}`).values = manifestRows;
styleBody(manifest, `A5:F${4 + manifestRows.length}`);
setWidths(manifest, [28, 20, 14, 68, 70, 22], 18);
manifest.freezePanes.freezeRows(4);

// Number formatting for raw sheets.
companies.getRange("G2:O5").format.numberFormat = "0.000";
facilities.getRange("E2:J18").format.numberFormat = "0.000";
financials.getRange("C2:E5").format.numberFormat = "#,##0.000";
workbook.worksheets.getItem("Technologies").getRange("C2:J7").format.numberFormat = "0.000";
workbook.worksheets.getItem("Scenarios").getRange("D2:H33").format.numberFormat = "#,##0.000";
const scenarioDefinitions = workbook.worksheets.getItem("Scenario_Definitions");
scenarioDefinitions.getRange("D2:D5").format.numberFormat = "0.0";
scenarioDefinitions.getRange("A2:N5").format.rowHeight = 42;
setWidths(
  scenarioDefinitions,
  [22, 33, 23, 16, 12, 25, 17, 48, 24, 18, 25, 28, 30, 58],
  8,
);
workbook.worksheets.getItem("Plans").getRange("D2:J12").format.numberFormat = "0.000";
workbook.worksheets.getItem("Policy").getRange("D2:E17").format.numberFormat = "0.0%";
setWidths(workbook.worksheets.getItem("Company_Constraints"), [22, 22, 22, 17, 38, 55], 8);
setWidths(workbook.worksheets.getItem("Tech_Constraints"), [22, 20, 20, 19, 17, 38, 55], 10);
setWidths(workbook.worksheets.getItem("Resource_Constraints"), [22, 23, 12, 22, 24, 25, 17, 38, 58], 36);
setWidths(workbook.worksheets.getItem("Resource_Benchmarks"), [28, 12, 15, 14, 18, 18, 22, 42, 28, 42, 58, 20, 17, 28, 42, 62], 20);
const transitionProjects = workbook.worksheets.getItem("Transition_Projects");
transitionProjects.getRange("N2:X10").format.numberFormat = "#,##0.000";
transitionProjects.getRange("T2:U10").format.numberFormat = "0.0%";
transitionProjects.getRange("W2:X10").format.numberFormat = "0.0%";
setWidths(transitionProjects, [27, 22, 28, 27, 42, 11, 22, 24, 16, 18, 16, 28, 18, 16, 18, 14, 13, 18, 20, 18, 19, 21, 14, 14, 27, 24, 48, 68, 18, 17, 72], 14);
const technologyCostEvidence = workbook.worksheets.getItem("Technology_Cost_Evidence");
technologyCostEvidence.getRange("F2:L8").format.numberFormat = "#,##0.000";
setWidths(technologyCostEvidence, [27, 27, 22, 18, 25, 16, 18, 14, 13, 18, 27, 22, 14, 62, 38, 19, 24, 68, 17, 56], 12);
setWidths(workbook.worksheets.getItem("Data_Gaps"), [24, 28, 54, 62, 62, 12, 54, 48, 58, 24, 68], 16);
setWidths(workbook.worksheets.getItem("GCAM_Run_Manifest"), [18, 18, 12, 15, 15, 55, 36, 68, 18, 38, 68, 48, 68, 42, 68, 15, 13, 14, 24, 22, 38, 68, 19, 25, 58], 6);
setWidths(workbook.worksheets.getItem("GCAM_Query_Manifest"), [18, 28, 38, 22, 20, 24, 55, 38, 68, 22, 24, 58, 55], 24);

// Compact verification payloads before export.
const inspectSummary = await workbook.inspect({
  kind: "workbook,sheet,formula",
  maxChars: 12000,
  tableMaxRows: 8,
  tableMaxCols: 10,
  options: { maxResults: 120 },
});
const errorScan = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  maxChars: 4000,
  options: { useRegex: true, maxResults: 100 },
});
await fs.writeFile(path.join(outputDir, "workbook_inspection.json"), JSON.stringify({ inspectSummary, errorScan }, null, 2));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(path.join(outputDir, "Capital_Allocation_Baseline_Audit.xlsx"));

const renderSheets = [
  "Cover", "Companies", "Facilities", "Financials", "Technologies", "Scenarios", "Scenario_Definitions", "Plans", "Policy",
  "Company_Constraints", "Tech_Constraints", "Resource_Constraints", "Resource_Benchmarks", "Transition_Projects", "Technology_Cost_Evidence", "Data_Gaps", "GCAM_Run_Manifest", "GCAM_Query_Manifest",
  "Price_Process", "Reconciliation", "Reasonableness", "Current_Results", "Scenario_Comparison",
  { name: "Candidate_Catalog", range: "A1:W60" },
  { name: "Robust_Candidates", range: "A1:AB80" },
  { name: "Candidate_Comparison", range: "A1:AA80" },
  "Refined_Decision",
  { name: "Refined_Metrics", range: "A1:AK80" },
  { name: "Refined_Robust", range: "A1:T50" },
  { name: "Refined_Comparison", range: "A1:AA50" },
  { name: "Refined_Facilities", range: "A1:AN60" },
  { name: "Refined_Resources", range: "A1:AV60" },
  "Sources", "CSV_Manifest",
];
for (let i = 0; i < renderSheets.length; i += 1) {
  const spec = typeof renderSheets[i] === "string" ? { name: renderSheets[i] } : renderSheets[i];
  const sheetName = spec.name;
  const preview = await workbook.render({ sheetName, ...(spec.range ? { range: spec.range } : {}), autoCrop: "all", scale: 0.8, format: "png" });
  const safe = sheetName.replace(/[^A-Za-z0-9_]/g, "_");
  await fs.writeFile(path.join(renderDir, `${String(i + 1).padStart(2, "0")}_${safe}.png`), new Uint8Array(await preview.arrayBuffer()));
}

console.log(JSON.stringify({
  workbook: path.join(outputDir, "Capital_Allocation_Baseline_Audit.xlsx"),
  renderedSheets: renderSheets.length,
  sourceFiles: inputSheets.length + auxiliaryFiles.length,
  errorScan,
}, null, 2));
