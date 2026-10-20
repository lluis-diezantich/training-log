# TODO

## Next
- [x] Fix three names in the sheet's `program` tab — they still differ from the
      `tracking` tab, so the dashboard silently drops exercises:
      `DB Wrist Curl` → `Wrist Curls`, `DB Wrist Extension` → `Wrist Extension`
      (both currently show as untracked and are hidden), and
      `Tricep Extension` → `Triceps Extension`
- [x] Delete the unused `TRAININGLOG_SHEET_ID` repo secret; the workflow reads
      `GOOGLE_SHEET_ID`
- [ ] Decide whether the dashboard should stay public. Pages serves publicly on
      Free/Pro even from a private repo, and the page carries bodyweight and
      sleep data. `noindex` + `robots.txt` are in place, which stops search
      engines but not anyone with the URL

## Nice to have
- [ ] Re-store `GOOGLE_SERVICE_ACCOUNT` base64-encoded. Raw multi-line JSON makes
      GitHub mask every `{` and `}`, which redacts braces in unrelated tracebacks
- [ ] Sparse-data guards in the page (no exercise with two sessions, no session
      or sleep rows) are written but not checked in a browser

## Open questions
- [ ] `valid_from 2026-10-03` was inferred from the earliest sets of the new
      exercises. Confirm the real start date
- [ ] Calf Raises: prescription says 2×15-20 but recent sets are 10 kg × 8.
      Stale target, or wrong load?
- [ ] Triceps Extension went 19 kg → 9.15 kg over 8 sessions while reps rose.
      Deliberate reset, or a different implementation?
- [ ] 91 completed rows have no reps and are dropped. Worth fixing at source?
- [ ] Session length covers the whole workout, not one exercise. Keep the
      sparkline or drop it?

## Done
Repo on GitHub under the personal account, history rewritten so the sheet id
never appears in it, `.env` and pre-commit in place, both secrets set, Pages
source on GitHub Actions, and `pages` deploying from the live sheet in ~35s.
`SheetsSource` works end to end. Queue delays resolved themselves.
