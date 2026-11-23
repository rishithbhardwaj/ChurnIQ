
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_PATH = (
    PROJECT_ROOT / "data" / "raw"
    / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_PATH = PROCESSED_DIR / "telco_customer_churn_cleaned.csv"


def preprocess_data():

    print("\n========== CHURNIQ DATA PREPROCESSING ==========\n")

    # Load original dataset
    df = pd.read_csv(RAW_PATH)

    print("Original dataset shape:", df.shape)

    # Convert TotalCharges to numeric
    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"].str.strip(),
        errors="coerce"
    )

    # Count missing values
    missing_count = df["TotalCharges"].isnull().sum()

    print("Missing TotalCharges:", missing_count)

    # Validate missing records
    missing_rows = df[df["TotalCharges"].isnull()]

    if not (missing_rows["tenure"] == 0).all():
        raise ValueError(
            "Unexpected missing TotalCharges records found."
        )

    # Handle missing values
    df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

    # Create output directory
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save cleaned dataset
    df.to_csv(OUTPUT_PATH, index=False)

    # Final validation
    print("\n========== VALIDATION ==========")

    print("Final dataset shape:", df.shape)
    print("Remaining missing values:", df.isnull().sum().sum())
    print("TotalCharges data type:", df["TotalCharges"].dtype)

    print("\nCleaned dataset saved at:")
    print(OUTPUT_PATH)

    print("\n========== PREPROCESSING COMPLETED ==========")


if __name__ == "__main__":
    preprocess_data()
