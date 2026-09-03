from confluent_kafka import Producer

from newsnlp.models.events import ArticleCreatedEvent


class KafkaArticleProducer:
    def __init__(self, producer: Producer, topic: str):
        self.producer = producer
        self.topic = topic

    def send(self, event: ArticleCreatedEvent) -> None:
        payload = event.model_dump_json()

        self.producer.produce(
            topic=self.topic,
            value=payload,
            callback=self._delivery_callback,
        )

    def flush(self) -> None:
        self.producer.flush()

    def _delivery_callback(self, err, msg) -> None:
        if err is not None:
            raise RuntimeError(f"Kafka delivery failed: {err}")