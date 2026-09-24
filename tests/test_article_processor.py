from datetime import datetime, timezone

from newsnlp.models.article import Article
from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.processing.article_processor import ArticleProcessor


def test_process_article():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="  This is   an article.\n\nIt contains   some text.  ",
        published_at=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        fetched_at=datetime(2026, 9, 9, 10, 5, tzinfo=timezone.utc),
    )

    processor = ArticleProcessor(
        language_detector=lambda text: "en"
    )

    processed = processor.process(article)

    assert isinstance(processed, ProcessedArticle)
    assert processed.article_id == article.id
    assert processed.source_id == article.source_id
    assert processed.title == article.title
    assert processed.url == article.url
    assert processed.content == "This is an article. It contains some text."
    assert processed.language == "en"
    assert processed.published_at == article.published_at
    assert processed.processed_at is not None
    assert processed.author == article.author
    assert processed.fetched_at == article.fetched_at


def test_process_article_preserves_optional_fields():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="This is a test article written in English.",
        summary="Test summary",
        published_at=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        fetched_at=datetime(2026, 9, 9, 10, 5, tzinfo=timezone.utc),
    )

    processor = ArticleProcessor(
        language_detector=lambda text: "en"
    )

    processed = processor.process(article)

    assert processed.summary == article.summary
    assert processed.language == "en"


def test_process_article_uses_language_detector():
    detected_text = None

    def language_detector(text: str) -> str:
        nonlocal detected_text
        detected_text = text
        return "it"

    article = Article(
        id="article-123",
        source_id="ansa",
        title="Articolo di prova",
        url="https://example.com/article",
        content="  Il governo   ha annunciato nuove elezioni.  ",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = ArticleProcessor(
        language_detector=language_detector
    )

    processed = processor.process(article)

    assert detected_text == "Il governo ha annunciato nuove elezioni."
    assert processed.language == "it"


def test_process_article_normalizes_whitespace():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="   First   sentence.\nSecond\t sentence.   ",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = ArticleProcessor(
        language_detector=lambda text: "en"
    )

    processed = processor.process(article)

    assert processed.content == "First sentence. Second sentence."


def test_process_article_sets_processed_at():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="Some content.",
        fetched_at=datetime.now(timezone.utc),
    )

    before = datetime.now(timezone.utc)

    processor = ArticleProcessor(
        language_detector=lambda text: "en"
    )

    processed = processor.process(article)

    after = datetime.now(timezone.utc)

    assert before <= processed.processed_at <= after
    assert processed.processed_at.tzinfo == timezone.utc


def test_process_article_detects_italian_language():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Articolo di prova",
        url="https://example.com/article",
        content="Il governo ha annunciato nuove elezioni per il prossimo lunedì.",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = ArticleProcessor()

    processed = processor.process(article)

    assert processed.language == "it"


def test_process_article_detects_english_language():
    article = Article(
        id="article-123",
        source_id="bbc",
        title="Test article",
        url="https://example.com/article",
        content="The government announced new elections for next Monday.",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = ArticleProcessor()

    processed = processor.process(article)

    assert processed.language == "en"
    

class FakeKeywordExtractor:

    def extract(self, text: str) -> list[str]:
        return ["government", "elections"]


class FakeSentimentAnalyzer:

    def analyze(self, text: str) -> str:
        return "positive"
    

def test_process_article_integrates_nlp_components():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="  The government   announced new elections.  ",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = ArticleProcessor(
        language_detector=lambda text: "en",
        keyword_extractor=FakeKeywordExtractor(),
        sentiment_analyzer=FakeSentimentAnalyzer(),
    )

    processed = processor.process(article)

    assert processed.language == "en"
    assert processed.keywords == ["government", "elections"]
    assert processed.sentiment == "positive"


def test_process_article_passes_normalized_content_to_nlp_components():
    received_keyword_text = None
    received_sentiment_text = None

    class KeywordExtractorSpy:

        def extract(self, text: str) -> list[str]:
            nonlocal received_keyword_text
            received_keyword_text = text
            return ["test"]

    class SentimentAnalyzerSpy:

        def analyze(self, text: str) -> str:
            nonlocal received_sentiment_text
            received_sentiment_text = text
            return "neutral"

    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="  This   is   a test.  ",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = ArticleProcessor(
        language_detector=lambda text: "en",
        keyword_extractor=KeywordExtractorSpy(),
        sentiment_analyzer=SentimentAnalyzerSpy(),
    )

    processed = processor.process(article)

    assert received_keyword_text == "This is a test."
    assert received_sentiment_text == "This is a test."
    assert processed.keywords == ["test"]
    assert processed.sentiment == "neutral"


class FakeStorage:

    def __init__(self):
        self.saved_articles = []

    def save(self, article: ProcessedArticle) -> None:
        self.saved_articles.append(article)


def test_process_article_saves_processed_article():
    article = Article(
        id="article-123",
        source_id="ansa",
        title="Test article",
        url="https://example.com/article",
        content="  The government   announced new elections.  ",
        fetched_at=datetime.now(timezone.utc),
    )

    storage = FakeStorage()

    processor = ArticleProcessor(
        language_detector=lambda text: "en",
        storage=storage,
    )

    processed = processor.process(article)

    assert len(storage.saved_articles) == 1
    assert storage.saved_articles[0] == processed