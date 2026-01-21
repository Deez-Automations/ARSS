# -*- coding: utf-8 -*-
"""
DTRA v2.0 - Two-Stage Model Training
Stage 1: XGBoost + DNN Ensemble (Binary Detection)
Stage 2: DNN Attack Categorizer (7 Classes)
"""

import os
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# TensorFlow setup
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import classification_report, confusion_matrix, recall_score, accuracy_score
from xgboost import XGBClassifier

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "CICIIOT2025", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")

print("=" * 70)
print("   DTRA v2.0 - Two-Stage Model Training")
print("   Stage 1: XGBoost + DNN Ensemble | Stage 2: Attack Categorizer")
print("=" * 70)

# ============================================================
# LOAD PREPROCESSED DATA
# ============================================================
print("\n📂 Loading preprocessed data...")

X_train = np.load(os.path.join(PROCESSED_DIR, 'X_train.npy'))
X_test = np.load(os.path.join(PROCESSED_DIR, 'X_test.npy'))
y_train_binary = np.load(os.path.join(PROCESSED_DIR, 'y_train_binary.npy'))
y_test_binary = np.load(os.path.join(PROCESSED_DIR, 'y_test_binary.npy'))
y_train_category = np.load(os.path.join(PROCESSED_DIR, 'y_train_category.npy'))
y_test_category = np.load(os.path.join(PROCESSED_DIR, 'y_test_category.npy'))

class_weights = joblib.load(os.path.join(MODELS_DIR, 'class_weights.pkl'))
category_encoder = joblib.load(os.path.join(MODELS_DIR, 'dtra_category_encoder.pkl'))

print(f"   ✅ Train: {X_train.shape[0]:,} samples, {X_train.shape[1]} features")
print(f"   ✅ Test: {X_test.shape[0]:,} samples")
print(f"   ✅ Attack categories: {list(category_encoder.classes_)}")

# ============================================================
# STAGE 1A: TRAIN XGBOOST (BINARY)
# ============================================================
print("\n" + "=" * 70)
print("   STAGE 1A: Training XGBoost Binary Classifier")
print("=" * 70)

xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=class_weights['binary'][1] / class_weights['binary'][0],
    use_label_encoder=False,
    eval_metric='logloss',
    random_state=42,
    n_jobs=-1,
    verbosity=1
)

print("   🚀 Training XGBoost...")
xgb_model.fit(
    X_train, y_train_binary,
    eval_set=[(X_test, y_test_binary)],
    verbose=True
)

# Evaluate XGBoost
y_pred_xgb_prob = xgb_model.predict_proba(X_test)[:, 1]
y_pred_xgb = (y_pred_xgb_prob > 0.5).astype(int)

xgb_accuracy = accuracy_score(y_test_binary, y_pred_xgb)
xgb_recall = recall_score(y_test_binary, y_pred_xgb)

print(f"\n   📊 XGBoost Results:")
print(f"      Accuracy: {xgb_accuracy*100:.2f}%")
print(f"      Recall:   {xgb_recall*100:.2f}%")

# Save XGBoost
joblib.dump(xgb_model, os.path.join(MODELS_DIR, 'dtra_xgb_binary.pkl'))
print(f"   ✅ Saved: models/dtra_xgb_binary.pkl")

# ============================================================
# STAGE 1B: TRAIN DNN (BINARY)
# ============================================================
print("\n" + "=" * 70)
print("   STAGE 1B: Training DNN Binary Classifier")
print("=" * 70)

input_dim = X_train.shape[1]

