import re
from html import unescape


class TextPreprocessor:
    """Clean and normalize raw article text."""

    def preprocess(self, text: str | None) -> str:
        """Clean and normalize the provided text."""
        if not text:
            return ""

        text = self._remove_html(text)
        text = unescape(text)
        text = self._normalize_whitespace(text)
        text = self._normalize_special_characters(text)

        return text.strip()

    @staticmethod
    def _remove_html(text: str) -> str:
        """Remove HTML tags from the text."""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        return text

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Normalize whitespace characters."""
        return re.sub(r"\s+", " ", text)

    @staticmethod
    def _normalize_special_characters(text: str) -> str:
        """Normalize common special characters."""
        replacements = {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u00a0": " ",
        }

        for character, replacement in replacements.items():
            text = text.replace(character, replacement)

        return text