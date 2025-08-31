#!/usr/bin/env python3
"""
Quick Patient Readmission Risk Prediction Model
Healthcare Risk Stratification - Fast and Accurate
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import xgboost as xgb
import warnings
import joblib
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

def main():
    """Main training function"""
    logger.info("🚀 Starting Quick Readmission Risk Prediction Model Training")
    logger.info("="*80)
    
    # Load dataset
    logger.info("Loading dataset...")
    df = pd.read_csv('index.csv')
    logger.info(f"Dataset loaded: {df.shape}")
    
    # Create readmission target based on risk scores
    df['READMISSION_RISK'] = (df['RISK_30D'] >= 60).astype(int)
    
    # Separate features and target
    feature_columns = [col for col in df.columns if col not in [
        'DESYNPUF_ID', 'RISK_30D', 'RISK_60D', 'RISK_90D', 'RISK_LABEL', 
        'TOP_3_FEATURES', 'AI_RECOMMENDATIONS', 'EMAIL', 'SHAP_EXPLANATION',
        'READMISSION_RISK'
    ]]
    
    X = df[feature_columns].copy()
    y = df['READMISSION_RISK']
    
    # Handle missing values
    X = X.fillna(X.median())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    logger.info(f"Features shape: {X_scaled.shape}")
    logger.info(f"Target distribution: {y.value_counts()}")
    logger.info(f"Readmission rate: {y.mean():.2%}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train XGBoost with optimized parameters
    logger.info("Training XGBoost model...")
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=7,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.1,
        reg_lambda=0.1,
        random_state=42,
        eval_metric='logloss',
        n_jobs=-1
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    auc = roc_auc_score(y_test, y_prob)
    
    # Cross-validation score
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
    avg_cv_score = cv_scores.mean()
    
    logger.info("\n" + "="*80)
    logger.info("PERFORMANCE RESULTS")
    logger.info("="*80)
    logger.info(f"Test Accuracy: {accuracy:.4f}")
    logger.info(f"Cross-Validation Accuracy: {avg_cv_score:.4f}")
    logger.info(f"Precision: {precision:.4f}")
    logger.info(f"Recall: {recall:.4f}")
    logger.info(f"F1-Score: {f1:.4f}")
    logger.info(f"AUC-ROC: {auc:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"\n📊 CONFUSION MATRIX:")
    logger.info(f"True Negatives: {cm[0,0]}")
    logger.info(f"False Positives: {cm[0,1]}")
    logger.info(f"False Negatives: {cm[1,0]}")
    logger.info(f"True Positives: {cm[1,1]}")
    
    # Classification Report
    logger.info(f"\n📋 CLASSIFICATION REPORT:")
    report = classification_report(y_test, y_pred, 
                                 target_names=['No Readmission', 'Readmission'])
    logger.info(report)
    
    # Feature Importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    logger.info(f"\n🔍 TOP 15 FEATURES:")
    for i, row in feature_importance.head(15).iterrows():
        logger.info(f"  {row['feature']:25s}: {row['importance']:.4f}")
    
    # Save model and results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('models', exist_ok=True)
    
    # Save model
    model_path = f'models/readmission_model_{timestamp}.pkl'
    joblib.dump(model, model_path)
    
    # Save scaler
    scaler_path = f'models/readmission_scaler_{timestamp}.pkl'
    joblib.dump(scaler, scaler_path)
    
    # Save feature importance
    importance_path = f'models/readmission_feature_importance_{timestamp}.csv'
    feature_importance.to_csv(importance_path, index=False)
    
    # Save results summary
    results_summary = {
        'Model': 'XGBoost',
        'Test_Accuracy': accuracy,
        'CV_Accuracy': avg_cv_score,
        'Precision': precision,
        'Recall': recall,
        'F1_Score': f1,
        'AUC_ROC': auc,
        'Timestamp': timestamp,
        'Model_Path': model_path,
        'Scaler_Path': scaler_path
    }
    
    results_path = f'models/readmission_results_{timestamp}.txt'
    with open(results_path, 'w') as f:
        f.write("READMISSION PREDICTION MODEL RESULTS\n")
        f.write("="*50 + "\n\n")
        for key, value in results_summary.items():
            f.write(f"{key}: {value}\n")
    
    logger.info("\n" + "="*80)
    logger.info("🎉 TRAINING COMPLETED SUCCESSFULLY!")
    logger.info("="*80)
    
    # Final summary
    logger.info(f"📊 Final Results:")
    logger.info(f"   Model: XGBoost")
    logger.info(f"   Test Accuracy: {accuracy:.4f}")
    logger.info(f"   Target Accuracy: 95%")
    logger.info(f"   Achieved Accuracy: {accuracy*100:.2f}%")
    
    if accuracy >= 0.95:
        logger.info("✅ Target accuracy achieved!")
    elif accuracy >= 0.90:
        logger.info("✅ Excellent accuracy achieved!")
    elif accuracy >= 0.85:
        logger.info("✅ Good accuracy achieved!")
    else:
        logger.info("⚠️ Accuracy can be improved with more training")
    
    logger.info(f"\n📁 Files saved:")
    logger.info(f"   Model: {model_path}")
    logger.info(f"   Scaler: {scaler_path}")
    logger.info(f"   Feature Importance: {importance_path}")
    logger.info(f"   Results: {results_path}")
    
    return model, scaler, feature_importance, results_summary

if __name__ == "__main__":
    model, scaler, feature_importance, results = main()
