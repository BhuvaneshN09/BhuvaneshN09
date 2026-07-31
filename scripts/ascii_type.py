"""Shared row-by-row typing animation: a grid of ASCII-ramp characters,
each row revealed by an animated clipPath wipe with a cursor block riding
the edge, staggered top to bottom, fill="freeze" so it plays once."""
import base64
from pathlib import Path

FONTS = Path(__file__).resolve().parent.parent / "fonts"

# Dark end last: brightness 255 (white/background) -> ' ', 0 (black) -> '@'.
RAMP = " .`:-=+*cs#%@"

CHAR_W = 7.74
FONT_SIZE = 12.9
LINE_HEIGHT = CHAR_W * 2 * 0.833  # ~1.667 * font-size, matches monospace vertical rhythm
FILL = "#c9d1d9"


def _b64(name: str) -> str:
    return base64.b64encode((FONTS / name).read_bytes()).decode("ascii")


def font_face_css() -> str:
    return f"""
    <style>
      @font-face {{
        font-family: 'RampMono';
        src: url(data:font/woff2;base64,{_b64('ramp.woff2')}) format('woff2');
        font-weight: 400; font-style: normal;
      }}
      text {{ font-family: 'RampMono', monospace; font-size: {FONT_SIZE}px; fill: {FILL}; white-space: pre; }}
    </style>"""


def render_svg(lines: list[str], cols: int) -> str:
    width = cols * CHAR_W
    height = len(lines) * LINE_HEIGHT
    defs = []
    rows = []
    for i, line in enumerate(lines):
        y = (i + 1) * LINE_HEIGHT - LINE_HEIGHT * 0.25
        clip_id = f"clip{i}"
        text_w = len(line) * CHAR_W
        begin = round(i * 0.09, 2)
        esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        defs.append(f"""
    <clipPath id="{clip_id}">
      <rect x="0" y="{y - LINE_HEIGHT:.2f}" width="0" height="{LINE_HEIGHT * 2:.2f}">
        <animate attributeName="width" from="0" to="{text_w:.2f}" begin="{begin}s" dur="0.5s" fill="freeze" />
      </rect>
    </clipPath>""")

        rows.append(f"""
    <g clip-path="url(#{clip_id})">
      <text x="0" y="{y:.2f}" xml:space="preserve">{esc}</text>
      <rect x="0" y="{y - LINE_HEIGHT * 0.75:.2f}" width="{CHAR_W:.2f}" height="{LINE_HEIGHT * 0.9:.2f}" fill="{FILL}">
        <animate attributeName="x" from="0" to="{text_w:.2f}" begin="{begin}s" dur="0.5s" fill="freeze" />
        <set attributeName="opacity" to="0" begin="{begin + 0.5}s" fill="freeze" />
      </rect>
    </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" width="460">
  <defs>{font_face_css()}
{"".join(defs)}
  </defs>
  <rect width="100%" height="100%" fill="none" />
{"".join(rows)}
</svg>"""
