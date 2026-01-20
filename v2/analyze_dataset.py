# Analyze CIC IIoT 2025 Dataset
import pandas as pd
import os

# Path to dataset
dataset_path = r"d:\GIKI\CS 351\DTRA\CICIIOT2025\combined_dataset.csv"

print("=" * 60)
print("   CIC IIoT 2025 Dataset Analysis")
print("=" * 60)

# Read just the first few rows and all columns
print("\n📊 Loading dataset headers...")
df_sample = pd.read_csv(dataset_path, nrows=1000, low_memory=False)

print(f"\n✅ Sample loaded: {len(df_sample)} rows")
print(f"📋 Total Columns: {len(df_sample.columns)}")

# Show all column names
print("\n" + "-" * 60)
print("COLUMN NAMES:")
print("-" * 60)
for i, col in enumerate(df_sample.columns):
    print(f"  {i+1:2}. {col}")

# Check for label column
print("\n" + "-" * 60)
print("LABEL/TARGET COLUMN SEARCH:")
print("-" * 60)
label_candidates = [col for col in df_sample.columns if 'label' in col.lower() or 'attack' in col.lower() or 'class' in col.lower()]
print(f"Potential label columns: {label_candidates}")

# If we found a label column, show unique values
if label_candidates:
    label_col = label_candidates[0]
    print(f"\nUsing '{label_col}' as label column:")
    
    # Read more rows to get attack types
    df_labels = pd.read_csv(dataset_path, usecols=[label_col], low_memory=False)
    unique_labels = df_labels[label_col].unique()
    
    print(f"\n📊 ATTACK TYPES FOUND: {len(unique_labels)}")
    print("-" * 40)
    for label in sorted(unique_labels):
        count = (df_labels[label_col] == label).sum()
        print(f"  • {label}: {count:,} samples")
    
    print(f"\n📈 Total samples: {len(df_labels):,}")

# Data types
print("\n" + "-" * 60)
print("COLUMN DATA TYPES (first 20):")
print("-" * 60)
for col in df_sample.columns[:20]:
    print(f"  {col}: {df_sample[col].dtype}")

print("\n✅ Analysis complete!")
