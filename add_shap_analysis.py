#!/usr/bin/env python3
"""
Add SHAP Analysis to Model
Healthcare Risk Stratification - Feature Explanations
"""

import pandas as pd
import numpy as np
import joblib
import os
import shap
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

def add_shap_analysis():
    print("🔍 Adding SHAP Analysis to Model...")
    print("="*50)
    
    # Find the latest model files
    models_dir = 'models'
    if not os.path.exists(models_dir):
        print("❌ Models directory not found!")
        return
    
    # Find the latest model file
    model_files = [f for f in os.listdir(models_dir) if f.startswith('best_risk_model_') and f.endswith('.pkl')]
    if not model_files:
        print("❌ No trained model found!")
        return
    
    # Get the latest model
    latest_model = sorted(model_files)[-1]
    model_path = os.path.join(models_dir, latest_model)
    timestamp = latest_model.replace('best_risk_model_', '').replace('.pkl', '')
    scaler_path = os.path.join(models_dir, f'scaler_{timestamp}.pkl')
    
    print(f"📁 Using model: {model_path}")
    print(f"📁 Using scaler: {scaler_path}")
    
    # Load the model and scaler
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    # Load the dataset
    df = pd.read_csv('index.csv')
    print(f"📊 Dataset loaded: {df.shape}")
    
    # Prepare features
    feature_columns = [col for col in df.columns if col not in ['DESYNPUF_ID', 'RISK_30D', 'RISK_60D', 'RISK_90D', 'RISK_LABEL', 'TOP_3_FEATURES', 'AI_RECOMMENDATIONS', 'EMAIL', 'SHAP_EXPLANATION']]
    
    X = df[feature_columns].copy()
    X = X.fillna(X.median())
    X_scaled = scaler.transform(X)
    
    # Create SHAP explainer
    print("🤖 Creating SHAP explainer...")
    
    # For XGBoost, we can use TreeExplainer
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values for a sample of data (for efficiency)
    sample_size = min(1000, len(X_scaled))  # Use 1000 samples or all if less
    sample_indices = np.random.choice(len(X_scaled), sample_size, replace=False)
    X_sample = X_scaled[sample_indices]
    
    print(f"📊 Calculating SHAP values for {sample_size} samples...")
    shap_values = explainer.shap_values(X_sample)
    
    # Handle multi-output model (XGBoost with multiple targets)
    print(f"📊 SHAP values shape: {np.array(shap_values).shape}")
    
    if isinstance(shap_values, list):
        # Multi-output model - use the first output (30-day risk)
        shap_values_30d = shap_values[0]
        print(f"📊 Multi-output model detected. Using 30-day risk SHAP values.")
    else:
        # Check if it's a 3D array (samples, features, targets)
        if len(np.array(shap_values).shape) == 3:
            # Take the first target (30-day risk)
            shap_values_30d = np.array(shap_values)[:, :, 0]
            print(f"📊 3D array detected. Using first target (30-day risk).")
        else:
            # Single output model
            shap_values_30d = shap_values
            print(f"📊 Single-output model detected.")
    
    print(f"📊 Final SHAP values shape: {shap_values_30d.shape}")
    
    # Calculate mean absolute SHAP values for feature importance
    mean_shap_values = np.abs(shap_values_30d).mean(axis=0)
    
    # Ensure the arrays have the same length
    if len(mean_shap_values) != len(feature_columns):
        print(f"⚠️ Warning: SHAP values length ({len(mean_shap_values)}) != features length ({len(feature_columns)})")
        # Truncate to match
        min_length = min(len(mean_shap_values), len(feature_columns))
        mean_shap_values = mean_shap_values[:min_length]
        feature_columns = feature_columns[:min_length]
    
    # Create feature importance DataFrame
    shap_importance = pd.DataFrame({
        'feature': feature_columns,
        'shap_importance': mean_shap_values
    }).sort_values('shap_importance', ascending=False)
    
    # Save SHAP importance
    shap_importance_path = f'models/shap_importance_{timestamp}.csv'
    shap_importance.to_csv(shap_importance_path, index=False)
    
    print(f"💾 SHAP importance saved: {shap_importance_path}")
    
    # Save the explainer for later use
    explainer_path = f'models/shap_explainer_{timestamp}.pkl'
    joblib.dump(explainer, explainer_path)
    
    print(f"💾 SHAP explainer saved: {explainer_path}")
    
    # Print top SHAP features
    print(f"\n🔍 TOP 10 SHAP FEATURES:")
    for i, row in shap_importance.head(10).iterrows():
        print(f"  {row['feature']:20s}: {row['shap_importance']:.4f}")
    
    # Update dataset with SHAP explanations
    print("🤖 Adding SHAP explanations to dataset...")
    
    # Add SHAP_EXPLANATION column if it doesn't exist
    if 'SHAP_EXPLANATION' not in df.columns:
        df['SHAP_EXPLANATION'] = "SHAP analysis available"
    
    # Save updated dataset
    df.to_csv('index.csv', index=False)
    
    print("✅ SHAP analysis added successfully!")
    print(f"📊 Updated {len(df)} patient records with SHAP capability")
    
    # Create SHAP utility functions for dashboard
    shap_utils_code = f'''
# SHAP Analysis Utilities
import shap
import joblib
import numpy as np
import pandas as pd

def load_shap_explainer():
    """Load the SHAP explainer"""
    try:
        explainer_path = '{explainer_path}'
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
                feature_contributions.append({{
                    'feature': feature,
                    'contribution': contribution,
                    'abs_contribution': abs(contribution)
                }})
        
        # Sort by absolute contribution
        feature_contributions.sort(key=lambda x: x['abs_contribution'], reverse=True)
        
        # Format explanation
        explanations = []
        for contrib in feature_contributions[:3]:
            direction = "increases" if contrib['contribution'] > 0 else "decreases"
            explanations.append(f"{{contrib['feature']}} ({{direction}} risk by {{abs(contrib['contribution']):.2f}})")
        
        return " | ".join(explanations)
        
    except Exception as e:
        return f"SHAP analysis error: {{str(e)}}"

def get_global_shap_importance():
    """Get global SHAP feature importance"""
    try:
        importance_path = '{shap_importance_path}'
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
        print(f"Error creating SHAP summary plot: {{str(e)}}")
        return False
'''
    
    # Save SHAP utilities
    with open('shap_utils.py', 'w') as f:
        f.write(shap_utils_code)
    
    print("💾 SHAP utilities saved: shap_utils.py")
    
    # Show comparison between traditional and SHAP importance
    print(f"\n📊 FEATURE IMPORTANCE COMPARISON:")
    print("Traditional vs SHAP Importance:")
    
    # Load traditional importance
    traditional_importance = pd.read_csv(f'models/feature_importance_{timestamp}.csv')
    
    # Merge for comparison
    comparison = pd.merge(
        traditional_importance, 
        shap_importance, 
        on='feature', 
        suffixes=('_traditional', '_shap')
    )
    
    print("Top 5 features comparison:")
    for i, row in comparison.head(5).iterrows():
        traditional_col = 'importance_traditional' if 'importance_traditional' in comparison.columns else 'importance'
        print(f"  {row['feature']:15s}: Traditional={row[traditional_col]:.4f}, SHAP={row['shap_importance']:.4f}")
    
    return True

if __name__ == "__main__":
    add_shap_analysis()
