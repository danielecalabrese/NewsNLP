from unittest.mock import patch

from newsnlp.cli import ingest
from newsnlp.models.feed import FeedConfiguration


def test_ingest_reads_enabled_feeds():
    feeds = [
        FeedConfiguration(
            name="Test Feed",
            url="https://example.com/feed.xml",
            enabled=True,
        )
    ]

    with patch("newsnlp.cli.RSSReader") as reader_class:
        reader = reader_class.return_value
        reader.read.return_value = []

        result = ingest(feeds)

        reader_class.assert_called_once_with(
            feed_url="https://example.com/feed.xml",
            source_id="Test Feed",
        )
        reader.read.assert_called_once()
        assert result == 0


def test_ingest_skips_disabled_feeds():
    feeds = [
        FeedConfiguration(
            name="Disabled Feed",
            url="https://example.com/disabled.xml",
            enabled=False,
        )
    ]

    with patch("newsnlp.cli.RSSReader") as reader_class:
        result = ingest(feeds)

        reader_class.assert_not_called()
        assert result == 0


def test_ingest_returns_error_when_feed_read_fails():
    feeds = [
        FeedConfiguration(
            name="Broken Feed",
            url="https://example.com/broken.xml",
            enabled=True,
        )
    ]

    with patch("newsnlp.cli.RSSReader") as reader_class:
        reader = reader_class.return_value
        reader.read.side_effect = ValueError("Invalid RSS feed")

        result = ingest(feeds)

        assert result == 1


def test_ingest_logs_error_when_feed_read_fails(caplog):
    feeds = [
        FeedConfiguration(
            name="Broken Feed",
            url="https://example.com/broken.xml",
            enabled=True,
        )
    ]

    with patch("newsnlp.cli.RSSReader") as reader_class:
        reader = reader_class.return_value
        reader.read.side_effect = ValueError("Invalid RSS feed")

        with caplog.at_level("ERROR"):
            result = ingest(feeds)

    assert result == 1
    assert "Error ingesting feed: Broken Feed" in caplog.text


def test_main_runs_ingestion():
    feeds = [
        FeedConfiguration(
            name="Test Feed",
            url="https://example.com/feed.xml",
            enabled=True,
        )
    ]

    with (
        patch("newsnlp.cli.load_feeds", return_value=feeds) as load_feeds_mock,
        patch("newsnlp.cli.ingest", return_value=0) as ingest_mock,
    ):
        from newsnlp.cli import main

        result = main(["ingest"])

    load_feeds_mock.assert_called_once()
    ingest_mock.assert_called_once_with(feeds)
    assert result == 0


def test_main_loads_feeds_and_runs_ingestion():
    feeds = [
        FeedConfiguration(
            name="Test Feed",
            url="https://example.com/feed.xml",
            enabled=True,
        )
    ]

    with (
        patch("newsnlp.cli.load_feeds", return_value=feeds) as load_feeds_mock,
        patch("newsnlp.cli.ingest", return_value=0) as ingest_mock,
    ):
        from newsnlp.cli import main

        result = main(["ingest"])

    load_feeds_mock.assert_called_once()
    ingest_mock.assert_called_once_with(feeds)
    assert result == 0


def test_load_feeds_reads_json_configuration(tmp_path):
    config_file = tmp_path / "feeds.json"
    config_file.write_text(
        """
        {
            "feeds": [
                {
                    "name": "Test Feed",
                    "url": "https://example.com/feed.xml",
                    "enabled": true
                }
            ]
        }
        """
    )

    with patch("newsnlp.cli.CONFIG_FILE", config_file):
        from newsnlp.cli import load_feeds

        feeds = load_feeds()

    assert feeds == [
        FeedConfiguration(
            name="Test Feed",
            url="https://example.com/feed.xml",
            enabled=True,
        )
    ]


def test_load_feeds_raises_error_when_config_file_is_missing(tmp_path):
    config_file = tmp_path / "missing.json"

    with patch("newsnlp.cli.CONFIG_FILE", config_file):
        from newsnlp.cli import load_feeds

        try:
            load_feeds()
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("Expected FileNotFoundError")
        

def test_main_returns_error_when_config_file_is_missing():
    with patch(
        "newsnlp.cli.load_feeds",
        side_effect=FileNotFoundError("Configuration file not found"),
    ):
        from newsnlp.cli import main

        result = main(["ingest"])

    assert result == 1


def test_main_logs_error_when_config_file_is_missing(caplog):
    with patch(
        "newsnlp.cli.load_feeds",
        side_effect=FileNotFoundError("Configuration file not found"),
    ):
        from newsnlp.cli import main

        with caplog.at_level("ERROR"):
            result = main(["ingest"])

    assert result == 1
    assert "Feed configuration file not found" in caplog.text