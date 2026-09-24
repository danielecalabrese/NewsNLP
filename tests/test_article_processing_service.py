from datetime import datetime, timezone
from unittest.mock import Mock

from newsnlp.kafka.producer import KafkaArticleProducer
from newsnlp.models.article import Article
from newsnlp.models.events import ProcessedArticleEvent
from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.processing.article_processing_service import ArticleProcessingService
from newsnlp.processing.article_processor import ArticleProcessor


def create_article() -> Article:
    return Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="  This is   an article.  ",
        fetched_at=datetime.now(timezone.utc),
    )


def test_process_and_publish():
    article = create_article()

    processor = Mock(spec=ArticleProcessor)
    producer = Mock(spec=KafkaArticleProducer)

    processed_article = ProcessedArticle(
        article_id=article.id,
        source_id=article.source_id,
        title=article.title,
        url=article.url,
        content="This is an article.",
        fetched_at=article.fetched_at,
        processed_at=datetime.now(timezone.utc),
    )

    processor.process.return_value = processed_article

    service = ArticleProcessingService(
        processor=processor,
        producer=producer,
    )

    result = service.process_and_publish(article)

    assert result == processed_article

    processor.process.assert_called_once_with(article)
    producer.send.assert_called_once()

    event = producer.send.call_args.args[0]

    assert isinstance(event, ProcessedArticleEvent)
    assert event.article == processed_article
    assert event.processed_at == processed_article.processed_at


def test_process_and_publish_processes_article_before_publishing():
    article = create_article()

    processor = Mock(spec=ArticleProcessor)
    producer = Mock(spec=KafkaArticleProducer)

    processed_article = ProcessedArticle(
        article_id=article.id,
        source_id=article.source_id,
        title=article.title,
        url=article.url,
        content="Processed content.",
        fetched_at=article.fetched_at,
        processed_at=datetime.now(timezone.utc),
    )

    processor.process.return_value = processed_article

    service = ArticleProcessingService(
        processor=processor,
        producer=producer,
    )

    service.process_and_publish(article)

    processor.process.assert_called_once_with(article)
    producer.send.assert_called_once()


class FakeStorage:

    def __init__(self):
        self.saved_articles = []

    def save(self, article: ProcessedArticle) -> None:
        self.saved_articles.append(article)


def test_process_and_publish_saves_processed_article():
    article = create_article()

    storage = FakeStorage()
    processor = ArticleProcessor(
        language_detector=lambda text: "en",
        storage=storage,
    )
    producer = Mock(spec=KafkaArticleProducer)

    service = ArticleProcessingService(
        processor=processor,
        producer=producer,
    )

    result = service.process_and_publish(article)

    assert len(storage.saved_articles) == 1
    assert storage.saved_articles[0] == result
    producer.send.assert_called_once()