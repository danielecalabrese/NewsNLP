# NewsNLP

NewsNLP is a personal data engineering and NLP project that collects news articles from RSS feeds, processes them through an event-driven pipeline, extracts meaningful information, and stores the results for further analysis.

## Project Goals

- Collect news articles from multiple RSS feeds.
- Build an event-driven ingestion pipeline using Apache Kafka.
- Normalize and process article content.
- Apply Natural Language Processing (NLP) techniques.
- Persist processed articles in MongoDB.
- Provide a foundation for future analytics and visualization.

## Architecture

NewsNLP uses an event-driven architecture based on Apache Kafka.

```text
RSS Feeds
    |
    v
RSS Reader
    |
    v
ArticleCreatedEvent
    |
    v
Kafka Producer
    |
    v
Kafka Topic: news.article
    |
    v
Kafka Consumer
    |
    v
Article Processing
    |
    +--> Text Preprocessing
    +--> Language Detection
    +--> Keyword Extraction
    +--> Sentiment Analysis
    |
    v
ProcessedArticle
    |
    +--> MongoDB Storage
    |
    v
ProcessedArticleEvent
    |
    v
Kafka Topic: news.article.processed
```

The RSS Reader collects articles from enabled feeds and publishes them to Kafka as `ArticleCreatedEvent` events.

The processing pipeline consumes these events, normalizes the article content, detects its language, extracts keywords, analyzes sentiment, and persists the resulting `ProcessedArticle` in MongoDB.

After processing, the application publishes a `ProcessedArticleEvent` to Kafka. This allows downstream consumers to use processed articles independently of the processing and storage components.

## Technology Stack
- Python 3.14+
- Apache Kafka 4.0.1
- MongoDB 7.0
- Docker Compose
- Pydantic
- Transformers and PyTorch
- langdetect
- pytest

## Requirements
Before running the application, ensure the following tools are installed:
- Python 3.14 or later
- Docker
- Docker Compose
  
## Getting Started
####  1. Clone the Repository
```
git clone <repository-url>
cd NewsNLP
```
Replace `<repository-url>` with the URL of your repository.
#### 2. Create a Virtual Environment
```
python3 -m venv .venv
source .venv/bin/activate
```
####  3. Install Dependencies
Install the project dependencies
```
python -m pip install -r requirements.txt
```
Install NewsNLP in editable mode:
```
python -m pip install -e .
```
Editable installation allows Python to import the package directly from the local source tree.
#### 4. Start the Infrastructure
Start Kafka and MongoDB using Docker Compose:
```
docker compose up -d
```
Check the running containers:
```
docker compose ps
```
The local infrastructure includes:
| Service      | Container         | Address           |
| ------------ | ----------------- | ----------------- |
| Apache Kafka | `newsnlp-kafka`   | `localhost:9092`  |
| MongoDB      | `newsnlp-mongodb` | `localhost:27018` |

Kafka uses KRaft mode and does not require a separate ZooKeeper service.
MongoDB data is persisted through the `mongodb_data` Docker volume.
To stop the services:
```
docker compose down
```
To stop the services and remove the persistent MongoDB volume:
```
docker compose down -v
```
Warning: removing the volume deletes the MongoDB data stored in it.

## Configuration

### RSS Feeds

RSS feed configuration is stored in `config/feeds.json` by default.
Example:
```
{
  "feeds": [
    {
      "name": "Example News",
      "url": "https://example.com/feed.xml",
      "enabled": false
    }
  ]
}
```
Each feed has three properties:
- `name`: identifies the feed and its source.
- `url`: the RSS feed URL.
- `enabled`: determines whether the feed is processed.
  
Replace the example URL with a valid RSS feed URL and set enabled to true to activate the feed.

Multiple feeds can be configured in the same file.

### Environment Variables

The application supports the following environment variables:
|        Variable         |           Default           |               Description                |
| :---------------------: | :-------------------------: | :--------------------------------------: |
|  `NEWSNLP_FEEDS_FILE`   |     `config/feeds.json`     | Path to the RSS feed configuration file  |
|     `KAFKA_BROKER`      |      `localhost:9092`       |           Kafka broker address           |
|      `KAFKA_TOPIC`      |       `news.article`        | Kafka topic for incoming article events  |
| `KAFKA_PROCESSED_TOPIC` |  `news.article.processed`   | Kafka topic for processed article events |
| `KAFKA_CONSUMER_GROUP`  |    `newsnlp-processing`     |           Kafka consumer group           |
|      `MONGODB_URI`      | `mongodb://localhost:27018` |          MongoDB connection URI          |
|   `MONGODB_DATABASE`    |          `newsnlp`          |          MongoDB database name           |