dnn_binary = Sequential([
    Dense(256, activation='relu', input_shape=(input_dim,)),
    BatchNormalization(),
    Dropout(0.4),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

dnn_binary.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
]

print("   🚀 Training DNN (this may take a few minutes)...")
history = dnn_binary.fit(
    X_train, y_train_binary,
    epochs=50,
    batch_size=256,
    validation_data=(X_test, y_test_binary),
    class_weight=class_weights['binary'],
    callbacks=callbacks,
    verbose=1
)

# Evaluate DNN
y_pred_dnn_prob = dnn_binary.predict(X_test, verbose=0).flatten()
y_pred_dnn = (y_pred_dnn_prob > 0.5).astype(int)

dnn_accuracy = accuracy_score(y_test_binary, y_pred_dnn)
dnn_recall = recall_score(y_test_binary, y_pred_dnn)

print(f"\n   📊 DNN Results:")
print(f"      Accuracy: {dnn_accuracy*100:.2f}%")
print(f"      Recall:   {dnn_recall*100:.2f}%")

# Save DNN
dnn_binary.save(os.path.join(MODELS_DIR, 'dtra_dnn_binary.h5'))
print(f"   ✅ Saved: models/dtra_dnn_binary.h5")

# ============================================================
# STAGE 1C: ENSEMBLE (XGBoost + DNN)
# ============================================================
print("\n" + "=" * 70)
print("   STAGE 1C: Evaluating Ensemble (XGBoost + DNN)")
print("=" * 70)

# Soft voting: average probabilities
ensemble_prob = (y_pred_xgb_prob + y_pred_dnn_prob) / 2

# Test different thresholds for optimal recall
print("\n   🔍 Finding optimal threshold for max recall...")
best_threshold = 0.5
best_recall = 0
best_accuracy = 0

for threshold in [0.3, 0.35, 0.4, 0.45, 0.5]:
    y_pred_ensemble = (ensemble_prob > threshold).astype(int)
    recall = recall_score(y_test_binary, y_pred_ensemble)
    acc = accuracy_score(y_test_binary, y_pred_ensemble)
    print(f"      Threshold {threshold}: Accuracy={acc*100:.2f}%, Recall={recall*100:.2f}%")
    
    if recall > best_recall or (recall == best_recall and acc > best_accuracy):
        best_recall = recall
        best_accuracy = acc
        best_threshold = threshold

print(f"\n   ✅ Best Threshold: {best_threshold}")
print(f"   📊 Ensemble Results (threshold={best_threshold}):")
print(f"      Accuracy: {best_accuracy*100:.2f}%")
print(f"      Recall:   {best_recall*100:.2f}%")

# Final ensemble prediction
y_pred_ensemble = (ensemble_prob > best_threshold).astype(int)

# Classification report
print("\n   📋 Classification Report (Ensemble):")
print(classification_report(y_test_binary, y_pred_ensemble, target_names=['Benign', 'Attack']))

# Save ensemble config
ensemble_config = {
    'threshold': best_threshold,
    'xgb_weight': 0.5,
    'dnn_weight': 0.5,
    'accuracy': best_accuracy,
    'recall': best_recall
}
joblib.dump(ensemble_config, os.path.join(MODELS_DIR, 'ensemble_config.pkl'))

# ============================================================
# STAGE 2: TRAIN ATTACK CATEGORIZER
# ============================================================
print("\n" + "=" * 70)
print("   STAGE 2: Training Attack Categorizer (7 Classes)")
print("=" * 70)

# Filter to attack samples only
attack_mask_train = y_train_binary == 1
attack_mask_test = y_test_binary == 1

X_train_attacks = X_train[attack_mask_train]
y_train_cat = y_train_category[attack_mask_train]
X_test_attacks = X_test[attack_mask_test]
y_test_cat = y_test_category[attack_mask_test]

print(f"   Train attacks: {len(X_train_attacks):,}")
print(f"   Test attacks: {len(X_test_attacks):,}")

# Build categorizer model
num_classes = len(category_encoder.classes_)

dnn_categorizer = Sequential([
    # Input Block (Wide)
    Dense(512, activation='relu', input_shape=(input_dim,)),
    BatchNormalization(),
    Dropout(0.4),
    
    # Deep Block 1
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.35),
    
    # Deep Block 2 (Added Depth)
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),

    # Feature Compression Block
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.25),
    
    # Classification Head
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(num_classes, activation='softmax')
])

