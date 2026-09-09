from datetime import datetime, timezone

from newsnlp.models.article import Article
from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.processing.article_processor import ArticleProcessor


def test_process_article():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="  This is   an article.\n\nIt contains   some text.  ",
        published_at=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        fetched_at=datetime(2026, 9, 9, 10, 5, tzinfo=timezone.utc),
    )

    processor = ArticleProcessor()

    processed = processor.process(article)

    assert isinstance(processed, ProcessedArticle)
    assert processed.article_id == article.id
    assert processed.source_id == article.source_id
    assert processed.title == article.title
    assert processed.url == article.url
    assert processed.content == "This is an article. It contains some text."
    assert processed.published_at == article.published_at
    assert processed.processed_at is not None


def test_process_article_preserves_optional_fields():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Some content.",
        summary="Test summary",
        language="en",
        published_at=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        fetched_at=datetime(2026, 9, 9, 10, 5, tzinfo=timezone.utc),
    )

    processor = ArticleProcessor()

    processed = processor.process(article)

    assert processed.summary == article.summary
    assert processed.language == article.language


def test_process_article_normalizes_whitespace():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="   First   sentence.\nSecond\t sentence.   ",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = ArticleProcessor()

    processed = processor.process(article)

    assert processed.content == "First sentence. Second sentence."