import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Application configuration settings."""

    feeds_file: Path
    kafka_broker: str
    kafka_topic: str
    kafka_processed_topic: str
    kafka_consumer_group: str
    mongodb_uri: str
    mongodb_database: str

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build application settings from environment variables."""

        return cls(
            feeds_file=Path(
                os.getenv("NEWSNLP_FEEDS_FILE", "config/feeds.json")
            ),
            kafka_broker=os.getenv(
                "KAFKA_BROKER", "localhost:9092"
            ),
            kafka_topic=os.getenv(
                "KAFKA_TOPIC", "news.article"
            ),
            kafka_processed_topic=os.getenv(
                "KAFKA_PROCESSED_TOPIC", "news.article.processed"
            ),
            kafka_consumer_group=os.getenv(
                "KAFKA_CONSUMER_GROUP", "newsnlp-processing"
            ),
            mongodb_uri=os.getenv(
                "MONGODB_URI", "mongodb://localhost:27018"
            ),
            mongodb_database=os.getenv(
                "MONGODB_DATABASE", "newsnlp"
            ),
        )


settings = Settings.from_environment()