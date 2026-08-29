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

The project will progressively evolve into an event-driven pipeline:

```text
RSS Feeds
    │
    ▼
RSS Reader
    │
    ▼
Kafka
    │
    ├──► Article Processing
    │
    ├──► NLP
    │
    └──► Storage & Analytics
```

## Roadmap

* [ ] M0 – Project Setup
* [ ] M1 – RSS Ingestion
* [ ] M2 – Kafka Pipeline
* [ ] M3 – Article Processing
* [ ] M4 – NLP Layer
* [ ] M5 – Storage
* [ ] M6 – Analytics
* [ ] M7 – Dashboard / API

## Getting Started

The project is currently under development.

More detailed setup and usage instructions will be added as the project evolves.

## Project Status

🚧 Work in progress
