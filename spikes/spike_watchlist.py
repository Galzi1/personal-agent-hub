"""
Watchlist Backtest Spike - Phase 0 Validation
Fetches 9 starter RSS/Atom feeds and reports items from the past 7 days.
"""
import feedparser
import httpx
from datetime import datetime, timedelta, timezone
from time import mktime
import sys

# The 9 starter feeds (from RISK-REVIEW.md A3 and RESEARCH.md)
# NOTE: URLs are best-guess and verification is PART of this spike
FEEDS = {
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "DeepMind Blog": "https://deepmind.google/blog/rss.xml",
    # Cursor Changelog: serves HTML for all /feed.xml, /rss, /rss.xml paths - no RSS available
    # Anthropic Blog: no RSS feed found (all /rss, /feed.xml, /news/rss return 404)
    "VS Code Blog": "https://code.visualstudio.com/feed.xml",  # was: /blogs/feed.xml (404)
    "Ollama Releases": "https://github.com/ollama/ollama/releases.atom",
    "TestingCatalog": "https://testingcatalog.com/feed/",  # was: /rss.xml (404)
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "Latent Space": "https://www.latent.space/feed",
}

CUTOFF = datetime.now(timezone.utc) - timedelta(days=7)
HEADERS = {"User-Agent": "PersonalAgentHub-Spike/0.1 (feed validation)"}


def fetch_feed(name: str, url: str) -> dict:
    """Fetch a single feed and return structured result."""
    result = {
        "name": name,
        "url": url,
        "status": "unknown",
        "http_status": None,
        "total_entries": 0,
        "recent_entries": [],
        "error": None,
    }

    try:
        # Use httpx to fetch with proper headers and timeout
        client = httpx.Client(follow_redirects=True, timeout=30.0)
        response = client.get(url, headers=HEADERS)
        result["http_status"] = response.status_code

        if response.status_code != 200:
            result["status"] = f"HTTP {response.status_code}"
            result["error"] = f"Non-200 response: {response.status_code}"
            return result

        # Parse with feedparser
        feed = feedparser.parse(response.text)

        if feed.bozo and not feed.entries:
            result["status"] = "PARSE_ERROR"
            result["error"] = str(feed.bozo_exception)
            return result

        result["total_entries"] = len(feed.entries)

        for entry in feed.entries:
            # Try to extract published date
            published = None
            for date_field in ["published_parsed", "updated_parsed", "created_parsed"]:
                parsed_time = entry.get(date_field)
                if parsed_time:
                    published = datetime.fromtimestamp(mktime(parsed_time), tz=timezone.utc)
                    break

            # Include entry if within 7 days or if no date available (include by default)
            include = True
            if published and published < CUTOFF:
                include = False

            if include:
                result["recent_entries"].append({
                    "title": entry.get("title", "[no title]"),
                    "link": entry.get("link", "[no link]"),
                    "published": published.isoformat() if published else "[no date]",
                    "source": name,
                })

        result["status"] = "OK"
        return result

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        return result


def main():
    print("=" * 70)
    print("WATCHLIST BACKTEST SPIKE - Phase 0 Validation")
    print(f"Cutoff: {CUTOFF.strftime('%Y-%m-%d %H:%M UTC')} (7 days ago)")
    print("=" * 70)
    print()

    all_results = []
    all_items = []

    for name, url in FEEDS.items():
        print(f"Fetching: {name}...")
        result = fetch_feed(name, url)
        all_results.append(result)
        all_items.extend(result["recent_entries"])

        if result["status"] == "OK":
            print(f"  -> OK: {result['total_entries']} total, {len(result['recent_entries'])} recent")
        else:
            print(f"  -> {result['status']}: {result.get('error', 'unknown error')}")

    print()
    print("=" * 70)
    print("FEED STATUS SUMMARY")
    print("=" * 70)

    working = sum(1 for r in all_results if r["status"] == "OK")
    failed = len(all_results) - working

    for r in all_results:
        status_icon = "OK" if r["status"] == "OK" else "FAIL"
        entry_count = (
            f"{len(r['recent_entries'])} recent / {r['total_entries']} total"
            if r["status"] == "OK"
            else r.get("error", "unknown")
        )
        print(f"  [{status_icon}] {r['name']}: {entry_count}")

    print(f"\nWorking: {working}/{len(FEEDS)} feeds")
    print(f"Failed: {failed}/{len(FEEDS)} feeds")

    print()
    print("=" * 70)
    print(f"ALL RECENT ITEMS ({len(all_items)} total)")
    print("=" * 70)

    # Sort by date (newest first), items without dates at the end
    def sort_key(item):
        if item["published"] == "[no date]":
            return ""
        return item["published"]

    all_items.sort(key=sort_key, reverse=True)

    for i, item in enumerate(all_items, 1):
        print(f"\n{i}. [{item['source']}] {item['title']}")
        print(f"   Date: {item['published']}")
        print(f"   Link: {item['link']}")

    print()
    print("=" * 70)
    print("COVERAGE REVIEW")
    print("=" * 70)
    print(f"Total items from past 7 days: {len(all_items)}")
    print(f"Sources contributing: {working}/{len(FEEDS)}")
    print()
    print("USER ACTION REQUIRED:")
    print("Compare the items above against your knowledge of important AI news this week.")
    print("Count: important stories CAUGHT vs. important stories MISSED.")
    print(f"Pass threshold: >= 50% coverage (per D-03)")
    print(f"If < 50%: accept and move on (per D-06). Do not block Phase 1.")


if __name__ == "__main__":
    main()
