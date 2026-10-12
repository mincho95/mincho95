"""Dessine contrib-heatmap.svg à partir de data/contributions.json.

Grille 53 semaines x 7 jours, révélée une fois en diagonale (keyframes CSS
joués au chargement puis figés). Tout le mouvement vit dans le SVG : GitHub
bloque le JS et le CSS externe dans les README.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
W, PAD_L, PAD_R, TOP = 860, 44, 20, 66
CELL, PITCH = 12, 15
MONTHS = ["jan", "fév", "mar", "avr", "mai", "juin", "juil", "août", "sep", "oct", "nov", "déc"]


def main() -> None:
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days, stats, user = data["days"], data["stats"], data["user"]

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub : semaine qui commence le dimanche
    cells, month_marks = [], {}
    for i, d in enumerate(days):
        idx = i + offset
        week, dow = divmod(idx, 7)
        dt = date.fromisoformat(d["date"])
        if dt.day <= 7 and dow == 0 or (i == 0):
            month_marks.setdefault(week, MONTHS[dt.month - 1])
        # niveau 5 (le plus clair) réservé aux gros jours pour de la profondeur
        level = 5 if d["level"] == 4 and d["count"] >= 2 * max(1, stats["best_day"]["count"]) // 3 else d["level"]
        delay = (week + dow) * 14
        cells.append(
            f'<rect class="c" x="{PAD_L + week * PITCH}" y="{TOP + dow * PITCH}" '
            f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[level]}" '
            f'style="animation-delay:{delay}ms"><title>{d["count"]} contribution(s) · {d["date"]}</title></rect>'
        )

    labels = []
    last_x = -99
    for week, name in sorted(month_marks.items()):
        x = PAD_L + week * PITCH
        if x - last_x >= 34:
            labels.append(f'<text x="{x}" y="{TOP - 9}" class="m">{name}</text>')
            last_x = x
    for dow, name in ((1, "lun"), (3, "mer"), (5, "ven")):
        labels.append(f'<text x="{PAD_L - 8}" y="{TOP + dow * PITCH + 10}" class="m" text-anchor="end">{name}</text>')

    grid_bottom = TOP + 7 * PITCH
    foot_y = grid_bottom + 56
    best = stats["best_day"]
    top_month = max(stats["months"].items(), key=lambda kv: kv[1])
    tm_label = f'{MONTHS[int(top_month[0][5:]) - 1]} {top_month[0][:4]}'
    items = [
        ("total", f'{stats["total"]}', "contributions / 12 mois"),
        ("série", f'{stats["current_streak"]}j', "en cours"),
        ("record", f'{stats["longest_streak"]}j', "plus longue série"),
        ("pic", f'{best["count"]}', f'le {best["date"]}'),
        ("top mois", f'{top_month[1]}', tm_label),
    ]
    col_w = (W - 40) / len(items)
    foot = []
    for n, (k, v, sub) in enumerate(items):
        x = 20 + n * col_w
        foot.append(
            f'<text x="{x:.0f}" y="{foot_y}" class="k">{k}</text>'
            f'<text x="{x:.0f}" y="{foot_y + 22}" class="v">{v}</text>'
            f'<text x="{x:.0f}" y="{foot_y + 38}" class="s">{sub}</text>'
        )

    legend_y = grid_bottom + 8
    sw0 = W - PAD_R - len(PALETTE) * 17 - 36  # x du premier carré de la légende
    legend = [f'<text x="{sw0 - 6}" y="{legend_y + 10}" class="m" text-anchor="end">moins</text>']
    for n, col in enumerate(PALETTE):
        legend.append(f'<rect x="{sw0 + n * 17}" y="{legend_y}" width="12" height="12" rx="3" fill="{col}"/>')
    legend.append(f'<text x="{sw0 + len(PALETTE) * 17 + 2}" y="{legend_y + 10}" class="m">plus</text>')

    H = foot_y + 56
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Graphique des contributions GitHub de {user}">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.m{{font-size:10px;fill:#7d8590}} .t{{font-size:12px;fill:#8b949e}}
.k{{font-size:10px;fill:#7d8590;text-transform:uppercase;letter-spacing:.08em}}
.v{{font-size:20px;fill:#39d353;font-weight:700}} .s{{font-size:10px;fill:#8b949e}}
.c{{opacity:0;animation:drop .5s ease-out forwards}}
@keyframes drop{{from{{opacity:0;transform:translateY(-8px)}}to{{opacity:1;transform:translateY(0)}}}}
.cur{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect width="{W}" height="30" rx="12" fill="#161b22"/><rect y="18" width="{W}" height="12" fill="#161b22"/>
<circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="38" cy="15" r="5" fill="#ffbd2e"/><circle cx="56" cy="15" r="5" fill="#27c93f"/>
<text x="76" y="19" class="t">{user}@github ~ $ ./contributions --live<tspan class="cur" fill="#39d353"> ▋</tspan></text>
{"".join(labels)}
{"".join(cells)}
{"".join(legend)}
<line x1="20" x2="{W - 20}" y1="{foot_y - 18}" y2="{foot_y - 18}" stroke="#21262d"/>
{"".join(foot)}
</svg>'''
    (ROOT / "contrib-heatmap.svg").write_text(svg)
    print("contrib-heatmap.svg écrit", len(svg), "octets")


if __name__ == "__main__":
    main()
