"""Génère info-card.svg : carte façon neofetch (contenu éditorial, pas de stats).

STATIC=1 produit une image figée (sans animation) pour les aperçus.
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
W, H = 490, 430

USER, HOST = "paul", "mincho95"
ROWS = [
    ("Now", "IIM Digital School · 2ᵉ année · axe Coding / IA"),
    ("Seeking", "alternance en développement"),
    ("Prod", "2 applis en production dans un atelier industriel"),
    ("Langages", "JavaScript · Python · PHP · C# · SQL · Java"),
    ("Stack", "Node.js · Electron · Unity · HTML/CSS"),
    ("Infra", "Linux · nginx · Cloudflare Tunnel · TLS"),
    ("Shipped", "extension Firefox publiée sur addons.mozilla.org"),
    ("Craft", "portfolio zéro dépendance · CSP stricte · CI"),
    ("Exploring", "agents autonomes · auto-hébergement"),
    ("Contact", "pfery@outlook.fr"),
]
KEY_COL = ["#58a6ff", "#39d353", "#d2a8ff", "#ffa657", "#79c0ff", "#ff7b72"]
SWATCH = ["#161b22", "#ff5f56", "#39d353", "#ffbd2e", "#58a6ff", "#d2a8ff", "#79c0ff", "#c9d1d9"]
LINE = 26
TOP = 78


def main() -> None:
    parts = []
    t = 0.2

    def delay() -> str:
        nonlocal t
        d = f' class="l" style="animation-delay:{t:.2f}s"' if not STATIC else ""
        t += 0.13
        return d

    parts.append(f'<text x="24" y="{TOP}"{delay()}><tspan fill="#39d353" font-weight="700">{USER}</tspan>'
                 f'<tspan fill="#8b949e">@</tspan><tspan fill="#39d353" font-weight="700">{HOST}</tspan></text>')
    parts.append(f'<text x="24" y="{TOP + 18}"{delay()} fill="#30363d">{"─" * (len(USER) + len(HOST) + 1)}</text>')
    for i, (k, v) in enumerate(ROWS):
        y = TOP + 18 + (i + 1) * LINE
        parts.append(
            f'<text x="24" y="{y}"{delay()}><tspan fill="{KEY_COL[i % len(KEY_COL)]}" font-weight="700">{k}</tspan>'
            f'<tspan x="108" fill="#c9d1d9">{escape(v)}</tspan></text>'
        )
    ys = TOP + 18 + (len(ROWS) + 1) * LINE + 8
    sw = "".join(f'<rect x="{24 + n * 22}" y="{ys}" width="20" height="14" rx="3" fill="{c}"/>' for n, c in enumerate(SWATCH))
    parts.append(f'<g{delay()}>{sw}</g>')

    anim = "" if STATIC else (
        ".l{opacity:0;animation:in .45s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}}"
        ".cur{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}"
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Carte d'infos de Paul">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;white-space:pre}}
.t{{font-size:12px;fill:#8b949e}}{anim}
</style>
<rect width="{W}" height="{H}" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect width="{W}" height="30" rx="12" fill="#161b22"/><rect y="18" width="{W}" height="12" fill="#161b22"/>
<circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="38" cy="15" r="5" fill="#ffbd2e"/><circle cx="56" cy="15" r="5" fill="#27c93f"/>
<text class="t" x="76" y="19">neofetch --paul</text>
{"".join(parts)}
<text class="t" x="24" y="{H - 14}">$ <tspan class="cur" fill="#39d353">▋</tspan></text>
</svg>'''
    out = ROOT / ("info-card-static.svg" if STATIC else "info-card.svg")
    out.write_text(svg)
    print(out.name, len(svg), "octets")


if __name__ == "__main__":
    main()
