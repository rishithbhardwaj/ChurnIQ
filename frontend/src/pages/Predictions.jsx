
import { useState } from "react";
import "./Predictions.css";

const initialValues = {
  gender: "Male",
  SeniorCitizen: "0",
  Partner: "Yes",
  Dependents: "No",
  tenure: "12",
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "Fiber optic",
  OnlineSecurity: "No",
  OnlineBackup: "No",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "No",
  StreamingMovies: "No",
  Contract: "Month-to-month",
  PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check",
  MonthlyCharges: "70",
  TotalCharges: "840",
};

const sections = [
  {
    title: "Customer Information",
    description: "Basic customer profile and account details.",
    fields: [
      {
        name: "gender",
        label: "Gender",
        type: "select",
        options: ["Female", "Male"],
      },
      {
        name: "SeniorCitizen",
        label: "Senior Citizen",
        type: "select",
        options: ["0", "1"],
        labels: ["No", "Yes"],
      },
      {
        name: "Partner",
        label: "Has Partner",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "Dependents",
        label: "Has Dependents",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "tenure",
        label: "Tenure (Months)",
        type: "number",
        min: 0,
        max: 72,
      },
    ],
  },
  {
    title: "Services & Subscriptions",
    description: "Select the services currently used by the customer.",
    fields: [
      {
        name: "PhoneService",
        label: "Phone Service",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "MultipleLines",
        label: "Multiple Lines",
        type: "select",
        options: ["Yes", "No", "No phone service"],
      },
      {
        name: "InternetService",
        label: "Internet Service",
        type: "select",
        options: ["DSL", "Fiber optic", "No"],
      },
      ...[
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
      ].map((name) => ({
        name,
        label: name.replace(/([A-Z])/g, " $1").trim(),
        type: "select",
        options: ["Yes", "No", "No internet service"],
      })),
    ],
  },
  {
    title: "Billing & Contract",
    description: "Configure the customer's contract and payment details.",
    fields: [
      {
        name: "Contract",
        label: "Contract Type",
        type: "select",
        options: ["Month-to-month", "One year", "Two year"],
      },
      {
        name: "PaperlessBilling",
        label: "Paperless Billing",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "PaymentMethod",
        label: "Payment Method",
        type: "select",
        options: [
          "Electronic check",
          "Mailed check",
          "Bank transfer (automatic)",
          "Credit card (automatic)",
        ],
      },
      {
        name: "MonthlyCharges",
        label: "Monthly Charges ($)",
        type: "number",
        min: 0,
        step: "0.01",
      },
      {
        name: "TotalCharges",
        label: "Total Charges ($)",
        type: "number",
        min: 0,
        step: "0.01",
      },
    ],
  },
];

function Predictions() {
  const [formData, setFormData] = useState(initialValues);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    setResult(null);
    setError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    const payload = {
      ...formData,
      SeniorCitizen: Number(formData.SeniorCitizen),
      tenure: Number(formData.tenure),
      MonthlyCharges: Number(formData.MonthlyCharges),
      TotalCharges: Number(formData.TotalCharges),
    };

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Prediction request failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to connect to the prediction API.");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData(initialValues);
    setResult(null);
    setError("");
  };

  const probability = result
    ? Number(result.churn_probability)
    : 0;

  const riskLevel =
    probability >= 70
      ? "High"
      : probability >= 40
        ? "Medium"
        : "Low";

  const recommendation =
    result?.prediction === "No Churn"
      ? "This customer is predicted to stay. Continue delivering a positive service experience and monitor their account."
      : riskLevel === "High"
        ? "Prioritize this customer for immediate retention outreach. Consider a personalized offer, contract review, or dedicated support."
        : "Consider proactive engagement, review service satisfaction, and offer relevant retention incentives.";

  return (
    <section className="dashboard predictions-page">
      <div className="welcome-section">
        <div>
          <p className="eyebrow">MACHINE LEARNING ENGINE</p>
          <h1>Churn Prediction</h1>
          <p className="subtitle">
            Analyze customer information and estimate the likelihood of churn.
          </p>
        </div>

        <span className="chart-tag">XGBOOST MODEL</span>
      </div>

      <form onSubmit={handleSubmit}>
        {sections.map((section, index) => (
          <section className="panel prediction-section" key={section.title}>
            <div className="prediction-section-header">
              <div className="section-number">
                {String(index + 1).padStart(2, "0")}
              </div>

              <div>
                <h3>{section.title}</h3>
                <p>{section.description}</p>
              </div>
            </div>

            <div className="prediction-form-grid">
              {section.fields.map((field) => (
                <div className="prediction-field" key={field.name}>
                  <label htmlFor={field.name}>
                    {field.label}
                  </label>

                  {field.type === "select" ? (
                    <select
                      id={field.name}
                      name={field.name}
                      value={formData[field.name]}
                      onChange={handleChange}
                      required
                    >
                      {field.options.map((option, optionIndex) => (
                        <option key={option} value={option}>
                          {field.labels?.[optionIndex] || option}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      id={field.name}
                      name={field.name}
                      type="number"
                      min={field.min}
                      max={field.max}
                      step={field.step || "1"}
                      value={formData[field.name]}
                      onChange={handleChange}
                      required
                    />
                  )}
                </div>
              ))}
            </div>
          </section>
        ))}

        <div className="prediction-actions">
          <button
            type="button"
            className="reset-button"
            onClick={resetForm}
            disabled={loading}
          >
            Reset Form
          </button>

          <button
            type="submit"
            className="predict-button"
            disabled={loading}
          >
            {loading ? "Analyzing Customer..." : "Generate Prediction"}
          </button>
        </div>
      </form>

      {error && (
        <div className="prediction-error">
          <strong>Prediction failed</strong>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <section className="panel prediction-result">
          <div className="result-header">
            <div>
              <p className="eyebrow">MODEL ANALYSIS COMPLETE</p>
              <h2>Prediction Results</h2>
              <p className="subtitle">
                Customer churn assessment from the trained XGBoost model.
              </p>
            </div>

            <span
              className={`result-status ${
                result.prediction === "Churn" ? "danger" : "success"
              }`}
            >
              {result.prediction}
            </span>
          </div>

          <div className="result-grid">
            <div className="result-metric">
              <span>Churn Probability</span>
              <strong>{probability.toFixed(2)}%</strong>

              <div className="probability-track">
                <div
                  className="probability-fill"
                  style={{ width: `${Math.min(100, Math.max(0, probability))}%` }}
                />
              </div>
            </div>

            <div className="result-metric">
              <span>Risk Classification</span>
              <strong className={`risk-${riskLevel.toLowerCase()}`}>
                {riskLevel} Risk
              </strong>
              <small>
                Display classification based on probability thresholds.
              </small>
            </div>

            <div className="result-metric">
              <span>Selected Model</span>
              <strong>XGBoost</strong>
              <small>Gradient Boosting Classifier</small>
            </div>
          </div>

          <div className="retention-recommendation">
            <span>RECOMMENDED ACTION</span>
            <p>{recommendation}</p>
          </div>
        </section>
      )}
    </section>
  );
}

export default Predictions;
