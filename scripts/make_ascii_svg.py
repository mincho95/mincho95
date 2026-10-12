"""Génère ascii-portrait.svg : contours ASCII de l'avatar, tracés ligne par ligne.

Usage : python scripts/make_ascii_svg.py avatar.png
On ne représente pas les tons mais les contours : filtre de Sobel sur l'image
lissée, puis pour chaque cellule de caractère on garde l'orientation dominante
du trait (tenseur de structure) et on l'écrit avec | - / \\. Les cellules sans
contour restent vides, donc le sujet se détache du fond.
"""
import sys
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 100, 50
CELL_W, CELL_H = 6, 12  # pixels d'image par caractère (rapport 1:2 d'une police mono)
THRESHOLD = 0.2  # force moyenne du gradient sous laquelle la cellule reste vide
BLUR = 1.3
W, H = 370, 430
FONT = 5.8
CHAR_W = W - 28
ROW_H = 7.0
TOP = 54

SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)


def convolve(a: np.ndarray, k: np.ndarray) -> np.ndarray:
    return (sliding_window_view(np.pad(a, 1, mode="edge"), (3, 3)) * k).sum((-1, -2))


def edge_rows(src: str) -> list[str]:
    img = ImageOps.autocontrast(Image.open(src).convert("L"), cutoff=1)
    img = img.resize((COLS * CELL_W, ROWS * CELL_H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(BLUR))
    a = np.asarray(img, dtype=float) / 255.0
    gx, gy = convolve(a, SOBEL_X), convolve(a, SOBEL_X.T)
    mag = np.hypot(gx, gy)
    rows = []
    for r in range(ROWS):
        line = ""
        for c in range(COLS):
            sl = (slice(r * CELL_H, (r + 1) * CELL_H), slice(c * CELL_W, (c + 1) * CELL_W))
            if mag[sl].mean() < THRESHOLD:
                line += " "
                continue
            bx, by = gx[sl], gy[sl]
            grad = 0.5 * np.arctan2(2 * (bx * by).sum(), (bx * bx).sum() - (by * by).sum())
            t = (np.degrees(grad) + 90) % 180  # le trait est perpendiculaire au gradient
            line += "-" if t < 22.5 or t >= 157.5 else "\\" if t < 67.5 else "|" if t < 112.5 else "/"
        rows.append(line.rstrip() or " ")
    return rows


def main(src: str) -> None:
    rows = edge_rows(src)
    clips, texts = [], []
    for i, line in enumerate(rows):
        y = TOP + i * ROW_H
        begin = 0.35 + i * 0.045
        clips.append(
            f'<clipPath id="r{i}"><rect x="14" y="{y - ROW_H:.1f}" width="0" height="{ROW_H + 1:.1f}">'
            f'<animate attributeName="width" from="0" to="{CHAR_W}" dur="0.55s" begin="{begin:.2f}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        esc = line.replace("&", "&amp;").replace("<", "&lt;")
        # textLength fige la largeur de ligne quelle que soit la police de repli
        texts.append(
            f'<text x="14" y="{y:.1f}" clip-path="url(#r{i})" xml:space="preserve" '
            f'textLength="{CHAR_W * len(line) / COLS:.1f}" lengthAdjust="spacing">{esc}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Portrait ASCII">
<defs>{"".join(clips)}</defs>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:{FONT}px;fill:#c9d1d9;white-space:pre}}
.t{{font-size:12px;fill:#8b949e}} .cur{{animation:b 1.1s steps(1) infinite}} @keyframes b{{50%{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect width="{W}" height="30" rx="12" fill="#161b22"/><rect y="18" width="{W}" height="12" fill="#161b22"/>
<circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="38" cy="15" r="5" fill="#ffbd2e"/><circle cx="56" cy="15" r="5" fill="#27c93f"/>
<text class="t" x="76" y="19">./portrait --ascii</text>
{"".join(texts)}
<text class="t" x="14" y="{H - 14}">$ <tspan class="cur" fill="#39d353">▋</tspan></text>
</svg>'''
    out = ROOT / "ascii-portrait.svg"
    out.write_text(svg)
    print(out.name, len(svg), "octets")
    print("\n".join(rows[::3]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "avatar.png"))
