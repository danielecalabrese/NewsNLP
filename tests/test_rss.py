import pytest
from datetime import datetime, timezone
from time import struct_time

from unittest.mock import patch

from feedparser import FeedParserDict

from newsnlp.readers.rss import RSSReader


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

    article = articles[0]

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