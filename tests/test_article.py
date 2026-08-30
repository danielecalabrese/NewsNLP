from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from newsnlp.models.article import Article


def test_article_creation():
    fetched_at = datetime.now(timezone.utc)

    article = Article(
        id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        content="This is the article content.",
        fetched_at=fetched_at,
    )

    assert article.id == "article-1"
    assert article.source_id == "source-1"
    assert article.title == "Test article"
    assert article.url == "https://example.com/article-1"
    assert article.content == "This is the article content."
    assert article.fetched_at == fetched_at


def test_article_optional_fields():
    article = Article(
        id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        content="This is the article content.",
        fetched_at=datetime.now(timezone.utc),
    )

    assert article.author is None
    assert article.published_at is None
    assert article.summary is None
    assert article.language is None


@pytest.mark.parametrize(
    "field",
    ["id", "source_id", "title", "url", "content"],
)
def test_article_rejects_empty_required_fields(field):
    data = {
        "id": "article-1",
        "source_id": "source-1",
        "title": "Test article",
        "url": "https://example.com/article-1",
        "content": "This is the article content.",
        "fetched_at": datetime.now(timezone.utc),
    }

    data[field] = ""

    with pytest.raises(ValidationError):
        Article(**data)


def test_article_requires_fetched_at():
    with pytest.raises(ValidationError):
        Article(
            id="article-1",
            source_id="source-1",
            title="Test article",
            url="https://example.com/article-1",
            content="This is the article content.",
        )