"""Prepare embedded fonts and equation images for the ReportLab manuscript builder.

Run with the repository Python, which supplies matplotlib and fontTools.
"""
import json
from pathlib import Path
import re
import subprocess

import matplotlib
matplotlib.use("Agg")
from matplotlib import mathtext, font_manager
from fontTools.ttLib import TTCollection, TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp/pdfs/methodology"
OUT.mkdir(parents=True, exist_ok=True)
fonts = {}
for family, stem in [("Nanum Myeongjo", "Body"), ("Nanum Gothic", "Heading")]:
    path = subprocess.check_output(["fc-match", "-f", "%{file}", family], text=True)
    collection = TTCollection(path)
    for index, suffix in [(0, ""), (1, "Bold")]:
        name = stem + suffix
        target = OUT / f"{name}.ttf"
        collection.fonts[index].save(target)
        fonts[name] = str(target)
fonts["Fallback"] = font_manager.findfont("DejaVu Sans")
# Body and table fonts have different CJK coverage. A character present only
# in Body must not silently render as a missing glyph inside a Heading cell.
fonts["FallbackCJK"] = subprocess.check_output(
    ["fc-match", "-f", "%{file}", "Arial Unicode MS"], text=True)
maps = {}
for name, path in fonts.items():
    font = TTFont(path)
    maps[name] = set(font.getBestCmap())
    font.close()
cmap = sorted(set.intersection(*(maps[n] for n in ["Body", "BodyBold", "Heading", "HeadingBold"])))
matplotlib.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
text = (ROOT / "paper/methodology/TCaR_METHOD_KO.md").read_text()
equations = []
for i, match in enumerate(re.finditer(r"\\\[(.*?)\\\]", text, re.S), 1):
    latex = re.sub(r"\\tag\{\d+\}", "", match[1]).strip()
    latex = latex.replace(r"\mathbb R", r"\mathbb{R}")
    latex = re.sub(r"\\mathcal ([A-Za-z])", r"\\mathcal{\1}", latex)
    latex = re.sub(r"\\le(?![A-Za-z])", r"\\leq ", latex)
    latex = re.sub(r"\\ne\b", r"\\neq", latex)
    latex = latex.replace(r"\frac", r"\dfrac")
    lines = [v.strip() for v in latex.splitlines() if v.strip()]
    if i in (1, 2, 5):
        lines = [lines[0] + lines[1]] + lines[2:]
    images = []
    for j, line in enumerate(lines):
        target = OUT / f"equation_{i}_{j}.png"
        mathtext.math_to_image(f"${line}$", target, dpi=240,
                              prop=font_manager.FontProperties(size=13), format="png")
        images.append(str(target))
    equations.append({"number": i, "images": images})
(OUT / "assets.json").write_text(json.dumps({"fonts": fonts, "body_cmap": cmap,
                                            "fallback_cmap": sorted(maps["Fallback"]),
                                            "fallback_cjk_cmap": sorted(maps["FallbackCJK"]),
                                            "equations": equations}, indent=2))
print(f"Prepared {len(equations)} equations and embedded font faces.")
