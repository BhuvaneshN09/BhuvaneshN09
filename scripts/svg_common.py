"""Shared SVG helpers: font embedding and a small text/rect drawing kit."""
import base64
from pathlib import Path

FONTS = Path(__file__).resolve().parent.parent / "fonts"

BG = "#0d1117"
FG = "#c9d1d9"
DIM = "#8b949e"
RULE = "#30363d"

RAMP = " .`:-=+*cs#%@"


def _b64(name: str) -> str:
    return base64.b64encode((FONTS / name).read_bytes()).decode("ascii")


def font_faces(*names: str) -> str:
    faces = []
    for name in names:
        family = "RampMono" if name.startswith("ramp") else ("HeadMono" if name.startswith("heading") else "BodyMono")
        weight = 500 if "medium" in name else 400
        faces.append(f"""
      @font-face {{
        font-family: '{family}';
        src: url(data:font/woff2;base64,{_b64(name)}) format('woff2');
        font-weight: {weight}; font-style: normal;
      }}""")
    return "<style>" + "".join(faces) + "</style>"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(width: float, height: float, extra_defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" '
        f'width="{int(width)}" font-family="BodyMono, monospace">\n'
        f"<defs>{font_faces('basic-regular.woff2', 'basic-medium.woff2', 'ramp.woff2')}{extra_defs}</defs>\n"
        f'<rect width="100%" height="100%" fill="{BG}" rx="6" />\n'
    )


def svg_close() -> str:
    return "</svg>"


def text(x, y, s, size=13, fill=FG, weight=400, family="BodyMono", anchor="start") -> str:
    fam = family if weight == 400 else f"{family}"
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" '
        f'font-family="{fam}, monospace" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>\n'
    )
