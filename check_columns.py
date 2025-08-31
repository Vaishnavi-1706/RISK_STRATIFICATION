import pandas as pd

# Load the dataset
df = pd.read_csv('index.csv')
print("Current columns:", list(df.columns))
print("Shape:", df.shape)

# Check for missing columns
missing_cols = ['TOP_3_FEATURES', 'AI_RECOMMENDATIONS', 'EMAIL']
for col in missing_cols:
    if col in df.columns:
        print(f"{col}: Present")
    else:
        print(f"{col}: Missing")

# Add missing columns if needed
if 'TOP_3_FEATURES' not in df.columns:
    df['TOP_3_FEATURES'] = ''
    print("Added TOP_3_FEATURES column")

if 'AI_RECOMMENDATIONS' not in df.columns:
    df['AI_RECOMMENDATIONS'] = ''
    print("Added AI_RECOMMENDATIONS column")

if 'EMAIL' not in df.columns:
    df['EMAIL'] = ''
    print("Added EMAIL column")

# Save updated dataset
df.to_csv('index.csv', index=False)
print("Updated dataset saved!")
print("Final columns:", list(df.columns))
