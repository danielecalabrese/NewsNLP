import json

from confluent_kafka import Consumer

from newsnlp.models.events import ArticleCreatedEvent


class KafkaArticleConsumer:
    def __init__(self, consumer: Consumer, topic: str):
        self.consumer = consumer
        self.topic = topic

    def subscribe(self) -> None:
        self.consumer.subscribe([self.topic])

    def consume(self, timeout: float = 1.0) -> ArticleCreatedEvent | None:
        message = self.consumer.poll(timeout)

        if message is None:
            return None

        if message.error():
            raise RuntimeError(f"Kafka consumption failed: {message.error()}")

        payload = json.loads(message.value().decode("utf-8"))

        return ArticleCreatedEvent.model_validate(payload)

    def close(self) -> None:
        self.consumer.close()