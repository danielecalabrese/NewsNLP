from confluent_kafka import Producer
from pydantic import BaseModel


class KafkaArticleProducer:
    def __init__(self, producer: Producer, topic: str):
        self.producer = producer
        self.topic = topic

    def send(self, event: BaseModel) -> None:
        """Publish an event asynchronously."""
        payload = event.model_dump_json()

        self.producer.produce(
            topic=self.topic,
            value=payload,
            callback=self._delivery_callback,
        )

    def send_and_wait(
        self,
        event: BaseModel,
        timeout: float = 10.0,
    ) -> None:
        """Publish an event and wait for Kafka delivery confirmation."""
        payload = event.model_dump_json()
        delivery_errors = []

        def on_delivery(err, msg):
            if err is not None:
                delivery_errors.append(err)

        self.producer.produce(
            topic=self.topic,
            value=payload,
            callback=on_delivery,
        )

        remaining = self.producer.flush(timeout)

        if remaining > 0:
            raise TimeoutError("Kafka delivery timed out")

        if delivery_errors:
            raise RuntimeError(
                f"Kafka delivery failed: {delivery_errors[0]}"
            )

    def flush(self) -> None:
        self.producer.flush()

    def _delivery_callback(self, err, msg) -> None:
        if err is not None:
            raise RuntimeError(f"Kafka delivery failed: {err}")