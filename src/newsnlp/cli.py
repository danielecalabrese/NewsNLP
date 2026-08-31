import argparse
import json
import logging
from pathlib import Path

from newsnlp.models.feed import FeedConfiguration
from newsnlp.readers.rss import RSSReader


logger = logging.getLogger(__name__)

CONFIG_FILE = Path("config/feeds.json")


def ingest(feeds: list[FeedConfiguration]) -> int:
    """Ingest articles from enabled RSS feeds."""

    for feed in feeds:
        if not feed.enabled:
            continue

        reader = RSSReader(
            feed_url=feed.url,
            source_id=feed.name,
        )

        try:
            reader.read()
        except ValueError:
            logger.error("Error ingesting feed: %s", feed.name)
            return 1

    return 0


def main(args: list[str] | None = None) -> int:
    """Run the NewsNLP command-line interface."""

    parser = argparse.ArgumentParser(description="NewsNLP CLI")
    parser.add_argument("command", choices=["ingest"])

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "ingest":
        try:
            feeds = load_feeds()
        except FileNotFoundError:
            logger.error("Feed configuration file not found: %s", CONFIG_FILE)
            return 1

        return ingest(feeds)

    return 1


def load_feeds() -> list[FeedConfiguration]:
    """Load feed configurations from the JSON configuration file."""

    with CONFIG_FILE.open(encoding="utf-8") as file:
        data = json.load(file)

    return [FeedConfiguration(**feed) for feed in data["feeds"]]


if __name__ == "__main__":
    raise SystemExit(main())