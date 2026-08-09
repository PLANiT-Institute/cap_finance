from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


DATA_PATTERN = re.compile(
    r'<script id="data" type="application/json">(.*?)</script>', re.DOTALL
)
HANGUL_PATTERN = re.compile(r"[\uac00-\ud7a3]")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload(html: str) -> Any:
    match = DATA_PATTERN.search(html)
    if not match:
        raise ValueError("Embedded dashboard JSON was not found")
    return json.loads(match.group(1))


def compare_structure(korean: Any, english: Any, path: str = "$") -> tuple[int, int]:
    """Verify structure and every non-string value; return leaf and translated counts."""

    if type(korean) is not type(english):
        raise ValueError(f"Type mismatch at {path}: {type(korean)} != {type(english)}")
    if isinstance(korean, dict):
        if korean.keys() != english.keys():
            raise ValueError(f"Dictionary keys differ at {path}")
        leaves = translated = 0
        for key in korean:
            child_leaves, child_translated = compare_structure(
                korean[key], english[key], f"{path}.{key}"
            )
            leaves += child_leaves
            translated += child_translated
        return leaves, translated
    if isinstance(korean, list):
        if len(korean) != len(english):
            raise ValueError(f"List length differs at {path}")
        leaves = translated = 0
        for index, (ko_item, en_item) in enumerate(zip(korean, english)):
            child_leaves, child_translated = compare_structure(
                ko_item, en_item, f"{path}[{index}]"
            )
            leaves += child_leaves
            translated += child_translated
        return leaves, translated
    if isinstance(korean, str):
        return 1, int(korean != english)
    if korean != english:
        raise ValueError(f"Non-string value differs at {path}: {korean!r} != {english!r}")
    return 1, 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate parity between Korean and English standalone dashboards."
    )
    parser.add_argument("--korean", type=Path, default=Path("outputs/dashboard.html"))
    parser.add_argument(
        "--english", type=Path, default=Path("outputs/dashboard_en.html")
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/bilingual_dashboard_audit.json"),
    )
    args = parser.parse_args()

    korean_html = args.korean.read_text(encoding="utf-8")
    english_html = args.english.read_text(encoding="utf-8")
    if HANGUL_PATTERN.search(english_html):
        raise ValueError("English dashboard still contains Hangul")
    required_markers = (
        '<html lang="en">',
        "Decision efficient frontier",
        "Asset-level transition execution map",
        "P50 net economic cost bridge",
        "Same portfolio across scenarios",
        'href="dashboard.html">Korean</a>',
    )
    missing = [marker for marker in required_markers if marker not in english_html]
    if missing:
        raise ValueError(f"English UI markers missing: {missing}")

    leaf_count, translated_string_count = compare_structure(
        payload(korean_html), payload(english_html)
    )
    report = {
        "status": "PASS",
        "korean_dashboard": {
            "path": str(args.korean.resolve()),
            "size_bytes": args.korean.stat().st_size,
            "sha256": sha256(args.korean),
        },
        "english_dashboard": {
            "path": str(args.english.resolve()),
            "size_bytes": args.english.stat().st_size,
            "sha256": sha256(args.english),
            "hangul_character_count": len(HANGUL_PATTERN.findall(english_html)),
        },
        "embedded_payload": {
            "structure_identical": True,
            "all_non_string_values_identical": True,
            "leaf_value_count": leaf_count,
            "translated_string_value_count": translated_string_count,
        },
        "required_english_ui_markers": list(required_markers),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
