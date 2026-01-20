# -*- coding: utf-8 -*-
"""
DTRA v2.0 Configuration Module
Centralized settings and feature definitions for the Two-Stage Hybrid Architecture.
"""

import os

# --- Project Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Root of v2
DATA_DIR = os.path.join(BASE_DIR, "CICIIOT2025")
MODELS_DIR = os.path.join(BASE_DIR, "models")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# Create models directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

# --- Model File Paths (v2) ---
# Stage 1: Binary Ensemble
XGB_MODEL_PATH = os.path.join(MODELS_DIR, "dtra_xgb_binary.pkl")
DNN_MODEL_PATH = os.path.join(MODELS_DIR, "dtra_dnn_binary.h5")
ENSEMBLE_CONFIG_PATH = os.path.join(MODELS_DIR, "ensemble_config.pkl")

# Stage 2: Attack Categorizer
CATEGORIZER_MODEL_PATH = os.path.join(MODELS_DIR, "dtra_categorizer.h5")

# Preprocessing Artifacts
IMPUTER_PATH = os.path.join(MODELS_DIR, "dtra_imputer_v2.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "dtra_scaler_v2.pkl")
ENCODER_PATH = os.path.join(MODELS_DIR, "dtra_category_encoder.pkl")
Q_TABLE_PATH = os.path.join(MODELS_DIR, "dtra_q_table_v2.npy")

# --- Attack Classes (Stage 2) ---
ATTACK_CLASSES = [
    'bruteforce', 'ddos', 'dos', 'malware', 'mitm', 'recon', 'web'
]
NUM_CLASSES = len(ATTACK_CLASSES)

# --- The 71 Numeric Features (CIC IIoT 2025) ---
NUMERIC_FEATURES = [
    'log_data-ranges_min', 'network_ips_dst_count', 'network_tcp-flags-fin_count',
    'network_ttl_std_deviation', 'network_fragmentation-score', 'network_tcp-flags_min',
    'network_payload-length_min', 'network_fragmented-packets',
    'network_header-length_std_deviation', 'network_mss_min', 'network_window-size_max',
    'network_header-length_min', 'network_ips_all_count', 'log_data-ranges_max',
    'log_data-ranges_std_deviation', 'network_ip-flags_std_deviation', 'network_ttl_min',
    'network_macs_src_count', 'network_ttl_max', 'log_messages_count',
    'network_ports_dst_count', 'network_ports_src_count', 'network_window-size_avg',
    'network_ip-length_std_deviation', 'network_packets_all_count', 'log_data-types_count',
    'log_data-ranges_avg', 'network_ip-length_min', 'network_time-delta_std_deviation',
    'network_payload-length_max', 'network_tcp-flags-urg_count', 'network_packet-size_min',
    'network_header-length_avg', 'network_tcp-flags_max', 'network_packet-size_max',
    'network_header-length_max', 'network_protocols_all_count', 'network_ip-flags_min',
    'network_window-size_std_deviation', 'network_macs_dst_count', 'network_packet-size_avg',
    'network_time-delta_max', 'network_macs_all_count', 'network_time-delta_min',
    'network_payload-length_avg', 'network_mss_std_deviation', 'network_ips_src_count',
    'network_interval-packets', 'network_ip-length_max', 'network_packets_dst_count',
    'network_mss_avg', 'network_ip-flags_avg', 'network_ip-length_avg',
    'network_payload-length_std_deviation', 'network_packet-size_std_deviation',
    'network_protocols_src_count', 'network_tcp-flags_avg', 'log_interval-messages',
    'network_window-size_min', 'network_ip-flags_max', 'network_ports_all_count',
    'network_ttl_avg', 'network_tcp-flags-psh_count', 'network_tcp-flags_std_deviation',
    'network_protocols_dst_count', 'network_mss_max', 'network_packets_src_count',
    'network_tcp-flags-rst_count', 'network_time-delta_avg', 'network_tcp-flags-syn_count',
    'network_tcp-flags-ack_count'
]
INPUT_DIM = len(NUMERIC_FEATURES)

# --- A* Decision Costs ---
BUSINESS_COSTS = {
    'Ignore': 0,
    'Log': 2,
    'Block': 20,
    'Isolate': 80
}

# --- Q-Learning Parameters (Enhanced) ---
RL_CONFIG = {
    'num_danger_states': 10,    # 0.0-1.0 quantized
    'num_attack_types': NUM_CLASSES,
    'actions': ['Ignore', 'Log', 'Block', 'Isolate'],
    'alpha': 0.1,
    'gamma': 0.9,
    'epsilon': 0.1,
    'num_episodes': 10000
}

# --- Dashboard Settings ---
DASHBOARD_CONFIG = {
    'page_title': "DTRA v2.0 | Advanced Threat Response",
    'page_icon': "🛡️",
    'layout': "wide"
}
