from transformers import pipeline


class SentimentAnalyzer:

    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="clapAI/roberta-base-multilingual-sentiment",
        )

    def analyze(self, text: str) -> str:
        result = self.classifier(text)[0]
        label = result["label"].lower()

        return label