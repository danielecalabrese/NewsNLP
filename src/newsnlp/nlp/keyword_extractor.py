import re
from collections import Counter


class KeywordExtractor:

    STOPWORDS = {
        "a",
        "ad",
        "al",
        "alla",
        "alle",
        "con",
        "da",
        "dal",
        "dalla",
        "de",
        "del",
        "della",
        "di",
        "e",
        "ed",
        "gli",
        "i",
        "il",
        "in",
        "la",
        "le",
        "lo",
        "ma",
        "nel",
        "nella",
        "non",
        "o",
        "per",
        "su",
        "un",
        "una",
        "uno",
        "the",
        "and",
        "of",
        "to",
        "in",
        "on",
        "for",
        "with",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "this",
        "that",
    }

    def __init__(self, max_keywords: int = 5):
        if max_keywords < 1:
            raise ValueError("max_keywords must be greater than 0")

        self.max_keywords = max_keywords

    def extract(self, text: str) -> list[str]:
        if not text.strip():
            return []

        words = re.findall(r"\b\w+\b", text.lower())

        filtered_words = [
            word
            for word in words
            if word not in self.STOPWORDS
        ]

        word_counts = Counter(filtered_words)

        return [
            word
            for word, _ in word_counts.most_common(self.max_keywords)
        ]