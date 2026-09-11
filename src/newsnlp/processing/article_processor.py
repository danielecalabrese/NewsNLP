from datetime import datetime, timezone
from typing import Callable

from langdetect import detect

from newsnlp.models.article import Article
from newsnlp.models.processed_article import ProcessedArticle


class ArticleProcessor:

    def __init__(self, language_detector: Callable[[str], str] = detect):
        self.language_detector = language_detector

    def process(self, article: Article) -> ProcessedArticle:
        normalized_content = " ".join(article.content.split())
        detected_language = self.language_detector(normalized_content)

        return ProcessedArticle(
            article_id=article.id,
            source_id=article.source_id,
            title=article.title,
            url=article.url,
            content=normalized_content,
            summary=article.summary,
            language=detected_language,
            author=article.author,
            published_at=article.published_at,
            processed_at=datetime.now(timezone.utc),
            fetched_at=article.fetched_at,
        )