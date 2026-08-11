"""Render docs/TECHNICAL_GUIDE.md as web/guide.html — the Arc-facing page.

The markdown file stays the master. This script only renders it: it never invents
a number and never edits the source. Relative links (which point at repository
files) are rewritten to GitHub blob URLs, because on the website there is no
`../METHODOLOGY.md` to reach.

The markdown subset here is exactly what the guide uses — headings, tables,
fenced code, blockquotes, ordered/unordered lists with lazy continuation, and
inline code/bold/italic/links. `--check` re-renders and verifies that every
source heading, table row and code block survived, so a construct the renderer
does not understand fails the build instead of disappearing from the page.

    .venv/bin/python scripts/build_guide_page.py [--check]
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _style import CSS  # noqa: E402

WEB = ROOT / "web"
GUIDE = ROOT / "docs" / "TECHNICAL_GUIDE.md"
BLOB = "https://github.com/PLANiT-Institute/cap_finance/blob/main"
DOCTYPE = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>')


def link_target(href: str) -> str:
    """docs/-relative repository link → GitHub blob URL. External links pass through."""
    if href.startswith(("http://", "https://", "#")):
        return href
    if href.startswith("../"):
        return f"{BLOB}/{href[3:]}"
    return f"{BLOB}/docs/{href}"


def inline(text: str) -> str:
    """Inline markdown. Code spans are extracted first so their contents stay literal."""
    spans: list[str] = []

    def stash(m: re.Match) -> str:
        spans.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{link_target(m.group(2))}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<i>\1</i>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


def slug(text: str) -> str:
    s = re.sub(r"[^\w\s.-]", "", re.sub(r"[`*]", "", text)).strip().lower()
    return re.sub(r"[\s.]+", "-", s)


IMG = re.compile(r"^!\[([^\]]*)\]\(([^)]+\.svg)\)$")
ROW = re.compile(r"^\s*\|")
SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
ITEM = re.compile(r"^([-*]|\d+\.)\s+(.*)$")


def cells(line: str) -> list[str]:
    """Split on unescaped pipes only — `\\|` is a literal pipe inside a cell, not a boundary."""
    return [c.strip().replace("\\|", "|")
            for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def render(md: str) -> tuple[str, list[tuple[int, str, str]]]:
    lines = md.splitlines()
    out: list[str] = []
    toc: list[tuple[int, str, str]] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if not s:
            i += 1
        elif s.startswith("```"):                                     # fenced code
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif s.startswith("<!-- GEN:"):     # generated block — label it, the reader should know
            name = s[len("<!-- GEN:"):].split("-->")[0].strip()
            out.append(f'<div class="gen"><div class="genlab">generated · {html.escape(name)}'
                       f'</div>')
            i += 1
        elif s.startswith("<!-- /GEN:"):
            out.append("</div>")
            i += 1
        elif s.startswith("<!--"):
            out.append(s)
            i += 1
        elif s.startswith("#"):                                       # heading
            level = len(s) - len(s.lstrip("#"))
            title = s[level:].strip()
            anchor = slug(title)
            if level in (2, 3):
                toc.append((level, anchor, re.sub(r"[`*]", "", title)))
            tag = f"h{min(level, 4)}"
            out.append(f'<{tag} id="{anchor}">{inline(title)}</{tag}>')
            i += 1
        elif s.startswith("---") and set(s) == {"-"}:                 # rule
            out.append("<hr>")
            i += 1
        elif s.startswith(">"):                                       # blockquote
            j = i
            body = []
            while j < len(lines) and lines[j].strip().startswith(">"):
                body.append(lines[j].strip().lstrip(">").strip())
                j += 1
            out.append(f'<blockquote>{inline(" ".join(body))}</blockquote>')
            i = j
        elif IMG.match(s):                                            # figure — inline the SVG
            alt, src = IMG.match(s).groups()
            svg = (GUIDE.parent / src)
            if not svg.exists():
                raise ValueError(f"line {i + 1}: figure {src} is referenced but not built")
            out.append(f'<figure role="img" aria-label="{html.escape(alt)}">'
                       f'{svg.read_text(encoding="utf-8")}</figure>')
            i += 1
        elif ROW.match(ln):                                           # table
            j = i
            while j < len(lines) and ROW.match(lines[j]):
                j += 1
            block = [c for c in lines[i:j] if not SEP.match(c)]
            head, *body = block
            t = ['<div class="tblwrap"><table><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in cells(head)]
            t.append("</tr></thead><tbody>")
            width = len(cells(head))
            for r in body:
                c = cells(r)
                if len(c) != width:
                    raise ValueError(f"line {i + 1}: {len(c)} cells under a {width}-column "
                                     f"header — an unescaped `|` inside a cell?\n  {r}")
                t.append("<tr>" + "".join(f"<td>{inline(x)}</td>" for x in c) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            i = j
        elif ITEM.match(s):                                           # list, lazy continuation
            ordered = ITEM.match(s).group(1).endswith(".")
            items: list[str] = []
            while i < len(lines) and lines[i].strip():
                m = ITEM.match(lines[i].strip())
                if m:
                    items.append(m.group(2))
                elif items and lines[i][:1] in (" ", "\t"):
                    items[-1] += " " + lines[i].strip()
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        else:                                                         # paragraph
            body = []
            while i < len(lines) and lines[i].strip() and not (
                    ROW.match(lines[i]) or lines[i].strip().startswith(("#", "```", ">", "<!--"))
                    or ITEM.match(lines[i].strip())):
                body.append(lines[i].strip())
                i += 1
            out.append(f'<p>{inline(" ".join(body))}</p>')
    return "\n".join(out), toc


def check(md: str, page: str) -> list[str]:
    """Every heading, table row and code fence in the source must reach the page."""
    problems = []
    src_rows = sum(1 for ln in md.splitlines() if ROW.match(ln) and not SEP.match(ln))
    got_rows = page.count("<tr>")
    if src_rows != got_rows:
        problems.append(f"table rows {src_rows} in markdown vs {got_rows} in HTML")
    src_fences = sum(1 for ln in md.splitlines() if ln.strip().startswith("```")) // 2
    if src_fences != page.count("<pre>"):
        problems.append(f"code blocks {src_fences} vs {page.count('<pre>')}")
    src_figs = sum(1 for ln in md.splitlines() if IMG.match(ln.strip()))
    if src_figs != page.count("<figure"):
        problems.append(f"figures {src_figs} in markdown vs {page.count('<figure')} in HTML")
    for ln in md.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            title = re.sub(r"[`*]", "", s.lstrip("#").strip())
            if html.escape(title.split("—")[0].strip()) not in page:
                problems.append(f"heading missing from page: {title}")
    return problems


PAGE = """<title>CAP — Technical Guide</title>
<style>
__CSS__
.layout{display:grid;grid-template-columns:minmax(0,1fr);gap:34px}
@media(min-width:1080px){.layout{grid-template-columns:236px minmax(0,1fr)}}
nav.toc{display:none}
@media(min-width:1080px){nav.toc{display:block;position:sticky;top:26px;align-self:start;
  max-height:calc(100vh - 52px);overflow-y:auto;font-size:12.5px;line-height:1.5}}
