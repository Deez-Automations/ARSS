# 🛡️ DTRA - Dynamic Threat Response Agent

**An AI-Powered Security Operations Center (SOC) Console for Real-Time Network Threat Detection.**

DTRA (Dynamic Threat Response Agent) is an advanced cybersecurity monitoring system that uses **Hybrid AI** (Deep Learning + Random Forest) and **Reinforcement Learning** (Q-Learning) to detect, classify, and respond to network attacks in real-time.


## 🚀 Key Features

*   **🧠 Hybrid AI Engine:** Combines the reliability of **Random Forest** with the complexity handling of **Deep Neural Networks** to achieve **98.9% accuracy** on the CICIDS2017 dataset.
*   **🤖 Q-Learning Guard Agent:** An autonomous reinforcement learning agent that dynamically decides the best response action (Block, Log, or Ignore) based on threat confidence and network state.
*   **📊 Professional SOC Dashboard:** A premium, dark-mode web console featuring:
    *   **Traffic Analysis:** Real-time animated traffic volume graphs.
    *   **Severity Distribution:** Live breakdown of threat levels (Critical vs. Low).
    *   **Packet Inspector:** Searchable, visible log of deeply analyzed network packets.
*   **⚡ High-Performance API:** Flask-based backend capable of processing 300k+ packet flows instantly using optimized vectorization and caching.

## 📂 Project Structure

The project is organized into two major versions:

### **v1/ - Classic DTRA (CICIDS2017)**
The original binary classification system.
```bash
DTRA/v1/
├── server/             # Flask API & Binary DNN
│   ├── api.py          # Legacy single-stage API
│   └── detector.py     # Binary classifier logic
├── ui/                 # Classic Dashboard
└── models/             # Legacy models (dtra_detector_model.h5)
```

### **v2/ - DTRA Next-Gen (CIC IIoT 2025)**
The upgraded **Two-Stage Hybrid Architecture** with Explainable AI.
```bash
DTRA/v2/
├── server/             # Advanced Backend
│   ├── config.py       # Updated for 71 features & 7 attack classes
│   └── api.py          # Multi-stage API logic
├── CICIIOT2025/        # New dataset processing
│   └── processed/      # Preprocessed numpy arrays
├── models/             # Two-stage models (XGBoost + DNN + Categorizer)
└── train_v2.py         # Advanced training pipeline
```

### **Global Files**
```bash
DTRA/
├── docs/               # Strategic planning & documentation
├── README.md           # This file
└── requirements.txt    # Project dependencies
```

## 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/StartLivin-DEEZ/DTRA.git
    cd DTRA
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start the Server**
    Navigate to the `server` directory and run the API:
    ```bash
    cd server
    python api.py
    ```
    *You should see:* `🚀 DTRA API Server running on port 5000`

4.  **Launch the Dashboard**
    *   Open `ui/soc_dashboard.html` directly in your web browser.
    *   Upload a CSV dataset (e.g., CICIDS2017 sample) to start analysis.

## 🧪 Usage

1.  **Select a Dataset:** Click the upload area in the dashboard.
2.  **Run Analysis:** Click "Run Analysis". The AI will process the file.
3.  **Monitor:** Watch the **Q-Learning Agent** make decisions in real-time and filter the **Threat Logs** to investigate specific attacks.

## 🤖 How It Works

1.  **Ingestion:** Configures raw PCAP/CSV data features into the exact 79-feature vector expected by the model.
2.  **Preprocessing:** Cleans data (Infinity/NaN handling) -> Imputes missing values -> Scales (StandardScaler).
3.  **Prediction:** The Neural Network predicts a `Danger Score` (0.0 - 1.0).
4.  **Decision:** The Q-Learning Agent observes the score + current threat rate -> Chooses an Action (Block/Log/Ignore).
5.  **Visualization:** Results are streamed to the Dashboard via JSON API.

## 🔒 Security & Performance

*   **Input Sanitization:** Robust handling of malformed CSVs and "Infinity" overflow attacks.
*   **Batch Processing:** Optimized for large datasets (300k+ rows) using NumPy vectorization.
*   **Local Execution:** All analysis happens locally; no data leaves your machine.

---
*Created for CS 351 Project - GIKI*
