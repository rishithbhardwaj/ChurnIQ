from flask import Flask, request, jsonify
import pandas as pd
import joblib
import sqlite3
from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "models"
DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
)
DATABASE_PATH = PROJECT_ROOT / "data" / "prediction_history.db"

# Ensure the database directory exists before SQLite opens the file.
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Load the trained model and preprocessing pipeline.
MODEL_PATH = MODEL_DIR / "best_churn_model.pkl"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.joblib"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

if not PREPROCESSOR_PATH.exists():
    raise FileNotFoundError(
        f"Preprocessor file not found: {PREPROCESSOR_PATH}"
    )

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_db_connection():
    """Create and return a SQLite database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the prediction history table if it does not exist."""
    connection = get_db_connection()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction TEXT NOT NULL,
                churn_probability REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


initialize_database()


# --------------------------------------------------
# DATASET LOADER
# --------------------------------------------------

def load_dataset():
    """Load the original Telco Customer Churn dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    # The source CSV stores TotalCharges as text and has 11 blank values.
    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce"
    ).fillna(0.0)

    return df


# --------------------------------------------------
# HOME AND HEALTH CHECK
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return "Welcome to ChurnIQ - Customer Churn Prediction System"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "ChurnIQ API is running"
    })


# --------------------------------------------------
# CUSTOMER CHURN PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "error": "Request body must contain valid JSON customer data."
            }), 400

        # These are the 19 input features used during model training.
        required_features = [
            "gender",
            "SeniorCitizen",
            "Partner",
            "Dependents",
            "tenure",
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaperlessBilling",
            "PaymentMethod",
            "MonthlyCharges",
            "TotalCharges"
        ]

        missing_features = [
            feature for feature in required_features if feature not in data
        ]

        if missing_features:
            return jsonify({
                "status": "error",
                "error": "Missing required customer fields.",
                "missing_fields": missing_features
            }), 400

        # Preserve the training feature order and ignore unrelated fields.
        input_df = pd.DataFrame([{
            feature: data[feature] for feature in required_features
        }])

        processed_data = preprocessor.transform(input_df)

        prediction_value = int(model.predict(processed_data)[0])
        probability = float(model.predict_proba(processed_data)[0][1])

        prediction_label = (
            "Churn" if prediction_value == 1 else "No Churn"
        )
        churn_probability = round(probability * 100, 2)

        # Save this prediction to the history database.
        connection = get_db_connection()
        try:
            connection.execute(
                """
                INSERT INTO predictions
                    (prediction, churn_probability, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    prediction_label,
                    churn_probability,
                    datetime.now().isoformat(timespec="seconds")
                )
            )
            connection.commit()
        finally:
            connection.close()

        return jsonify({
            "status": "success",
            "prediction": prediction_label,
            "churn_probability": churn_probability,
            "model": "XGBoost"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400


# --------------------------------------------------
# CUSTOMER RECORDS
# --------------------------------------------------

@app.route("/customers", methods=["GET"])
def get_customers():
    try:
        customers = load_dataset()

        # Search by customer ID.
        search = request.args.get("search", "").strip()
        if search:
            customers = customers[
                customers["customerID"].astype(str).str.contains(
                    search,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        # Filter by churn status.
        churn_filter = request.args.get("churn", "All")

        if churn_filter == "Churn":
            customers = customers[customers["Churn"] == "Yes"]
        elif churn_filter == "No Churn":
            customers = customers[customers["Churn"] == "No"]

        # Pagination.
        page = max(1, request.args.get("page", 1, type=int))
        per_page = min(
            100,
            max(1, request.args.get("per_page", 10, type=int))
        )

        total = len(customers)
        total_pages = (total + per_page - 1) // per_page

        # If there are no records, total_pages is zero.
        start = (page - 1) * per_page

        display_columns = [
            "customerID",
            "tenure",
            "Contract",
            "MonthlyCharges",
            "TotalCharges",
            "Churn"
        ]

        records = (
            customers[display_columns]
            .iloc[start:start + per_page]
            .fillna("")
            .to_dict(orient="records")
        )

        return jsonify({
            "status": "success",
            "customers": records,
            "total": int(total),
            "page": page,
            "per_page": per_page,
            "total_pages": int(total_pages)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# ANALYTICS DASHBOARD
# --------------------------------------------------

@app.route("/analytics", methods=["GET"])
def get_analytics():
    try:
        df = load_dataset()

        total_customers = int(len(df))
        churned = int((df["Churn"] == "Yes").sum())
        retained = int((df["Churn"] == "No").sum())

        churn_rate = (
            round((churned / total_customers) * 100, 2)
            if total_customers else 0.0
        )

        # 1. Overall churn distribution.
        churn_distribution = [
            {"name": "Churn", "value": churned},
            {"name": "No Churn", "value": retained}
        ]

        # 2. Churn counts by contract.
        contract_data = (
            df.groupby("Contract")["Churn"]
            .value_counts()
            .unstack(fill_value=0)
            .reset_index()
        )

        contract_churn = []
        for _, row in contract_data.iterrows():
            contract_churn.append({
                "contract": str(row["Contract"]),
                "churn": int(row.get("Yes", 0)),
                "retained": int(row.get("No", 0))
            })

        # 3. Churn counts by payment method.
        payment_data = (
            df.groupby("PaymentMethod")["Churn"]
            .value_counts()
            .unstack(fill_value=0)
            .reset_index()
        )

        payment_churn = []
        for _, row in payment_data.iterrows():
            payment_churn.append({
                "payment_method": str(row["PaymentMethod"]),
                "churn": int(row.get("Yes", 0)),
                "retained": int(row.get("No", 0))
            })

        # 4. Churn counts by tenure group.
        df["TenureGroup"] = pd.cut(
            df["tenure"],
            bins=[-1, 12, 24, 48, 60, 72],
            labels=[
                "0-12 Months",
                "13-24 Months",
                "25-48 Months",
                "49-60 Months",
                "61-72 Months"
            ]
        )

        tenure_data = (
            df.groupby("TenureGroup", observed=False)["Churn"]
            .value_counts()
            .unstack(fill_value=0)
            .reset_index()
        )

        tenure_churn = []
        for _, row in tenure_data.iterrows():
            tenure_churn.append({
                "tenure_group": str(row["TenureGroup"]),
                "churn": int(row.get("Yes", 0)),
                "retained": int(row.get("No", 0))
            })

        # 5. Average monthly charges by churn status.
        monthly_data = (
            df.groupby("Churn")["MonthlyCharges"]
            .mean()
            .reset_index()
        )

        monthly_charges = [
            {
                "status": str(row["Churn"]),
                "average_charges": round(
                    float(row["MonthlyCharges"]), 2
                )
            }
            for _, row in monthly_data.iterrows()
        ]

        # Helper function to calculate churn rate for a category.
        def calculate_churn_rates(column):
            grouped = (
                df.groupby(column, observed=False)
                .agg(
                    total_customers=("Churn", "size"),
                    churned_customers=(
                        "Churn",
                        lambda values: int((values == "Yes").sum())
                    )
                )
                .reset_index()
            )

            grouped["churn_rate"] = (
                grouped["churned_customers"]
                / grouped["total_customers"]
                * 100
            )

            return grouped

        contract_rates = calculate_churn_rates("Contract")
        payment_rates = calculate_churn_rates("PaymentMethod")
        tenure_rates = calculate_churn_rates("TenureGroup")

        highest_contract = contract_rates.loc[
            contract_rates["churn_rate"].idxmax()
        ]
        highest_payment = payment_rates.loc[
            payment_rates["churn_rate"].idxmax()
        ]
        highest_tenure = tenure_rates.loc[
            tenure_rates["churn_rate"].idxmax()
        ]

        # 6. Compare average monthly charges for churned and retained users.
        churned_avg_charges = float(
            df.loc[df["Churn"] == "Yes", "MonthlyCharges"].mean()
        )
        retained_avg_charges = float(
            df.loc[df["Churn"] == "No", "MonthlyCharges"].mean()
        )

        charge_difference = round(
            abs(churned_avg_charges - retained_avg_charges),
            2
        )

        # 7. Business insights.
        insights = [
            {
                "title": "Highest Churn Contract",
                "category": str(highest_contract["Contract"]),
                "churn_rate": round(
                    float(highest_contract["churn_rate"]), 2
                ),
                "description": (
                    f'{highest_contract["Contract"]} customers have '
                    f'the highest churn rate of '
                    f'{highest_contract["churn_rate"]:.2f}%.'
                ),
                "recommendation": (
                    "Focus on improving contract renewal incentives "
                    "and customer retention."
                )
            },
            {
                "title": "Highest Churn Payment Method",
                "category": str(highest_payment["PaymentMethod"]),
                "churn_rate": round(
                    float(highest_payment["churn_rate"]), 2
                ),
                "description": (
                    f'{highest_payment["PaymentMethod"]} has the '
                    f'highest customer churn rate of '
                    f'{highest_payment["churn_rate"]:.2f}%.'
                ),
                "recommendation": (
                    "Review payment experience and investigate "
                    "possible billing-related customer concerns."
                )
            },
            {
                "title": "Highest Churn Tenure Group",
                "category": str(highest_tenure["TenureGroup"]),
                "churn_rate": round(
                    float(highest_tenure["churn_rate"]), 2
                ),
                "description": (
                    f'Customers in the {highest_tenure["TenureGroup"]} '
                    f'group have the highest churn rate of '
                    f'{highest_tenure["churn_rate"]:.2f}%.'
                ),
                "recommendation": (
                    "Prioritize engagement and retention campaigns "
                    "for customers in this tenure group."
                )
            },
            {
                "title": "Monthly Charges Comparison",
                "category": "Churn vs No Churn",
                "churn_rate": None,
                "badge": f"${charge_difference:.2f}",
                "description": (
                    f"Churned customers pay an average of "
                    f"${churned_avg_charges:.2f} per month, compared "
                    f"with ${retained_avg_charges:.2f} for retained "
                    f"customers."
                ),
                "recommendation": (
                    "Review pricing, service value and suitable "
                    "retention offers for at-risk customers."
                )
            }
        ]

        return jsonify({
            "status": "success",
            "summary": {
                "total_customers": total_customers,
                "churned_customers": churned,
                "retained_customers": retained,
                "churn_rate": churn_rate
            },
            "churn_distribution": churn_distribution,
            "contract_churn": contract_churn,
            "payment_churn": payment_churn,
            "tenure_churn": tenure_churn,
            "monthly_charges": monthly_charges,
            "insights": insights
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# PREDICTION HISTORY
# --------------------------------------------------

@app.route("/history", methods=["GET"])
def get_prediction_history():
    try:
        connection = get_db_connection()
        try:
            records = connection.execute(
                """
                SELECT id, prediction, churn_probability, created_at
                FROM predictions
                ORDER BY id DESC
                """
            ).fetchall()
        finally:
            connection.close()

        history = [dict(record) for record in records]

        return jsonify({
            "status": "success",
            "total": len(history),
            "history": history
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
