import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, confusion_matrix, classification_report
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import shap
import joblib
import os
import pickle
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# -------------------------------
# 1. Preprocessing function
# -------------------------------
chronic_cols = [
    "ALZHEIMER", "HEARTFAILURE", "CANCER", "PULMONARY",
    "OSTEOPOROSIS", "RHEUMATOID", "STROKE", "RENAL_DISEASE"
]

def preprocess_features(df):
    df = df.copy()
    # Claims flag
    df["CLAIMS_FLAG"] = (df["TOTAL_CLAIMS_COST"].fillna(0) > 0).astype(int)
    
    # Disease weightage system (instead of simple count)
    # Each disease gets a specific weight based on severity/risk impact
    disease_weights = {
        'HEARTFAILURE': 3.0,    # Highest risk - heart failure
        'STROKE': 2.8,          # Very high risk - stroke
        'CANCER': 2.5,          # High risk - cancer
        'RENAL_DISEASE': 2.3,   # High risk - kidney disease
        'PULMONARY': 2.0,       # Moderate-high risk - lung disease
        'ALZHEIMER': 1.8,       # Moderate risk - dementia
        'RHEUMATOID': 1.5,      # Moderate risk - arthritis
        'OSTEOPOROSIS': 1.2     # Lower risk - bone disease
    }
    
    # Calculate weighted comorbidity score instead of simple count
    df["COMOR_WEIGHTED_SCORE"] = 0
    for disease, weight in disease_weights.items():
        if disease in df.columns:
            df["COMOR_WEIGHTED_SCORE"] += df[disease] * weight
    
    # Keep the original count for backward compatibility
    df["COMOR_COUNT"] = df[chronic_cols].sum(axis=1)
    
    return df


