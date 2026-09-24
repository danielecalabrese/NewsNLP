import pytest

from newsnlp.storage import ArticleStorage


def test_article_storage_is_abstract():

    with pytest.raises(TypeError):

        ArticleStorage()


def test_article_storage_defines_required_methods():

    assert hasattr(ArticleStorage, "save")
    assert hasattr(ArticleStorage, "get")
    assert hasattr(ArticleStorage, "delete")
    assert hasattr(ArticleStorage, "exists")