import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "models"
DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
DATABASE_PATH = Path(os.getenv(
    "DATABASE_PATH",
    str(PROJECT_ROOT / "data" / "prediction_history.db")
))
MODEL_PATH = MODEL_DIR / "best_churn_model.pkl"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.joblib"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# CORS: configure FRONTEND_URL or comma-separated CORS_ORIGINS on Render.
ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}
ALLOWED_ORIGINS.update(
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
)
frontend_url = os.getenv("FRONTEND_URL", "").strip()
if frontend_url:
    ALLOWED_ORIGINS.add(frontend_url.rstrip("/"))

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin and origin.rstrip("/") in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "600"
    return response

# Load model artifacts once at process startup.
if not MODEL_PATH.is_file():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
if not PREPROCESSOR_PATH.is_file():
    raise FileNotFoundError(f"Preprocessor file not found: {PREPROCESSOR_PATH}")

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

REQUIRED_FEATURES = [
    "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges",
]


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def initialize_database():
    connection = get_db_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction TEXT NOT NULL,
                churn_probability REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        connection.commit()
    finally:
        connection.close()


def save_prediction(prediction_label, churn_probability):
    connection = get_db_connection()
    try:
        connection.execute("""
            INSERT INTO predictions (prediction, churn_probability, created_at)
            VALUES (?, ?, ?)
        """, (
            prediction_label,
            float(churn_probability),
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ))
        connection.commit()
    finally:
        connection.close()


initialize_database()


# --------------------------------------------------
# DATASET
# --------------------------------------------------

def load_dataset():
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(
            f"Dataset file not found: {DATASET_PATH}. "
            "Ensure the dataset is included in the deployed repository."
        )

    df = pd.read_csv(DATASET_PATH)
    required_columns = {
        "customerID", "tenure", "Contract", "MonthlyCharges",
        "TotalCharges", "PaymentMethod", "Churn",
    }
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(sorted(missing))
        )

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"], errors="coerce"
    ).fillna(0.0)
    return df


# --------------------------------------------------
# HOME AND HEALTH
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "Welcome to ChurnIQ - Customer Churn Prediction System",
        "health": "/health",
    })


@app.route("/health", methods=["GET"])
def health():
    checks = {
        "model": MODEL_PATH.is_file(),
        "preprocessor": PREPROCESSOR_PATH.is_file(),
        "dataset": DATASET_PATH.is_file(),
    }
    connection = None
    try:
        connection = get_db_connection()
        connection.execute("SELECT 1")
        checks["database"] = True
    except sqlite3.Error:
        checks["database"] = False
    finally:
        if connection is not None:
            connection.close()

    healthy = all(checks.values())
    return jsonify({
        "status": "success" if healthy else "degraded",
        "message": "ChurnIQ API is running" if healthy else "One or more resources are unavailable",
        "checks": checks,
    }), (200 if healthy else 503)


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "error": "Request body must contain valid JSON customer data.",
            }), 400

        missing = [feature for feature in REQUIRED_FEATURES if feature not in data]
        if missing:
            return jsonify({
                "status": "error",
                "error": "Missing required customer fields.",
                "missing_fields": missing,
            }), 400

        # Keep the same feature order used during model training.
        input_df = pd.DataFrame([{
            feature: data[feature] for feature in REQUIRED_FEATURES
        }])
        processed_data = preprocessor.transform(input_df)
        prediction_value = int(model.predict(processed_data)[0])
        churn_probability = round(
            float(model.predict_proba(processed_data)[0][1]) * 100, 2
        )
        prediction_label = "Churn" if prediction_value == 1 else "No Churn"

        save_prediction(prediction_label, churn_probability)

        return jsonify({
            "status": "success",
            "prediction": prediction_label,
            "churn_probability": churn_probability,
            "model": "XGBoost",
        })

    except (TypeError, ValueError, KeyError) as error:
        return jsonify({
            "status": "error",
            "error": f"Invalid customer data: {str(error)}",
        }), 400
    except Exception:
        app.logger.exception("Prediction request failed")
        return jsonify({
            "status": "error",
            "error": "Prediction failed due to a server error.",
        }), 500