# -------------------------------
# 2. Training pipeline
# -------------------------------
def quick_train():
    print("🚀 Starting Risk Model Training...")
    print("="*50)

    # Load data
    df = pd.read_csv("trainingk.csv")
    df = preprocess_features(df)
    print(f"📊 Dataset loaded: {df.shape}")
    
    # Clean data - remove rows with missing target values
    target_cols = ["RISK_30D", "RISK_60D", "RISK_90D"]
    initial_rows = len(df)
    df = df.dropna(subset=target_cols)
    print(f"🧹 Data cleaning: Removed {initial_rows - len(df)} rows with missing target values")
    print(f"📊 Clean dataset: {df.shape}")

    # Features + targets
    target_cols = ["RISK_30D", "RISK_60D", "RISK_90D"]
    
    # Use ALL available features from the CSV (excluding ID, targets, and non-numeric columns)
    exclude_cols = [
        "DESYNPUF_ID", "RISK_30D", "RISK_60D", "RISK_90D", "RISK_LABEL", 
        "EMAIL", "TOP_3_FEATURES", "AI_RECOMMENDATIONS", "INDEX_DATE"
    ]
    
    # Get all numeric columns that are not in exclude list
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    # Replace COMOR_COUNT with COMOR_WEIGHTED_SCORE for better predictions
    if 'COMOR_COUNT' in feature_cols and 'COMOR_WEIGHTED_SCORE' in feature_cols:
        feature_cols.remove('COMOR_COUNT')  # Remove simple count
        print("✅ Using weighted disease score instead of simple count")
    elif 'COMOR_WEIGHTED_SCORE' in feature_cols:
        print("✅ Using weighted disease score for predictions")
    
    print(f"🔍 Using {len(feature_cols)} features:")
    for i, col in enumerate(feature_cols, 1):
        print(f"  {i:2d}. {col}")
    
    # Use ALL available features - no limitations
    print(f"✅ Using ALL {len(feature_cols)} available features for training")
    print("🎯 Model will be trained with complete feature set for maximum accuracy")

    # Handle missing values in features
    X = df[feature_cols].fillna(0)  # Fill missing values with 0
    y = df[target_cols]
    
    print(f"🔍 Feature matrix shape: {X.shape}")
    print(f"🔍 Target matrix shape: {y.shape}")
    
    # Check for any remaining NaN values
    if X.isnull().any().any():
        print("⚠️  Warning: Still have NaN values in features, filling with 0")
        X = X.fillna(0)
    
    if y.isnull().any().any():
        print("⚠️  Warning: Still have NaN values in targets, removing those rows")
        valid_mask = ~y.isnull().any(axis=1)
        X = X[valid_mask]
        y = y[valid_mask]
        print(f"🔍 Final clean dataset: {X.shape[0]} rows")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Train one regressor per target
    regressors = {}
    metrics = {}
    for col in target_cols:
        reg = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(
                n_estimators=100,  # Increased for better performance with more features
                max_depth=8,       # Increased depth for more complex patterns
                min_samples_leaf=20,  # Reduced for more sensitivity
                min_samples_split=10, # Reduced for more sensitivity
                max_features="sqrt",  # Better for larger feature sets
                random_state=42
            ))
        ])
        reg.fit(X_train, y_train[col])
        regressors[col] = reg

        # Eval
        preds = reg.predict(X_test)
        mae = mean_absolute_error(y_test[col], preds)
        mse = mean_squared_error(y_test[col], preds)
        r2 = r2_score(y_test[col], preds)
        metrics[col] = {"MAE": mae, "MSE": mse, "R2": r2}

    avg_r2 = np.mean([m["R2"] for m in metrics.values()])

    # Print metrics
    print("\n📊 TRAINING RESULTS")
    print("="*50)
    print(f"Average R²: {avg_r2:.3f}  (Target: 0.70+ for comprehensive model)")
    for col, m in metrics.items():
        print(f"{col} → MAE: {m['MAE']:.3f}, R²: {m['R2']:.3f}")

    # -------------------------------
    # 3. SHAP feature importance
    # -------------------------------
    model_30d = regressors["RISK_30D"].named_steps["rf"]
    X_transformed = regressors["RISK_30D"].named_steps["scaler"].transform(X_test)

    explainer = shap.TreeExplainer(model_30d)
    shap_values = explainer.shap_values(X_transformed)

    feature_importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": np.abs(shap_values).mean(axis=0)
    }).sort_values("importance", ascending=False)

    print("\n🔍 TOP 10 FEATURES (SHAP):")
    for i, row in feature_importance.head(10).iterrows():
        print(f"{row['feature']:20s}: {row['importance']:.4f}")

    # -------------------------------
    # 4. Classification Report (30D label)
    # -------------------------------
    def assign_label(score):
        if score < 20: return "Very Low"
        elif score < 40: return "Low"
        elif score < 60: return "Medium"
        elif score < 85: return "High"
        else: return "Very High"

    y_true_labels = y_test["RISK_30D"].apply(assign_label)
    y_pred_labels = pd.Series(regressors["RISK_30D"].predict(X_test)).apply(assign_label)

    labels = ["Very Low", "Low", "Medium", "High", "Very High"]
    cm = confusion_matrix(y_true_labels, y_pred_labels, labels=labels)

    print("\nConfusion Matrix:\n", cm)
    print("\nClassification Report:\n")
    print(classification_report(y_true_labels, y_pred_labels, target_names=labels))

    # -------------------------------
    # 5. Save model
    # -------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("models", exist_ok=True)

    model_path = f"models/risk_model_{timestamp}.pkl"
    importance_path = f"models/feature_importance_{timestamp}.csv"

    # Save in the format expected by the app (simple regressors dict)
    with open(model_path, "wb") as f:
        pickle.dump(regressors, f)
    
    # Also save the comprehensive model info separately
    comprehensive_model = {
        "regressors": regressors,
        "feature_cols": feature_cols,
        "target_cols": target_cols,
        "preprocess": preprocess_features
    }
    
    comprehensive_path = f"models/risk_model_comprehensive_{timestamp}.pkl"
    with open(comprehensive_path, "wb") as f:
        pickle.dump(comprehensive_model, f)
    feature_importance.to_csv(importance_path, index=False)

    print(f"\n💾 Models saved:")
    print(f"   App-compatible: {model_path}")
    print(f"   Comprehensive: {comprehensive_path}")
    print(f"   Features: {importance_path}")
    print("="*50)

    return comprehensive_model, avg_r2, metrics, feature_importance


if __name__ == "__main__":
    model, score, metrics, feats = quick_train()