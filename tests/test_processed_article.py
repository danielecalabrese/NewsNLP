from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from newsnlp.models.processed_article import ProcessedArticle


@pytest.fixture
def valid_processed_article():
    return {
        "article_id": "article-123",
        "source_id": "ansa",
        "title": "Test article",
        "url": "https://example.com/article",
        "content": "This is the processed article content.",
        "summary": "Test summary",
        "language": "en",
        "published_at": datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        "processed_at": datetime(2026, 9, 9, 10, 5, tzinfo=timezone.utc),
    }


def test_processed_article_creation(valid_processed_article):
    article = ProcessedArticle(**valid_processed_article)

    assert article.article_id == "article-123"
    assert article.source_id == "ansa"
    assert article.title == "Test article"
    assert article.url == "https://example.com/article"
    assert article.content == "This is the processed article content."
    assert article.summary == "Test summary"
    assert article.language == "en"
    assert article.published_at == valid_processed_article["published_at"]
    assert article.processed_at == valid_processed_article["processed_at"]


def test_processed_article_optional_fields():
    article = ProcessedArticle(
        article_id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Processed content.",
        processed_at=datetime.now(timezone.utc),
    )

    assert article.summary is None
    assert article.language is None
    assert article.published_at is None


@pytest.mark.parametrize(
    "field",
    ["article_id", "source_id", "title", "url", "content", "processed_at"],
)
def test_processed_article_required_fields(valid_processed_article, field):
    valid_processed_article.pop(field)

    with pytest.raises(ValidationError):
        ProcessedArticle(**valid_processed_article)


@pytest.mark.parametrize(
    "field",
    ["article_id", "source_id", "title", "url", "content"],
)
def test_processed_article_string_fields_cannot_be_empty(
    valid_processed_article, field
):
    valid_processed_article[field] = ""

    with pytest.raises(ValidationError):
        ProcessedArticle(**valid_processed_article)