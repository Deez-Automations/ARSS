# -*- coding: utf-8 -*-
"""
DTRA v2.0 - Data Preprocessing Pipeline
Prepares CIC IIoT 2025 dataset for two-stage classification.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import joblib
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "CICIIOT2025", "combined_dataset.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "CICIIOT2025", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("   DTRA v2.0 - Data Preprocessing Pipeline")
print("   CIC IIoT 2025 Dataset")
print("=" * 60)

# ============================================================
# STEP 1: Load Dataset
# ============================================================
print("\n📂 STEP 1: Loading dataset...")

df = pd.read_csv(DATASET_PATH, low_memory=False)
print(f"   ✅ Loaded {len(df):,} samples")
print(f"   ✅ Columns: {len(df.columns)}")

# ============================================================
# STEP 2: Identify Feature Types
# ============================================================
print("\n🔍 STEP 2: Identifying feature types...")

# Get column info
label_cols = ['label_full', 'label1', 'label2', 'label3', 'label4']
meta_cols = ['device_name', 'device_mac', 'timestamp', 'timestamp_start', 'timestamp_end']
text_cols = ['log_data-types']

# All other columns are potential numeric features
all_cols = set(df.columns)
exclude_cols = set(label_cols + meta_cols + text_cols)
numeric_candidates = list(all_cols - exclude_cols)

print(f"   Label columns: {len(label_cols)}")
print(f"   Meta columns: {len(meta_cols)}")
print(f"   Numeric candidates: {len(numeric_candidates)}")

# ============================================================
# STEP 3: Extract Numeric Features
# ============================================================
print("\n📊 STEP 3: Extracting numeric features...")

# Keep only truly numeric columns
numeric_features = []
for col in numeric_candidates:
    if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
        numeric_features.append(col)

print(f"   ✅ Found {len(numeric_features)} numeric features")

# Create feature dataframe
X = df[numeric_features].copy()

# ============================================================
# STEP 4: Clean Data (Infinity, NaN)
# ============================================================
print("\n🧹 STEP 4: Cleaning data...")

# Count issues before
inf_count = np.isinf(X.values).sum()
nan_count = X.isnull().sum().sum()
print(f"   Before: {inf_count:,} infinity, {nan_count:,} NaN values")

# Replace infinity with NaN first
X = X.replace([np.inf, -np.inf], np.nan)

# Count NaN after infinity conversion
nan_after_inf = X.isnull().sum().sum()
print(f"   After inf→NaN: {nan_after_inf:,} NaN values")

# Fill NaN with median (robust to outliers)
imputer = SimpleImputer(strategy='median')
X_imputed = pd.DataFrame(
    imputer.fit_transform(X),
    columns=X.columns,
    index=X.index
)

# Clip extreme values (defensive)
X_clipped = X_imputed.clip(-1e10, 1e10)

print(f"   ✅ Cleaned: {X_clipped.shape}")

# Save imputer
joblib.dump(imputer, os.path.join(MODELS_DIR, 'dtra_imputer_v2.pkl'))
print(f"   ✅ Saved imputer to models/")

# ============================================================
# STEP 5: Create Labels for Two-Stage Model
# ============================================================
print("\n🏷️ STEP 5: Creating labels for two-stage model...")

# STAGE 1: Binary label (attack vs benign)
# label1 contains 'attack' or 'benign'
df['binary_label'] = df['label1'].apply(
    lambda x: 0 if 'benign' in str(x).lower() else 1
)

# Count distribution
benign_count = (df['binary_label'] == 0).sum()
attack_count = (df['binary_label'] == 1).sum()
print(f"   Stage 1 (Binary):")
print(f"      Benign: {benign_count:,} ({benign_count/len(df)*100:.1f}%)")
print(f"      Attack: {attack_count:,} ({attack_count/len(df)*100:.1f}%)")

# STAGE 2: Attack category label (from label2)
# Only for attack samples
attack_categories = df[df['binary_label'] == 1]['label2'].unique()
print(f"\n   Stage 2 (Attack Categories):")
print(f"      Found {len(attack_categories)} categories:")
for cat in sorted(attack_categories):
    count = (df['label2'] == cat).sum()
    print(f"         • {cat}: {count:,}")

# Encode attack categories
category_encoder = LabelEncoder()
df['attack_category_label'] = -1  # Default for benign
attack_mask = df['binary_label'] == 1
df.loc[attack_mask, 'attack_category_label'] = category_encoder.fit_transform(
    df.loc[attack_mask, 'label2']
)

# Save encoder
joblib.dump(category_encoder, os.path.join(MODELS_DIR, 'dtra_category_encoder.pkl'))
print(f"\n   ✅ Saved category encoder (classes: {list(category_encoder.classes_)})")

# ============================================================
# STEP 6: Scale Features
# ============================================================
print("\n📏 STEP 6: Scaling features...")

scaler = StandardScaler()
X_scaled = pd.DataFrame(
    scaler.fit_transform(X_clipped),
    columns=X_clipped.columns,
    index=X_clipped.index
)

# Final cleanup after scaling
X_scaled = X_scaled.clip(-10, 10)  # Prevent extreme scaled values

joblib.dump(scaler, os.path.join(MODELS_DIR, 'dtra_scaler_v2.pkl'))
print(f"   ✅ Saved scaler to models/")

# ============================================================
# STEP 7: Train/Test Split (Stratified)
# ============================================================
print("\n📂 STEP 7: Splitting into train/test (70/30)...")

y_binary = df['binary_label'].values
y_category = df['attack_category_label'].values

X_train, X_test, y_train_bin, y_test_bin, y_train_cat, y_test_cat = train_test_split(
    X_scaled, y_binary, y_category,
    test_size=0.3,
    stratify=y_binary,  # Stratified by attack/benign
    random_state=42
)

print(f"   Train: {len(X_train):,} samples")
print(f"   Test:  {len(X_test):,} samples")

# ============================================================
# STEP 8: Calculate Class Weights (for imbalance)
# ============================================================
print("\n⚖️ STEP 8: Calculating class weights...")

from sklearn.utils.class_weight import compute_class_weight

# Binary weights
binary_weights = compute_class_weight(
    'balanced', classes=np.array([0, 1]), y=y_train_bin
)
binary_weight_dict = {0: binary_weights[0], 1: binary_weights[1]}
print(f"   Binary weights: {binary_weight_dict}")

# Category weights (for attacks only)
attack_mask_train = y_train_bin == 1
y_cat_attacks = y_train_cat[attack_mask_train]
unique_cats = np.unique(y_cat_attacks)
category_weights = compute_class_weight(
    'balanced', classes=unique_cats, y=y_cat_attacks
)
category_weight_dict = {int(c): w for c, w in zip(unique_cats, category_weights)}
print(f"   Category weights: {category_weight_dict}")

# Save weights
joblib.dump({
    'binary': binary_weight_dict,
    'category': category_weight_dict
}, os.path.join(MODELS_DIR, 'class_weights.pkl'))

# ============================================================
# STEP 9: Save Preprocessed Data
# ============================================================
print("\n💾 STEP 9: Saving preprocessed data...")

# Save as numpy arrays (faster loading)
np.save(os.path.join(OUTPUT_DIR, 'X_train.npy'), X_train.values)
np.save(os.path.join(OUTPUT_DIR, 'X_test.npy'), X_test.values)
np.save(os.path.join(OUTPUT_DIR, 'y_train_binary.npy'), y_train_bin)
np.save(os.path.join(OUTPUT_DIR, 'y_test_binary.npy'), y_test_bin)
np.save(os.path.join(OUTPUT_DIR, 'y_train_category.npy'), y_train_cat)
np.save(os.path.join(OUTPUT_DIR, 'y_test_category.npy'), y_test_cat)

# Save feature names
with open(os.path.join(OUTPUT_DIR, 'feature_names.txt'), 'w') as f:
    for feature in X_scaled.columns:
        f.write(f"{feature}\n")

print(f"   ✅ Saved to: {OUTPUT_DIR}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("   ✅ PREPROCESSING COMPLETE")
print("=" * 60)
print(f"""
📊 Dataset Summary:
   • Total samples: {len(df):,}
   • Features: {len(numeric_features)}
   • Train samples: {len(X_train):,}
   • Test samples: {len(X_test):,}

🏷️ Labels:
   • Stage 1 (Binary): benign=0, attack=1
   • Stage 2 (Categories): {list(category_encoder.classes_)}

📁 Output Files:
   • {OUTPUT_DIR}/X_train.npy
   • {OUTPUT_DIR}/X_test.npy
   • {OUTPUT_DIR}/y_train_binary.npy
   • {OUTPUT_DIR}/y_test_binary.npy
   • {OUTPUT_DIR}/y_train_category.npy
   • {OUTPUT_DIR}/y_test_category.npy
   • {OUTPUT_DIR}/feature_names.txt

🔧 Model Files:
   • {MODELS_DIR}/dtra_imputer_v2.pkl
   • {MODELS_DIR}/dtra_scaler_v2.pkl
   • {MODELS_DIR}/dtra_category_encoder.pkl
   • {MODELS_DIR}/class_weights.pkl

🚀 Next Steps:
   1. Run train_v2.py to train Stage 1 (XGBoost + DNN)
   2. Run train_v2.py to train Stage 2 (Categorizer)
""")
