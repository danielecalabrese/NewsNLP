import pytest
import feedparser
import logging
from datetime import datetime, timezone
from time import struct_time
from unittest.mock import patch
from feedparser import FeedParserDict
from newsnlp.readers.rss import RSSReader
from newsnlp.models.article import Article


def test_rss_reader_returns_articles_from_feed():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "author": "John Doe",
                    "published_parsed": None,
                    "description": "This is the article content.",
                }
            ],
            "bozo": False,
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()
        

    assert len(articles) == 1

    article = articles[0]
    assert isinstance(article, Article)

    assert article.id == "article-1"
    assert article.source_id == "source-1"
    assert article.title == "Test article"
    assert article.url == "https://example.com/article-1"
    assert article.author == "John Doe"
    assert article.content == "This is the article content."
    assert article.fetched_at <= datetime.now(timezone.utc)


def test_rss_reader_parses_published_at():
    published_at = struct_time(
        (2026, 8, 30, 10, 30, 0, 6, 242, 0)
    )

    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "description": "This is the article content.",
                    "published_parsed": published_at,
                }
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert articles[0].published_at == datetime(
        2026, 8, 30, 10, 30, tzinfo=timezone.utc
    )

def test_rss_reader_parses_summary():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "description": "This is the article content.",
                    "summary": "This is the article summary.",
                }
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert articles[0].summary == "This is the article summary."

def test_rss_reader_returns_empty_list_for_empty_feed():
    feed = FeedParserDict({"entries": []})

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert articles == []

def test_rss_reader_uses_content_when_description_is_missing():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "content": [
                        {
                            "value": "This is the article content."
                        }
                    ],
                }
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert articles[0].content == "This is the article content."

def test_rss_reader_uses_summary_when_content_is_missing():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "summary": "This is the article summary.",
                }
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert articles[0].content == "This is the article summary."

def test_rss_reader_skips_entries_without_content():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Article without content",
                    "link": "https://example.com/article-1",
                },
                {
                    "id": "article-2",
                    "title": "Valid article",
                    "link": "https://example.com/article-2",
                    "description": "This is valid content.",
                },
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert len(articles) == 1
    assert articles[0].id == "article-2"

def test_rss_reader_raises_error_for_invalid_feed():
    feed = FeedParserDict(
        {
            "entries": [],
            "bozo": True,
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/invalid-rss",
            source_id="source-1",
        )

        with pytest.raises(ValueError, match="Invalid RSS feed"):
            reader.read()

def test_rss_reader_preserves_optional_fields_when_missing():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "description": "This is the article content.",
                }
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    article = articles[0]

    assert article.author is None
    assert article.published_at is None
    assert article.summary is None


def test_rss_reader_prefers_description_over_content_and_summary():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "description": "Description content.",
                    "content": [{"value": "Content value."}],
                    "summary": "Summary content.",
                }
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert articles[0].content == "Description content."


def test_rss_reader_prefers_content_over_summary():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "content": [{"value": "Content value."}],
                    "summary": "Summary content.",
                }
            ]
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert articles[0].content == "Content value."

def test_rss_reader_logs_error_for_invalid_feed(caplog):
    reader = RSSReader("https://example.com/invalid-feed")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Invalid RSS feed"):
            reader.read()

    assert "Invalid RSS feed" in caplog.text


def test_rss_reader_logs_error_for_invalid_feed(caplog, monkeypatch):
    def fake_parse(_):
        return FeedParserDict({"bozo": True})

    monkeypatch.setattr(feedparser, "parse", fake_parse)

    reader = RSSReader(
        "https://example.com/invalid-feed",
        "test-source",
    )

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Invalid RSS feed"):
            reader.read()

    assert "Invalid RSS feed" in caplog.text


def test_rss_reader_logs_success(caplog, monkeypatch):
    fake_feed = FeedParserDict(
        {
            "bozo": False,
            "entries": [
                {
                    "id": "article-1",
                    "title": "Test article",
                    "link": "https://example.com/article-1",
                    "description": "Test article content",
                }
            ],
        }
    )

    monkeypatch.setattr(feedparser, "parse", lambda _: fake_feed)

    reader = RSSReader(
        "https://example.com/feed",
        "test-source",
    )

    with caplog.at_level(logging.INFO):
        articles = reader.read()

    assert len(articles) == 1
    assert "Successfully read RSS feed" in caplog.text


def test_rss_reader_logs_and_skips_invalid_entry(caplog, monkeypatch):
    fake_feed = FeedParserDict(
        {
            "bozo": False,
            "entries": [
                {
                    "id": "article-1",
                    "title": "Valid article",
                    "link": "https://example.com/article-1",
                    "description": "Valid article content",
                },
                {
                    "id": "article-2",
                    "title": "Invalid article",
                    "link": "https://example.com/article-2",
                    "description": "Invalid article content",
                },
            ],
        }
    )

    monkeypatch.setattr(feedparser, "parse", lambda _: fake_feed)

    reader = RSSReader(
        "https://example.com/feed",
        "test-source",
    )

    original_parse_entry = reader._parse_entry

    def fake_parse_entry(entry):
        if entry["id"] == "article-2":
            raise ValueError("Invalid article")

        return original_parse_entry(entry)

    monkeypatch.setattr(reader, "_parse_entry", fake_parse_entry)

    with caplog.at_level(logging.ERROR):
        articles = reader.read()

    assert len(articles) == 1
    assert articles[0].id == "article-1"
    assert "Error parsing RSS entry article-2" in caplog.text


def test_rss_reader_creates_one_article_per_feed_entry():
    feed = FeedParserDict(
        {
            "entries": [
                {
                    "id": "article-1",
                    "title": "First article",
                    "link": "https://example.com/article-1",
                    "description": "First article content.",
                },
                {
                    "id": "article-2",
                    "title": "Second article",
                    "link": "https://example.com/article-2",
                    "description": "Second article content.",
                },
            ],
            "bozo": False,
        }
    )

    with patch("newsnlp.readers.rss.feedparser.parse", return_value=feed):
        reader = RSSReader(
            feed_url="https://example.com/rss",
            source_id="source-1",
        )

        articles = reader.read()

    assert len(articles) == 2
    assert all(isinstance(article, Article) for article in articles)
    assert articles[0].id == "article-1"
    assert articles[1].id == "article-2"