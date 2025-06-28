
# AI-Based Security Log Analyzer

An open-source, lightweight tool to **analyze security logs**, detect anomalies, and classify threats using **machine learning**.

### Built With:

- **Scikit-learn** – ML models for anomaly detection and threat classification  
- **FastAPI** – High-performance backend  
- **React.js + Tailwind CSS** – Modern, interactive frontend  
- **Elasticsearch** – Storage and query engine  
- **WebSockets** – Live log stream updates  

---

## Features

- Upload `.log` files and visualize security insights  
- Real-time detection of anomalies and threat types  
- Dashboard with charts and live stream panel  
- Time-based and threat/source filters  
- Classic ML model pipeline (Isolation Forest + Gradient Boosting)

---

## Prerequisites

1. Python 3.10+  
2. Node.js + npm  
3. Elasticsearch (installed locally or via Docker)

### Installing Elasticsearch (Linux):

```bash
sudo dnf install elasticsearch
sudo systemctl enable --now elasticsearch
````

Or run via Docker:

```bash
docker run -d --name es -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.7.0
```

---

## Installation & Setup

> Clone the repository and run the setup script.

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/AI-Based-Security-Log-Analyzer.git
cd AI-Based-Security-Log-Analyzer
```

### Step 2: Run the setup script

```bash
bash setup.sh
```

This will:

* Set up Python virtual environment
* Install all backend and ML dependencies
* Install frontend dependencies and build dashboard
* Start backend (port `8000`) and frontend (port `5173`)

---

## Usage

1. Visit `http://localhost:5173` in your browser
2. Click “Upload .log File”
3. The system will:

   * Parse and analyze logs
   * Detect anomalies
   * Classify threats
   * Show insights in real-time
4. Use filters to explore logs

---

## Project Structure

```
AI-Based-Security-Log-Analyzer/
├── backend_api/
│   ├── main.py
│   └── websocket_manager.py
│
├── ml_pipeline/
│   ├── train_isolation.py
│   ├── train_classic_model.py
│   ├── infer.py
│   └── preprocess.py
│
├── scripts/
│   └── bulk_upload_to_es.py
│
├── frontend_dashboard/
│   ├── src/App.jsx
│   └── components/LiveStream.jsx
│
├── data/                  # Raw and parsed logs
├── models/                # ML .joblib models
├── setup.sh               # Auto setup script
├── requirements.txt
└── README.md
```

---

## Example Log Lines

```
Jun 14 15:16:02 combo sshd(pam_unix)[19937]: check pass; user unknown  
Too many connections from 192.168.1.100  
Failed login attempt for user root from 10.0.0.5  
```

---

## Testing

Run:

```bash
python tests/test_infer.py
```

---

## Notes

* This is a **local-first project** – no login, no cloud.
* Elasticsearch **must be running locally**.
* Logs are streamed in real-time using WebSocket.

---

## License

MIT License © 2025 \AngadVM

---
