import os

from traininglog.sources.base import Row

SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"
DOCS = "see docs/google-cloud.md"


def _explain(status: int, tab: str) -> str:
    if status == 404:
        return (
            "spreadsheet not found. Either TRAININGLOG_SHEET_ID is wrong - it is the segment "
            f"between /d/ and /edit, not the gid - or the sheet is not shared with the "
            f"service account, which Google also reports as 404. {DOCS}"
        )
    if status == 403:
        return (
            "access denied. Enable the Google Sheets API on the project, and share the sheet "
            f"with the service account's client_email. {DOCS}"
        )
    if status == 400:
        return (
            f"bad range for tab {tab!r}. Tab names are case-sensitive and set in config.toml "
            f"under [tabs]. {DOCS}"
        )
    return f"Sheets API error {status}. {DOCS}"


class SheetsSource:
    """Reads tabs through the Sheets API using a service account.

    Credentials come from GOOGLE_APPLICATION_CREDENTIALS. Share the spreadsheet
    with the service account's email (Viewer is enough).
    """

    def __init__(self, sheet_id: str, tabs: dict[str, str]) -> None:
        self._sheet_id = sheet_id
        self._tabs = tabs

    @staticmethod
    def _a1(title: str) -> str:
        """Quote a sheet title for A1 notation; internal quotes double."""
        return "'" + title.replace("'", "''") + "'"

    def fetch(self, tab: str) -> list[Row]:
        values = self._values(f"{self._a1(self._tabs[tab])}!A:Z", tab)
        if not values:
            return []
        header = [h.strip() for h in values[0]]
        rows = []
        for raw in values[1:]:
            padded = list(raw) + [""] * (len(header) - len(raw))
            rows.append({h: v for h, v in zip(header, padded, strict=False) if h})
        return rows

    def _values(self, rng: str, tab: str) -> list[list[str]]:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not key:
            raise RuntimeError("set GOOGLE_APPLICATION_CREDENTIALS to the service account key")
        creds = service_account.Credentials.from_service_account_file(key, scopes=[SCOPE])
        api = build("sheets", "v4", credentials=creds, cache_discovery=False)
        try:
            result = (
                api.spreadsheets().values().get(spreadsheetId=self._sheet_id, range=rng).execute()
            )
        except HttpError as err:
            raise RuntimeError(_explain(err.resp.status, tab)) from err
        return result.get("values", [])
