#!/usr/bin/env python3
"""Renders a name as a block-letter ASCII banner using the same typing
animation as the portrait pipeline, minus any photo. A 5x7 dot-matrix
font is drawn with the ramp's darkest character ('@') for "on" pixels.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ascii_type import render_svg

ROOT = Path(__file__).resolve().parent.parent

FONT_H = 7
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
}


def build_rows(word: str, spacing: int = 1) -> list[str]:
    rows = [""] * FONT_H
    letters = word.upper()
    for i, ch in enumerate(letters):
        glyph = FONT[ch]
        for r in range(FONT_H):
            rows[r] += glyph[r]
        if i != len(letters) - 1:
            for r in range(FONT_H):
                rows[r] += " " * spacing
    return rows


def scale(rows: list[str], sx: int, sy: int) -> list[str]:
    out = []
    for row in rows:
        wide = "".join(ch * sx for ch in row)
        out.extend([wide] * sy)
    return out


def to_ramp(rows: list[str]) -> list[str]:
    return ["".join("@" if ch == "#" else " " for ch in row) for row in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--word", default="BHUVANESH")
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--output", type=Path, default=ROOT / "assets" / "name.svg")
    args = ap.parse_args()

    rows = build_rows(args.word)
    rows = scale(rows, args.scale, args.scale)
    lines = to_ramp(rows)
    cols = len(lines[0])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(lines, cols=cols), encoding="utf-8")
    print(f"wrote {args.output} ({len(lines)} rows x {cols} cols)")


if __name__ == "__main__":
    main()
