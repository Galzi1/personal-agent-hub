import uuid
import httpx
import feedparser
from datetime import datetime, timezone
from time import mktime
from typing import Optional
from pydantic import BaseModel

class RawItem(BaseModel):
    """Schema for raw items discovered in RSS feeds."""
    id: str
    run_id: str
    source_name: str
    title: str
    link: str
    published_at: Optional[str]
    summary: str
    ingested_at: str

class IngestionError(Exception):
    """Raised when feed fetching or parsing fails."""
    pass

def fetch_feed(name: str, url: str) -> list[RawItem]:
    """Fetch and parse RSS/Atom feed into RawItem objects."""
    headers = {"User-Agent": "PersonalAgentHub/0.1"}

    try:
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
    except Exception as e:
        raise IngestionError(f"HTTP fetch failed for {name}: {e}")

    feed = feedparser.parse(response.text)
    if feed.bozo and not feed.entries:
        raise IngestionError(f"Malformed feed and no entries for {name}: {feed.bozo_exception}")

    ingested_at = datetime.now(timezone.utc).isoformat()
    items = []

    for entry in feed.entries:
        # Date fallback chain: published_parsed -> updated_parsed -> created_parsed
        parsed_date = (
            entry.get("published_parsed") or
            entry.get("updated_parsed") or
            entry.get("created_parsed")
        )

        published_at = None
        if parsed_date:
            published_at = datetime(*parsed_date[:6], tzinfo=timezone.utc).isoformat()

        items.append(RawItem(
            id=str(uuid.uuid4()),
            run_id="",
            source_name=name,
            title=entry.get("title", "No Title"),
            link=entry.get("link", ""),
            published_at=published_at,
            summary=entry.get("summary", ""),
            ingested_at=ingested_at
        ))

    return items
