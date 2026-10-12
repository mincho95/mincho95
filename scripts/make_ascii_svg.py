"""Génère ascii-portrait.svg : portrait ASCII monochrome qui s'écrit ligne par ligne.

Usage : python scripts/make_ascii_svg.py avatar.png
L'image source est déjà en noir et blanc très contrasté, donc pas de
détourage (rembg) : on lisse un peu, on étire le contraste, puis on convertit
l'encre en caractère. Encre = dense, papier = vide : sur fond sombre,
le dessin ressort en traits lumineux. Le trait est épaissi avant réduction
(filtre min), sinon les lignes fines disparaissent à 100 colonnes.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .:-=+*#%@"  # papier (vide) -> encre (dense)
COLS, ROWS = 100, 50
W, H = 370, 430
FONT = 5.8
CHAR_W = W - 28
ROW_H = 7.0
TOP = 54


def main(src: str) -> None:
    img = Image.open(src).convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.filter(ImageFilter.MinFilter(3))  # épaissit le trait pour qu'il survive à la réduction
    img = img.resize((COLS, ROWS), Image.BOX)
    px = 1 - np.asarray(img, dtype=float) / 255.0
    rows = []
    for r in range(ROWS):
        line = "".join(RAMP[int(v ** 0.8 * (len(RAMP) - 1) + 0.5)] for v in px[r])
        rows.append(line.rstrip() or " ")

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
