import csv
from pathlib import Path

from traininglog.sources.base import Row


class CsvSource:
    def __init__(self, paths: dict[str, Path]) -> None:
        self._paths = paths

    def fetch(self, tab: str) -> list[Row]:
        path = self._paths[tab]
        if not path.exists():
            raise FileNotFoundError(f"export the {tab!r} tab to {path}")
        with path.open(newline="", encoding="utf-8-sig") as fh:
            return [{k: (v or "") for k, v in row.items() if k} for row in csv.DictReader(fh)]
