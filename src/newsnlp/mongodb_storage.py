from pymongo import MongoClient

from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.storage import ArticleStorage


class MongoArticleStorage(ArticleStorage):
    """MongoDB implementation of the ArticleStorage interface."""

    def __init__(
        self,
        client: MongoClient,
        database_name: str,
        collection_name: str = "articles",
    ) -> None:
        self._collection = client[database_name][collection_name]

    def save(self, article: ProcessedArticle) -> None:
        self._collection.replace_one(
            {"article_id": article.article_id},
            article.model_dump(mode="json"),
            upsert=True,
        )

    def get(self, article_id: str) -> ProcessedArticle | None:
        document = self._collection.find_one({"article_id": article_id})

        if document is None:
            return None

        document.pop("_id", None)
        return ProcessedArticle.model_validate(document)

    def delete(self, article_id: str) -> None:
        self._collection.delete_one({"article_id": article_id})

    def exists(self, article_id: str) -> bool:
        return self._collection.find_one(
            {"article_id": article_id},
            {"_id": 1},
        ) is not None