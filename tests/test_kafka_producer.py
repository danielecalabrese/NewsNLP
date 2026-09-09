from datetime import datetime
from unittest.mock import Mock

import pytest

from newsnlp.kafka.producer import KafkaArticleProducer
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


def test_kafka_article_producer_send():
    producer = Mock()
    kafka_producer = KafkaArticleProducer(producer, "news.article")

    event = create_event()

    kafka_producer.send(event)

    producer.produce.assert_called_once()

    call_kwargs = producer.produce.call_args.kwargs

    assert call_kwargs["topic"] == "news.article"
    assert call_kwargs["value"] == event.model_dump_json()
    assert call_kwargs["callback"] == kafka_producer._delivery_callback


def test_kafka_article_producer_flush():
    producer = Mock()
    kafka_producer = KafkaArticleProducer(producer, "news.article")

    kafka_producer.flush()

    producer.flush.assert_called_once()


def test_kafka_article_producer_delivery_callback_success():
    producer = Mock()
    kafka_producer = KafkaArticleProducer(producer, "news.article")

    kafka_producer._delivery_callback(None, Mock())


def test_kafka_article_producer_delivery_callback_error():
    producer = Mock()
    kafka_producer = KafkaArticleProducer(producer, "news.article")

    with pytest.raises(RuntimeError, match="Kafka delivery failed"):
        kafka_producer._delivery_callback("delivery error", Mock())


def test_kafka_article_producer_send_processed_article_event():
    producer = Mock()
    kafka_producer = KafkaArticleProducer(producer, "news.article")

    processed_article = ProcessedArticle(
        article_id="article-123",
        source_id="ansa",
        title="Processed article",
        url="https://example.com/article",
        content="Processed content",
        fetched_at=datetime.now(),
        processed_at=datetime.now(),
    )

    event = ProcessedArticleEvent(
        article=processed_article,
        processed_at=processed_article.processed_at,
    )

    kafka_producer.send(event)

    producer.produce.assert_called_once()

    call_kwargs = producer.produce.call_args.kwargs

    assert call_kwargs["topic"] == "news.article"
    assert call_kwargs["value"] == event.model_dump_json()
    assert call_kwargs["callback"] == kafka_producer._delivery_callback