# NewsNLP

NewsNLP is a personal data engineering and NLP project that collects news articles from RSS feeds and processes them through an event-driven pipeline to extract meaningful information and insights.

## Project Goals

* Collect news articles from multiple RSS feeds
* Build an event-driven ingestion pipeline
* Process and normalize article data
* Apply NLP techniques to news content
* Store and analyze the processed data
* Provide meaningful insights through analytics and visualization

## Architecture

The project uses an event-driven architecture based on Apache Kafka.

```text
RSS Feeds
    │
    ▼
RSS Reader
    │
    ▼
ArticleCreatedEvent
    │
    ▼
Kafka Producer
    │
    ▼
Kafka Topic
    │
    ▼
Kafka Consumer
    │
    ├──► Article Processing
    │
    ├──► NLP
    │
    └──► Storage & Analytics
```

Articles collected by the RSS Reader are converted into `ArticleCreatedEvent` events and published to Kafka. Consumers can then subscribe to the corresponding topic and process the events independently.

## Event Streaming

NewsNLP uses Apache Kafka as the event streaming platform.

Kafka is currently configured to run locally using Docker Compose.

### Kafka Configuration

* **Broker:** `localhost:9092`
* **Mode:** KRaft
* **Image:** `apache/kafka:4.0.1`

The Kafka infrastructure can be started with:

```bash
docker compose up -d
```

To stop the Kafka infrastructure:

```bash
docker compose down
```

### Event Model

The main event currently used by the pipeline is `ArticleCreatedEvent`.

The event represents the creation of a new article and contains the information required by downstream consumers to process it.

The event is serialized before being published to Kafka by the `KafkaArticleProducer`.

The `KafkaArticleConsumer` is responsible for consuming these events from the Kafka topic and deserializing them back into application objects.

### Producer and Consumer

The Kafka producer publishes `ArticleCreatedEvent` messages to the configured Kafka topic.

The consumer subscribes to the same topic and retrieves the published events.

Producer and consumer logic are implemented as separate components so that the ingestion and processing stages remain decoupled.

## Testing

The Kafka producer and consumer are covered by unit tests.

The tests use mocks for the Kafka client, allowing the producer and consumer logic to be tested without requiring a running Kafka broker.

Run the complete test suite with:

```bash
pytest
```

## Roadmap

* [x] M0 – Project Setup
* [x] M1 – RSS Ingestion
* [ ] M2 – Kafka Pipeline
* [ ] M3 – Article Processing
* [ ] M4 – NLP Layer
* [ ] M5 – Storage
* [ ] M6 – Analytics
* [ ] M7 – Dashboard / API

## Getting Started

The project is currently under development.

### Requirements

* Python 3.14+
* Docker
* Docker Compose

### Setup

Clone the repository and create the Python virtual environment:

```bash
git clone <repository-url>
cd NewsNLP

python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Start the Kafka infrastructure:

```bash
docker compose up -d
```

Run the test suite to verify the installation:

```bash
pytest
```

More detailed usage instructions will be added as the project evolves.

## Project Status

🚧 Work in progress
