import datetime as dt
from collections import defaultdict

from traininglog.config import Config
from traininglog.ingest import Prescription, Set, key

RECENT_SESSIONS = 3  # how far back "is this loaded?" looks


def _by_exercise(sets: list[Set]) -> dict[str, list[Set]]:
    out: dict[str, list[Set]] = defaultdict(list)
    for s in sets:
        out[key(s.exercise)].append(s)
    return {k: sorted(v, key=lambda s: s.date) for k, v in out.items()}


def _sessions(entries: list[Set]) -> dict[dt.date, list[Set]]:
    days: dict[dt.date, list[Set]] = defaultdict(list)
    for s in entries:
        days[s.date].append(s)
    return days


def _is_loaded(days: dict[dt.date, list[Set]]) -> bool:
    recent = sorted(days)[-RECENT_SESSIONS:]
    return any(s.added_load > 0 for d in recent for s in days[d])


def status_of(p: Prescription, last: list[Set], age: int, cfg: Config) -> str:
    if age > cfg.stale_days:
        return "stale"
    reps = [s.reps for s in last]
    short = bool(p.sets) and len(last) < p.sets
    if p.lo == p.hi:  # a fixed target is met or missed, never a ceiling
        if min(reps) < p.lo:
            return "below-range"
    elif min(reps) >= p.hi:
        return "add-load"
    elif min(reps) < p.lo:
        return "below-range"
    return "short-sets" if short else "on-target"


def program_panel(
    program: list[Prescription], sets: list[Set], cfg: Config, today: dt.date
) -> list[dict]:
    logged = _by_exercise(sets)
    panel: list[dict] = []
    for p in program:
        entries = logged.get(key(p.exercise), [])
        row: dict = {"label": p.exercise, "log": p.exercise, "target": p.target}
        if not entries:
            row |= {"status": "untracked", "sets": 0}
        else:
            days = _sessions(entries)
            last_day = max(days)
            last = days[last_day]
            age = (today - last_day).days
            row |= {
                "status": status_of(p, last, age, cfg),
                "sets": len(entries),
                "last": last_day.isoformat(),
                "age": age,
                "nsets": len(last),
                "unloaded": not _is_loaded(days),
                "actual": ", ".join(
                    f"{s.load:g}×{s.reps:g}" if s.added_load else f"{s.reps:g}" for s in last
                ),
            }
        if not panel or panel[-1]["name"] != p.session:
            panel.append({"name": p.session, "ex": []})
        panel[-1]["ex"].append(row)
    return panel


def exercise_series(program: list[Prescription], sets: list[Set], cfg: Config) -> dict[str, dict]:
    """Per-session reps and load for each prescribed exercise, for the progression chart."""
    logged = _by_exercise(sets)
    out: dict[str, dict] = {}
    for p in program:
        entries = logged.get(key(p.exercise), [])
        days = _sessions(entries)
        if len(days) < 2:
            continue
        is_bw = key(p.exercise) in {key(x) for x in cfg.bodyweight_exercises}
        series = []
        for day in sorted(days):
            day_sets = days[day]
            reps = [s.reps for s in day_sets]
            loads = [s.load for s in day_sets if s.load is not None]
            series.append(
                {
                    "d": day.isoformat(),
                    "sets": [[s.load, s.reps, s.rpe] for s in day_sets],
                    "minr": min(reps),
                    "maxr": max(reps),
                    "load": max(loads) if loads else None,
                }
            )
        out[p.exercise] = {
            "log": p.exercise,
            "session": p.session,
            "bw": is_bw,
            "loaded": _is_loaded(days),
            "unit": p.unit,
            "target": p.target,
            "lo": p.lo,
            "hi": p.hi,
            "nsets": p.sets,
            "series": series,
        }
    return out


def weekly_sets(sets: list[Set]) -> list[dict]:
    """Set counts per ISO week, used by the summary tiles."""
    weeks: dict[str, int] = defaultdict(int)
    for s in sets:
        monday = s.date - dt.timedelta(days=s.date.weekday())
        weeks[monday.isoformat()] += 1
    return [{"week": w, "sets": n} for w, n in sorted(weeks.items())]
