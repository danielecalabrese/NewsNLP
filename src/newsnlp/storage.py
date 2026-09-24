from abc import ABC, abstractmethod

from newsnlp.models.processed_article import ProcessedArticle


class ArticleStorage(ABC):
    """Interface for persistent storage of processed articles."""

    @abstractmethod
    def save(self, article: ProcessedArticle) -> None:
        """Persist a processed article."""
        raise NotImplementedError

    @abstractmethod
    def get(self, article_id: str) -> ProcessedArticle | None:
        """Retrieve a processed article by its ID."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, article_id: str) -> None:
        """Delete a processed article by its ID."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, article_id: str) -> bool:
        """Check whether a processed article exists."""
        raise NotImplementedError