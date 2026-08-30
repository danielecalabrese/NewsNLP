from datetime import datetime, timezone

import feedparser

from newsnlp.models.article import Article


class RSSReader:
    def __init__(self, feed_url: str, source_id: str):
        """Initialize the RSS reader with a feed URL and source identifier."""

        self.feed_url = feed_url
        self.source_id = source_id

    def read(self) -> list[Article]:
        """Read the RSS feed and return its entries as Article objects."""
    
        feed = feedparser.parse(self.feed_url)

        if getattr(feed, "bozo", False):
            raise ValueError("Invalid RSS feed")
        
        articles = []
    
        for entry in feed.entries:
            article = self._parse_entry(entry)
    
            if article is not None:
                articles.append(article)
    
        return articles

    def _parse_entry(self, entry) -> Article | None:
        """Convert a single RSS entry into an Article object."""

        content = self._parse_content(entry)

        if not content:
            return None

        return Article(
            id=entry["id"],
            source_id=self.source_id,
            title=entry["title"],
            url=entry["link"],
            author=entry.get("author"),
            published_at=self._parse_published_at(entry),
            content=content,
            summary=entry.get("summary"),
            fetched_at=datetime.now(timezone.utc),
        )
    
    def _parse_published_at(self, entry) -> datetime | None:
        """Convert the RSS published date to a timezone-aware datetime."""

        published_parsed = entry.get("published_parsed")

        if published_parsed is None:
            return None

        return datetime(
            *published_parsed[:6],
            tzinfo=timezone.utc,
        )
    
    def _parse_content(self, entry) -> str:
        """Extract article content from an RSS entry."""

        description = entry.get("description")

        if description:
            return description

        content = entry.get("content")

        if content:
            return content[0].get("value", "")

        summary = entry.get("summary")

        if summary:
            return summary

        return ""