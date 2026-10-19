import datetime as dt
from pathlib import Path

import pytest

from traininglog.config import Config
from traininglog.ingest import load_log, load_program
from traininglog.sources import CsvSource

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = dt.date(2026, 10, 19)


@pytest.fixture
def cfg() -> Config:
    return Config(
        sheet_id="test",
        source="csv",
        output=Path("docs/index.html"),
        tabs={"tracking": "tracking", "program": "program"},
        csv_paths={"tracking": FIXTURES / "tracking.csv", "program": FIXTURES / "program.csv"},
        stale_days=14,
        default_bodyweight=73.0,
        bodyweight_exercises=frozenset({"pull up"}),
    )


@pytest.fixture
def source(cfg: Config) -> CsvSource:
    return CsvSource(cfg.csv_paths)


@pytest.fixture
def log(source: CsvSource):
    return load_log(source.fetch("tracking"))


@pytest.fixture
def program(source: CsvSource):
    return load_program(source.fetch("program"), on=TODAY)
