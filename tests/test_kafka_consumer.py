import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from newsnlp.kafka.consumer import KafkaArticleConsumer
from newsnlp.models.article import Article
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.models.events import ArticleCreatedEvent, ProcessedArticleEvent
from newsnlp.models.processed_article import ProcessedArticle


def create_event() -> ArticleCreatedEvent:
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Test article content",
        fetched_at=datetime.now(),
    )

    return ArticleCreatedEvent(
        article=article,
        created_at=datetime.now(),
    )


def test_kafka_article_consumer_subscribe():
    consumer = Mock()
    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
        event_model=ArticleCreatedEvent,
    )

    kafka_consumer.subscribe()

    consumer.subscribe.assert_called_once_with(["news.article"])


def test_kafka_article_consumer_consume_no_message():
    consumer = Mock()
    consumer.poll.return_value = None

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
        event_model=ArticleCreatedEvent,
    )

    result = kafka_consumer.consume()

    assert result is None
    consumer.poll.assert_called_once_with(1.0)


def test_kafka_article_consumer_consume_message():
    consumer = Mock()
    message = Mock()

    event = create_event()
    payload = event.model_dump_json().encode("utf-8")

    message.error.return_value = None
    message.value.return_value = payload
    consumer.poll.return_value = message

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
        event_model=ArticleCreatedEvent,
    )

    result = kafka_consumer.consume()

    assert result == event
    consumer.poll.assert_called_once_with(1.0)


def test_kafka_article_consumer_consume_error():
    consumer = Mock()
    message = Mock()

    message.error.return_value = "consumer error"
    consumer.poll.return_value = message

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
        event_model=ArticleCreatedEvent,
    )

    with pytest.raises(RuntimeError, match="Kafka consumption failed"):
        kafka_consumer.consume()


def test_kafka_article_consumer_close():
    consumer = Mock()
    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
        event_model=ArticleCreatedEvent,
    )

    kafka_consumer.close()

    consumer.close.assert_called_once()


def test_kafka_article_consumer_consumes_processed_article_event():
    consumer = Mock()
    message = Mock()

    processed_at = datetime.now()

    processed_article = ProcessedArticle(
        article_id="article-123",
        source_id="ansa",
        title="Processed article",
        url="https://example.com/article",
        content="Processed article content",
        fetched_at=datetime.now(),
        processed_at=processed_at,
    )

    event = ProcessedArticleEvent(
        article=processed_article,
        processed_at=processed_at,
    )

    message.error.return_value = None
    message.value.return_value = event.model_dump_json().encode("utf-8")
    consumer.poll.return_value = message

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic="news.article",
        event_model=ProcessedArticleEvent,
    )

    result = kafka_consumer.consume()

    assert result == event
    assert result.article.article_id == "article-123"
    assert result.article.content == "Processed article content"