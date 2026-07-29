#!/usr/bin/env python3
"""Section headings as SVG: a lowercase mono label with a hairline rule
running to the right edge — the only way to get a custom typeface on a
heading, since <style>/inline <svg>/@font-face in raw markdown are all
stripped by GitHub's sanitiser.
"""
from pathlib import Path

from svg_common import DIM, FG, RULE, esc, font_faces, svg_close

ASSETS = Path(__file__).resolve().parent.parent / "assets"

W = 800
H = 30
FONT_SIZE = 15
PAD_L = 2
LABEL_GAP = 14


def render_heading(label: str) -> str:
    text_w = len(label) * FONT_SIZE * 0.6
    rule_x = PAD_L + text_w + LABEL_GAP
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
            f"<defs>{font_faces('headings.woff2')}</defs>",
            f'<text x="{PAD_L}" y="{H - 9}" font-family="HeadMono, monospace" '
            f'font-size="{FONT_SIZE}" fill="{FG}">{esc(label)}</text>',
            f'<line x1="{rule_x:.1f}" y1="{H/2:.1f}" x2="{W - 2}" y2="{H/2:.1f}" '
            f'stroke="{RULE}" stroke-width="1"/>',
            svg_close(),
        ]
    )


HEADINGS = ["about", "live stats", "how this works", "credits"]


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for label in HEADINGS:
        slug = label.replace(" ", "-")
        out = ASSETS / f"heading-{slug}.svg"
        out.write_text(render_heading(label), encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
