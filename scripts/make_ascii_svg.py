"""Génère ascii-portrait.svg : portrait ASCII du trait, tracé ligne par ligne.

Usage : python scripts/make_ascii_svg.py avatar.png
L'avatar est un dessin au trait (encre noire sur papier blanc) : le contour,
c'est l'encre. On épaissit donc le trait (filtre min), on réduit à 100 x 50
cellules en moyennant, et la quantité d'encre de chaque cellule choisit le
caractère. Papier = vide, encre = dense : le sujet se détache du fond.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .:-=+*#%@"  # papier (vide) -> encre (dense)
COLS, ROWS = 100, 50
GAMMA = 0.7  # < 1 : remonte les traits fins, sinon ils s'effacent à la réduction
W, H = 370, 430
FONT = 5.8
CHAR_W = W - 28
ROW_H = 7.0
TOP = 54


def ink_rows(src: str) -> list[str]:
    img = ImageOps.autocontrast(Image.open(src).convert("L"), cutoff=1)
    img = img.filter(ImageFilter.MinFilter(3))  # épaissit le trait avant réduction
    img = img.resize((COLS, ROWS), Image.BOX)
    ink = (1 - np.asarray(img, dtype=float) / 255.0) ** GAMMA
    rows = []
    for r in range(ROWS):
        line = "".join(RAMP[int(v * (len(RAMP) - 1) + 0.5)] for v in ink[r])
        rows.append(line.rstrip() or " ")
    return rows


def main(src: str) -> None:
    rows = ink_rows(src)
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