nav.toc a{display:block;color:var(--ink2);text-decoration:none;padding:2.5px 0}
nav.toc a:hover{color:var(--accent)}
nav.toc a.l3{padding-left:12px;color:var(--ink3);font-size:12px}
nav.toc .navhead{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink3);
  font-weight:700;margin-bottom:8px}
article{max-width:82ch}
article h2{font-size:22px;margin:54px 0 10px;font-weight:780;letter-spacing:-.01em;
  padding-top:14px;border-top:1px solid var(--line)}
article h3{font-size:16.5px;margin:34px 0 8px;font-weight:730}
article h4{font-size:14px;margin:22px 0 6px;font-weight:700;color:var(--ink2)}
article p{margin:11px 0;color:var(--ink2);font-size:14.5px}
article p b,article li b,td b{color:var(--ink)}
article ul,article ol{padding-left:20px;margin:11px 0}
article li{margin:5px 0;color:var(--ink2);font-size:14.5px;line-height:1.6}
article td{white-space:normal;text-align:left;font-size:13px;color:var(--ink2);vertical-align:top}
article th{text-align:left;white-space:normal}
article .tblwrap{margin:14px 0}
article code{font-size:12.5px;background:var(--panel2);border:1px solid var(--line);
  border-radius:5px;padding:1px 5px;color:var(--ink)}
