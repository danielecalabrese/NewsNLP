import json
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from newsnlp.models.article import Article
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.kafka.producer import KafkaArticleProducer
from newsnlp.kafka.consumer import KafkaArticleConsumer


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
        topic="news.article",
    )

    assert kafka_producer.topic == "news.article"
    assert kafka_producer.producer is producer


def test_kafka_article_producer_sends_event():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="news.article",
    )

    event = create_test_event()

    kafka_producer.send(event)

    producer.produce.assert_called_once()

    call_kwargs = producer.produce.call_args.kwargs

    assert call_kwargs["topic"] == "news.article"

    payload = json.loads(call_kwargs["value"])

    assert payload["article"]["id"] == "article-1"
    assert payload["article"]["title"] == "Test article"


def test_kafka_article_producer_registers_delivery_callback():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="news.article",
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
        topic="news.article",
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
        topic="news.article",
    )

    event = create_test_event()

    kafka_producer.send(event)

    producer.flush.assert_not_called()


def test_kafka_article_producer_flush():
    producer = Mock()

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic="news.article",
    )

    kafka_producer.flush()

    producer.flush.assert_called_once()


def test_kafka_article_consumer_initialization():
    consumer = Mock()

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
    )

    assert kafka_consumer.topic == "news.article"
    assert kafka_consumer.consumer is consumer


def test_kafka_article_consumer_subscribes_to_topic():
    consumer = Mock()

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
    )

    kafka_consumer.subscribe()

    consumer.subscribe.assert_called_once_with(["news.article"])


def test_kafka_article_consumer_consumes_event():
    consumer = Mock()
    message = Mock()

    event = create_test_event()

    message.error.return_value = None
    message.value.return_value = event.model_dump_json().encode("utf-8")

    consumer.poll.return_value = message

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
    )

    result = kafka_consumer.consume()

    assert result is not None
    assert result.article.id == "article-1"
    assert result.article.title == "Test article"


def test_kafka_article_consumer_returns_none_when_no_message():
    consumer = Mock()
    consumer.poll.return_value = None

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
    )

    result = kafka_consumer.consume()

    assert result is None


def test_kafka_article_consumer_raises_on_kafka_error():
    consumer = Mock()
    message = Mock()

    message.error.return_value = Exception("Kafka error")
    consumer.poll.return_value = message

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
    )

    with pytest.raises(RuntimeError, match="Kafka consumption failed"):
        kafka_consumer.consume()


def test_kafka_article_consumer_close():
    consumer = Mock()

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
    )

    kafka_consumer.close()

    consumer.close.assert_called_once()
