#!/usr/bin/env python3
"""Generate the profile's animated terminal-style ASCII portrait from photo-input/."""

from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "photo-input"
OUTPUT = ROOT / "assets" / "avi-ascii.svg"
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
CHARS = "  .`'^\",:;Il!i><~+_-?][}{1)(|\\/*tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
COLS = 72
CELL_H = 10
FONT_SIZE = 9
SVG_WIDTH = 540
LEFT = 18
TOP = 58


def last_commit_time(path: Path) -> int:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        return int(result.stdout.strip() or "0")
    except (subprocess.CalledProcessError, ValueError):
        return 0


def latest_photo() -> Path:
    photos = [p for p in INPUT_DIR.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED]
    if not photos:
        raise SystemExit(
            "No photo found. Upload a .jpg, .jpeg, .png, .webp, or .bmp file into photo-input/."
        )
    return max(photos, key=lambda p: (last_commit_time(p), p.name.lower()))


def escape_xml(text: str) -> str:
    return html.escape(text, quote=False)


def main() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    photo = latest_photo()

    try:
        with Image.open(photo) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
            width, height = image.size
            # Compensate for the proportions of monospace characters.
            rows = max(18, min(70, round(COLS * height / max(width, 1) * 0.56)))
            image = ImageOps.fit(image, (COLS, rows), method=Image.Resampling.LANCZOS,
                                 centering=(0.5, 0.45)).convert("L")
            pixels = list(image.getdata())
    except Exception as exc:
        raise SystemExit(f"Could not read {photo.name}: {exc}") from exc

    lines = []
    for y in range(rows):
        chars = []
        for x in range(COLS):
            brightness = pixels[y * COLS + x]
            index = round((255 - brightness) / 255 * (len(CHARS) - 1))
            chars.append(CHARS[index])
        lines.append("".join(chars))

    svg_height = TOP + rows * CELL_H + 46
    title = f"Photo source: photo-input/{photo.name}"
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{svg_height}" viewBox="0 0 {SVG_WIDTH} {svg_height}">',
        f'<rect width="{SVG_WIDTH}" height="{svg_height}" rx="16" fill="#0d1117"/>',
        f'<rect x="1" y="1" width="{SVG_WIDTH-2}" height="{svg_height-2}" rx="15" fill="none" stroke="#263341"/>',
        f'<rect width="{SVG_WIDTH}" height="42" rx="16" fill="#111820"/>',
        f'<path d="M0 42H{SVG_WIDTH}" stroke="#263341"/>',
        '<circle cx="20" cy="21" r="5" fill="#ff5f56"/>',
        '<circle cx="38" cy="21" r="5" fill="#ffbd2e"/>',
        '<circle cx="56" cy="21" r="5" fill="#27c93f"/>',
        '<text x="76" y="25" fill="#7d8b99" font-family="monospace" font-size="12">abhisek@github: ~/portrait</text>',
    ]

    for i, line in enumerate(lines):
        delay = i * 0.035
        svg.append(
            f'<text x="{LEFT}" y="{TOP + i * CELL_H}" fill="#c9d1d9" '
            f'font-family="monospace" font-size="{FONT_SIZE}" xml:space="preserve" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" '
            f'dur="0.16s" fill="freeze"/>{escape_xml(line)}</text>'
        )

    footer_y = svg_height - 18
    svg.append(
        f'<text x="18" y="{footer_y}" fill="#00e5a8" font-family="monospace" font-size="11">'
        f'[ ASCII portrait generated automatically ]</text>'
    )
    svg.append("</svg>")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)} from {photo.relative_to(ROOT)} ({COLS}x{rows} characters).")


if __name__ == "__main__":
    main()
