from datetime import datetime, timezone

from newsnlp.models.article import Article
from newsnlp.models.processed_article import ProcessedArticle


class ArticleProcessor:

    def process(self, article: Article) -> ProcessedArticle:
        normalized_content = " ".join(article.content.split())

        return ProcessedArticle(
            article_id=article.id,
            source_id=article.source_id,
            title=article.title,
            url=article.url,
            author=article.author,
            published_at=article.published_at,
            content=normalized_content,
            summary=article.summary,
            language=article.language,
            fetched_at=article.fetched_at,
            processed_at=datetime.now(timezone.utc),
        )