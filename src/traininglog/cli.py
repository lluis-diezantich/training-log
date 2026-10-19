import argparse
import datetime as dt
from pathlib import Path

from traininglog.config import Config
from traininglog.ingest import load_log, load_program
from traininglog.render import payload, render
from traininglog.sources import build_source


def build(cfg: Config, today: dt.date | None = None) -> Path:
    source = build_source(cfg)
    log = load_log(source.fetch("tracking"))
    program = load_program(source.fetch("program"), on=today)
    out = render(payload(log, program, cfg, today), cfg.output)
    skipped = f", {log.skipped} skipped (no reps)" if log.skipped else ""
    print(f"{out}  {len(log.sets)} sets{skipped}  {len(program)} prescribed exercises")
    return out


def check(cfg: Config) -> None:
    source = build_source(cfg)
    for tab in ("tracking", "program"):
        print(f"{tab:<9} {len(source.fetch(tab))} rows")


def main() -> None:
    parser = argparse.ArgumentParser(prog="traininglog")
    parser.add_argument("command", choices=["build", "check"])
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    args = parser.parse_args()
    cfg = Config.load(args.config)
    if args.command == "check":
        check(cfg)
    else:
        build(cfg)
