import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from confluent_kafka import Consumer, Producer
from pymongo import MongoClient

from newsnlp.kafka.consumer import KafkaArticleConsumer
from newsnlp.kafka.producer import KafkaArticleProducer
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.models.feed import FeedConfiguration
from newsnlp.mongodb_storage import MongoArticleStorage
from newsnlp.nlp.keyword_extractor import KeywordExtractor
from newsnlp.nlp.sentiment_analyzer import SentimentAnalyzer
from newsnlp.processing.article_processing_service import ArticleProcessingService
from newsnlp.processing.article_processor import ArticleProcessor
from newsnlp.processing.pipeline import NewsNLPPipeline
from newsnlp.readers.rss import RSSReader

logger = logging.getLogger(__name__)

CONFIG_FILE = Path("config/feeds.json")
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "news.article"
KAFKA_PROCESSED_TOPIC = "news.article.processed"
KAFKA_CONSUMER_GROUP = "newsnlp-processing"
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DATABASE = "newsnlp"

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


def process() -> int:
    """Consume article events and run the NewsNLP processing pipeline."""

    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BROKER,
            "group.id": KAFKA_CONSUMER_GROUP,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )

    producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    mongo_client = MongoClient(MONGODB_URI)

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic=KAFKA_TOPIC,
        event_model=ArticleCreatedEvent,
    )

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic=KAFKA_PROCESSED_TOPIC,
    )

    storage = MongoArticleStorage(
        client=mongo_client,
        database_name=MONGODB_DATABASE,
    )

    processor = ArticleProcessor(
        keyword_extractor=KeywordExtractor(),
        sentiment_analyzer=SentimentAnalyzer(),
        storage=storage,
    )

    processing_service = ArticleProcessingService(
        processor=processor,
        producer=kafka_producer,
    )

    pipeline = NewsNLPPipeline(
        consumer=kafka_consumer,
        processing_service=processing_service,
    )

    try:
        pipeline.consumer.subscribe()

        logger.info("NewsNLP processing pipeline started")

        while True:
            pipeline.run_once()

    except KeyboardInterrupt:
        logger.info("Stopping NewsNLP processing pipeline")

    except Exception:
        logger.exception("Error in NewsNLP processing pipeline")
        return 1

    finally:
        pipeline.close()
        producer.flush()
        mongo_client.close()

    return 0


def main(args: list[str] | None = None) -> int:
    """Run the NewsNLP command-line interface."""

    parser = argparse.ArgumentParser(description="NewsNLP CLI")
    parser.add_argument("command", choices=["ingest", "process"])

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "ingest":
        try:
            feeds = load_feeds()
        except FileNotFoundError:
            logger.error("Feed configuration file not found: %s", CONFIG_FILE)
            return 1

        return ingest(feeds)

    if parsed_args.command == "process":
        return process()

    return 1


def load_feeds() -> list[FeedConfiguration]:
    """Load feed configurations from the JSON configuration file."""

    with CONFIG_FILE.open(encoding="utf-8") as file:
        data = json.load(file)

    return [FeedConfiguration(**feed) for feed in data["feeds"]]


if __name__ == "__main__":
    raise SystemExit(main())