article pre code{border:0;background:none;padding:0;font-size:12.5px}
article pre{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:14px 16px;overflow-x:auto;margin:14px 0;line-height:1.5}
article blockquote{margin:14px 0;padding:12px 16px;background:var(--panel);
  border-left:3px solid var(--accent);border-radius:0 10px 10px 0;font-size:13.5px;color:var(--ink2)}
article hr{border:0;border-top:1px solid var(--line);margin:30px 0}
article h1{display:none}
article figure{margin:18px 0;background:var(--panel);border:1px solid var(--line);
  border-radius:12px;padding:12px 10px}
article figure svg{width:100%;height:auto;display:block}
article .gen{border-left:2px solid var(--line);padding-left:16px;margin:16px 0}
article .gen .genlab{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink3);font-weight:700;margin-bottom:4px}
article .gen>p:first-of-type,article .gen>.tblwrap:first-of-type{margin-top:0}
</style>
<div class="wrap">
<div class="eyebrow">PLANiT Institute · CAP</div>
<h1>Capital Allocation Pathway — Technical Guide</h1>
<p class="lede">Rendered from <code>docs/TECHNICAL_GUIDE.md</code>. Blocks marked <i>generated</i>
are written by <code>scripts/build_tech_guide.py</code> from the live repository; everything else
is hand-written prose that points at the file behind it.</p>
<p class="lede" style="margin-top:10px"><a href="/">← CAP 홈</a> ·
<a href="__BLOB__/docs/TECHNICAL_GUIDE.md">markdown source</a> ·
<a href="__BLOB__/METHODOLOGY.md">METHODOLOGY.md</a></p>
<div class="layout" style="margin-top:36px">
<nav class="toc"><div class="navhead">Contents</div>__TOC__</nav>
<article>__BODY__</article>
</div>
<div class="footer">PLANiT Institute · generated from the repository · __STAMP__</div>
</div>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="render and verify, do not write")
    a = ap.parse_args()

    md = GUIDE.read_text(encoding="utf-8")
    body, toc = render(md)
    problems = check(md, body)
    if problems:
        print("[guide] 렌더가 원문을 잃었다:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    if a.check:
        print(f"[guide] ok — {len(toc)} sections, {body.count('<tr>')} table rows")
        return 0

    nav = "".join(f'<a class="l{lvl}" href="#{anc}">{html.escape(t)}</a>' for lvl, anc, t in toc)
    stamp = re.search(r"hash to `(\w+)`", md)
    page = (PAGE.replace("__CSS__", CSS).replace("__TOC__", nav).replace("__BODY__", body)
            .replace("__BLOB__", BLOB)
            .replace("__STAMP__", f"state {stamp.group(1)}" if stamp else "unstamped"))
    WEB.mkdir(exist_ok=True)
    (WEB / "guide.html").write_text(DOCTYPE + page + "</body></html>", encoding="utf-8")
    print(f"[guide] web/guide.html ({(WEB / 'guide.html').stat().st_size:,} bytes) — "
          f"{len(toc)} sections, {body.count('<tr>')} table rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
