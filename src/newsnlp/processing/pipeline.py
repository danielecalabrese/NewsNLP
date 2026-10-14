from newsnlp.kafka.consumer import KafkaArticleConsumer
from newsnlp.models.events import ArticleCreatedEvent
from newsnlp.processing.article_processing_service import (
    ArticleProcessingService,
)


class NewsNLPPipeline:
    """Coordinate Kafka consumption and article processing."""

    def __init__(
        self,
        consumer: KafkaArticleConsumer,
        processing_service: ArticleProcessingService,
    ) -> None:
        self.consumer = consumer
        self.processing_service = processing_service

    def run_once(self, timeout: float = 1.0) -> bool:
        """Process one available article event.

        Returns True if an article was processed, False otherwise.
        """
        event = self.consumer.consume(timeout=timeout)

        if event is None:
            return False

        if not isinstance(event, ArticleCreatedEvent):
            raise TypeError("Expected an ArticleCreatedEvent")

        self.processing_service.process_and_publish(event.article)

        return True

    def close(self) -> None:
        """Close the Kafka consumer."""
        self.consumer.close()