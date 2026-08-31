import pytest

from newsnlp.models.feed import FeedConfiguration


def test_feed_configuration_creation():
    feed = FeedConfiguration(
        name="BBC News",
        url="https://example.com/rss",
    )

    assert feed.name == "BBC News"
    assert feed.url == "https://example.com/rss"
    assert feed.enabled is True


def test_feed_configuration_can_be_disabled():
    feed = FeedConfiguration(
        name="BBC News",
        url="https://example.com/rss",
        enabled=False,
    )

    assert feed.enabled is False


@pytest.mark.parametrize("field", ["name", "url"])
def test_feed_configuration_rejects_empty_required_fields(field):
    data = {
        "name": "BBC News",
        "url": "https://example.com/rss",
    }

    data[field] = ""

    with pytest.raises(ValueError):
        FeedConfiguration(**data)