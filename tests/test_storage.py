import pytest

from newsnlp.storage import ArticleStorage


def test_article_storage_is_abstract():
    with pytest.raises(TypeError):
        ArticleStorage()