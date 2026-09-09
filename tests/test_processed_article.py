from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from newsnlp.models.processed_article import ProcessedArticle


def test_processed_article_creation():
    article = ProcessedArticle(
        article_id="article-1",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Article content",
        fetched_at=datetime.now(timezone.utc),
        processed_at=datetime.now(timezone.utc),
        keywords=["news", "technology"],
        entities=["OpenAI"],
        sentiment="positive",
    )

    assert article.article_id == "article-1"
    assert article.source_id == "ansa"
    assert article.title == "Test article"
    assert article.keywords == ["news", "technology"]
    assert article.entities == ["OpenAI"]
    assert article.sentiment == "positive"


def test_processed_article_optional_fields():
    article = ProcessedArticle(
        article_id="article-1",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Article content",
        fetched_at=datetime.now(timezone.utc),
        processed_at=datetime.now(timezone.utc),
    )

    assert article.author is None
    assert article.published_at is None
    assert article.summary is None
    assert article.language is None
    assert article.sentiment is None
    assert article.keywords == []
    assert article.entities == []


def test_processed_article_requires_valid_article_id():
    with pytest.raises(ValidationError):
        ProcessedArticle(
            article_id="",
            source_id="ansa",
            title="Test article",
            url="https://example.com/article",
            content="Article content",
            fetched_at=datetime.now(timezone.utc),
            processed_at=datetime.now(timezone.utc),
        )


def test_processed_article_requires_content():
    with pytest.raises(ValidationError):
        ProcessedArticle(
            article_id="article-1",
            source_id="ansa",
            title="Test article",
            url="https://example.com/article",
            content="",
            fetched_at=datetime.now(timezone.utc),
            processed_at=datetime.now(timezone.utc),
        )


def test_processed_article_serialization():
    fetched_at = datetime.now(timezone.utc)
    processed_at = datetime.now(timezone.utc)

    article = ProcessedArticle(
        article_id="article-1",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Article content",
        fetched_at=fetched_at,
        processed_at=processed_at,
        keywords=["news"],
        entities=["OpenAI"],
        sentiment="positive",
    )

    data = article.model_dump()

    assert data["article_id"] == "article-1"
    assert data["keywords"] == ["news"]
    assert data["entities"] == ["OpenAI"]
    assert data["processed_at"] == processed_at