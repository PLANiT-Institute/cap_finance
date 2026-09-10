"""Typeset the current Korean methodology draft with ReportLab.

Prepare assets with the repository Python first; run this file with the bundled
document Python (reportlab). This creates a draft, not a validation certificate.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from xml.sax.saxutils import escape, quoteattr

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, PageBreak

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp/pdfs/methodology"
SOURCE = ROOT / "paper/methodology/TCaR_METHOD_KO.md"
VERSION = re.search(r'연구 원고 (v[0-9.]+)', SOURCE.read_text()).group(1)
_date = re.search(r'연구 원고 v[0-9.]+ · (\d{4})년 (\d+)월 (\d+)일', SOURCE.read_text())
DOCUMENT_DATE = '-'.join(f'{int(v):02d}' for v in _date.groups())
OUT = ROOT / "output/pdf/TCaR_methodology.pdf"
assets = json.loads((TMP / "assets.json").read_text())
for name, path in assets["fonts"].items():
    pdfmetrics.registerFont(TTFont(name, path))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold", italic="Body", boldItalic="BodyBold")
pdfmetrics.registerFontFamily("Heading", normal="Heading", bold="HeadingBold", italic="Heading", boldItalic="HeadingBold")
cmap = set(assets["body_cmap"])
fallback_cmap = set(assets.get("fallback_cmap", []))
fallback_cjk_cmap = set(assets.get("fallback_cjk_cmap", []))
ink, blue = colors.HexColor("#172432"), colors.HexColor("#234e72")
W = A4[0] - 108
styles = {
    "body": ParagraphStyle("body", fontName="Body", fontSize=9.6, leading=15.5,
                           textColor=ink, spaceAfter=7, wordWrap="CJK", allowWidows=0, allowOrphans=0),
    "title": ParagraphStyle("title", fontName="HeadingBold", fontSize=20, leading=27,
                            spaceAfter=9, textColor=blue, wordWrap="CJK", keepWithNext=True),
    "subtitle": ParagraphStyle("subtitle", fontName="Heading", fontSize=12.4, leading=18,
                               spaceAfter=14, textColor=ink, wordWrap="CJK", keepWithNext=True),
    "h2": ParagraphStyle("h2", fontName="HeadingBold", fontSize=13.5, leading=19,
                         spaceBefore=15, spaceAfter=8, textColor=blue, wordWrap="CJK", keepWithNext=True),
    "h3": ParagraphStyle("h3", fontName="HeadingBold", fontSize=10.7, leading=16,
                         spaceBefore=10, spaceAfter=6, textColor=ink, wordWrap="CJK", keepWithNext=True),
    "cell": ParagraphStyle("cell", fontName="Heading", fontSize=8.2, leading=12,
                           textColor=ink, wordWrap="CJK"),
    "caption": ParagraphStyle("caption", fontName="Heading", fontSize=8.3, leading=12.5,
                              spaceBefore=5, spaceAfter=9, textColor=ink, wordWrap="CJK"),
    "reference": ParagraphStyle("reference", fontName="Body", fontSize=8.6, leading=12.2,
                                leftIndent=13, firstLineIndent=-13, spaceAfter=4,
                                textColor=ink, wordWrap="CJK", allowWidows=0, allowOrphans=0),
    "note": ParagraphStyle("note", fontName="Heading", fontSize=8.6, leading=13.5,
                           borderColor=colors.HexColor("#d8e2eb"), borderWidth=.6,
                           backColor=colors.HexColor("#f3f6f8"), borderPadding=8,
                           spaceBefore=4, spaceAfter=14, textColor=ink, wordWrap="CJK"),
}


def plain(value):
    value = value.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    def glyphs(part):
        result = []
        for ch in part:
            if ord(ch) in cmap or ord(ch) < 128:
                result.append(escape(ch))
            elif ord(ch) in fallback_cjk_cmap:
                result.append(f'<font name="FallbackCJK">{escape(ch)}</font>')
            elif ord(ch) in fallback_cmap:
                result.append(f'<font name="Fallback">{escape(ch)}</font>')
            else:
                raise ValueError(f'No embedded font supports U+{ord(ch):04X}: {ch}')
        return "".join(result)
    superscripts = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
    return "".join(f'<super>{part.translate(superscripts)}</super>'
                   if re.fullmatch(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+", part) else glyphs(part)
                   for part in re.split(r"([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", value))


def inline(value):
    token = re.compile(r"\[[^\]]+\]\((?:[^()]|\([^()]*\))*\)|\*\*.+?\*\*|`[^`]+`|\*[^*]+\*")
    parts, cursor = [], 0
    for m in token.finditer(value):
        parts.append(plain(value[cursor:m.start()]))
        v = m.group()
        if v.startswith("["):
            label, href = re.fullmatch(r"\[([^\]]+)\]\((.*)\)", v).groups()
            parts.append(f'<link href={quoteattr(href)} color="#234e72">{plain(label)}</link>')
        elif v.startswith("**"):
            parts.append(f'<b>{plain(v[2:-2])}</b>')
        elif v.startswith("`"):
            parts.append(f'<font name="Heading">{plain(v[1:-1])}</font>')
        else:
            parts.append(plain(v[1:-1]))
        cursor = m.end()
    parts.append(plain(value[cursor:]))
    return "".join(parts)


def para(value, kind="body"):
    return Paragraph(inline(value), styles[kind])


def equation(number):
    lines = []
    for path in assets["equations"][number - 1]["images"]:
        width, height = PILImage.open(path).size
        scale = min(72/240, (W - 42)/width)
        im = Image(path, width=width*scale, height=height*scale)
        im.hAlign = "CENTER"
        lines.extend([im, Spacer(1, 3)])
    table = Table([[lines, para(f"({number})", "cell")]], colWidths=[W-32,32])
    table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                               ("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("TOPPADDING",(0,0),(-1,-1),5),
                               ("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    return table


def make_table(lines):
    rows = [[v.strip() for v in line.strip().strip("|").split("|")]
            for line in lines if not re.match(r"^\|[\s:|-]+\|$", line)]
    n = len(rows[0])
    def est(cell):  # display-length estimate: CJK ~1.8 units, ASCII 1
        return sum(1.8 if ord(ch) > 0x2E80 else 1 for ch in re.sub(r"[`*]", "", cell))
    # column need = longest cell, header weighted lower because it may wrap; clamp so no column starves
    need = [max([est(r[j]) for r in rows[1:]] + [0.7*est(rows[0][j])]) for j in range(n)]
    need = [min(max(v, 6), 42) for v in need]
    widths = [W*v/sum(need) for v in need]
    if rows[0] == ['전력 사양', '기존 논문 2025', 'DEA 2025', '기존 논문 2050', 'DEA 2050']:
        widths = [W*.32] + [W*.17]*4
    assert all(len(row)==n for row in rows), 'Unequal table row lengths'
    data = [[para(v, "cell") for v in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e8eff4")),
        ("LINEABOVE",(0,0),(-1,0),.8,blue),
        ("LINEBELOW",(0,0),(-1,0),.5,blue),
        ("LINEBELOW",(0,-1),(-1,-1),.6,blue),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f7f9fa")]),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),6)]))
    return KeepTogether([Spacer(1,5),t,Spacer(1,9)])


def page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Heading",7.3)
        canvas.setFillColor(colors.HexColor("#74818b"))
        canvas.drawString(54,A4[1]-31,"TCaR | 기후 전환비용의 불확실성과 기업 내 효율경계")
    canvas.setStrokeColor(colors.HexColor("#d7dfe5"))
    canvas.line(54,37,A4[0]-54,37)
    canvas.setFont("Heading",7.2)
    canvas.setFillColor(colors.HexColor("#74818b"))
    canvas.drawString(54,25,f"TCaR 방법론 {VERSION} | 조건부 사례·공정 사양·공동 가격분포 | {DOCUMENT_DATE}")
    canvas.drawRightString(A4[0]-54,25,str(doc.page))
    canvas.restoreState()


def main():
    text = SOURCE.read_text()
    text = re.sub(r"\\\[(.*?)\\\]", lambda m: "\nEQUATION:"+re.search(r"\\tag\{(\d+)\}",m[1])[1]+"\n", text, flags=re.S)
    lines, story, i = text.splitlines(), [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            table = []
            while i < len(lines) and lines[i].startswith("|"):
                table.append(lines[i]); i += 1
            story.append(make_table(table))
            continue
        if line.startswith("EQUATION:"):
            story.append(equation(int(line.split(":")[1])))
        elif line.startswith("!["):
            reference=re.fullmatch(r'!\[[^\]]*\]\((.+)\)',line).group(1)
            p=(SOURCE.parent/reference).resolve()
            width,height = PILImage.open(p).size
            im = Image(str(p),width=W,height=W*height/width)
            im.keepWithNext = True
            story.append(im)
        elif line.startswith("# "):
            story.append(para(line[2:],"title"))
        elif line.startswith("## "):
            if line[3:].startswith("참고문헌"):
                story.append(PageBreak())
            story.append(para(line[3:],"subtitle" if "Transition Cost" in line else "h2"))
        elif line.startswith("### "):
            story.append(para(line[4:],"h3"))
        elif re.match(r"^\d+\. ",line):
            story.append(KeepTogether([para(line,"reference")]))
        else:
            body = [line]
            while i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(("#","|","![","EQUATION:")):
                i += 1; body.append(lines[i].strip())
            joined = " ".join(body)
            kind = "note" if joined.startswith("**연구 원고") else "caption" if joined.startswith(("**그림", "**표", "v2 자료와 변환 근거는", "문헌 확인 범위")) else "body"
            paragraph = para(joined,kind)
            next_content = next((v.strip() for v in lines[i+1:] if v.strip()), "")
            if next_content.startswith("EQUATION:"):
                paragraph.keepWithNext = True
            story.append(paragraph)
        i += 1
    OUT.parent.mkdir(parents=True,exist_ok=True)
    doc = SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=54,rightMargin=54,
                            topMargin=48,bottomMargin=49,title="TCaR 방법론과 조건부 산업 사례",
                            author="CAP research project")
    doc.build(story,onFirstPage=page,onLaterPages=page)
    print(OUT)


if __name__ == "__main__":
    main()
