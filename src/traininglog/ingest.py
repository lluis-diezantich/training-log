import datetime as dt
from collections import defaultdict
from dataclasses import dataclass

from traininglog.sources.base import Row

# rows in the exercise column that are not exercises, compared through key()
SESSION_MARKS = ("workout start", "workout end")
DAILY = ("sleep score", "body weight")
IGNORED = ("meditation",)


def key(name: str) -> str:
    """Match key for an exercise name. Collapses the case and trailing-space
    collisions in the log (Calf Raises/Calf raises, Wall Sit/Wall sit)."""
    return " ".join(name.split()).lower()


def parse_date(value: str) -> dt.date | None:
    head = value.strip().split(" ")[0]
    try:
        day, month, year = (int(p) for p in head.split("/"))
    except ValueError:
        return None
    try:
        return dt.date(year, month, day)
    except ValueError:
        return None


def parse_time(value: str) -> dt.time | None:
    parts = value.strip().split(" ")
    if len(parts) < 2:
        return None
    fmt = "%H:%M:%S" if parts[1].count(":") == 2 else "%H:%M"
    try:
        return dt.datetime.strptime(parts[1], fmt).time()
    except ValueError:
        return None


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


@dataclass(frozen=True)
class Set:
    date: dt.date
    exercise: str
    load: float | None  # kg; None and 0.0 both mean bodyweight
    reps: float
    rpe: float | None

    @property
    def added_load(self) -> float:
        return self.load or 0.0


@dataclass(frozen=True)
class Prescription:
    session: str
    order: int
    exercise: str
    sets: int
    lo: float
    hi: float
    unit: str
    valid_from: dt.date

    @property
    def target(self) -> str:
        if self.unit == "sec":
            return f"{self.sets}×{self.lo:g} sec"
        span = f"{self.lo:g}" if self.lo == self.hi else f"{self.lo:g}-{self.hi:g}"
        return f"{self.sets}×{span}"


@dataclass(frozen=True)
class Log:
    sets: list[Set]
    sleep: list[tuple[dt.date, float]]
    bodyweight: list[tuple[dt.date, float]]
    sessions: list[tuple[dt.date, int]]
    skipped: int = 0  # completed rows with no reps, unusable for any chart


def load_log(rows: list[Row]) -> Log:
    sets: list[Set] = []
    sleep: list[tuple[dt.date, float]] = []
    weight: list[tuple[dt.date, float]] = []
    marks: dict[dt.date, dict[str, dt.time]] = defaultdict(dict)
    skipped = 0

    for row in rows:
        name = row.get("exercise", "").strip()
        if not name:
            continue
        tag = key(name)
        date = parse_date(row.get("date", ""))
        value = parse_float(row.get("value1", ""))

        if tag in SESSION_MARKS:
            stamp = parse_time(row.get("date", ""))
            if date and stamp:
                marks[date][tag] = stamp
            continue
        if tag in DAILY:
            if date and value is not None:
                (sleep if tag == "sleep score" else weight).append((date, value))
            continue
        if tag in IGNORED or row.get("checkbox", "").strip() != "TRUE" or not date:
            continue

        reps = parse_float(row.get("reps", ""))
        if reps is None:
            skipped += 1
            continue
        sets.append(
            Set(
                date=date,
                exercise=" ".join(name.split()),
                load=value,
                reps=reps,
                rpe=parse_float(row.get("rpe", "")),
            )
        )

    return Log(
        sets=sets,
        sleep=sorted(sleep),
        bodyweight=sorted(weight),
        sessions=sorted(_durations(marks)),
        skipped=skipped,
    )


def _durations(marks: dict[dt.date, dict[str, dt.time]]) -> list[tuple[dt.date, int]]:
    out = []
    for date, pair in marks.items():
        start, end = pair.get("workout start"), pair.get("workout end")
        if not (start and end):
            continue
        minutes = round(
            (dt.datetime.combine(date, end) - dt.datetime.combine(date, start)).total_seconds() / 60
        )
        if 10 <= minutes <= 240:
            out.append((date, minutes))
    return out


def load_program(rows: list[Row], on: dt.date | None = None) -> list[Prescription]:
    """The program snapshot in force on `on`. Rows sharing a valid_from are one
    complete version, so the latest version at or before `on` wins outright."""
    parsed: list[Prescription] = []
    for row in rows:
        exercise = row.get("exercise", "").strip()
        start = parse_date(row.get("valid_from", "")) or _parse_iso(row.get("valid_from", ""))
        if not exercise or not start:
            continue
        lo = parse_float(row.get("lo", "")) or 0.0
        parsed.append(
            Prescription(
                session=row.get("session", "").strip(),
                order=int(parse_float(row.get("order", "")) or 0),
                exercise=exercise,
                sets=int(parse_float(row.get("sets", "")) or 0),
                lo=lo,
                hi=parse_float(row.get("hi", "")) or lo,
                unit=(row.get("unit", "").strip() or "reps"),
                valid_from=start,
            )
        )
    if not parsed:
        return []

    cutoff = on or dt.date.today()
    eligible = [p.valid_from for p in parsed if p.valid_from <= cutoff]
    current = max(eligible) if eligible else min(p.valid_from for p in parsed)
    snapshot = [p for p in parsed if p.valid_from == current]
    # sessions keep the order they appear in the sheet, not alphabetical
    seen: dict[str, int] = {}
    for p in snapshot:
        seen.setdefault(p.session, len(seen))
    return sorted(snapshot, key=lambda p: (seen[p.session], p.order))


def _parse_iso(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value.strip())
    except ValueError:
        return None
