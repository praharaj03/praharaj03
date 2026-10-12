#!/usr/bin/env python3
"""Generate animated terminal-style SVG art for the GitHub profile README.

To use a different portrait later, change AVATAR_URL below to a public image URL.
The default uses the GitHub profile avatar, so no image upload is required.
"""
from datetime import date, timedelta
from html import escape
from io import BytesIO
from pathlib import Path
import re
import urllib.request
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

USERNAME = "praharaj03"
AVATAR_URL = f"https://github.com/{USERNAME}.png?size=256"
BG, PANEL, BORDER = "#0d1117", "#111820", "#263341"
TEXT, MUTED, GREEN, BLUE = "#c9d1d9", "#7d8b99", "#00e5a8", "#58a6ff"
RAMP = " .:-=+*#%@"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-art/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()

def save_ascii_portrait():
    lines = []
    try:
        im = Image.open(BytesIO(fetch(AVATAR_URL))).convert("RGB")
        im = ImageOps.fit(im, (54, 54)).convert("L")
        for y in range(0, 54, 2):
            lines.append("".join(RAMP[min(len(RAMP)-1, im.getpixel((x, y)) * len(RAMP) // 256)] for x in range(54)))
    except Exception as exc:
        lines = ["Could not load GitHub avatar.", "Check AVATAR_URL and rerun the workflow."]
    row_svg = []
    for i, line in enumerate(lines):
        row_svg.append(
            f'<text x="18" y="{56 + i * 9}" fill="{TEXT}" font-family="monospace" font-size="8" '
            f'xml:space="preserve" opacity="0"><animate attributeName="opacity" from="0" to="1" '
            f'begin="{i * 0.055:.3f}s" dur="0.18s" fill="freeze"/>{escape(line)}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="570" viewBox="0 0 520 570">
<rect width="520" height="570" rx="16" fill="{BG}"/><rect x="1" y="1" width="518" height="568" rx="15" fill="none" stroke="{BORDER}"/>
<rect width="520" height="42" rx="16" fill="{PANEL}"/><path d="M0 42H520" stroke="{BORDER}"/>
<circle cx="20" cy="21" r="5" fill="#ff5f56"/><circle cx="38" cy="21" r="5" fill="#ffbd2e"/><circle cx="56" cy="21" r="5" fill="#27c93f"/>
<text x="76" y="25" fill="{MUTED}" font-family="monospace" font-size="12">abhisek@github: ~/portrait</text>
{''.join(row_svg)}
<text x="18" y="550" fill="{GREEN}" font-family="monospace" font-size="11">[ profile avatar → ASCII ]</text></svg>'''
    (ASSETS / "avi-ascii.svg").write_text(svg, encoding="utf-8")

def save_info_card():
    fields = [
        ("NAME", "Abhisek Praharaj", GREEN),
        ("ROLE", "B.Tech CSE • Developer", TEXT),
        ("FOCUS", "Java • DSA • Next.js • AI", TEXT),
        ("INTERESTS", "Web • Backend • Problem solving", TEXT),
        ("PORTFOLIO", "praharajdev.vercel.app", BLUE),
        ("CURRENT MODE", "learn / build / ship", GREEN),
    ]
    items, y = [], 112
    for i, (key, value, color) in enumerate(fields):
        items.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{0.25 + i * 0.22:.2f}s" dur="0.35s" fill="freeze"/>'
                     f'<text x="28" y="{y}" fill="{MUTED}" font-family="monospace" font-size="12">{key}</text>'
                     f'<text x="28" y="{y+23}" fill="{color}" font-family="monospace" font-size="15">{escape(value)}</text></g>')
        y += 65
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="570" viewBox="0 0 600 570">
<rect width="600" height="570" rx="16" fill="{BG}"/><rect x="1" y="1" width="598" height="568" rx="15" fill="none" stroke="{BORDER}"/>
<rect width="600" height="42" rx="16" fill="{PANEL}"/><path d="M0 42H600" stroke="{BORDER}"/>
<circle cx="20" cy="21" r="5" fill="#ff5f56"/><circle cx="38" cy="21" r="5" fill="#ffbd2e"/><circle cx="56" cy="21" r="5" fill="#27c93f"/>
<text x="76" y="25" fill="{MUTED}" font-family="monospace" font-size="12">abhisek@github — neofetch</text>
<text x="28" y="76" fill="{GREEN}" font-family="monospace" font-size="18" font-weight="bold">abhisek@github</text>
<text x="28" y="92" fill="{MUTED}" font-family="monospace" font-size="11">--------------------</text>
{''.join(items)}
<text x="28" y="540" fill="{MUTED}" font-family="monospace" font-size="11">Code. Learn. Build. Repeat.</text></svg>'''
    (ASSETS / "info-card.svg").write_text(svg, encoding="utf-8")

def save_heatmap():
    url = f"https://github.com/users/{USERNAME}/contributions"
    try:
        page = fetch(url).decode("utf-8", "replace")
    except Exception:
        page = ""
    cells = re.findall(r'<(?:td|rect)\b[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', page)
    if not cells:
        cells = [(d, level) for level, d in re.findall(r'<(?:td|rect)\b[^>]*data-level="(\d)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', page)]
    data = {d: int(level) for d, level in cells}
    today = date.today()
    start = today - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    rects = []
    for offset in range(371):
        current = start + timedelta(days=offset)
        if current > today:
            continue
        x, y = 25 + (offset // 7) * 12, 48 + (offset % 7) * 12
        level = data.get(current.isoformat(), 0)
        rects.append(f'<rect x="{x}" y="{y}" width="9" height="9" rx="2" fill="{palette[level]}" opacity="0.15"><title>{current.isoformat()} — level {level}</title><animate attributeName="opacity" from="0.15" to="1" begin="{offset * 0.006:.3f}s" dur="0.25s" fill="freeze"/></rect>')
    note = "Live contribution levels parsed from GitHub" if data else "No contribution cells parsed — check GitHub markup or rerun"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="160" viewBox="0 0 720 160">
<rect width="720" height="160" rx="12" fill="{BG}"/><rect x="1" y="1" width="718" height="158" rx="11" fill="none" stroke="{BORDER}"/>
<text x="24" y="25" fill="{TEXT}" font-family="Arial,sans-serif" font-size="14" font-weight="bold">Contribution activity · last 12 months</text>
{''.join(rects)}
<text x="24" y="146" fill="{MUTED}" font-family="Arial,sans-serif" font-size="10">{escape(note)}</text>
<text x="565" y="146" fill="{MUTED}" font-family="Arial,sans-serif" font-size="10">Less</text>
{''.join(f'<rect x="{600+i*14}" y="137" width="10" height="10" rx="2" fill="{c}"/>' for i,c in enumerate(palette))}
<text x="678" y="146" fill="{MUTED}" font-family="Arial,sans-serif" font-size="10">More</text></svg>'''
    (ASSETS / "contrib-heatmap.svg").write_text(svg, encoding="utf-8")

if __name__ == "__main__":
    save_ascii_portrait()
    save_info_card()
    save_heatmap()
