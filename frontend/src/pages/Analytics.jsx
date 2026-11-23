
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import "./Analytics.css";

const COLORS = ["#9275ff", "#35c6b5"];

const tooltipStyle = {
  contentStyle: {
    backgroundColor: "#111b30",
    border: "1px solid #9275ff",
    borderRadius: "12px",
    padding: "14px 18px",
    boxShadow: "0 8px 25px rgba(0, 0, 0, 0.4)",
  },
  labelStyle: {
    color: "#a78bfa",
    fontSize: "13px",
    fontWeight: 600,
    marginBottom: "8px",
  },
  itemStyle: {
    color: "#35c6b5",
    fontSize: "13px",
    fontWeight: 600,
  },
};

function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch("/api/analytics");

        if (!response.ok) {
          throw new Error("Unable to load analytics data.");
        }

        const data = await response.json();

        if (data.status !== "success") {
          throw new Error(data.message || "Analytics request failed.");
        }

        setAnalytics(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return <div className="dashboard">Loading analytics...</div>;
  }

  if (error) {
    return (
      <div className="dashboard">
        <h2>Analytics unavailable</h2>
        <p>{error}</p>
      </div>
    );
  }

  const summary = analytics.summary;

  return (
    <section className="dashboard analytics-page">
      <div className="welcome-section">
        <div>
          <p className="eyebrow">CUSTOMER INTELLIGENCE</p>
          <h1>Analytics</h1>
          <p className="subtitle">
            Understand customer churn patterns and retention performance.
          </p>
        </div>
        <span className="chart-tag">LIVE DATASET ANALYSIS</span>
      </div>

      {/* Summary cards */}
      <section className="metrics-grid">
        <div className="metric-card">
          <div className="metric-top">
            <span>Total Customers</span>
          </div>
          <h2>{summary.total_customers.toLocaleString()}</h2>
          <p>All dataset records</p>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>Churned Customers</span>
          </div>
          <h2>{summary.churned_customers.toLocaleString()}</h2>
          <p>Customers who left</p>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>Retained Customers</span>
          </div>
          <h2>{summary.retained_customers.toLocaleString()}</h2>
          <p>Customers who stayed</p>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>Churn Rate</span>
          </div>
          <h2>{summary.churn_rate}%</h2>
          <p>Overall churn percentage</p>
        </div>
      </section>

      <section className="analytics-grid">

        {/* Churn Distribution */}
        <div className="panel analytics-panel">
          <div className="panel-header">
            <div>
              <h3>Churn Distribution</h3>
              <p>Customer retention overview</p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics.churn_distribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={75}
                  outerRadius={105}
                  paddingAngle={4}
                >
                  {analytics.churn_distribution.map((entry, index) => (
                    <Cell
                      key={entry.name}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>

                <Tooltip
                  cursor={false}
                  {...tooltipStyle}
                />

                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Contract Analysis */}
        <div className="panel analytics-panel">
          <div className="panel-header">
            <div>
              <h3>Churn by Contract</h3>
              <p>Customer status across contract types</p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.contract_churn}>
                <CartesianGrid
                  stroke="#253149"
                  strokeDasharray="3 3"
                />
                <XAxis dataKey="contract" stroke="#8999b5" />
                <YAxis stroke="#8999b5" />
                <Tooltip
                  cursor={false}
                  {...tooltipStyle}
                />
                <Legend />

                <Bar
                  dataKey="churn"
                  name="Churn"
                  fill="#9275ff"
                  radius={[5, 5, 0, 0]}
                />

                <Bar
                  dataKey="retained"
                  name="Retained"
                  fill="#35c6b5"
                  radius={[5, 5, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Payment Method Analysis */}
        <div className="panel analytics-panel">
          <div className="panel-header">
            <div>
              <h3>Churn by Payment Method</h3>
              <p>Customer churn across payment methods</p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={analytics.payment_churn}
                layout="vertical"
                margin={{ left: 25, right: 20 }}
              >
                <CartesianGrid
                  stroke="#253149"
                  strokeDasharray="3 3"
                />

                <XAxis type="number" stroke="#8999b5" />

                <YAxis
                  type="category"
                  dataKey="payment_method"
                  width={155}
                  stroke="#8999b5"
                  tick={{ fontSize: 10 }}
                />

                <Tooltip
                  cursor={false}
                  {...tooltipStyle}
                />

                <Legend />

                <Bar
                  dataKey="churn"
                  name="Churn"
                  fill="#9275ff"
                  radius={[0, 5, 5, 0]}
                />

                <Bar
                  dataKey="retained"
                  name="Retained"
                  fill="#35c6b5"
                  radius={[0, 5, 5, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tenure Analysis */}
        <div className="panel analytics-panel">
          <div className="panel-header">
            <div>
              <h3>Churn by Customer Tenure</h3>
              <p>Customer retention across tenure groups</p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.tenure_churn}>
                <CartesianGrid
                  stroke="#253149"
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="tenure_group"
                  stroke="#8999b5"
                />

                <YAxis stroke="#8999b5" />

                <Tooltip
                  cursor={false}
                  {...tooltipStyle}
                />

                <Legend />

                <Bar
                  dataKey="churn"
                  name="Churn"
                  fill="#9275ff"
                  radius={[5, 5, 0, 0]}
                />

                <Bar
                  dataKey="retained"
                  name="Retained"
                  fill="#35c6b5"
                  radius={[5, 5, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Average Monthly Charges */}
        <div className="panel analytics-panel charges-panel">
          <div className="panel-header">
            <div>
              <h3>Average Monthly Charges</h3>
              <p>
                Comparison between churned and retained customers
              </p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={analytics.monthly_charges}>
                <CartesianGrid
                  stroke="#253149"
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="status"
                  stroke="#8999b5"
                  tickFormatter={(value) =>
                    value === "Yes" ? "Churn" : "No Churn"
                  }
                />

                <YAxis stroke="#8999b5" />

                <Tooltip
                  cursor={false}
                  contentStyle={{
                    backgroundColor: "#111b30",
                    border: "1px solid #9275ff",
                    borderRadius: "12px",
                    padding: "14px 18px",
                    boxShadow: "0 8px 25px rgba(0, 0, 0, 0.4)",
                  }}
                  labelStyle={{
                    color: "#a78bfa",
                    fontSize: "13px",
                    fontWeight: 600,
                    marginBottom: "8px",
                  }}
                  itemStyle={{
                    color: "#35c6b5",
                    fontSize: "13px",
                    fontWeight: 600,
                  }}
                  formatter={(value) => [
                    `$${Number(value).toFixed(2)}`,
                    "Average Monthly Charges",
                  ]}
                  labelFormatter={(value) =>
                    value === "Yes" ? "Churn" : "No Churn"
                  }
                />

                <Bar
                  dataKey="average_charges"
                  name="Average Monthly Charges"
                  fill="#9275ff"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </section>

            {/* Customer Retention Insights */}
      <section className="insights-section">
        <div className="insights-heading">
          <div>
            <p className="eyebrow">DATA-DRIVEN RECOMMENDATIONS</p>
            <h2>Customer Retention Insights</h2>
            <p className="subtitle">
              Key churn patterns identified from your customer dataset.
            </p>
          </div>
          <span className="insight-count">
            {analytics.insights?.length || 0} INSIGHTS
          </span>
        </div>

        <div className="insights-grid">
          {analytics.insights?.map((insight, index) => (
            <article className="insight-card" key={`${insight.title}-${index}`}>
              <div className="insight-card-top">
                <span className="insight-number">
                  INSIGHT 0{index + 1}
                </span>
                <span className="insight-rate">
  {insight.badge || `${insight.churn_rate}%`}
</span>
              </div>

              <h3>{insight.title}</h3>

              <p className="insight-description">
                {insight.description}
              </p>

              <div className="insight-recommendation">
                <span>RECOMMENDED ACTION</span>
                <p>{insight.recommendation}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <footer>
        ChurnIQ © 2026 · Customer Analytics
        <span>Powered by Machine Learning</span>
      </footer>
    </section>
  );
}

export default Analytics;
