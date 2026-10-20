# training-log

Static dashboard for a Google Sheets training log, built for a reps-then-load
program: reps climb to the top of the range, then load steps up.

```sh
make install
# export the `tracking` and `program` tabs to data/raw/*.csv first
make build      # writes site/index.html
```

Reading the sheet directly instead needs `source = "sheets"` and two env vars —
see [setup](docs/setup.md).

- [Data model](docs/data-model.md) — the two sheet tabs and their quirks
- [Metrics](docs/metrics.md) — what each chart shows and why
- [Setup](docs/setup.md) — local runs, `.env`, publishing
- [Google Cloud setup](docs/google-cloud.md) — service account, step by step
- [CLAUDE.md](CLAUDE.md) — project context
- [TODO.md](TODO.md) — current status and open questions

Status: live. CI builds from the sheet and deploys to Pages; local runs use the
CSV exports.
