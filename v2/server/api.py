# -*- coding: utf-8 -*-
"""
DTRA v2.0 - API Server
Flask backend that serves the Two-Stage Hybrid Detection System.
Integrates Ensemble Detection, Attack Categorization, Q-Learning, and SHAP Explanation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import joblib
import os
import time
import tensorflow as tf
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization # Needed for model loading if custom layers used
import config
from explainer import DTRAExplainer

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for dashboard

# ============================================================
# GLOBAL AI ENGINE STATE
# ============================================================
class DTRASystem:
    def __init__(self):
        print("🚀 DTRA v2.0 System Initialization...")
        
        # 1. Load Preprocessing Artifacts
        print("   📂 Loading preprocessors...")
        self.scaler = joblib.load(config.SCALER_PATH)
        self.imputer = joblib.load(config.IMPUTER_PATH)
        self.encoder = joblib.load(config.ENCODER_PATH)
        self.feature_names = config.NUMERIC_FEATURES
        
        # 2. Load Stage 1 Models (Binary Ensemble)
        print("   🛡️ Loading Stage 1: Ensemble Detector...")
        self.xgb_model = joblib.load(config.XGB_MODEL_PATH)
        self.dnn_binary = load_model(config.DNN_MODEL_PATH)
        self.ensemble_config = joblib.load(config.ENSEMBLE_CONFIG_PATH)
        self.threshold = self.ensemble_config.get('threshold', 0.5)
        print(f"      Detection Threshold: {self.threshold}")

        # 3. Load Stage 2 Models (DNN + XGBoost Stacking)
        print("   🧠 Loading Stage 2: Attack Categorizer (Ensemble)...")
        self.categorizer = load_model(config.CATEGORIZER_MODEL_PATH)
        self.categorizer_xgb = joblib.load(os.path.join(config.MODELS_DIR, 'dtra_xgb_categorizer.pkl'))
        self.attack_classes = config.ATTACK_CLASSES

        # 4. Load Explainability Module
        print("   💡 Loading SHAP Explainer...")
        self.explainer = DTRAExplainer()

        # 5. Load Q-Learning Agent
        print("   🤖 Loading Q-Learning Agent...")
        self.q_table = np.load(config.Q_TABLE_PATH) if os.path.exists(config.Q_TABLE_PATH) else None
        # (Simple greedy agent logic implemented inline for inference)

        print("✅ DTRA System Ready.")

    def preprocess(self, raw_data):
        """Standardizes input data to match model expectations."""
        # Convert list to DataFrame if needed
        if isinstance(raw_data, list):
             # Assuming raw_data is a list of dicts or list of lists
             # For simplicity, if it's a list, assume it matches standard feature order
             df = pd.DataFrame(raw_data, columns=self.feature_names)
        else:
            df = raw_data

        # Impute missing values
        X = self.imputer.transform(df)
        # Scale features
        X_scaled = self.scaler.transform(X)
        return X_scaled, df

    def predict_packet(self, raw_packet_data):
        """
        Full v2 Pipeline:
        1. Preprocess
        2. Stage 1 (Ensemble) -> Attack/Benign
        3. Stage 2 (Ensemble) -> Attack Type (if Attack)
        4. Explain -> SHAP (if Attack)
        5. Decide -> Q-Action
        """
        start_time = time.time()
        
        # 1. Preprocess
        # raw_packet_data is expected to be a dict input from JSON
        input_df = pd.DataFrame([raw_packet_data])
        
        # Handle missing columns by filling with 0 (edge case safety)
        for col in self.feature_names:
            if col not in input_df.columns:
                input_df[col] = 0
        
        # Ensure correct order
        input_df = input_df[self.feature_names]
        
        X_scaled = self.scaler.transform(self.imputer.transform(input_df))
        
        # 2. Stage 1: Ensemble Detection (Binary)
        xgb_prob = self.xgb_model.predict_proba(X_scaled)[:, 1][0]
        dnn_prob = self.dnn_binary.predict(X_scaled, verbose=0).flatten()[0]
        
        # Soft Voting
        danger_score = (xgb_prob + dnn_prob) / 2
        is_attack = danger_score > self.threshold
        
        result = {
            "timestamp": time.time(),
            "danger_score": float(danger_score),
            "is_attack": bool(is_attack),
            "processing_time": 0.0
        }

        # 3. Stage 2 & 4. Decisions (Only if Attack)
        if is_attack:
            # Predict Category (ENSEMBLE STACKING)
            try:
                # DNN Probabilities
                dnn_cat_probs = self.categorizer.predict(X_scaled, verbose=0)[0]
                # XGBoost Probabilities
                xgb_cat_probs = self.categorizer_xgb.predict_proba(X_scaled)[0]
                
                # Soft Voting (Average)
                cat_probs = (dnn_cat_probs + xgb_cat_probs) / 2
            except Exception as e:
                print(f"⚠️ Ensemble Error: {e}. Fallback to DNN only.")
                cat_probs = self.categorizer.predict(X_scaled, verbose=0)[0]

            cat_idx = np.argmax(cat_probs)
            attack_type = self.attack_classes[cat_idx]
            confidence = float(cat_probs[cat_idx])
            
            result["attack_type"] = attack_type
            result["confidence"] = confidence
            
            # Generate Explanation (SHAP)
            explanation = self.explainer.explain_packet(X_scaled[0])
            result["explanation"] = explanation
            
            # Q-Learning Action Selection
            # State = (Danger Bucket 0-9, Attack Type Index 0-6)
            danger_bucket = min(int(danger_score * 10), 9)
            
            if self.q_table is not None:
                # 4 actions: Ignore, Log, Block, Isolate
                action_idx = np.argmax(self.q_table[danger_bucket, cat_idx])
                actions = config.RL_CONFIG['actions']
                result["action"] = actions[action_idx]
            else:
                # Fallback rule-based
                result["action"] = "Block" if danger_score > 0.8 else "Log"
                
        else:
            result["attack_type"] = "Benign"
            result["action"] = "Allow"
            result["explanation"] = None

        result["processing_time"] = time.time() - start_time
        return result

# Initialize System
dtra = DTRASystem()

# Global cache for recent results (shared between replay_traffic and dashboard)
recent_results = []
MAX_CACHED_RESULTS = 100
packet_counter = 0  # Counter for logging

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "DTRA v2.0 API Server",
        "status": "online",
        "endpoints": {
            "GET /api/status": "Check system status",
            "POST /api/analyze": "Analyze network packets",
            "GET /api/recent": "Get recent analysis results"
        }
    })

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "active", 
        "version": "v2.0", 
        "system": "DTRA Hybrid",
        "cached_results": len(recent_results)
    })

@app.route('/api/recent', methods=['GET'])
def get_recent():
    """Returns the most recent analysis results from ALL sources."""
    return jsonify({"results": recent_results})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyzes a single packet or list of packets.
    Payload: { "packets": [ {feature_1: val, ...} ] }
    """
    global recent_results, packet_counter
    
    try:
        data = request.json
        if not data or 'packets' not in data:
            return jsonify({"error": "No packets provided"}), 400
            
        packets = data['packets']
        results = []
        
        for pkt in packets:
            packet_counter += 1
            result = dtra.predict_packet(pkt)
            result['packet_id'] = packet_counter  # Unique ID for dashboard deduplication
            results.append(result)
            
            # Console logging for live visibility
            status_icon = "🔴 ATTACK" if result['is_attack'] else "🟢 BENIGN"
            attack_type = result.get('attack_type', 'N/A')
            action = result.get('action', 'N/A')
            score = result['danger_score'] * 100
            
            print(f"[{packet_counter:04d}] {status_icon} | Type: {attack_type:<12} | Score: {score:5.1f}% | Action: {action}", flush=True)
        
        # Cache results for dashboard polling
        recent_results = results + recent_results
        recent_results = recent_results[:MAX_CACHED_RESULTS]
            
        return jsonify({"results": results})

    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("   DTRA v2.0 - API Server")
    print("=" * 60)
    print("\n📡 Listening for traffic on http://127.0.0.1:5000")
    print("\n📊 Live Traffic Analysis Log:")
    print("-" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
