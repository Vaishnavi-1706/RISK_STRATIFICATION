
# SHAP Analysis Utilities
import shap
import joblib
import numpy as np
import pandas as pd

def load_shap_explainer():
    """Load the SHAP explainer"""
    try:
        explainer_path = 'models/shap_explainer_20250831_193236.pkl'
        return joblib.load(explainer_path)
    except:
        return None

def get_patient_shap_explanation(patient_data, feature_columns, scaler, explainer):
    """Get SHAP explanation for a specific patient"""
    try:
        # Prepare patient data
        patient_features = patient_data[feature_columns].values.reshape(1, -1)
        patient_features = np.nan_to_num(patient_features, nan=np.nanmedian(patient_features))
        patient_scaled = scaler.transform(patient_features)
        
        # Get SHAP values
        patient_shap = explainer.shap_values(patient_scaled)
        
        # Handle multi-output model
        if isinstance(patient_shap, list):
            patient_shap_30d = patient_shap[0][0]  # First output, first patient
        elif len(np.array(patient_shap).shape) == 3:
            patient_shap_30d = np.array(patient_shap)[0, :, 0]  # First patient, all features, first target
        else:
            patient_shap_30d = patient_shap[0]  # First patient
        
        # Get top contributing features
        feature_contributions = []
        for i, feature in enumerate(feature_columns):
            if i < len(patient_shap_30d):
                contribution = patient_shap_30d[i]
                feature_contributions.append({
                    'feature': feature,
                    'contribution': contribution,
                    'abs_contribution': abs(contribution)
                })
        
        # Sort by absolute contribution
        feature_contributions.sort(key=lambda x: x['abs_contribution'], reverse=True)
        
        # Format explanation
        explanations = []
        for contrib in feature_contributions[:3]:
            direction = "increases" if contrib['contribution'] > 0 else "decreases"
            explanations.append(f"{contrib['feature']} ({direction} risk by {abs(contrib['contribution']):.2f})")
        
        return " | ".join(explanations)
        
    except Exception as e:
        return f"SHAP analysis error: {str(e)}"

def get_global_shap_importance():
    """Get global SHAP feature importance"""
    try:
        importance_path = 'models/shap_importance_20250831_193236.csv'
        return pd.read_csv(importance_path)
    except:
        return None

def create_shap_summary_plot(explainer, X_sample, feature_names):
    """Create SHAP summary plot"""
    try:
        shap_values = explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]  # Use first output
        elif len(np.array(shap_values).shape) == 3:
            shap_values = np.array(shap_values)[:, :, 0]  # Use first target
        
        # Create summary plot
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False)
        return True
    except Exception as e:
        print(f"Error creating SHAP summary plot: {str(e)}")
        return False
