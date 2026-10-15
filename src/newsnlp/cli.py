import argparse
import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path

from confluent_kafka import Consumer, Producer
from pymongo import MongoClient
from newsnlp.config import settings

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

CONFIG_FILE = settings.feeds_file
KAFKA_BROKER = settings.kafka_broker
KAFKA_TOPIC = settings.kafka_topic
KAFKA_PROCESSED_TOPIC = settings.kafka_processed_topic
KAFKA_CONSUMER_GROUP = settings.kafka_consumer_group
MONGODB_URI = settings.mongodb_uri
MONGODB_DATABASE = settings.mongodb_database

def ingest(feeds: list[FeedConfiguration]) -> int:
    """Ingest articles from enabled RSS feeds and publish them to Kafka."""

    producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic=KAFKA_TOPIC,
    )

    has_errors = False

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

        except (ValueError, requests.RequestException):
            logger.exception("Error ingesting feed: %s", feed.name)
            has_errors = True
            continue

    try:
        kafka_producer.flush()
    except (RuntimeError, TimeoutError):
        logger.exception("Failed to flush Kafka messages")
        has_errors = True

    return 1 if has_errors else 0


def process() -> int:
    """Consume article events and run the NewsNLP processing pipeline."""

    consumer = None
    producer = None
    mongo_client = None
    pipeline = None
    exit_code = 0

    try:
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

        pipeline.consumer.subscribe()
        logger.info("NewsNLP processing pipeline started")

        while True:
            pipeline.run_once()

    except KeyboardInterrupt:
        logger.info("Stopping NewsNLP processing pipeline")

    except Exception:
        logger.exception("Error in NewsNLP processing pipeline")
        exit_code = 1

    finally:
        if pipeline is not None:
            try:
                pipeline.close()
            except Exception:
                logger.exception("Error closing NewsNLP pipeline")
                exit_code = 1

        if producer is not None:
            try:
                remaining = producer.flush(10.0)
                if remaining > 0:
                    logger.error(
                        "Kafka producer shutdown timed out: %s messages remain",
                        remaining,
                    )
                    exit_code = 1
            except Exception:
                logger.exception("Error flushing Kafka producer")
                exit_code = 1

        if mongo_client is not None:
            try:
                mongo_client.close()
            except Exception:
                logger.exception("Error closing MongoDB client")
                exit_code = 1

    return exit_code


def run(config_file: Path | None = None) -> int:
    """Ingest configured feeds, then start processing the Kafka pipeline."""

    try:
        feeds = load_feeds(config_file)
    except FileNotFoundError:
        logger.error(
            "Feed configuration file not found: %s",
            config_file or CONFIG_FILE,
        )
        return 1
    except ValueError as exc:
        logger.error("Invalid feed configuration: %s", exc)
        return 1

    ingestion_result = ingest(feeds)
    processing_result = process()

    return 1 if ingestion_result or processing_result else 0


def main(args: list[str] | None = None) -> int:
    """Run the NewsNLP command-line interface."""

    parser = argparse.ArgumentParser(description="NewsNLP CLI")
    parser.add_argument(
        "command",
        choices=["ingest", "process", "run"],
        help="Application command to execute",
    )
    parser.add_argument(
        "--feeds-file",
        type=Path,
        default=None,
        help="Path to the JSON file containing RSS feed configurations",
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "ingest":
        try:
            feeds = load_feeds(parsed_args.feeds_file)
        except FileNotFoundError:
            logger.error(
                "Feed configuration file not found: %s",
                parsed_args.feeds_file or CONFIG_FILE,
            )
            return 1
        except ValueError as exc:
            logger.error("Invalid feed configuration: %s", exc)
            return 1

        return ingest(feeds)

    if parsed_args.command == "process":
        return process()

    if parsed_args.command == "run":
        return run(parsed_args.feeds_file)

    return 1


def load_feeds(
    config_file: Path | None = None,
) -> list[FeedConfiguration]:
    """Load and validate feed configurations from a JSON file."""

    config_file = config_file or CONFIG_FILE

    try:
        with config_file.open(encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in feed configuration file: {config_file}"
        ) from exc

    if not isinstance(data, dict) or not isinstance(data.get("feeds"), list):
        raise ValueError(
            f"Feed configuration must contain a 'feeds' list: {config_file}"
        )

    try:
        return [FeedConfiguration(**feed) for feed in data["feeds"]]
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid feed configuration in file: {config_file}"
        ) from exc


if __name__ == "__main__":
    raise SystemExit(main())
