"""Renders the four stats graphics: hero/sparkline, streak, languages, year grid."""
from datetime import date

from svg_common import BG, DIM, FG, RAMP, RULE, esc, font_faces, svg_close, text

WEEK_W = 10  # px per week column in the sparkline / year grid


def _weekly_totals(days):
    """Sum daily counts into whole ISO weeks, oldest first."""
    weeks = []
    bucket = []
    for d in days:
        bucket.append(d["count"])
        if len(bucket) == 7:
            weeks.append(sum(bucket))
            bucket = []
    if bucket:
        weeks.append(sum(bucket))
    return weeks


def render_hero(total: int, days: list) -> str:
    weeks = _weekly_totals(days)
    w, h = 460, 160
    pad_l, pad_r, pad_t, pad_b = 20, 20, 54, 24
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b
    maxv = max(weeks) or 1

    step = plot_w / max(1, len(weeks) - 1)
    pts = []
    for i, v in enumerate(weeks):
        x = pad_l + i * step
        y = pad_t + plot_h - (v / maxv) * plot_h
        pts.append((x, y))

    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{pad_l:.1f},{pad_t + plot_h:.1f} " + line + f" {pts[-1][0]:.1f},{pad_t + plot_h:.1f}"

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" font-family="BodyMono, monospace">',
        f"<defs>{font_faces('basic-regular.woff2', 'basic-medium.woff2')}"
        '<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#58a6ff" stop-opacity="0.35"/>'
        '<stop offset="100%" stop-color="#58a6ff" stop-opacity="0"/>'
        "</linearGradient></defs>",
        f'<rect width="100%" height="100%" fill="{BG}" rx="6"/>',
        text(20, 30, f"{total:,}", size=26, weight=500, family="BodyMono"),
        text(20, 46, "contributions in the last year", size=11, fill=DIM),
        f'<polyline points="{area}" fill="url(#fade)" stroke="none"/>',
        f'<polyline points="{line}" fill="none" stroke="#58a6ff" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>',
        text(20, h - 6, "week 1", size=9, fill=DIM),
        text(w - 20, h - 6, "this week", size=9, fill=DIM, anchor="end"),
        svg_close(),
    ]
    return "\n".join(out)


def _compute_streaks(days):
    current = 0
    longest = 0
    longest_range = (None, None)
    cur_start = None
    run_start = None
    run_len = 0
    prev_date = None

    for d in days:
        if d["count"] > 0:
            if run_len == 0:
                run_start = d["date"]
            run_len += 1
            if run_len > longest:
                longest = run_len
                longest_range = (run_start, d["date"])
        else:
            run_len = 0
        prev_date = d["date"]

    # current streak: walk backward from the most recent day
    run_len = 0
    end_date = None
    for d in reversed(days):
        if d["count"] > 0:
            if run_len == 0:
                end_date = d["date"]
            run_len += 1
            cur_start = d["date"]
        else:
            if d["date"] == days[-1]["date"]:
                # today has no contributions yet; don't break the streak on day one
                continue
            break
    current = run_len
    return {
        "current": current,
        "current_range": (cur_start, end_date) if current else (None, None),
        "longest": longest,
        "longest_range": longest_range,
    }


def render_streak(days: list) -> str:
    s = _compute_streaks(days)
    w, h = 460, 130

    def fmt(range_):
        a, b = range_
        if not a:
            return "—"
        return f"{a} → {b}"

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" font-family="BodyMono, monospace">',
        f"<defs>{font_faces('basic-regular.woff2', 'basic-medium.woff2')}</defs>",
        f'<rect width="100%" height="100%" fill="{BG}" rx="6"/>',
        f'<line x1="{w/2:.1f}" y1="16" x2="{w/2:.1f}" y2="{h-16}" stroke="{RULE}" stroke-width="1"/>',
        text(24, 40, str(s["current"]), size=30, weight=500),
        text(24, 60, "current streak", size=11, fill=DIM),
        text(24, 78, fmt(s["current_range"]), size=10, fill=DIM),
        text(w / 2 + 24, 40, str(s["longest"]), size=30, weight=500),
        text(w / 2 + 24, 60, "longest streak", size=11, fill=DIM),
        text(w / 2 + 24, 78, fmt(s["longest_range"]), size=10, fill=DIM),
        svg_close(),
    ]
    return "\n".join(out)


