"""ASX announcements via the public Markit Digital API that backs asx.com.au."""
from dataclasses import dataclass
from datetime import datetime

import requests

LIST_URL = "https://asx.api.markitdigital.com/asx-research/1.0/companies/{ticker}/announcements"
# Public token embedded in asx.com.au's own announcement pages.
FILE_URL = ("https://cdn-api.markitdigital.com/apiman-gateway/ASX/asx-research/1.0/file/{key}"
            "?access_token=83ff96335c2d45a094df02a206a39ff4")
HEADERS = {"User-Agent": "Mozilla/5.0 (Veritas watchlist announcements)"}


@dataclass(frozen=True)
class Announcement:
    ticker: str
    key: str            # ASX documentKey, e.g. "2924-03152828-2A1706009"
    headline: str
    type: str
    price_sensitive: bool
    released: str       # ISO-8601 UTC


def parse_announcements(payload):
    data = payload.get("data") or {}
    return [
        Announcement(
            ticker=data["symbol"],
            key=item["documentKey"],
            headline=item["headline"].strip(),
            type=item["announcementType"],
            price_sensitive=bool(item["isPriceSensitive"]),
            released=datetime.fromisoformat(item["date"].replace("Z", "+00:00")).replace(microsecond=0).isoformat(),
        )
        for item in data.get("items") or []
    ]


def pdf_filename(a):
    return f"{a.key.split('-')[1]}.pdf"


def fetch_announcements(ticker, count=10):
    resp = requests.get(LIST_URL.format(ticker=ticker.lower()), headers=HEADERS, timeout=30,
                        params={"count": count, "market_sensitive": "false"})
    resp.raise_for_status()
    return parse_announcements(resp.json())


def fetch_pdf(a):
    resp = requests.get(FILE_URL.format(key=a.key), headers=HEADERS, timeout=60)
    resp.raise_for_status()
    if not resp.content.startswith(b"%PDF"):
        raise ValueError(f"{a.ticker} {a.key}: response is not a PDF")
    return resp.content
