#!/usr/bin/env python3
"""Fetches contribution + language data via the GitHub GraphQL API and
writes assets/stats.svg, streak.svg, langs.svg, year.svg.

Requires env vars GITHUB_TOKEN and GH_LOGIN. Uses only the standard
library plus the sibling gh_api/svg_stats/svg_common modules, so there
are no third-party dependencies to break in CI.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gh_api
import svg_stats

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def main():
    login = os.environ["GH_LOGIN"]
    contrib = gh_api.fetch_contributions(login)
    langs = gh_api.fetch_languages(login)

    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "stats.svg").write_text(svg_stats.render_hero(contrib["total"], contrib["days"]), encoding="utf-8")
    (ASSETS / "streak.svg").write_text(svg_stats.render_streak(contrib["days"]), encoding="utf-8")
    (ASSETS / "langs.svg").write_text(
        svg_stats.render_languages(langs["by_bytes"], langs["by_repo"]), encoding="utf-8"
    )
    (ASSETS / "year.svg").write_text(svg_stats.render_year(contrib["days"]), encoding="utf-8")
    print(f"wrote stats.svg, streak.svg, langs.svg, year.svg for {login}")


if __name__ == "__main__":
    main()