# --------------------------------------------------
# CUSTOMER RECORDS
# --------------------------------------------------

@app.route("/customers", methods=["GET"])
def get_customers():
    try:
        customers = load_dataset()

        search = request.args.get("search", "").strip()
        if search:
            customers = customers[
                customers["customerID"].astype(str).str.contains(
                    search, case=False, na=False, regex=False
                )
            ]

        churn_filter = request.args.get("churn", "All")
        if churn_filter == "Churn":
            customers = customers[customers["Churn"] == "Yes"]
        elif churn_filter == "No Churn":
            customers = customers[customers["Churn"] == "No"]

        page = max(1, request.args.get("page", 1, type=int))
        per_page = min(100, max(1, request.args.get("per_page", 10, type=int)))
        total = len(customers)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page

        columns = [
            "customerID", "tenure", "Contract",
            "MonthlyCharges", "TotalCharges", "Churn",
        ]
        records = (
            customers[columns]
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
            "total_pages": int(total_pages),
        })
    except Exception:
        app.logger.exception("Customer records request failed")
        return jsonify({
            "status": "error",
            "message": "Unable to load customer records.",
        }), 500


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@app.route("/analytics", methods=["GET"])
def get_analytics():
    try:
        df = load_dataset()
        total_customers = int(len(df))
        churned = int((df["Churn"] == "Yes").sum())
        retained = int((df["Churn"] == "No").sum())
        churn_rate = round(churned / total_customers * 100, 2) if total_customers else 0.0

        churn_distribution = [
            {"name": "Churn", "value": churned},
            {"name": "No Churn", "value": retained},
        ]

        contract_data = (
            df.groupby("Contract")["Churn"].value_counts()
            .unstack(fill_value=0).reset_index()
        )
        contract_churn = [{
            "contract": str(row["Contract"]),
            "churn": int(row.get("Yes", 0)),
            "retained": int(row.get("No", 0)),
        } for _, row in contract_data.iterrows()]

        payment_data = (
            df.groupby("PaymentMethod")["Churn"].value_counts()
            .unstack(fill_value=0).reset_index()
        )
        payment_churn = [{
            "payment_method": str(row["PaymentMethod"]),
            "churn": int(row.get("Yes", 0)),
            "retained": int(row.get("No", 0)),
        } for _, row in payment_data.iterrows()]

        df["TenureGroup"] = pd.cut(
            df["tenure"],
            bins=[-1, 12, 24, 48, 60, 72],
            labels=[
                "0-12 Months", "13-24 Months", "25-48 Months",
                "49-60 Months", "61-72 Months",
            ],
        )
        tenure_data = (
            df.groupby("TenureGroup", observed=False)["Churn"]
            .value_counts().unstack(fill_value=0).reset_index()
        )
        tenure_churn = [{
            "tenure_group": str(row["TenureGroup"]),
            "churn": int(row.get("Yes", 0)),
            "retained": int(row.get("No", 0)),
        } for _, row in tenure_data.iterrows()]

        monthly_data = df.groupby("Churn")["MonthlyCharges"].mean().reset_index()
        monthly_charges = [{
            "status": str(row["Churn"]),
            "average_charges": round(float(row["MonthlyCharges"]), 2),
        } for _, row in monthly_data.iterrows()]

        def calculate_churn_rates(column):
            grouped = (
                df.groupby(column, observed=False)
                .agg(
                    total_customers=("Churn", "size"),
                    churned_customers=(
                        "Churn", lambda values: int((values == "Yes").sum())
                    ),
                )
                .reset_index()
            )
            grouped["churn_rate"] = (
                grouped["churned_customers"]
                / grouped["total_customers"].replace(0, pd.NA) * 100
            )
            return grouped.dropna(subset=["churn_rate"])

        insights = []

        contract_rates = calculate_churn_rates("Contract")
        if not contract_rates.empty:
            row = contract_rates.loc[contract_rates["churn_rate"].idxmax()]
            rate = float(row["churn_rate"])
            category = str(row["Contract"])
            insights.append({
                "title": "Highest Churn Contract",
                "category": category,
                "churn_rate": round(rate, 2),
                "description": f"{category} customers have the highest churn rate of {rate:.2f}%.",
                "recommendation": "Focus on improving contract renewal incentives and customer retention.",
            })

        payment_rates = calculate_churn_rates("PaymentMethod")
        if not payment_rates.empty:
            row = payment_rates.loc[payment_rates["churn_rate"].idxmax()]
            rate = float(row["churn_rate"])
            category = str(row["PaymentMethod"])
            insights.append({
                "title": "Highest Churn Payment Method",
                "category": category,
                "churn_rate": round(rate, 2),
                "description": f"{category} has the highest customer churn rate of {rate:.2f}%.",
                "recommendation": "Review payment experience and investigate possible billing-related customer concerns.",
            })

        tenure_rates = calculate_churn_rates("TenureGroup")
        if not tenure_rates.empty:
            row = tenure_rates.loc[tenure_rates["churn_rate"].idxmax()]
            rate = float(row["churn_rate"])
            category = str(row["TenureGroup"])
            insights.append({
                "title": "Highest Churn Tenure Group",
                "category": category,
                "churn_rate": round(rate, 2),
                "description": f"Customers in the {category} group have the highest churn rate of {rate:.2f}%.",
                "recommendation": "Prioritize engagement and retention campaigns for customers in this tenure group.",
            })

        churned_avg = df.loc[df["Churn"] == "Yes", "MonthlyCharges"].mean()
        retained_avg = df.loc[df["Churn"] == "No", "MonthlyCharges"].mean()
        churned_avg = 0.0 if pd.isna(churned_avg) else float(churned_avg)
        retained_avg = 0.0 if pd.isna(retained_avg) else float(retained_avg)
        charge_difference = round(abs(churned_avg - retained_avg), 2)

        insights.append({
            "title": "Monthly Charges Comparison",
            "category": "Churn vs No Churn",
            "churn_rate": None,
            "badge": f"${charge_difference:.2f}",
            "description": (
                f"Churned customers pay an average of ${churned_avg:.2f} per month, "
                f"compared with ${retained_avg:.2f} for retained customers."
            ),
            "recommendation": "Review pricing, service value and suitable retention offers for at-risk customers.",
        })

        return jsonify({
            "status": "success",
            "summary": {
                "total_customers": total_customers,
                "churned_customers": churned,
                "retained_customers": retained,
                "churn_rate": churn_rate,
            },
            "churn_distribution": churn_distribution,
            "contract_churn": contract_churn,
            "payment_churn": payment_churn,
            "tenure_churn": tenure_churn,
            "monthly_charges": monthly_charges,
            "insights": insights,
        })

    except Exception:
        app.logger.exception("Analytics request failed")
        return jsonify({
            "status": "error",
            "message": "Unable to generate analytics.",
        }), 500


# --------------------------------------------------
# PREDICTION HISTORY
# --------------------------------------------------

@app.route("/history", methods=["GET"])
def get_prediction_history():
    connection = None
    try:
        connection = get_db_connection()
        rows = connection.execute("""
            SELECT id, prediction, churn_probability, created_at
            FROM predictions
            ORDER BY id DESC
        """).fetchall()
        history = [dict(row) for row in rows]

        return jsonify({
            "status": "success",
            "total": len(history),
            "history": history,
        })
    except Exception:
        app.logger.exception("Prediction history request failed")
        return jsonify({
            "status": "error",
            "message": "Unable to load prediction history.",
        }), 500
    finally:
        if connection is not None:
            connection.close()


# Local development only. Render runs this app with Gunicorn.
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
