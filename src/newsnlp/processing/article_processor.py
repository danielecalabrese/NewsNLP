from datetime import datetime, timezone
from typing import Callable

from langdetect import detect

from newsnlp.models.article import Article
from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.nlp.keyword_extractor import KeywordExtractor
from newsnlp.nlp.sentiment_analyzer import SentimentAnalyzer


class ArticleProcessor:

    def __init__(
        self,
        language_detector: Callable[[str], str] = detect,
        keyword_extractor: KeywordExtractor | None = None,
        sentiment_analyzer: SentimentAnalyzer | None = None,
    ):
        self.language_detector = language_detector
        self.keyword_extractor = keyword_extractor
        self.sentiment_analyzer = sentiment_analyzer

    def process(self, article: Article) -> ProcessedArticle:
        normalized_content = " ".join(article.content.split())
        detected_language = self.language_detector(normalized_content)

        keywords = (
            self.keyword_extractor.extract(normalized_content)
            if self.keyword_extractor
            else []
        )

        sentiment = (
            self.sentiment_analyzer.analyze(normalized_content)
            if self.sentiment_analyzer
            else None
        )

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
            keywords=keywords,
            sentiment=sentiment,
        )