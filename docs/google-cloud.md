# Google Cloud setup

One-time setup so the build can read the sheet without a browser login. A
service account is a Google account belonging to an application rather than a
person, which is what lets a scheduled job authenticate on its own.

## 1. Create a project

[console.cloud.google.com](https://console.cloud.google.com) → project menu in
the top bar → **New Project**. Name it something like `training-log`, press
**Create**, then make sure it is the selected project before continuing.

## 2. Enable the Sheets API

**APIs & Services** → **Enable APIs and Services** → search
**Google Sheets API** → **Enable**.

That is the only API needed. Guides usually tell you to enable the Google Drive
API as well, which is required to *create* spreadsheets or change their sharing
from code. This project only reads an existing sheet by id, so leave Drive off.

## 3. Create the service account

**APIs & Services** → **Credentials** → **Create Credentials** →
**Service account**. Give it a name, press **Create and Continue**.

At "Grant this service account access to the project", **skip it** — press
**Continue**, then **Done**.

Guides commonly grant **Editor** here. Don't. Project roles control access to
Google Cloud resources, and the spreadsheet is not one of them — it lives in
Drive and is reached by sharing it in the next step. Editor on the project
grants broad rights over the project itself and nothing at all over the sheet.

## 4. Download a JSON key

Open the service account → **Keys** → **Add Key** → **Create new key** →
**JSON** → **Create**. The file downloads once; Google keeps no copy.

Move it outside the repository:

```sh
mkdir -p ~/.config/training-log
mv ~/Downloads/training-log-*.json ~/.config/training-log/service-account.json
chmod 600 ~/.config/training-log/service-account.json
```

The key is a long-lived credential for an account that can read the sheet.
`.gitignore` covers `service-account*.json` as a backstop, but keeping it out of
the working tree is the real protection.

## 5. Share the sheet with the service account

This is the step that actually grants access. Open the JSON key and copy
`client_email` — it looks like
`training-log@<project>.iam.gserviceaccount.com`.

In the spreadsheet: **Share** → paste that address → role **Viewer** → uncheck
**Notify people** → **Share**.

Read-only is enough; this project never writes to the sheet.

## 6. Point the build at the key

```sh
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/training-log/service-account.json
```

Set `source = "sheets"` in `config.toml`, then check the connection before a
full build:

```sh
make check
```

It fetches both tabs and prints the row counts. Then:

```sh
make build
```

Both go through `uv run`, which uses the project's virtual environment. Running
`traininglog` bare only works with the venv activated (`source .venv/bin/activate`).

## 7. For CI

**Settings → Secrets and variables → Actions → New repository secret**, named
`GOOGLE_SERVICE_ACCOUNT`, with the entire JSON file as the value.

`.github/workflows/pages.yml` already consumes it: the secret reaches the step
as an environment variable, gets written to a `chmod 600` file under
`RUNNER_TEMP`, and `GOOGLE_APPLICATION_CREDENTIALS` points at that path. It is
passed through the environment rather than interpolated into a `run:` line,
because command arguments appear in process listings and can surface in logs.

## Troubleshooting

| message | cause |
|---|---|
| `403 The caller does not have permission` | step 5 was missed, or shared with the wrong address. Compare against `client_email` in the key |
| `403 Google Sheets API has not been used in project ... before or it is disabled` | step 2 was missed, or a different project is selected |
| `404 Requested entity was not found` | wrong `sheet_id` in `config.toml`. It is the segment between `/d/` and `/edit` in the sheet URL |
| `Unable to parse range: program!A:Z` | no tab named `program`. Tab names are case-sensitive and set in `config.toml` under `[tabs]` |
| `set GOOGLE_APPLICATION_CREDENTIALS...` | the env var is unset, or points at a path that does not exist |

## Why not gspread

`gspread` is friendlier for read-write work. This project makes two read calls
and already has `google-auth` as a transitive dependency, so the official client
avoids an extra layer for no gain.
