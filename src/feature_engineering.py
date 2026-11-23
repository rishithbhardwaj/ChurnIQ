
"""
ChurnIQ - Feature Engineering

Purpose:
Prepare the cleaned customer churn dataset
for machine learning.
"""

import pandas as pd
from pathlib import Path

# Project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Processed dataset path
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "telco_customer_churn_cleaned.csv"
)

# Load cleaned dataset
df = pd.read_csv(INPUT_PATH)

print("\n========== CHURNIQ FEATURE ENGINEERING ==========")

print("\nDataset Shape:")
print(df.shape)

print("\nDataset Columns:")
print(df.columns.tolist())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nFirst Five Records:")
print(df.head())

print("\n========== DATA LOADING COMPLETED ==========")


print("\n========== FEATURE INSPECTION ==========")

print("\nColumn Data Types:")
print(df.dtypes)

print("\nUnique Values in Categorical Columns:")

categorical_columns = df.select_dtypes(
    include="object"
).columns

for column in categorical_columns:
    print(f"\n{column}:")
    print(df[column].unique())

print("\n========== INSPECTION COMPLETED ==========")


# ==========================================
# STEP 2: FEATURE ENGINEERING
# ==========================================

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

print("\n========== FEATURE ENGINEERING STARTED ==========")

# 1. Remove customer ID and separate target
X = df.drop(columns=["Churn", "customerID"])
y = df["Churn"].map({"No": 0, "Yes": 1})

# Validate target encoding
if y.isnull().any():
    raise ValueError("Unexpected values found in Churn column.")

print("\nTarget Distribution:")
print(y.value_counts())

# 2. Identify numerical and categorical columns
numerical_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

print("\nNumerical Features:")
print(numerical_features)

print("\nCategorical Features:")
print(categorical_features)

# 3. Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining Shape:", X_train.shape)
print("Testing Shape:", X_test.shape)

# 4. Create preprocessing pipelines
numerical_pipeline = Pipeline([
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("encoder", OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False
    ))
])

# 5. Combine numerical and categorical transformations
preprocessor = ColumnTransformer([
    ("num", numerical_pipeline, numerical_features),
    ("cat", categorical_pipeline, categorical_features)
])

# 6. Fit only on training data
X_train_processed = preprocessor.fit_transform(X_train)

# Transform test data without fitting again
X_test_processed = preprocessor.transform(X_test)

# 7. Get transformed feature names
feature_names = preprocessor.get_feature_names_out()

X_train_processed = pd.DataFrame(
    X_train_processed,
    columns=feature_names
)

X_test_processed = pd.DataFrame(
    X_test_processed,
    columns=feature_names
)

# 8. Save processed datasets and pipeline
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

X_train_processed.to_csv(
    OUTPUT_DIR / "X_train.csv", index=False
)

X_test_processed.to_csv(
    OUTPUT_DIR / "X_test.csv", index=False
)

y_train.to_csv(
    OUTPUT_DIR / "y_train.csv", index=False
)

y_test.to_csv(
    OUTPUT_DIR / "y_test.csv", index=False
)

joblib.dump(
    preprocessor,
    OUTPUT_DIR / "preprocessor.joblib"
)

print("\nProcessed Training Shape:", X_train_processed.shape)
print("Processed Testing Shape:", X_test_processed.shape)

print("\nFeature Engineering Completed Successfully!")
