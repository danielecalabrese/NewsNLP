import json
from typing import TypeVar

from confluent_kafka import Consumer
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class KafkaArticleConsumer:
    def __init__(
        self,
        consumer: Consumer,
        topic: str,
        event_model: type[T],
    ):
        self.consumer = consumer
        self.topic = topic
        self.event_model = event_model

    def subscribe(self) -> None:
        self.consumer.subscribe([self.topic])

    def consume(self, timeout: float = 1.0) -> T | None:
        message = self.consumer.poll(timeout)

        if message is None:
            return None

        if message.error():
            raise RuntimeError(f"Kafka consumption failed: {message.error()}")

        payload = json.loads(message.value().decode("utf-8"))

        return self.event_model.model_validate(payload)

    def close(self) -> None:
        self.consumer.close()