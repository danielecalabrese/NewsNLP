from unittest.mock import Mock

import pytest

from newsnlp.kafka.consumer import KafkaArticleConsumer
from newsnlp.models.article import Article
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.processing.article_processing_service import (
    ArticleProcessingService,
)
from newsnlp.processing.pipeline import NewsNLPPipeline


@pytest.fixture
def article():
    from datetime import datetime, timezone

    return Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Test article content",
        fetched_at=datetime.now(timezone.utc),
    )


def test_pipeline_processes_article_event(article):
    consumer = Mock(spec=KafkaArticleConsumer)
    processing_service = Mock(spec=ArticleProcessingService)

    event = ArticleCreatedEvent(
        article=article,
        created_at=article.fetched_at,
    )

    consumer.consume.return_value = event

    pipeline = NewsNLPPipeline(
        consumer=consumer,
        processing_service=processing_service,
    )

    result = pipeline.run_once(timeout=0.5)

    assert result is True
    consumer.consume.assert_called_once_with(timeout=0.5)
    processing_service.process_and_publish.assert_called_once_with(article)


def test_pipeline_returns_false_when_no_event():
    consumer = Mock(spec=KafkaArticleConsumer)
    consumer.consume.return_value = None

    processing_service = Mock(spec=ArticleProcessingService)

    pipeline = NewsNLPPipeline(
        consumer=consumer,
        processing_service=processing_service,
    )

    assert pipeline.run_once() is False

    processing_service.process_and_publish.assert_not_called()


def test_pipeline_rejects_unexpected_event():
    consumer = Mock(spec=KafkaArticleConsumer)
    consumer.consume.return_value = "unexpected event"

    processing_service = Mock(spec=ArticleProcessingService)

    pipeline = NewsNLPPipeline(
        consumer=consumer,
        processing_service=processing_service,
    )

    with pytest.raises(TypeError, match="Expected an ArticleCreatedEvent"):
        pipeline.run_once()

    processing_service.process_and_publish.assert_not_called()


def test_pipeline_close():
    consumer = Mock(spec=KafkaArticleConsumer)
    processing_service = Mock(spec=ArticleProcessingService)

    pipeline = NewsNLPPipeline(
        consumer=consumer,
        processing_service=processing_service,
    )

    pipeline.close()

    consumer.close.assert_called_once()