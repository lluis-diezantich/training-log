import os

from traininglog.sources.base import Row

SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"


class SheetsSource:
    """Reads tabs through the Sheets API using a service account.

    Credentials come from GOOGLE_APPLICATION_CREDENTIALS. Share the spreadsheet
    with the service account's email (Viewer is enough).
    """

    def __init__(self, sheet_id: str, tabs: dict[str, str]) -> None:
        self._sheet_id = sheet_id
        self._tabs = tabs

    def fetch(self, tab: str) -> list[Row]:
        values = self._values(f"{self._tabs[tab]}!A:Z")
        if not values:
            return []
        header = [h.strip() for h in values[0]]
        rows = []
        for raw in values[1:]:
            padded = list(raw) + [""] * (len(header) - len(raw))
            rows.append({h: v for h, v in zip(header, padded, strict=False) if h})
        return rows

    def _values(self, rng: str) -> list[list[str]]:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not key:
            raise RuntimeError("set GOOGLE_APPLICATION_CREDENTIALS to the service account key")
        creds = service_account.Credentials.from_service_account_file(key, scopes=[SCOPE])
        api = build("sheets", "v4", credentials=creds, cache_discovery=False)
        result = api.spreadsheets().values().get(spreadsheetId=self._sheet_id, range=rng).execute()
        return result.get("values", [])
