from datetime import datetime, timezone

from confluent_kafka import Consumer, Producer

from newsnlp.kafka.consumer import KafkaArticleConsumer
from newsnlp.kafka.producer import KafkaArticleProducer
from newsnlp.models.article import Article
from newsnlp.models.events import ArticleCreatedEvent


BROKER = "localhost:9092"
TOPIC = "news.article"
GROUP_ID = "newsnlp-integration-test"


def test_producer_consumer_integration():
    article = Article(
        id="integration-test-1",
        source_id="source-1",
        title="Kafka integration test",
        url="https://example.com/integration-test",
        content="This is an integration test.",
        fetched_at=datetime.now(timezone.utc),
    )

    event = ArticleCreatedEvent(
        article=article,
        created_at=datetime.now(timezone.utc),
    )

    producer = Producer({"bootstrap.servers": BROKER})

    kafka_producer = KafkaArticleProducer(
        producer=producer,
        topic=TOPIC,
    )

    kafka_producer.send(event)
    kafka_producer.flush()

    consumer = Consumer(
        {
            "bootstrap.servers": BROKER,
            "group.id": GROUP_ID,
            "auto.offset.reset": "earliest",
        }
    )

    kafka_consumer = KafkaArticleConsumer(
        consumer=consumer,
        topic=TOPIC,
    )

    kafka_consumer.subscribe()

    result = kafka_consumer.consume(timeout=5.0)

    kafka_consumer.close()

    assert result is not None
    assert result.article.id == "integration-test-1"
    assert result.article.title == "Kafka integration test"