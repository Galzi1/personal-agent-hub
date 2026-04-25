import sqlite3
import pytest

SAMPLE_RSS = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>GPT-5.5 released</title>
      <link>https://example.com/gpt55</link>
      <description>OpenAI releases GPT-5.5 with coding improvements.</description>
      <pubDate>Thu, 24 Apr 2026 12:00:00 +0000</pubDate>
    </item>
    <item>
      <title>How to use Codex (academy)</title>
      <link>https://openai.com/academy/codex</link>
      <description>Learn how to use Codex in 5 minutes.</description>
      <pubDate>Thu, 24 Apr 2026 11:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>"""

@pytest.fixture
def sample_rss():
    return SAMPLE_RSS

@pytest.fixture
def mock_openrouter_pass_response():
    return {
        "choices": [{"message": {"content": '[{"id":1,"verdict":"PASS"}]'}}],
        "usage": {"cost": 0.0},
    }

@pytest.fixture
def mock_openrouter_fail_response():
    return {
        "choices": [{"message": {"content": '[{"id":1,"verdict":"PASS"},{"id":2,"verdict":"FAIL"}]'}}],
        "usage": {"cost": 0.0},
    }

@pytest.fixture
def tmp_db_conn():
    """In-memory SQLite connection. init_db() called by test_db.py once db.py exists."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

@pytest.fixture
def sample_sources():
    return [
        {"name": "Test Feed A", "url": "https://example.com/feed.xml", "enabled": True, "note": ""},
        {"name": "Test Feed B", "url": "https://example.com/feed2.xml", "enabled": False, "note": "disabled"},
    ]
