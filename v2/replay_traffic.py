# -*- coding: utf-8 -*-
"""
DTRA v2.0 - Traffic Sender (Silent)
Sends packets to server. No response handling - just fire and forget.
"""

import os
import time
import requests
import numpy as np
import joblib
import random

# Configuration
API_URL = "http://127.0.0.1:5000/api/analyze"
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "CICIIOT2025", "processed")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

print("=" * 50)
print("   DTRA v2.0 - Traffic Sender")
print("=" * 50)

# Load data
print("\n📂 Loading test data...")
X_test = np.load(os.path.join(PROCESSED_DIR, 'X_test.npy'))
scaler = joblib.load(os.path.join(MODELS_DIR, 'dtra_scaler_v2.pkl'))

with open(os.path.join(PROCESSED_DIR, 'feature_names.txt'), 'r') as f:
    features = [line.strip() for line in f if line.strip()]

print(f"   ✅ Loaded {len(X_test):,} samples")
print(f"\n🚀 Sending traffic to {API_URL}")
print("   Press Ctrl+C to stop\n")

packet_count = 0
try:
    while True:
        # Pick random sample
        idx = random.randint(0, len(X_test) - 1)
        scaled_vector = X_test[idx]
        
        # Inverse transform to get raw values
        raw_vector = scaler.inverse_transform([scaled_vector])[0]
        packet_dict = dict(zip(features, raw_vector))
        
        # Send to server (fire and forget - minimal waiting)
        try:
            requests.post(API_URL, json={"packets": [packet_dict]}, timeout=5)
            packet_count += 1
            print(f"   📤 Sent packet #{packet_count}", flush=True)
        except:
            print(f"   ⚠️ Failed to send packet #{packet_count + 1}", flush=True)
        
        time.sleep(1)  # 1 packet per second

except KeyboardInterrupt:
    print(f"\n\n🛑 Stopped. Sent {packet_count} packets total.")
