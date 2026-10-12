"""Récupère le calendrier de contributions public d'un utilisateur GitHub.

Aucun token : on lit le fragment HTML public
https://github.com/users/<user>/contributions, puis on écrit
data/contributions.json (jours bruts + statistiques dérivées).
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "mincho95")
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days(user: str) -> list[dict]:
    url = f"https://github.com/users/{user}/contributions"
    resp = requests.get(url, timeout=30, headers={"User-Agent": "profile-readme-bot"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"(\d+) contribution", tip.get_text(strip=True))
        counts[tip.get("for")] = int(m.group(1)) if m else 0

    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append(
            {
                "date": cell["data-date"],
                "level": int(cell.get("data-level", 0)),
                "count": counts.get(cell.get("id"), 0),
            }
        )
    days.sort(key=lambda d: d["date"])
    if not days:
        sys.exit("Aucune cellule trouvée : le markup de GitHub a changé ?")
    return days


def streaks(days: list[dict]) -> tuple[int, int]:
    active = {d["date"] for d in days if d["count"] > 0}
    longest = run = 0
    prev = None
    for d in days:
        if d["count"] > 0:
            run = run + 1 if prev and date.fromisoformat(d["date"]) - prev == timedelta(1) else 1
            longest = max(longest, run)
            prev = date.fromisoformat(d["date"])
    # série en cours : on tolère que "aujourd'hui" soit encore vide
    cur = 0
    day = date.fromisoformat(days[-1]["date"])
    if day.isoformat() not in active:
        day -= timedelta(1)
    while day.isoformat() in active:
        cur += 1
        day -= timedelta(1)
    return cur, longest


def main() -> None:
    days = fetch_days(USER)
    cur, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    months = defaultdict(int)
    for d in days:
        months[d["date"][:7]] += d["count"]
    stats = {
        "total": sum(d["count"] for d in days),
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": dict(sorted(months.items())),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"user": USER, "stats": stats, "days": days}, indent=1))
    print(f"{len(days)} jours, {stats['total']} contributions, série max {longest}")


if __name__ == "__main__":
    main()
