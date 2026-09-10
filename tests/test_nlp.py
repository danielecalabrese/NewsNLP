from datetime import datetime, timezone

from newsnlp.models.article import Article
from newsnlp.models.nlp import NLPResult
from newsnlp.processing.nlp_processor import NLPProcessor


def test_nlp_result_defaults():
    result = NLPResult()

    assert result.keywords == []
    assert result.entities == []
    assert result.sentiment is None


def test_nlp_result_with_values():
    result = NLPResult(
        keywords=["technology", "AI"],
        entities=["OpenAI"],
        sentiment="positive",
    )

    assert result.keywords == ["technology", "AI"]
    assert result.entities == ["OpenAI"]
    assert result.sentiment == "positive"


def test_nlp_processor_interface():
    class TestNLPProcessor(NLPProcessor):

        def process(self, article: Article) -> NLPResult:
            return NLPResult(
                keywords=["test"],
                entities=["Test Entity"],
                sentiment="neutral",
            )

    article = Article(
        id="article-123",
        source_id="test-source",
        title="Test article",
        url="https://example.com/article",
        content="Test content",
        fetched_at=datetime.now(timezone.utc),
    )

    processor = TestNLPProcessor()
    result = processor.process(article)

    assert isinstance(result, NLPResult)
    assert result.keywords == ["test"]
    assert result.entities == ["Test Entity"]
    assert result.sentiment == "neutral"