def render_languages(by_bytes: dict, by_repo: dict, top_n: int = 6) -> str:
    total_bytes = sum(v["bytes"] for v in by_bytes.values()) or 1
    ranked = sorted(by_bytes.items(), key=lambda kv: kv[1]["bytes"], reverse=True)[:top_n]

    w = 460
    row_h = 22
    top_pad = 40
    h = top_pad + row_h * len(ranked) + 70

    rows = []
    bar_x = 150
    bar_max_w = w - bar_x - 60
    for i, (name, info) in enumerate(ranked):
        y = top_pad + i * row_h
        pct = info["bytes"] / total_bytes
        bw = bar_max_w * pct
        rows.append(text(20, y + 14, name, size=12))
        rows.append(f'<rect x="{bar_x}" y="{y+4}" width="{bar_max_w:.1f}" height="10" fill="{RULE}" rx="2"/>')
        rows.append(f'<rect x="{bar_x}" y="{y+4}" width="{bw:.1f}" height="10" fill="{info["color"]}" rx="2"/>')
        rows.append(text(w - 20, y + 14, f"{pct*100:.1f}%", size=11, fill=DIM, anchor="end"))

    repo_y = top_pad + row_h * len(ranked) + 24
    repo_ranked = sorted(by_repo.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    repo_line = "  ".join(f"{name} {count}" for name, count in repo_ranked)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" font-family="BodyMono, monospace">',
        f"<defs>{font_faces('basic-regular.woff2', 'basic-medium.woff2')}</defs>",
        f'<rect width="100%" height="100%" fill="{BG}" rx="6"/>',
        text(20, 22, "top languages, by bytes", size=11, fill=DIM),
        *rows,
        f'<line x1="20" y1="{repo_y - 14}" x2="{w-20}" y2="{repo_y - 14}" stroke="{RULE}"/>',
        text(20, repo_y, "by repo:", size=10, fill=DIM),
        text(90, repo_y, repo_line, size=10),
        svg_close(),
    ]
    return "\n".join(out)


def render_year(days: list) -> str:
    weeks = []
    bucket = []
    for d in days:
        bucket.append(d)
        if len(bucket) == 7:
            weeks.append(bucket)
            bucket = []
    if bucket:
        weeks.append(bucket)

    maxv = max((d["count"] for d in days), default=0) or 1
    n = len(RAMP) - 1
    cell = WEEK_W

    w = 40 + len(weeks) * cell
    h = 40 + 7 * cell

    rows = []
    month_labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        x = 30 + wi * cell
        first_day = date.fromisoformat(week[0]["date"])
        if first_day.month != last_month:
            month_labels.append(text(x, 14, first_day.strftime("%b"), size=9, fill=DIM))
            last_month = first_day.month
        for di, d in enumerate(week):
            count = d["count"]
            idx = 0 if count == 0 else round((count / maxv) * n)
            ch = RAMP[idx]
            y = 24 + di * cell
            rows.append(
                f'<text x="{x:.1f}" y="{y:.1f}" font-family="RampMono, monospace" '
                f'font-size="11" fill="{FG}">{esc(ch)}</text>'
            )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}">',
        f"<defs>{font_faces('ramp.woff2', 'basic-regular.woff2')}</defs>",
        f'<rect width="100%" height="100%" fill="{BG}" rx="6"/>',
        *month_labels,
        *rows,
        svg_close(),
    ]
    return "\n".join(out)
