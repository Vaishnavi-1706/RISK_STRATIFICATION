import pandas as pd
"""
chronic_cols = [
    "ALZHEIMER","HEARTFAILURE","CANCER","PULMONARY",
    "OSTEOPOROSIS","RHEUMATOID","STROKE","RENAL_DISEASE"
]

def preprocess_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Claims flag
    df["CLAIMS_FLAG"] = (df["TOTAL_CLAIMS_COST"].fillna(0) > 0).astype(int)
    # Comorbidity count
    df["COMOR_COUNT"] = df[chronic_cols].sum(axis=1)
    return df

feature_cols = [
    "AGE", "TOTAL_CLAIMS_COST", "IN_ADM", "OUT_VISITS", "RX_ADH",
    "CLAIMS_FLAG", "COMOR_COUNT"
] + chronic_cols + [
    "BP_S", "GLUCOSE", "HbA1c","CHOLESTEROL"
]

target_cols = ["RISK_30D", "RISK_60D", "RISK_90D"]

"""


chronic_cols = [
    "ALZHEIMER","HEARTFAILURE","CANCER","PULMONARY",
    "OSTEOPOROSIS","RHEUMATOID","STROKE","RENAL_DISEASE"
]

# Updated to match the 29 features used in the new model with weighted disease scoring
feature_cols = [
    "AGE", "GENDER", "RENAL_DISEASE", "PARTA", "PARTB", "HMO", "PARTD",
    "ALZHEIMER", "HEARTFAILURE", "CANCER", "PULMONARY", "OSTEOPOROSIS", 
    "RHEUMATOID", "STROKE", "BMI", "BP_S", "GLUCOSE", "HbA1c", "CHOLESTEROL",
    "RX_ADH", "BP_trend", "HbA1c_trend", "OUTPATIENT_COST", "ED_COST",
    "TOTAL_CLAIMS_COST", "COMOR_WEIGHTED_SCORE", "IN_ADM", "ED_VISITS", "CLAIMS_FLAG"
]

# Targets
target_cols = ["RISK_30D", "RISK_60D", "RISK_90D"]

def preprocess_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Ensure all column names are strings (fix for sklearn compatibility)
    df.columns = df.columns.astype(str)

    # Ensure all feature columns exist (fill missing with 0 where appropriate)
    for c in feature_cols:
        if c not in df: 
            if c in ["GENDER"]:  # Gender should be 0/1
                df[c] = 0
            elif c in ["PARTA", "PARTB", "HMO", "PARTD"]:  # Insurance parts
                df[c] = 0
            elif c in ["BMI", "BP_S", "GLUCOSE", "HbA1c", "CHOLESTEROL"]:  # Vitals
                df[c] = 0
            elif c in ["BP_trend", "HbA1c_trend"]:  # Trends
                df[c] = 0
            elif c in ["OUTPATIENT_COST", "ED_COST", "TOTAL_CLAIMS_COST"]:  # Costs
                df[c] = 0
            elif c in ["IN_ADM", "OUT_VISITS", "ED_VISITS", "COMOR_COUNT"]:  # Counts
                df[c] = 0
            elif c in ["RX_ADH"]:  # Adherence (0-1)
                df[c] = 0
            else:
                df[c] = 0

    # Claims flag
    df["TOTAL_CLAIMS_COST"] = pd.to_numeric(df["TOTAL_CLAIMS_COST"], errors="coerce").fillna(0)
    df["CLAIMS_FLAG"] = (df["TOTAL_CLAIMS_COST"] > 0).astype(int)

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

