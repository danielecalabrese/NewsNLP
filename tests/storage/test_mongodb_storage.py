from datetime import datetime, timezone
from unittest.mock import MagicMock

from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.mongodb_storage import MongoArticleStorage


def create_article() -> ProcessedArticle:
    now = datetime.now(timezone.utc)

    return ProcessedArticle(
        article_id="article-1",
        source_id="source-1",
        title="Test article",
        url="https://example.com/article-1",
        author="Test Author",
        published_at=now,
        content="This is test content.",
        summary="Test summary",
        language="en",
        fetched_at=now,
        processed_at=now,
        keywords=["test", "article"],
        entities=["Example"],
        sentiment="positive",
    )


def create_storage() -> tuple[MongoArticleStorage, MagicMock]:
    client = MagicMock()
    collection = client["newsnlp"]["articles"]

    storage = MongoArticleStorage(
        client=client,
        database_name="newsnlp",
    )

    return storage, collection


def test_save_replaces_article_and_upserts() -> None:
    storage, collection = create_storage()
    article = create_article()

    storage.save(article)

    collection.replace_one.assert_called_once_with(
        {"article_id": "article-1"},
        article.model_dump(mode="json"),
        upsert=True,
    )


def test_get_returns_article() -> None:
    storage, collection = create_storage()
    article = create_article()

    collection.find_one.return_value = {
        **article.model_dump(mode="json"),
        "_id": "mongo-id",
    }

    result = storage.get("article-1")

    assert result == article
    collection.find_one.assert_called_once_with(
        {"article_id": "article-1"},
    )


def test_get_returns_none_when_article_does_not_exist() -> None:
    storage, collection = create_storage()

    collection.find_one.return_value = None

    result = storage.get("missing")

    assert result is None


def test_delete_removes_article() -> None:
    storage, collection = create_storage()

    storage.delete("article-1")

    collection.delete_one.assert_called_once_with(
        {"article_id": "article-1"},
    )


def test_exists_returns_true_when_article_exists() -> None:
    storage, collection = create_storage()

    collection.find_one.return_value = {"_id": "mongo-id"}

    assert storage.exists("article-1") is True

    collection.find_one.assert_called_once_with(
        {"article_id": "article-1"},
        {"_id": 1},
    )


def test_exists_returns_false_when_article_does_not_exist() -> None:
    storage, collection = create_storage()

    collection.find_one.return_value = None

    assert storage.exists("missing") is False