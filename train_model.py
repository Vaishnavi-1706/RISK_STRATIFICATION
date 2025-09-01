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
    # Comorbidity count
    df["COMOR_COUNT"] = df[chronic_cols].sum(axis=1)
    return df


# -------------------------------
# 2. Training pipeline
# -------------------------------
def quick_train():
    print("🚀 Starting Risk Model Training...")
    print("="*50)

    # Load data
    df = pd.read_csv("risk_training.csv")
    df = preprocess_features(df)
    print(f"📊 Dataset loaded: {df.shape}")

    # Features + targets
    target_cols = ["RISK_30D", "RISK_60D", "RISK_90D"]
    feature_cols = [
        "AGE", "TOTAL_CLAIMS_COST", "IN_ADM", "OUT_VISITS", "RX_ADH",
        "CLAIMS_FLAG", "COMOR_COUNT"
    ] + chronic_cols + [
        "BP_S", "GLUCOSE", "HbA1c", "CHOLESTEROL"
    ]

    X = df[feature_cols]
    y = df[target_cols]

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
                n_estimators=50,
                max_depth=4,
                min_samples_leaf=50,
                min_samples_split=20,
                max_features="log2",
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
    print(f"Average R²: {avg_r2:.3f}  (Target: 0.90–0.95)")
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

    risk_model = {
        "regressors": regressors,
        "feature_cols": feature_cols,
        "target_cols": target_cols,
        "preprocess": preprocess_features
    }

    with open(model_path, "wb") as f:
        pickle.dump(risk_model, f)
    feature_importance.to_csv(importance_path, index=False)

    print(f"\n💾 Model saved: {model_path}")
    print(f"   Features saved: {importance_path}")
    print("="*50)

    return risk_model, avg_r2, metrics, feature_importance


if __name__ == "__main__":
    model, score, metrics, feats = quick_train()