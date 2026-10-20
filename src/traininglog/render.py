import datetime as dt
import json
from pathlib import Path

from traininglog.config import Config
from traininglog.ingest import Log, Prescription
from traininglog.metrics import exercise_series, program_panel, weekly_sets

TEMPLATE = Path(__file__).parent / "templates" / "dashboard.html"
PLACEHOLDER = "/*__DATA__*/"
ROBOTS = "User-agent: *\nDisallow: /\n"


def payload(
    log: Log, program: list[Prescription], cfg: Config, today: dt.date | None = None
) -> dict:
    today = today or dt.date.today()
    bodyweight = log.bodyweight[-1][1] if log.bodyweight else cfg.default_bodyweight
    dates = [s.date for s in log.sets]
    return {
        "bodyweight": bodyweight,
        "weekly": weekly_sets(log.sets),
        "sessions": [[d.isoformat(), m] for d, m in log.sessions],
        "sleep": [[d.isoformat(), v] for d, v in log.sleep],
        "totalSets": len(log.sets),
        "span": [min(dates).isoformat(), max(dates).isoformat()] if dates else ["", ""],
        "exCount": len({s.exercise.lower() for s in log.sets}),
        "program": program_panel(program, log.sets, cfg, today),
        "exSessions": exercise_series(program, log.sets, cfg),
    }


def render(data: dict, output: Path) -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise ValueError(f"{TEMPLATE} is missing {PLACEHOLDER}")
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace(PLACEHOLDER, blob), encoding="utf-8")
    (output.parent / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    return output
