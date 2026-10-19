# TODO

## Next
- [ ] Rewrite history to drop the sheet id, then force push (commands in
      `docs/setup.md`). Cheap now at 3 commits
- [ ] Add the `GOOGLE_SHEET_ID` repo secret alongside `GOOGLE_SERVICE_ACCOUNT`
- [ ] Copy `.env.example` to `.env` and fill it in
- [ ] Commit the move to `site/` — `docs/index.html` is deleted and needs
      staging, `.gitignore` now covers `site/`
- [ ] Settings → Pages → Source: **GitHub Actions**
- [ ] Decide whether the dashboard should be public at all. Pages is public on
      Free/Pro even from a private repo, and the page carries bodyweight and
      sleep data
- [ ] Run `pre-commit install` once, locally

## Blocked
- [ ] `SheetsSource` is written but never run against the live API — needs the
      service account: enable Sheets API, create account + JSON key, share the
      sheet with its email (Viewer). User is handling this later
- [ ] `pages.yml` is written and will fail until the `GOOGLE_SERVICE_ACCOUNT`
      repo secret exists
- [ ] `gh` is authenticated as the work account only

## Unverified
- [ ] `SheetsSource` error paths (404/403/400 messages, A1 quoting) are unit
      tested but have never hit the live API
- [ ] Sparse-data guards in the page (no exercise with 2 sessions, no session or
      sleep rows) are written but not checked in a browser

## Open questions
- [ ] `valid_from 2026-10-03` in `data/raw/program.csv` is inferred from the
      earliest sets of the new exercises. Confirm the real start date
- [ ] Calf Raises: prescription says 2×15-20 but recent sets are 10 kg × 8.
      Stale target, or wrong load?
- [ ] Triceps Extension went 19 kg → 9.15 kg over 8 sessions while reps rose.
      Deliberate reset, or a different implementation?
- [ ] 91 completed rows have no reps and are dropped. Worth fixing at source?
- [ ] Session length covers the whole workout, not one exercise. Keep the
      sparkline or drop it?
