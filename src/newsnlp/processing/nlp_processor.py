from abc import ABC, abstractmethod

from newsnlp.models.article import Article
from newsnlp.models.nlp import NLPResult


class NLPProcessor(ABC):

    @abstractmethod
    def process(self, article: Article) -> NLPResult:
        pass