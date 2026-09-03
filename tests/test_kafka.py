import json
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from newsnlp.models.article import Article
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.kafka.producer import KafkaArticleProducer


def create_test_event() -> ArticleCreatedEvent:
    article = Article(
        id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        content="This is a test article.",
        fetched_at=datetime.now(timezone.utc),
    )

    return ArticleCreatedEvent(
        article=article,
        created_at=datetime.now(timezone.utc),
    )


def test_kafka_article_producer_initialization():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="article-created",
    )

    assert kafka_producer.topic == "article-created"
    assert kafka_producer.producer is producer


def test_kafka_article_producer_sends_event():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="article-created",
    )

    event = create_test_event()

    kafka_producer.send(event)

    producer.produce.assert_called_once()

    call_kwargs = producer.produce.call_args.kwargs

    assert call_kwargs["topic"] == "article-created"

    payload = json.loads(call_kwargs["value"])

    assert payload["article"]["id"] == "article-1"
    assert payload["article"]["title"] == "Test article"


def test_kafka_article_producer_registers_delivery_callback():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="article-created",
    )

    event = create_test_event()

    kafka_producer.send(event)

    producer.produce.assert_called_once()

    call_kwargs = producer.produce.call_args.kwargs

    assert "callback" in call_kwargs
    assert callable(call_kwargs["callback"])


def test_kafka_article_producer_delivery_callback_raises_on_error():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="article-created",
    )

    with pytest.raises(RuntimeError, match="Kafka delivery failed"):
        kafka_producer._delivery_callback(
            Exception("Kafka error"),
            None,
        )


def test_kafka_article_producer_does_not_flush_after_send():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="article-created",
    )

    event = create_test_event()

    kafka_producer.send(event)

    producer.flush.assert_not_called()


def test_kafka_article_producer_flush():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="article-created",
    )

    kafka_producer.flush()

    producer.flush.assert_called_once()