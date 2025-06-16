from sklearn.ensemble import IsolationForest
from joblib import dump
from preprocess import preprocess_logs

def train_model():
    df = preprocess_logs()
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(df)
    dump(model, "ml_pipeline/model.joblib")
    print("Model trained and saved.")

if __name__ == "__main__":
    train_model()
