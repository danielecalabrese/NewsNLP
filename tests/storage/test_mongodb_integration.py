from datetime import datetime, timezone

from pymongo import MongoClient

from newsnlp.mongodb_storage import MongoArticleStorage
from newsnlp.models.processed_article import ProcessedArticle


MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "newsnlp_test"


def create_article() -> ProcessedArticle:
    now = datetime.now(timezone.utc)

    return ProcessedArticle(
        article_id="integration-test-article",
        source_id="test-source",
        title="Integration test article",
        url="https://example.com/integration-test",
        content="This is integration test content.",
        fetched_at=now,
        processed_at=now,
        keywords=["integration", "test"],
        entities=["Example"],
        sentiment="positive",
    )


def test_mongodb_storage_crud() -> None:
    client = MongoClient(MONGO_URI)
    storage = MongoArticleStorage(
        client=client,
        database_name=DATABASE_NAME,
    )

    article = create_article()

    try:
        storage.delete(article.article_id)

        assert storage.exists(article.article_id) is False

        storage.save(article)

        assert storage.exists(article.article_id) is True
        assert storage.get(article.article_id) == article

        storage.delete(article.article_id)

        assert storage.exists(article.article_id) is False
        assert storage.get(article.article_id) is None
    finally:
        client.drop_database(DATABASE_NAME)
        client.close()