Example configuration:
```
export KAFKA_BROKER="localhost:9092"
export MONGODB_URI="mongodb://localhost:27018"
export MONGODB_DATABASE="newsnlp"
```
The default values are suitable for the local Docker Compose environment.

### Command-Line Interface

NewsNLP provides three commands through its CLI:
```
python -m newsnlp.cli --help
```

The CLI accepts an optional `--feeds-file` argument to specify a custom RSS feed configuration file.

### Ingest Articles
```
python -m newsnlp.cli ingest
```
This command:
1. Loads the configured RSS feeds.
2. Skips disabled feeds.
3. Retrieves articles from enabled feeds.
4. Publishes each article to Kafka as an `ArticleCreatedEvent`.
To use a custom feed configuration:
```
python -m newsnlp.cli --feeds-file config/custom-feeds.json ingest
```

### Process Articles
```
python -m newsnlp.cli process
```
This command starts the Kafka processing pipeline.

The consumer retrieves incoming article events, processes the articles, persists the results in MongoDB, and publishes processed article events to Kafka.

The processing loop runs continuously until interrupted with `Ctrl+C`.

### Run the Complete Pipeline
```
python -m newsnlp.cli run
```
This command:
1. Loads and validates the RSS feed configuration.
2. Ingests articles from enabled feeds.
3. Publishes the articles to Kafka.
4. Starts the processing pipeline.
5. Stores processed articles in MongoDB.
6. Publishes processed article events to Kafka.

The processing stage runs continuously until interrupted with `Ctrl+C`.

To use a custom feed configuration:
```
python -m newsnlp.cli --feeds-file config/custom-feeds.json run
```
Note: At least one valid, enabled RSS feed should be configured before running ingestion. Kafka and MongoDB must be available for the complete pipeline to operate.

### Article Processing and NLP
The processing pipeline enriches collected articles with NLP information.
The current implementation includes:
- Text preprocessing: normalizes article content.
- Language detection: identifies the language of the article.
- Keyword extraction: extracts relevant keywords from the text.
- Sentiment analysis: classifies the sentiment of supported article content.

Processed articles are represented by the `ProcessedArticle` model.

The model retains the original article information and includes processing metadata and NLP results, such as extracted keywords and sentiment.

### Storage

NewsNLP defines an ArticleStorage abstraction to separate storage operations from article processing.

The storage interface supports:
- Saving an article.
- Retrieving an article.
- Deleting an article.
- Checking whether an article exists.

The current implementation, MongoArticleStorage, persists processed articles in MongoDB.

Default connection settings:
- Host: `localhost`
- Port: `27017`
- Database: `newsnlp`

MongoDB is started through Docker Compose, and its data is persisted in the `mongodb_data` volume.

### Testing

The project includes unit, integration, and end-to-end tests.
The test suite covers:
- RSS ingestion.
- Event models and serialization.
- Kafka producers and consumers.
- Article processing and pipeline orchestration.
- Text preprocessing and NLP components.
- Storage interfaces.
- MongoDB storage.
- CLI behavior.
- End-to-end pipeline integration.

Run the complete test suite:
```
pytest
```
For a concise summary:
```
pytest -q
```

### Integration Tests

Some integration tests require external infrastructure.

Start Docker services before running the MongoDB integration tests:
```
docker compose up -d
pytest tests/storage/test_mongodb_integration.py -v
```

Kafka integration tests may also require a running Kafka broker.

Refer to individual test definitions for their infrastructure requirements.

## Project Structure
```
NewsNLP/
├── config/
│   └── feeds.json
├── src/
│   └── newsnlp/
│       ├── kafka/
│       ├── models/
│       ├── nlp/
│       ├── processing/
│       ├── readers/
│       ├── cli.py
│       ├── config.py
│       ├── mongodb_storage.py
│       └── storage.py
├── tests/
├── compose.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Roadmap
- [x] M0 - Project Setup
- [x] M1 - RSS Ingestion
- [x] M2 - Kafka Pipeline
- [x] M3 - Article Processing
- [x] M4 - NLP Layer
- [x] M5 - Storage
- [ ] M6 - Analytics
- [ ] M7 - Dashboard / API


## Project Status
NewsNLP is a work in progress.

Milestones M0 through M5 are completed. The current implementation provides an end-to-end foundation for RSS ingestion, event-driven processing, NLP enrichment, and MongoDB persistence.

Future milestones will extend the project with analytics and additional ways to explore processed news data.