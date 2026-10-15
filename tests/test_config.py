import pytest

from newsnlp.config import Settings


def test_settings_use_default_values(monkeypatch):
    """Settings should use default values when no environment variables are set."""

    variables = [
        "NEWSNLP_FEEDS_FILE",
        "KAFKA_BROKER",
        "KAFKA_TOPIC",
        "KAFKA_PROCESSED_TOPIC",
        "KAFKA_CONSUMER_GROUP",
        "MONGODB_URI",
        "MONGODB_DATABASE",
    ]

    for variable in variables:
        monkeypatch.delenv(variable, raising=False)

    settings = Settings.from_environment()

    assert str(settings.feeds_file) == "config/feeds.json"
    assert settings.kafka_broker == "localhost:9092"
    assert settings.kafka_topic == "news.article"
    assert settings.kafka_processed_topic == "news.article.processed"
    assert settings.kafka_consumer_group == "newsnlp-processing"
    assert settings.mongodb_uri == "mongodb://localhost:27018"
    assert settings.mongodb_database == "newsnlp"


def test_settings_read_environment_variables(monkeypatch):
    """Settings should read values from environment variables."""

    monkeypatch.setenv("NEWSNLP_FEEDS_FILE", "custom/feeds.json")
    monkeypatch.setenv("KAFKA_BROKER", "kafka:9093")
    monkeypatch.setenv("KAFKA_TOPIC", "custom.articles")
    monkeypatch.setenv("KAFKA_PROCESSED_TOPIC", "custom.processed")
    monkeypatch.setenv("KAFKA_CONSUMER_GROUP", "custom-group")
    monkeypatch.setenv("MONGODB_URI", "mongodb://mongo:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "custom_db")

    settings = Settings.from_environment()

    assert str(settings.feeds_file) == "custom/feeds.json"
    assert settings.kafka_broker == "kafka:9093"
    assert settings.kafka_topic == "custom.articles"
    assert settings.kafka_processed_topic == "custom.processed"
    assert settings.kafka_consumer_group == "custom-group"
    assert settings.mongodb_uri == "mongodb://mongo:27017"
    assert settings.mongodb_database == "custom_db"


def test_settings_are_immutable():
    """Settings instances should be immutable."""

    settings = Settings.from_environment()

    with pytest.raises(AttributeError):
        settings.kafka_broker = "kafka:9093"