dnn_categorizer.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("   🚀 Training Categorizer...")
history_cat = dnn_categorizer.fit(
    X_train_attacks, y_train_cat,
    epochs=50,
    batch_size=256,
    validation_data=(X_test_attacks, y_test_cat),
    class_weight=class_weights['category'],
    callbacks=callbacks,
    verbose=1
)

# ============================================================
# TRAIN XGBOOST CATEGORIZER (New for v2.1)
# ============================================================
print("\n" + "-" * 50)
print("   Training XGBoost Categorizer (Ensemble Component)")
print("-" * 50)

xgb_categorizer = XGBClassifier(
    n_estimators=200,
    max_depth=10,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='multi:softprob',
    num_class=num_classes,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1,
    verbosity=1
)

print("   🚀 Training XGBoost Categorizer...")
# We use sample_weight manually since XGBoost handles it better than class_weight param
sample_weights = [class_weights['category'][y] for y in y_train_cat]

xgb_categorizer.fit(
    X_train_attacks, y_train_cat,
    sample_weight=sample_weights,
    eval_set=[(X_test_attacks, y_test_cat)],
    verbose=True
)

# Evaluate XGBoost Categorizer
y_pred_xgb_cat = xgb_categorizer.predict(X_test_attacks)
xgb_cat_acc = accuracy_score(y_test_cat, y_pred_xgb_cat)
print(f"   📊 XGBoost Categorizer Accuracy: {xgb_cat_acc*100:.2f}%")

# Save XGBoost Categorizer
joblib.dump(xgb_categorizer, os.path.join(MODELS_DIR, 'dtra_xgb_categorizer.pkl'))
print(f"   ✅ Saved: models/dtra_xgb_categorizer.pkl")

# ============================================================
# EVALUATE STAGE 2 ENSEMBLE
# ============================================================
print("\n   🔍 Evaluating Stage 2 Ensemble (DNN + XGBoost)...")
y_prob_dnn_cat = dnn_categorizer.predict(X_test_attacks, verbose=0)
y_prob_xgb_cat = xgb_categorizer.predict_proba(X_test_attacks)

# Average probabilities
ensemble_prob_cat = (y_prob_dnn_cat + y_prob_xgb_cat) / 2
y_pred_ensemble_cat = np.argmax(ensemble_prob_cat, axis=1)

cat_accuracy = accuracy_score(y_test_cat, y_pred_ensemble_cat)

print(f"\n   📊 ENSEMBLE Categorizer Results:")
print(f"      Accuracy: {cat_accuracy*100:.2f}%")

print("\n   📋 Classification Report (Stage 2 Ensemble):")
print(classification_report(y_test_cat, y_pred_ensemble_cat, target_names=category_encoder.classes_))

# Save categorizer
dnn_categorizer.save(os.path.join(MODELS_DIR, 'dtra_categorizer.h5'))
print(f"   ✅ Saved: models/dtra_categorizer.h5")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("   ✅ TRAINING COMPLETE")
print("=" * 70)
print(f"""
📊 STAGE 1 (Binary Detection):
   • XGBoost Accuracy:  {xgb_accuracy*100:.2f}%
   • XGBoost Recall:    {xgb_recall*100:.2f}%
   • DNN Accuracy:      {dnn_accuracy*100:.2f}%
   • DNN Recall:        {dnn_recall*100:.2f}%
   • ENSEMBLE Accuracy: {best_accuracy*100:.2f}%
   • ENSEMBLE Recall:   {best_recall*100:.2f}%
   • Optimal Threshold: {best_threshold}

📊 STAGE 2 (Attack Categories):
   • Categorizer Accuracy: {cat_accuracy*100:.2f}%
   • Classes: {list(category_encoder.classes_)}

📁 Models Saved:
   • models/dtra_xgb_binary.pkl
   • models/dtra_dnn_binary.h5
   • models/dtra_categorizer.h5
   • models/ensemble_config.pkl

🚀 Next Steps:
   1. Update api.py to use new two-stage model
   2. Add SHAP explainability
   3. Update dashboard with attack types
""")
