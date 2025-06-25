import pandas as pd
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report

# --- Feature Extraction ---

def extract_features(df):
    def has_keyword(text, keyword):
        return int(keyword in text.lower())

    df["length"] = df["raw"].apply(len)
    df["contains_ip"] = df["raw"].apply(lambda t: int(bool(re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", t))))
    df["hour"] = df["timestamp"].apply(lambda t: pd.to_datetime(t, format="%b %d %H:%M:%S", errors='coerce').hour if t else -1)
    df["failed"] = df["raw"].apply(lambda t: has_keyword(t, "failed"))
    df["connection"] = df["raw"].apply(lambda t: has_keyword(t, "connection"))
    df["invalid"] = df["raw"].apply(lambda t: has_keyword(t, "invalid"))
    df["malicious"] = df["raw"].apply(lambda t: has_keyword(t, "malicious"))
    df["scan"] = df["raw"].apply(lambda t: has_keyword(t, "scan"))
    return df[["length", "contains_ip", "hour", "failed", "connection", "invalid", "malicious", "scan"]]

# --- Load Data ---
df = pd.read_csv("data/threat_logs.csv")
X = extract_features(df)
y = df["label"]
print(df["label"].value_counts())

# --- Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# --- Model Training ---
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# --- Evaluation ---
y_pred = model.predict(X_test)
print(" Classification Report:\n", classification_report(y_test, y_pred))

# --- Save Model ---
joblib.dump(model, "ml_pipeline/classic_classifier.joblib")
print(" Model saved as classic_classifier.joblib")

