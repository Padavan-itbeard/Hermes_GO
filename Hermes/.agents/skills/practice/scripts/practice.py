# Отчёт по практике за период: JSON из строк «Практика N мин: … — M мин» в log/study_log.md.
# python .agents/skills/practice/scripts/practice.py [сегодня|вчера|неделя|месяц|YYYY-MM-DD|YYYY-MM-DD..YYYY-MM-DD]
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

LOG = Path(__file__).resolve().parents[4] / "log" / "study_log.md"
ROW = re.compile(r"^\|\s*Практика (\d+) (мин|ч): (.+?) — (\d+) мин\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d{1,2}:\d{2})\s*\|")


def period(arg):
    today = date.today()
    a = (arg or "сегодня").strip().lower()
    if a in ("сегодня", "today", "день", "day"):
        return today, today
    if a in ("вчера", "yesterday"):
        return today - timedelta(1), today - timedelta(1)
    if a in ("неделя", "week"):
        return today - timedelta(today.weekday()), today
    if a in ("месяц", "month"):
        return today.replace(day=1), today
    if ".." in a:
        f, t = a.split("..", 1)
        return date.fromisoformat(f.strip()), date.fromisoformat(t.strip())
    d = date.fromisoformat(a)
    return d, d


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        start, end = period(" ".join(sys.argv[1:]))
    except ValueError:
        print("СТОП: не понял период. Можно: сегодня, вчера, неделя, месяц, 2026-11-06 или 2026-11-01..2026-11-06")
        sys.exit(1)
    if start > end:
        start, end = end, start

    practices = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        size, unit, title, spent, day, clock = m.groups()
        finished = datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M")
        if not start <= finished.date() <= end:
            continue
        planned = int(size) * (60 if unit == "ч" else 1)
        practices.append({
            "title": title.strip(),
            "kind": f"{size}h" if unit == "ч" else f"{size}min",
            "planned_min": planned,
            "started_at": (finished - timedelta(minutes=int(spent))).strftime("%Y-%m-%dT%H:%M"),
            "finished_at": finished.strftime("%Y-%m-%dT%H:%M"),
            "duration_min": int(spent),
        })
    practices.sort(key=lambda p: p["finished_at"])

    print(json.dumps({
        "range": {"from": start.isoformat(), "to": end.isoformat()},
        "practices": practices,
        "total": {
            "count": len(practices),
            "duration_min": sum(p["duration_min"] for p in practices),
            "planned_min": sum(p["planned_min"] for p in practices),
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
