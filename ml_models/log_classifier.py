from transformers import pipeline

class LogClassifier:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model ="distilbert-base-uncased-finetuned-sst-2-english"
        )

    def classify(self, text):
        result = self.classifier(text)[0]
        return result["label"], result["score"]

if __name__ == "__main__":
    clf = LogClassifier()
    label, score = clf.classify("Failed login attempt from 192.168.1.1")
    print(label, score)

