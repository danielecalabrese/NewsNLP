import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from confluent_kafka import Producer

from newsnlp.kafka.producer import KafkaArticleProducer
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.models.feed import FeedConfiguration
from newsnlp.readers.rss import RSSReader

logger = logging.getLogger(__name__)

CONFIG_FILE = Path("config/feeds.json")
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "news.article"


def ingest(feeds: list[FeedConfiguration]) -> int:
    """Ingest articles from enabled RSS feeds and publish them to Kafka."""

    producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic=KAFKA_TOPIC,
    )

    for feed in feeds:
        if not feed.enabled:
            continue

        reader = RSSReader(
            feed_url=feed.url,
            source_id=feed.name,
        )

        try:
            articles = reader.read()

            for article in articles:
                event = ArticleCreatedEvent(
                    article=article,
                    created_at=datetime.now(timezone.utc),
                )
                kafka_producer.send(event)

        except ValueError:
            logger.error("Error ingesting feed: %s", feed.name)
            return 1

    kafka_producer.flush()

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