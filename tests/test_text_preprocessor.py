from newsnlp.processing.text_preprocessor import TextPreprocessor


def test_remove_html_tags():
    preprocessor = TextPreprocessor()

    text = "<p>This is <strong>news</strong>.</p>"

    result = preprocessor.preprocess(text)

    assert result == "This is news."


def test_decode_html_entities():
    preprocessor = TextPreprocessor()

    text = "This is a&nbsp;news article &amp; example."

    result = preprocessor.preprocess(text)

    assert result == "This is a news article & example."


def test_normalize_whitespace():
    preprocessor = TextPreprocessor()

    text = "This   is\n\na\tnews   article."

    result = preprocessor.preprocess(text)

    assert result == "This is a news article."


def test_normalize_special_characters():
    preprocessor = TextPreprocessor()

    text = "‘News’ – today — important."

    result = preprocessor.preprocess(text)

    assert result == "'News' - today - important."


def test_strip_leading_and_trailing_whitespace():
    preprocessor = TextPreprocessor()

    text = "   This is a news article.   "

    result = preprocessor.preprocess(text)

    assert result == "This is a news article."


def test_empty_text_returns_empty_string():
    preprocessor = TextPreprocessor()

    result = preprocessor.preprocess("")

    assert result == ""


def test_none_text_returns_empty_string():
    preprocessor = TextPreprocessor()

    result = preprocessor.preprocess(None)

    assert result == ""


def test_preserve_meaningful_content():
    preprocessor = TextPreprocessor()

    text = """
        <p>Breaking news: <strong>New elections</strong> announced.</p>
        The election will take place on Monday.
    """

    result = preprocessor.preprocess(text)

    assert result == (
        "Breaking news: New elections announced. "
        "The election will take place on Monday."
    )