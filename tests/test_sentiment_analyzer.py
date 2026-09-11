import pytest

from newsnlp.nlp.sentiment_analyzer import SentimentAnalyzer


@pytest.fixture(scope="module")
def analyzer():
    return SentimentAnalyzer()


def test_positive_sentiment_english(analyzer):
    result = analyzer.analyze(
        "This is an excellent and wonderful experience."
    )

    assert result == "positive"


def test_negative_sentiment_english(analyzer):
    result = analyzer.analyze(
        "This is a terrible and disappointing experience."
    )

    assert result == "negative"


def test_neutral_sentiment_english(analyzer):
    result = analyzer.analyze(
        "The meeting will take place tomorrow at ten o'clock."
    )

    assert result == "neutral"


def test_positive_sentiment_italian(analyzer):
    result = analyzer.analyze(
        "È stata un'esperienza eccellente e meravigliosa."
    )

    assert result == "positive"


def test_negative_sentiment_italian(analyzer):
    result = analyzer.analyze(
        "È stata un'esperienza terribile e molto deludente."
    )

    assert result == "negative"


def test_neutral_sentiment_italian(analyzer):
    result = analyzer.analyze(
        "La riunione si terrà domani alle dieci."
    )

    assert result == "neutral"