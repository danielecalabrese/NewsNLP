import time
import uuid
from datetime import datetime, timezone

import pytest
from confluent_kafka import Consumer, Producer
from pymongo import MongoClient

from newsnlp.kafka.consumer import KafkaArticleConsumer
from newsnlp.kafka.producer import KafkaArticleProducer
from newsnlp.models.article import Article
from newsnlp.models.events import ArticleCreatedEvent, ProcessedArticleEvent
from newsnlp.mongodb_storage import MongoArticleStorage
from newsnlp.nlp.keyword_extractor import KeywordExtractor
from newsnlp.nlp.sentiment_analyzer import SentimentAnalyzer
from newsnlp.processing.article_processing_service import ArticleProcessingService
from newsnlp.processing.article_processor import ArticleProcessor
from newsnlp.processing.pipeline import NewsNLPPipeline


BROKER = "localhost:9092"
MONGO_URI = "mongodb://localhost:27017"


def test_end_to_end_article_pipeline():
    suffix = uuid.uuid4().hex

    input_topic = f"news.article.e2e.{suffix}"
    output_topic = f"news.article.processed.e2e.{suffix}"
    consumer_group = f"newsnlp-e2e-{suffix}"
    database_name = f"newsnlp_e2e_{suffix}"

    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command("ping")

    storage = MongoArticleStorage(
        client=mongo_client,
        database_name=database_name,
    )

    input_producer = Producer({"bootstrap.servers": BROKER})
    output_producer = Producer({"bootstrap.servers": BROKER})

    input_consumer = Consumer(
        {
            "bootstrap.servers": BROKER,
            "group.id": consumer_group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )

    output_consumer = Consumer(
        {
            "bootstrap.servers": BROKER,
            "group.id": f"{consumer_group}-output",
            "auto.offset.reset": "earliest",
        }
    )

    pipeline = None

    try:
        article = Article(
            id=f"e2e-article-{suffix}",
            source_id="e2e-test",
            title="Government announces positive economic growth",
            url=f"https://example.com/{suffix}",
            content=(
                "  The government announced   positive economic growth "
                "and successful results.  "
            ),
            fetched_at=datetime.now(timezone.utc),
        )

        input_event = ArticleCreatedEvent(
            article=article,
            created_at=datetime.now(timezone.utc),
        )

        input_kafka_producer = KafkaArticleProducer(
            producer=input_producer,
            topic=input_topic,
        )
        input_kafka_producer.send_and_wait(input_event)

        kafka_input_consumer = KafkaArticleConsumer(
            consumer=input_consumer,
            topic=input_topic,
            event_model=ArticleCreatedEvent,
        )
        kafka_input_consumer.subscribe()

        processor = ArticleProcessor(
            language_detector=lambda text: "en",
            keyword_extractor=KeywordExtractor(),
            sentiment_analyzer=SentimentAnalyzer(),
            storage=storage,
        )

        processing_service = ArticleProcessingService(
            processor=processor,
            producer=KafkaArticleProducer(
                producer=output_producer,
                topic=output_topic,
            ),
        )

        pipeline = NewsNLPPipeline(
            consumer=kafka_input_consumer,
            processing_service=processing_service,
        )

        deadline = time.monotonic() + 15
        processed = False

        while time.monotonic() < deadline:
            if pipeline.run_once(timeout=1.0):
                processed = True
                break

        assert processed, "The pipeline did not process the input event"

        output_consumer.subscribe([output_topic])

        stored_article = storage.get(article.id)

        assert stored_article is not None
        assert stored_article.article_id == article.id
        assert stored_article.source_id == article.source_id
        assert stored_article.title == article.title
        assert stored_article.content == (
            "The government announced positive economic growth "
            "and successful results."
        )
        assert stored_article.language == "en"
        assert stored_article.processed_at is not None

        deadline = time.monotonic() + 10
        output_event = None

        while time.monotonic() < deadline:
            message = output_consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                raise RuntimeError(
                    f"Kafka output consumption failed: {message.error()}"
                )

            output_event = ProcessedArticleEvent.model_validate_json(
                message.value()
            )
            break

        assert output_event is not None, (
            "No processed article event was published to Kafka"
        )
        assert output_event.article.article_id == article.id
        assert output_event.article.content == stored_article.content
        assert output_event.article.language == "en"

    finally:
        if pipeline is not None:
            pipeline.close()

        output_consumer.close()
        input_producer.flush()
        output_producer.flush()
        mongo_client.drop_database(database_name)
        mongo_client.close()