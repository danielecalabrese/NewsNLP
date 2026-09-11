from datetime import datetime, timezone

from langdetect import detect

from newsnlp.models.article import Article
from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.nlp.keyword_extractor import KeywordExtractor


class ArticleProcessor:

    def __init__(self, keyword_extractor: KeywordExtractor | None = None):
        self.keyword_extractor = keyword_extractor or KeywordExtractor()

    def process(self, article: Article) -> ProcessedArticle:
        normalized_content = " ".join(article.content.split())
        detected_language = detect(normalized_content)
        keywords = self.keyword_extractor.extract(normalized_content)

        return ProcessedArticle(
            article_id=article.id,
            source_id=article.source_id,
            title=article.title,
            url=article.url,
            author=article.author,
            published_at=article.published_at,
            content=normalized_content,
            summary=article.summary,
            language=detected_language,
            fetched_at=article.fetched_at,
            processed_at=datetime.now(timezone.utc),
            keywords=keywords,
        )