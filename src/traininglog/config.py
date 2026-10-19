import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    sheet_id: str
    source: str
    output: Path
    tabs: dict[str, str]
    csv_paths: dict[str, Path]
    stale_days: int
    default_bodyweight: float
    bodyweight_exercises: frozenset[str]

    @classmethod
    def load(cls, path: Path | str = "config.toml") -> "Config":
        """TRAININGLOG_SOURCE overrides `source`, so CI reads the sheet
        without the committed config having to change."""
        raw = tomllib.loads(Path(path).read_text())
        rules = raw["rules"]
        return cls(
            sheet_id=os.environ.get("TRAININGLOG_SHEET_ID", raw.get("sheet_id", "")),
            source=os.environ.get("TRAININGLOG_SOURCE", raw["source"]),
            output=Path(raw["output"]),
            tabs=raw["tabs"],
            csv_paths={k: Path(v) for k, v in raw["csv"].items()},
            stale_days=rules["stale_days"],
            default_bodyweight=rules["default_bodyweight"],
            bodyweight_exercises=frozenset(rules["bodyweight_exercises"]),
        )
