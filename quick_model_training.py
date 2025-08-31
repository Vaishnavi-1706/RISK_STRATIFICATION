#!/usr/bin/env python3
"""
Quick Model Training - Fast and Efficient
Healthcare Risk Stratification
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def quick_train():
    print("🚀 Starting Quick Model Training...")
    print("="*50)
    
    # Load data
    print("📊 Loading dataset...")
    df = pd.read_csv('index.csv')
    print(f"Dataset loaded: {df.shape}")
    
    # Prepare features and targets
    feature_columns = [col for col in df.columns if col not in ['DESYNPUF_ID', 'RISK_30D', 'RISK_60D', 'RISK_90D', 'RISK_LABEL']]
    
    X = df[feature_columns].copy()
    y_30d = df['RISK_30D']
    y_60d = df['RISK_60D']
    y_90d = df['RISK_90D']
    
    # Handle missing values
    X = X.fillna(X.median())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Combine targets
    y_combined = np.column_stack([y_30d, y_60d, y_90d])
    
    print(f"Features: {X_scaled.shape}, Targets: {y_combined.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_combined, test_size=0.2, random_state=42)
    
    # Train XGBoost model with optimized parameters
    print("🤖 Training XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=7,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.1,
        reg_lambda=0.1,
        random_state=42,
        n_jobs=-1
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    target_names = ['RISK_30D', 'RISK_60D', 'RISK_90D']
    metrics = {}
    
    for i, target in enumerate(target_names):
        mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
        mse = mean_squared_error(y_test[:, i], y_pred[:, i])
        r2 = r2_score(y_test[:, i], y_pred[:, i])
        
        metrics[target] = {
            'MAE': mae,
            'MSE': mse,
            'R2': r2
        }
    
    # Average R2 score
    avg_r2 = np.mean([metrics[target]['R2'] for target in target_names])
    
    # Print results
    print("\n" + "="*50)
    print("📊 TRAINING RESULTS")
    print("="*50)
    print(f"🏆 Model: XGBoost")
    print(f"📈 Average R² Score: {avg_r2:.4f}")
    print(f"🎯 Target Accuracy: ~95% (R² = 0.95)")
    print(f"✅ Achieved Accuracy: {avg_r2*100:.2f}%")
    
    print(f"\n📋 DETAILED METRICS:")
    for target, metric in metrics.items():
        print(f"{target}:")
        print(f"  MAE: {metric['MAE']:.3f}")
        print(f"  MSE: {metric['MSE']:.3f}")
        print(f"  R²:  {metric['R2']:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🔍 TOP 10 FEATURES:")
    for i, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:20s}: {row['importance']:.4f}")
    
    # Save model
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('models', exist_ok=True)
    
    model_path = f'models/best_risk_model_{timestamp}.pkl'
    scaler_path = f'models/scaler_{timestamp}.pkl'
    importance_path = f'models/feature_importance_{timestamp}.csv'
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    feature_importance.to_csv(importance_path, index=False)
    
    print(f"\n💾 Model saved successfully!")
    print(f"   Model: {model_path}")
    print(f"   Scaler: {scaler_path}")
    print(f"   Features: {importance_path}")
    
    # Final assessment
    if avg_r2 >= 0.95:
        print("🎉 EXCELLENT! Target accuracy achieved!")
    elif avg_r2 >= 0.90:
        print("✅ GREAT! Excellent accuracy achieved!")
    elif avg_r2 >= 0.85:
        print("✅ GOOD! Good accuracy achieved!")
    else:
        print("⚠️ ACCEPTABLE accuracy achieved")
    
    print("\n" + "="*50)
    print("🎯 TRAINING COMPLETED!")
    print("="*50)
    
    return model, scaler, avg_r2, metrics

if __name__ == "__main__":
    model, scaler, score, metrics = quick_train()
