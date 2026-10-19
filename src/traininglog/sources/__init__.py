from traininglog.config import Config
from traininglog.sources.base import Source
from traininglog.sources.csv_source import CsvSource


def build_source(cfg: Config) -> Source:
    if cfg.source == "csv":
        return CsvSource(cfg.csv_paths)
    if cfg.source == "sheets":
        if not cfg.sheet_id:
            raise RuntimeError("set TRAININGLOG_SHEET_ID to the spreadsheet id")
        from traininglog.sources.sheets import SheetsSource

        return SheetsSource(cfg.sheet_id, cfg.tabs)
    raise ValueError(f"unknown source {cfg.source!r}")


__all__ = ["CsvSource", "Source", "build_source"]
