from datetime import datetime, timezone
from unittest.mock import Mock, patch

from newsnlp.models.article import Article

from newsnlp.cli import ingest, load_feeds
from newsnlp.models.feed import FeedConfiguration

import pytest


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


def test_ingest_publishes_articles_to_kafka():
    feeds = [
        FeedConfiguration(
            name="Test Feed",
            url="https://example.com/feed.xml",
            enabled=True,
        )
    ]

    articles = [
        Article(
            id="article-1",
            source_id="Test Feed",
            title="First article",
            url="https://example.com/1",
            content="First article content",
            fetched_at=datetime.now(timezone.utc),
        ),
        Article(
            id="article-2",
            source_id="Test Feed",
            title="Second article",
            url="https://example.com/2",
            content="Second article content",
            fetched_at=datetime.now(timezone.utc),
        ),
    ]

    with (
        patch("newsnlp.cli.RSSReader") as reader_class,
        patch("newsnlp.cli.Producer"),
        patch("newsnlp.cli.KafkaArticleProducer") as kafka_producer_class,
    ):
        reader = reader_class.return_value
        reader.read.return_value = articles

        kafka_producer = kafka_producer_class.return_value

        result = ingest(feeds)

    assert result == 0
    assert kafka_producer.send.call_count == 2
    kafka_producer.flush.assert_called_once()

    first_event = kafka_producer.send.call_args_list[0].args[0]
    second_event = kafka_producer.send.call_args_list[1].args[0]

    assert first_event.article.id == "article-1"
    assert second_event.article.id == "article-2"



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


def test_ingest_continues_after_a_feed_read_fails():
    feeds = [
        FeedConfiguration(
            name="Broken Feed",
            url="https://example.com/broken.xml",
            enabled=True,
        ),
        FeedConfiguration(
            name="Working Feed",
            url="https://example.com/working.xml",
            enabled=True,
        ),
    ]

    with (
        patch("newsnlp.cli.RSSReader") as reader_class,
        patch("newsnlp.cli.Producer"),
        patch("newsnlp.cli.KafkaArticleProducer") as kafka_producer_class,
    ):
        broken_reader = Mock()
        broken_reader.read.side_effect = ValueError("Invalid RSS feed")
        working_reader = Mock()
        working_reader.read.return_value = []
        reader_class.side_effect = [broken_reader, working_reader]

        result = ingest(feeds)

    assert result == 1
    assert reader_class.call_count == 2
    kafka_producer_class.return_value.flush.assert_called_once()


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


def test_run_ingests_before_processing():
    with (
        patch("newsnlp.cli.load_feeds", return_value=[]) as load_feeds_mock,
        patch("newsnlp.cli.ingest", return_value=0) as ingest_mock,
        patch("newsnlp.cli.process", return_value=0) as process_mock,
    ):
        from newsnlp.cli import run

        result = run()

    load_feeds_mock.assert_called_once()
    ingest_mock.assert_called_once_with([])
    process_mock.assert_called_once()
    assert result == 0


def test_run_processes_articles_even_if_one_feed_failed():
    with (
        patch("newsnlp.cli.load_feeds", return_value=[]),
        patch("newsnlp.cli.ingest", return_value=1),
        patch("newsnlp.cli.process", return_value=0) as process_mock,
    ):
        from newsnlp.cli import run

        result = run()

    process_mock.assert_called_once()
    assert result == 1


def test_main_runs_complete_application():
    with patch("newsnlp.cli.run", return_value=0) as run_mock:
        from newsnlp.cli import main

        result = main(["run"])

    run_mock.assert_called_once()
    assert result == 0


def test_process_configures_pipeline():
    with (
        patch("newsnlp.cli.Consumer") as consumer_class,
        patch("newsnlp.cli.Producer") as producer_class,
        patch("newsnlp.cli.MongoClient") as mongo_class,
        patch("newsnlp.cli.MongoArticleStorage"),
        patch("newsnlp.cli.KeywordExtractor"),
        patch("newsnlp.cli.SentimentAnalyzer"),
        patch("newsnlp.cli.ArticleProcessor"),
        patch("newsnlp.cli.ArticleProcessingService"),
        patch("newsnlp.cli.NewsNLPPipeline") as pipeline_class,
    ):
        pipeline = pipeline_class.return_value
        pipeline.run_once.side_effect = KeyboardInterrupt

        from newsnlp.cli import process

        result = process()

    assert result == 0

    consumer_class.assert_called_once()
    producer_class.assert_called_once()
    mongo_class.assert_called_once_with("mongodb://localhost:27017")

    pipeline.subscribe.assert_not_called()
    pipeline.consumer.subscribe.assert_called_once()
    pipeline.close.assert_called_once()
    producer_class.return_value.flush.assert_called_once()
    mongo_class.return_value.close.assert_called_once()


def test_process_returns_error_on_pipeline_failure():
    with (
        patch("newsnlp.cli.Consumer"),
        patch("newsnlp.cli.Producer"),
        patch("newsnlp.cli.MongoClient"),
        patch("newsnlp.cli.MongoArticleStorage"),
        patch("newsnlp.cli.KeywordExtractor"),
        patch("newsnlp.cli.SentimentAnalyzer"),
        patch("newsnlp.cli.ArticleProcessor"),
        patch("newsnlp.cli.ArticleProcessingService"),
        patch("newsnlp.cli.NewsNLPPipeline") as pipeline_class,
    ):
        pipeline = pipeline_class.return_value
        pipeline.run_once.side_effect = RuntimeError("Pipeline failure")

        from newsnlp.cli import process

        result = process()

    assert result == 1
    pipeline.close.assert_called_once()


def test_load_feeds_raises_error_when_json_is_invalid(tmp_path):
    """Loading an invalid JSON configuration should raise ValueError."""

    config_file = tmp_path / "feeds.json"
    config_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_feeds(config_file)


def test_load_feeds_raises_error_when_feeds_list_is_missing(tmp_path):
    """Loading a configuration without a feeds list should raise ValueError."""

    config_file = tmp_path / "feeds.json"
    config_file.write_text('{"sources": []}', encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a 'feeds' list"):
        load_feeds(config_file)