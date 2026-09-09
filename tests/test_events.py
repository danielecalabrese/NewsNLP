from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from newsnlp.models.article import Article
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.models.events import ArticleCreatedEvent, ProcessedArticleEvent
from newsnlp.models.processed_article import ProcessedArticle


def test_article_created_event_creation():
    article = Article(
        id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        content="This is the article content.",
        fetched_at=datetime.now(timezone.utc),
    )

    created_at = datetime.now(timezone.utc)

    event = ArticleCreatedEvent(
        article=article,
        created_at=created_at,
    )

    assert event.article == article
    assert event.created_at == created_at


def test_article_created_event_requires_article():
    with pytest.raises(ValidationError):
        ArticleCreatedEvent(
            created_at=datetime.now(timezone.utc),
        )


def test_article_created_event_requires_created_at():
    article = Article(
        id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        content="This is the article content.",
        fetched_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValidationError):
        ArticleCreatedEvent(article=article)


def test_article_created_event_serialization():
    article = Article(
        id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        content="This is the article content.",
        fetched_at=datetime.now(timezone.utc),
    )

    created_at = datetime.now(timezone.utc)

    event = ArticleCreatedEvent(
        article=article,
        created_at=created_at,
    )

    data = event.model_dump()

    assert data["article"]["id"] == "article-1"
    assert data["article"]["source_id"] == "source-1"
    assert data["created_at"] == created_at


def create_processed_article() -> ProcessedArticle:
    return ProcessedArticle(
        article_id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        content="This is the processed article content.",
        fetched_at=datetime.now(timezone.utc),
        processed_at=datetime.now(timezone.utc),
    )


def test_processed_article_event_creation():
    article = create_processed_article()
    processed_at = datetime.now(timezone.utc)

    event = ProcessedArticleEvent(
        article=article,
        processed_at=processed_at,
    )

    assert event.article == article
    assert event.processed_at == processed_at


def test_processed_article_event_requires_article():
    with pytest.raises(ValidationError):
        ProcessedArticleEvent(
            processed_at=datetime.now(timezone.utc),
        )


def test_processed_article_event_requires_processed_at():
    article = create_processed_article()

    with pytest.raises(ValidationError):
        ProcessedArticleEvent(article=article)


def test_processed_article_event_serialization():
    article = create_processed_article()
    processed_at = datetime.now(timezone.utc)

    event = ProcessedArticleEvent(
        article=article,
        processed_at=processed_at,
    )

    data = event.model_dump()

    assert data["article"]["article_id"] == "article-1"
    assert data["article"]["source_id"] == "source-1"
    assert data["processed_at"] == processed_at