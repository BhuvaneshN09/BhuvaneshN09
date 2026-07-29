#!/usr/bin/env python3
"""ASCII portrait generator: photo -> cutout -> contrast curve -> character ramp -> typing SVG.

Usage:
    python scripts/generate_portrait.py --input path/to/photo.jpg --output portrait.svg

If --input is omitted, a synthetic placeholder headshot is generated so the
pipeline can be exercised end-to-end before a real photo is available.
"""
import argparse
import base64
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

# Dark end last: v=255 (white/background) -> ' ', v=0 (black/shadow) -> '@'.
RAMP = " .`:-=+*cs#%@"

COLS = 90
CHAR_W = 7.74
FONT_SIZE = 12.9
LINE_HEIGHT = CHAR_W * 2 * 0.833  # ~1.667 * font-size, matches monospace vertical rhythm
FILL = "#c9d1d9"


def make_placeholder(size=1400):
    """Procedural side-lit grayscale headshot silhouette, used only when no
    real photo has been supplied yet. Swap in a real photo via --input."""
    h = w = size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h * 0.52
    # head as an ellipse
    head = (((xx - cx) / (w * 0.30)) ** 2 + ((yy - cy) / (h * 0.38)) ** 2) <= 1.0
    canvas = np.full((h, w), 255, dtype=np.float32)
    # side light: horizontal gradient across the head, left bright / right dark
    grad = (xx - (cx - w * 0.30)) / (w * 0.60)
    grad = np.clip(grad, 0, 1)
    skin = 235 - grad * 150
    canvas[head] = skin[head]
    # eyes
    for ex in (cx - w * 0.11, cx + w * 0.11):
        eye = (((xx - ex) / (w * 0.045)) ** 2 + ((yy - (cy - h * 0.03)) / (h * 0.025)) ** 2) <= 1.0
        canvas[eye] = np.minimum(canvas[eye], 60)
    # nose shadow
    nose = (np.abs(xx - (cx + w * 0.02)) < w * 0.012) & (yy > cy - h * 0.02) & (yy < cy + h * 0.08)
    canvas[nose] = np.minimum(canvas[nose], 140)
    # mouth
    mouth = (((xx - cx) / (w * 0.09)) ** 2 + ((yy - (cy + h * 0.16)) / (h * 0.02)) ** 2) <= 1.0
    canvas[mouth] = np.minimum(canvas[mouth], 120)
    return Image.fromarray(canvas.astype(np.uint8), mode="L").convert("RGB")


def remove_background(img: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError:
        return img
    cut = remove(img)
    bg = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    bg.paste(cut, mask=cut.split()[3])
    return bg.convert("RGB")


def enhance(img: Image.Image) -> np.ndarray:
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    arr = cv2.bilateralFilter(arr, d=9, sigmaColor=75, sigmaSpace=75)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    arr = clahe.apply(arr)
    # darkening curve: the fix that keeps glasses/brows/lips from washing out
    normalized = arr.astype(np.float32) / 255.0
    curved = np.power(normalized, 1.7) * 255.0
    return curved.astype(np.uint8)


def to_ascii_rows(gray: np.ndarray, cols: int = COLS) -> list[str]:
    h, w = gray.shape
    rows = max(1, round(cols * (h / w) * 0.48))
    small = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)
    n = len(RAMP) - 1
    lines = []
    for row in small:
        chars = [RAMP[int(((255 - int(v)) / 255) * n)] for v in row]
        lines.append("".join(chars).rstrip() or " ")
    return lines


def font_face_css() -> str:
    def b64(name):
        return base64.b64encode((FONTS / name).read_bytes()).decode("ascii")

    return f"""
    <style>
      @font-face {{
        font-family: 'RampMono';
        src: url(data:font/woff2;base64,{b64('ramp.woff2')}) format('woff2');
        font-weight: 400; font-style: normal;
      }}
      text {{ font-family: 'RampMono', monospace; font-size: {FONT_SIZE}px; fill: {FILL}; white-space: pre; }}
    </style>"""


def render_svg(lines: list[str]) -> str:
    width = COLS * CHAR_W
    height = len(lines) * LINE_HEIGHT
    body = []
    for i, line in enumerate(lines):
        y = (i + 1) * LINE_HEIGHT - LINE_HEIGHT * 0.25
        clip_id = f"clip{i}"
        text_w = len(line) * CHAR_W
        begin = round(i * 0.09, 2)
        dur = 0.5
        body.append(f"""
    <clipPath id="{clip_id}">
      <rect x="0" y="{y - LINE_HEIGHT:.2f}" width="0" height="{LINE_HEIGHT * 2:.2f}">
        <animate attributeName="width" from="0" to="{text_w:.2f}" begin="{begin}s" dur="{dur}s" fill="freeze" />
      </rect>
    </clipPath>""")
    defs = "\n".join(body)

    rows = []
    for i, line in enumerate(lines):
        y = (i + 1) * LINE_HEIGHT - LINE_HEIGHT * 0.25
        clip_id = f"clip{i}"
        text_w = len(line) * CHAR_W
        begin = round(i * 0.09, 2)
        esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
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
{defs}
  </defs>
  <rect width="100%" height="100%" fill="none" />
{"".join(rows)}
</svg>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=ROOT / "assets" / "portrait.svg")
    ap.add_argument("--cols", type=int, default=COLS)
    args = ap.parse_args()

    if args.input and args.input.exists():
        img = Image.open(args.input).convert("RGB")
    else:
        print("no --input given (or file missing); using synthetic placeholder", file=sys.stderr)
        img = make_placeholder()

    img = remove_background(img)
    gray = enhance(img)
    lines = to_ascii_rows(gray, cols=args.cols)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(lines), encoding="utf-8")
    print(f"wrote {args.output} ({len(lines)} rows x {args.cols} cols)")


if __name__ == "__main__":
    main()
