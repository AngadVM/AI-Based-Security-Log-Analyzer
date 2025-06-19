import json
import torch
import random
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from torch.optim import AdamW
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
)

# Define labels
LABELS = ["brute_force", "port_scan", "suspicious_login", "dos_attack", "malware_activity", "normal"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for label, i in LABEL2ID.items()}

def load_data(path="synthetic_logs.jsonl"):
    data = []
    with open(path) as f:
        for line in f:
            entry = json.loads(line)
            if entry["label"] in LABEL2ID:
                data.append({
                    "text": entry["raw"],
                    "label": LABEL2ID[entry["label"]]
                })
    return pd.DataFrame(data)

def encode_data(tokenizer, texts, labels):
    encoding = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    encoding["labels"] = torch.tensor(labels)
    return encoding

# Main training logic
def train_model():
    df = load_data()
    print(f"✅ Loaded {len(df)} samples")

    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)

    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )

    train_enc = encode_data(tokenizer, train_df["text"].tolist(), train_df["label"].tolist())
    test_enc = encode_data(tokenizer, test_df["text"].tolist(), test_df["label"].tolist())

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    model.train()

    EPOCHS = 4
    BATCH_SIZE = 16

    for epoch in range(EPOCHS):
        print(f"\n🚀 Epoch {epoch+1}/{EPOCHS}")
        for i in tqdm(range(0, len(train_df), BATCH_SIZE)):
            batch = {k: v[i:i+BATCH_SIZE].to(device) for k, v in train_enc.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        print(f"✅ Epoch {epoch+1} complete.")

    # Evaluation
    model.eval()
    with torch.no_grad():
        input_ids = test_enc["input_ids"].to(device)
        attention_mask = test_enc["attention_mask"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, axis=1).cpu().numpy()

    print("\n📊 Classification Report:")
    print(classification_report(test_df["label"], preds, target_names=LABELS))

    model.save_pretrained("threat_classifier_model")
    tokenizer.save_pretrained("threat_classifier_model")
    print("\n✅ Model saved to ./threat_classifier_model")

if __name__ == "__main__":
    train_model()

