# -*- coding: utf-8 -*-
"""
DTRA v2.0 - Explainable AI Module
Uses SHAP (SHapley Additive exPlanations) to provide real-time insights 
into why a specific packet was flagged as a threat.
"""

import os
import shap
import joblib
import pandas as pd
import numpy as np
import config

class DTRAExplainer:
    def __init__(self):
        """
        Initializes the SHAP explainer using the trained Stage 1 XGBoost model.
        We use XGBoost for explanations because TreeExplainer is fast and optimized for real-time APIs.
        """
        print("   🧠 Initializing DTRA Explainer...")
        
        # Load the binary XGBoost model (Stage 1)
        if not os.path.exists(config.XGB_MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {config.XGB_MODEL_PATH}")
            
        self.model = joblib.load(config.XGB_MODEL_PATH)
        
        # Initialize TreeExplainer (optimized for XGBoost)
        # feature_perturbation='interventional' is more robust but requires background data.
        # 'tree_path_dependent' is faster and standard for trees.
        self.explainer = shap.TreeExplainer(self.model)
        
        print("   ✅ SHAP Explainer ready.")

    def explain_packet(self, packet_data):
        """
        Generates a SHAP explanation for a single packet.
        
        Args:
            packet_data (dict or list): The processed feature vector of the packet.
            
        Returns:
            dict: JSON-serializable explanation data including:
                  - Base value (average model output)
                  - Influence of top contributing features
                  - Text description of the decision
        """
        # Ensure input is a DataFrame with correct feature names for SHAP
        if isinstance(packet_data, (list, np.ndarray)):
            df = pd.DataFrame([packet_data], columns=config.NUMERIC_FEATURES)
        elif isinstance(packet_data, dict):
             # Ensure order matches config
            df = pd.DataFrame([packet_data], columns=config.NUMERIC_FEATURES)
        else:
            df = packet_data

        # Calculate SHAP values
        shap_values = self.explainer(df)
        
        # Extract values for the first (and only) instance
        # shap_values is an Explanation object
        base_value = float(shap_values.base_values[0])
        values = shap_values.values[0]
        
        # Map features to their SHAP impact
        feature_impact = list(zip(config.NUMERIC_FEATURES, values))
        
        # Sort by absolute impact (magnitude of contribution)
        # Positive SHAP = pushes towards "Attack" (1)
        # Negative SHAP = pushes towards "Benign" (0)
        feature_impact.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Get top 5 contributors
        top_contributors = []
        for feature, impact in feature_impact[:5]:
            description = "Increases Threat Risk" if impact > 0 else "Lowers Threat Risk"
            top_contributors.append({
                "feature": feature,
                "impact": float(impact),  # Convert numpy float to python float
                "description": description,
                "value": float(df.iloc[0][feature]) # The actual feature value
            })

        return {
            "base_value": base_value,
            "prediction_score": float(np.sum(values) + base_value), # Log-odds score usually
            "top_features": top_contributors
        }

if __name__ == "__main__":
    # Tiny test
    explainer = DTRAExplainer()
    dummy_packet = np.random.rand(1, config.INPUT_DIM)
    explanation = explainer.explain_packet(dummy_packet[0])
    print("\nTest Explanation Output:")
    print(explanation)
