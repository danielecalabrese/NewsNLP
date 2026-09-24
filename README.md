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
    ▼
Article Processing
    │
    ▼
NLP
    │
    ▼
ProcessedArticleEvent
    │
    ▼
MongoDB Storage
```

Articles collected by the RSS Reader are converted into `ArticleCreatedEvent` events and published to Kafka.

Downstream consumers process the events through the article processing and NLP pipeline. Processed articles are represented by `ProcessedArticle` and can be published as `ProcessedArticleEvent` events before being persisted to MongoDB.

The processing and storage components are decoupled through interfaces and event models, allowing individual components to be tested independently.

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

To stop the infrastructure:

```bash
docker compose down
```

### Event Models

The pipeline currently uses two main event models:

* `ArticleCreatedEvent` represents the creation of a new article and is published after RSS ingestion.
* `ProcessedArticleEvent` represents an article after processing and NLP enrichment.

Events are serialized before being published to Kafka and deserialized by downstream consumers.

### Producer and Consumer

The Kafka producer publishes events to the configured Kafka topic.

The consumer subscribes to the topic and retrieves published events.

Producer and consumer logic are implemented as separate components so that the ingestion and processing stages remain decoupled.

## Article Processing and NLP

The article processing pipeline normalizes article content and enriches processed articles with NLP information.

The current NLP layer includes:

* Text preprocessing and normalization
* Language detection
* Keyword extraction
* Sentiment analysis

Processed articles are represented by the `ProcessedArticle` model and contain the original article information together with the results of the processing and NLP stages.

## Storage

Processed articles are persisted using a storage abstraction defined by the `ArticleStorage` interface.

The interface currently provides operations for:

* Saving an article
* Retrieving an article
* Deleting an article
* Checking whether an article exists

MongoDB is the current storage implementation through `MongoArticleStorage`.

MongoDB is configured to run locally using Docker Compose.

### MongoDB Configuration

- **Host:** `localhost`
- **Port:** `27017`
- **Image:** `mongo:7.0`

The default MongoDB connection is configured for the local Docker environment.

MongoDB data is persisted using a Docker volume so that the database state can survive container restarts.

## Testing

The project includes unit tests and integration tests covering the main pipeline components.

Unit tests cover:

* RSS ingestion
* Kafka producer and consumer logic
* Article processing
* NLP components
* Event models
* Storage interfaces
* MongoDB storage implementation

Integration tests verify the interaction with external infrastructure such as MongoDB.

Run the complete test suite with:

```bash
pytest
```

For the MongoDB integration tests, the Docker infrastructure must be running:

```bash
docker compose up -d
pytest tests/storage/test_mongodb_integration.py -v
```

## Roadmap

* [x] M0 - Project Setup
* [x] M1 - RSS Ingestion
* [x] M2 - Kafka Pipeline
* [x] M3 - Article Processing
* [x] M4 - NLP Layer
* [x] M5 - Storage
* [ ] M6 - Analytics
* [ ] M7 - Dashboard / API

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

Start the local infrastructure:

```bash
docker compose up -d
```

Run the test suite to verify the installation:

```bash
pytest
```

The Docker Compose configuration currently provides the Kafka and MongoDB infrastructure required by the project.

## Project Status

🚧 Work in progress

M0 through M5 are currently completed. The next planned milestone is M6 - Analytics.
