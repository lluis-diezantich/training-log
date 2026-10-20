# TODO

## Next
- [ ] Decide whether the dashboard should stay public. Pages serves publicly on
      Free/Pro even from a private repo, and the page carries bodyweight and
      sleep data. `noindex` + `robots.txt` are in place, which stops search
      engines but not anyone with the URL

## Nice to have
- [ ] Re-store `GOOGLE_SERVICE_ACCOUNT` base64-encoded. Raw multi-line JSON makes
      GitHub mask every `{` and `}`, which redacts braces in unrelated tracebacks
- [ ] Sparse-data guards in the page (no exercise with two sessions, no session
      or sleep rows) are written but not checked in a browser

## Done
Repo on GitHub under the personal account, history rewritten so the sheet id
never appears in it, `.env` and pre-commit in place, both secrets set, Pages
source on GitHub Actions, and `pages` deploying from the live sheet in ~35s.
`SheetsSource` works end to end. Queue delays resolved themselves.

2026-10-20: the three `program` tab names now match `tracking`, so no exercise is
silently dropped, and the unused `TRAININGLOG_SHEET_ID` secret is gone. Four code
fixes: an unfinished session reads `short-sets` instead of `add-load`; each chart
point is one real set rather than the session's heaviest load against its worst
reps; the payload escapes `</` before going into the `<script>`; and the
non-exercise row names match case-insensitively.
