"""Minimal GitHub GraphQL client, stdlib only (urllib + json)."""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

API_URL = "https://api.github.com/graphql"

CONTRIB_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""

REPOS_QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def _post(query: str, variables: dict) -> dict:
    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-stats-generator",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def utc_window():
    """Whole-UTC-day window: [today-364d 00:00:00Z, today 23:59:59Z].

    Pinning to day boundaries keeps two runs minutes apart from bucketing
    days into different weeks, which would otherwise shift the sparkline.
    """
    today = datetime.now(timezone.utc).date()
    start = datetime.combine(today - timedelta(days=364), datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(today, datetime.max.time().replace(microsecond=0), tzinfo=timezone.utc)
    return start.isoformat().replace("+00:00", "Z"), end.isoformat().replace("+00:00", "Z")


def fetch_contributions(login: str) -> dict:
    from_, to_ = utc_window()
    data = _post(CONTRIB_QUERY, {"login": login, "from": from_, "to": to_})
    calendar = data["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in calendar["weeks"]:
        for d in week["contributionDays"]:
            days.append({"date": d["date"], "count": d["contributionCount"]})
    return {"total": calendar["totalContributions"], "days": days}


def fetch_languages(login: str) -> dict:
    """Bytes-by-language across public, non-fork, owned repos, plus a
    per-repo primary-language tally. Public-only so the numbers agree
    regardless of whether a personal token or the Actions token ran this."""
    by_bytes = {}
    by_repo = {}
    after = None
    while True:
        data = _post(REPOS_QUERY, {"login": login, "after": after})
        repos = data["user"]["repositories"]
        for repo in repos["nodes"]:
            edges = repo["languages"]["edges"]
            if not edges:
                continue
            top_name = edges[0]["node"]["name"]
            by_repo[top_name] = by_repo.get(top_name, 0) + 1
            for edge in edges:
                name = edge["node"]["name"]
                color = edge["node"]["color"] or "#8b949e"
                size = edge["size"]
                entry = by_bytes.setdefault(name, {"bytes": 0, "color": color})
                entry["bytes"] += size
        if not repos["pageInfo"]["hasNextPage"]:
            break
        after = repos["pageInfo"]["endCursor"]
    return {"by_bytes": by_bytes, "by_repo": by_repo}
