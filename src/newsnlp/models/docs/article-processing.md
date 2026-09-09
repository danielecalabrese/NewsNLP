# Article Processing

## Overview

The article processing pipeline transforms raw articles collected from RSS feeds
into normalized and processed articles.

The processing stage is responsible for preparing article content and metadata
for downstream NLP processing and event streaming.

## Processing Flow

```
RSS Feed
   ↓
RSSReader
   ↓
Article
   ↓
ArticleProcessor
   ↓
ProcessedArticle
   ↓
ProcessedArticleEvent
   ↓
Kafka Producer
   ↓
Kafka Topic
```

## Article


The `Article` model represents an article collected from an RSS feed.

It contains the original article data, including:

* article ID
* source ID
* title
* URL
* author
* publication timestamp
* content
* summary
* language
* fetch timestamp

The `Article` represents the raw article before processing.

## ArticleProcessor

The `ArticleProcessor` transforms an `Article` into a `ProcessedArticle`.

The processor currently performs content normalization by:

* removing leading and trailing whitespace
* replacing consecutive whitespace characters with a single space

Example:
```
processor = ArticleProcessor()

processed_article = processor.process(article)
```

The processor also records the processing timestamp using UTC.

## ProcessedArticle

The `ProcessedArticle` model represents the result of the article processing stage.

It contains the article data together with processing-related information.

In addition to the original article metadata, it contains fields for future NLP processing:

* keywords
* entities
* sentiment

These fields are initialized with empty or null values and can be populated by
future processing components.

The model also contains:

fetched_at - timestamp of article retrieval
processed_at - timestamp of article processing
Events

The event models represent messages exchanged between different stages of the
pipeline.

ArticleCreatedEvent

ArticleCreatedEvent represents the creation of a raw article.

It contains:

* `article` - the original Article
* `created_at` - event creation timestamp

## ProcessedArticleEvent

`ProcessedArticleEvent` represents a processed article ready for downstream
consumers.

It contains:

* article - the processed ProcessedArticle
* processed_at - processing timestamp

### Example

A raw article can be processed as follows:
```
article = Article(...)

processor = ArticleProcessor()

processed_article = processor.process(article)

event = ProcessedArticleEvent(
    article=processed_article,
    processed_at=processed_article.processed_at,
)
```
The resulting event can then be serialized and published to Kafka.

## Current Processing Capabilities

The current implementation provides the foundation for the NLP processing
pipeline.

At this stage, the processor performs content normalization while preserving
the original article metadata.

Future processing stages can extend the `ArticleProcessor` to add:

* keyword extraction
* named entity recognition
* sentiment analysis
* language detection
* text summarization
* other NLP transformations

## Testing

The article processing components are covered by automated tests.

The tests verify:

* `ProcessedArticle` model creation and validation
* `ArticleProcessor` transformation
* content normalization
* processing timestamp generation
* `ProcessedArticleEvent` creation