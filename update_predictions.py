import pandas as pd
import numpy as np
import sqlite3
import pickle
import shap
from train_model import preprocess_features

# -------------------------------
# 1. Load model
# -------------------------------
model_file = "models/risk_model_20250901_195429.pkl"  
with open(model_file, "rb") as f:
    risk_model = pickle.load(f)

regressors = risk_model["regressors"]
feature_cols = risk_model["feature_cols"]
target_cols = risk_model["target_cols"]
preprocess_fn = risk_model["preprocess"]

# -------------------------------
# 2. Load new dataset
# -------------------------------
df = pd.read_csv("trainingk.csv")

# -------------------------------
# 3. Preprocess features
# -------------------------------
df_proc = preprocess_fn(df.copy())

# -------------------------------
# 3a. Clean numeric features
# -------------------------------
# Replace "." or any string placeholders with NaN
df_proc = df_proc.replace('.', np.nan)

# Fill missing values in numeric features (here using 0)
df_proc[feature_cols] = df_proc[feature_cols].fillna(0)

# Ensure all features are numeric
df_proc[feature_cols] = df_proc[feature_cols].apply(pd.to_numeric, errors='coerce')

# -------------------------------
# 4. Run predictions for each target
# -------------------------------
for target in target_cols:
    df_proc[target] = regressors[target].predict(df_proc[feature_cols])

# -------------------------------
# 5. Assign risk label based on RISK_30D
# -------------------------------
def assign_label(score):
    if score < 20: return "Very Low"
    elif score < 40: return "Low"
    elif score < 60: return "Medium"
    elif score < 85: return "High"
    else: return "Very High"

df_proc["RISK_LABEL"] = df_proc["RISK_30D"].apply(assign_label)

# -------------------------------
# 6. SHAP explanations for top 3 features
# -------------------------------
model_30d = regressors["RISK_30D"].named_steps["rf"]
scaler_30d = regressors["RISK_30D"].named_steps["scaler"]
X_scaled = scaler_30d.transform(df_proc[feature_cols])

explainer = shap.TreeExplainer(model_30d)
shap_values = explainer.shap_values(X_scaled)

top_features = []
for i in range(len(df_proc)):
    contribs = dict(zip(feature_cols, shap_values[i]))
    sorted_feats = sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
    formatted = ", ".join([f for f, _ in sorted_feats])
    top_features.append(formatted)

df_proc["TOP_3_FEATURES"] = top_features

# -------------------------------
# 7. Remove rows where all columns are NULL
# -------------------------------
df_proc = df_proc.dropna(how='all')

# -------------------------------
# 8. Save updated dataset to SQLite
# -------------------------------
conn = sqlite3.connect("training.db")
df_proc.to_sql("risk_score", conn, if_exists="replace", index=False)
conn.close()

print("✅ Predictions and SHAP top features updated and saved to training.db")