from newsnlp.kafka.producer import KafkaArticleProducer
from newsnlp.models.article import Article
from newsnlp.models.events import ProcessedArticleEvent
from newsnlp.models.processed_article import ProcessedArticle
from newsnlp.processing.article_processor import ArticleProcessor


class ArticleProcessingService:

    def __init__(
        self,
        processor: ArticleProcessor,
        producer: KafkaArticleProducer,
    ):
        self.processor = processor
        self.producer = producer

    def process_and_publish(self, article: Article) -> ProcessedArticle:
        processed_article = self.processor.process(article)

        event = ProcessedArticleEvent(
            article=processed_article,
            processed_at=processed_article.processed_at,
        )

        self.producer.send(event)

        return processed_article