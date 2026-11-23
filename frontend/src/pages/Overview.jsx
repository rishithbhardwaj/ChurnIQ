
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Overview.css";

function Overview() {
  const [analytics, setAnalytics] = useState(null);
  const [apiStatus, setApiStatus] = useState("Checking...");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  // Fetch analytics from Flask backend
  const fetchAnalytics = async () => {
    try {
      setError("");
      setRefreshing(true);

      const response = await fetch("/api/analytics");

      if (!response.ok) {
        throw new Error("Unable to load dashboard analytics.");
      }

      const data = await response.json();

      if (data.status !== "success") {
        throw new Error("Analytics data could not be retrieved.");
      }

      setAnalytics(data);
      setApiStatus("Available");
    } catch (err) {
      setError(err.message);
      setApiStatus("Unavailable");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const summary = analytics?.summary;

  // Dashboard metrics
  const metrics = [
    {
      title: "Total Customers",
      value: summary?.total_customers?.toLocaleString("en-IN") ?? "—",
      change: "Dataset records",
      icon: "♙",
    },
    {
      title: "Churn Rate",
      value: summary ? `${summary.churn_rate}%` : "—",
      change: "Customers lost",
      icon: "↗",
    },
    {
      title: "Churned Customers",
      value: summary?.churned_customers?.toLocaleString("en-IN") ?? "—",
      change: "Predicted to leave in dataset",
      icon: "◎",
    },
    {
      title: "Retained Customers",
      value: summary?.retained_customers?.toLocaleString("en-IN") ?? "—",
      change: "Customers staying",
      icon: "✦",
    },
  ];

  return (
    <section className="dashboard">

      {/* Welcome section */}
      <div className="welcome-section">
        <div>
          <p className="eyebrow">CUSTOMER INTELLIGENCE</p>
          <h1>Dashboard Overview</h1>
          <p className="subtitle">
            Monitor customer retention and predict churn with machine learning.
          </p>
        </div>

        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          flexWrap: "wrap"
        }}>
          <div className="date-label">
            2026 · CHURN ANALYTICS
          </div>

          <button
            type="button"
            onClick={fetchAnalytics}
            disabled={refreshing}
            style={{
              padding: "11px 16px",
              border: "1px solid #34415c",
              borderRadius: "9px",
              background: "#172238",
              color: "#e8edf8",
              fontWeight: 600,
              cursor: refreshing ? "not-allowed" : "pointer",
              opacity: refreshing ? 0.65 : 1,
              whiteSpace: "nowrap"
            }}
          >
            {refreshing ? "↻ Refreshing..." : "↻ Refresh"}
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="history-error">
          <strong>Dashboard data unavailable</strong>
          <p>{error}</p>
          <button type="button" onClick={fetchAnalytics}>
            Try Again
          </button>
        </div>
      )}

      {/* Dashboard metrics */}
      <section className="metrics-grid">
        {metrics.map((metric) => (
          <div className="metric-card" key={metric.title}>
            <div className="metric-top">
              <span>{metric.title}</span>
              <div className="metric-icon">{metric.icon}</div>
            </div>

            <h2>{loading ? "..." : metric.value}</h2>
            <p>{metric.change}</p>
          </div>
        ))}
      </section>

      {/* Customer distribution */}
      <section className="panel distribution-panel">
        <div className="panel-header">
          <div>
            <h3>Customer Distribution</h3>
            <p>Overall churn and retention breakdown</p>
          </div>
          <span className="chart-tag">DATASET</span>
        </div>

        {loading ? (
          <div className="history-message">
            Loading customer distribution...
          </div>
        ) : summary ? (
          <div className="distribution-content">
            <div
              className="donut-chart"
              style={{
                background: `conic-gradient(#ff777d 0% ${summary.churn_rate}%, #35c6b5 ${summary.churn_rate}% 100%)`,
              }}
            >
              <div className="donut-center">
                <strong>
                  {summary.total_customers.toLocaleString("en-IN")}
                </strong>
                <span>Total Customers</span>
              </div>
            </div>

            <div className="distribution-legend">
              <div>
                <span className="legend-dot churn-dot" />
                <div>
                  <strong>Churned</strong>
                  <p>
                    {summary.churned_customers.toLocaleString("en-IN")} customers
                  </p>
                </div>
                <strong className="distribution-percent">
                  {summary.churn_rate}%
                </strong>
              </div>

              <div>
                <span className="legend-dot retained-dot" />
                <div>
                  <strong>Retained</strong>
                  <p>
                    {summary.retained_customers.toLocaleString("en-IN")} customers
                  </p>
                </div>
                <strong className="distribution-percent">
                  {(100 - summary.churn_rate).toFixed(2)}%
                </strong>
              </div>
            </div>
          </div>
        ) : (
          <div className="history-message">
            Distribution data unavailable.
          </div>
        )}
      </section>

      {/* Top churn risk insights */}
      <section className="panel insights-panel">
        <div className="panel-header">
          <div>
            <h3>Top Churn Risk Insights</h3>
            <p>Key customer segments requiring retention attention</p>
          </div>
          <span className="chart-tag">AI INSIGHTS</span>
        </div>

        <div className="insights-grid">
          {analytics?.insights?.slice(0, 3).map((insight, index) => (
            <div className="insight-card" key={insight.title}>
              <div className="insight-card-top">
                <span className="insight-number">
                  0{index + 1}
                </span>
                <span className="insight-risk">
                  {insight.churn_rate}% churn
                </span>
              </div>

              <h4>{insight.title}</h4>
              <p>{insight.description}</p>

              <div className="insight-recommendation">
                <strong>Recommended Action</strong>
                <p>{insight.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Contract analytics and model information */}
      <section className="content-grid">

        <div className="panel chart-panel">
          <div className="panel-header">
            <div>
              <h3>Churn by Contract</h3>
              <p>Actual customer distribution across contract types</p>
            </div>
            <span className="chart-tag">DATASET</span>
          </div>

          {loading ? (
            <div className="history-message">
              Loading contract analytics...
            </div>
          ) : (
            <div className="contract-chart">
              {analytics?.contract_churn?.map((item) => {
                const total = item.churn + item.retained;
                const churnWidth = total
                  ? (item.churn / total) * 100
                  : 0;

                return (
                  <div className="contract-row" key={item.contract}>
                    <div className="contract-label">
                      <span>{item.contract}</span>
                      <strong>{churnWidth.toFixed(1)}% churn</strong>
                    </div>

                    <div className="contract-bar">
                      <div
                        className="contract-churn"
                        style={{ width: `${churnWidth}%` }}
                      />
                      <div
                        className="contract-retained"
                        style={{ width: `${100 - churnWidth}%` }}
                      />
                    </div>

                    <div className="contract-legend">
                      <span>
                        Churn: {item.churn.toLocaleString("en-IN")}
                      </span>
                      <span>
                        Retained: {item.retained.toLocaleString("en-IN")}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="contract-key">
            <span><i className="key-churn" /> Churn</span>
            <span><i className="key-retained" /> Retained</span>
          </div>
        </div>

        <div className="panel model-panel">
          <div className="panel-header">
            <div>
              <h3>Model Information</h3>
              <p>Machine learning engine</p>
            </div>
            <span className="model-icon">✦</span>
          </div>

          <div className="model-name">
            <span>SELECTED ALGORITHM</span>
            <h2>XGBoost</h2>
            <p>Gradient Boosting Classifier</p>
          </div>

          <div className="model-detail">
            <span>Cross-validation F1</span>
            <strong>63.47%</strong>
          </div>

          <div className="model-detail">
            <span>Test accuracy</span>
            <strong>76.15%</strong>
          </div>

          <div className="model-detail">
            <span>Prediction API</span>
            <strong className={apiStatus === "Available" ? "online" : ""}>
              ● {apiStatus}
            </strong>
          </div>
        </div>

      </section>

      {/* Quick actions */}
      <section className="panel activity-panel">
        <div className="panel-header">
          <div>
            <h3>Quick Actions</h3>
            <p>Explore the ChurnIQ platform</p>
          </div>
        </div>

        <div className="action-grid">

          <Link to="/predictions" className="action-card">
            <span>◈</span>
            <strong>New Prediction</strong>
            <small>Predict customer churn</small>
          </Link>

          <Link to="/customers" className="action-card">
            <span>♙</span>
            <strong>Customer Records</strong>
            <small>Explore customer data</small>
          </Link>

          <Link to="/analytics" className="action-card">
            <span>▥</span>
            <strong>View Analytics</strong>
            <small>Explore model insights</small>
          </Link>

        </div>
      </section>

      {/* Footer */}
      <footer>
        ChurnIQ © 2026 · Customer Churn Prediction System
        <span>Powered by Machine Learning</span>
      </footer>

    </section>
  );
}

export default Overview;
