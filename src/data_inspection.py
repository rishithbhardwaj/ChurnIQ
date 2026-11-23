
"""
ChurnIQ - Dataset Inspection
Phase 2: Data Acquisition and Validation
"""

import pandas as pd
from pathlib import Path

# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Dataset location
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"


def inspect_dataset():
    print("\n========== CHURNIQ DATA INSPECTION ==========\n")

    # Load dataset
    df = pd.read_csv(DATA_PATH)

    print("\nALL DATASET COLUMNS:")
    print(df.columns.tolist())

    print("\nDATA TYPES:")
    print(df.dtypes)

    print("\nSAMPLE RECORDS:")
    print(df.head().to_string())

    # 1. Dataset dimensions
    print("1. Dataset Shape:")
    print(df.shape)

    # 2. First five records
    print("\n2. First Five Records:")
    print(df.head())

    # 3. Column information
    print("\n3. Dataset Information:")
    df.info()

    # 4. Missing values
    print("\n4. Missing Values:")
    print(df.isnull().sum())

    # 5. Duplicate records
    print("\n5. Duplicate Records:")
    print(df.duplicated().sum())

    # 6. Target distribution
    print("\n6. Churn Distribution:")
    print(df["Churn"].value_counts())


    # 7. Data types
    print("\n7. Column Data Types:")
    print(df.dtypes)

    # 8. Statistical summary
    print("\n8. Statistical Summary:")
    print(df.describe(include="all").T)

    # 9. Unique values
    print("\n9. Unique Values Per Column:")
    print(df.nunique())

    # 10. TotalCharges investigation
    print("\n10. TotalCharges Information:")
    print(df["TotalCharges"].value_counts().head(10))
    print("TotalCharges data type:", df["TotalCharges"].dtype)


    # 11. Investigate blank TotalCharges values

    print("\n11. TotalCharges Data Quality Check:")

    blank_values = df["TotalCharges"].str.strip().eq("").sum()

    print("Blank TotalCharges entries:", blank_values)

    # Convert a temporary copy to numeric
    total_charges_numeric = pd.to_numeric(
        df["TotalCharges"].str.strip(),
        errors="coerce"
    )

    print(
        "Missing values after numeric conversion:",
        total_charges_numeric.isna().sum()
    )

    # Display affected records
    print("\nAffected Customer Records:")

    print(
        df.loc[
            total_charges_numeric.isna(),
            ["customerID", "tenure", "MonthlyCharges", "TotalCharges"]
        ]
    )



    print("\n========== INSPECTION COMPLETED ==========\n")


if __name__ == "__main__":
    inspect_dataset()



