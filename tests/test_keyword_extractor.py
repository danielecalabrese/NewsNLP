import pytest

from newsnlp.nlp.keyword_extractor import KeywordExtractor


def test_extract_keywords():
    extractor = KeywordExtractor(max_keywords=3)

    text = (
        "The government announced new elections. "
        "The elections will take place on Monday."
    )

    result = extractor.extract(text)

    assert result == ["elections", "government", "announced"]


def test_extract_keywords_excludes_stopwords():
    extractor = KeywordExtractor()

    text = "The cat and the dog are in the house."

    result = extractor.extract(text)

    assert "the" not in result
    assert "and" not in result
    assert "in" not in result


def test_extract_keywords_empty_text():
    extractor = KeywordExtractor()

    assert extractor.extract("") == []
    assert extractor.extract("   ") == []


def test_extract_keywords_max_keywords():
    extractor = KeywordExtractor(max_keywords=2)

    text = "apple apple banana banana cherry cherry"

    result = extractor.extract(text)

    assert len(result) == 2


def test_invalid_max_keywords():
    with pytest.raises(ValueError):
        KeywordExtractor(max_keywords=0)