from typing import Protocol

Row = dict[str, str]


class Source(Protocol):
    """Returns raw rows for a named tab, exactly as the sheet holds them."""

    def fetch(self, tab: str) -> list[Row]: ...
