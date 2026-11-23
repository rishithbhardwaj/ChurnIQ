
import { useEffect, useMemo, useState } from "react";
import "./History.css";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch("/api/history");

      if (!response.ok) {
        throw new Error("Unable to fetch prediction history.");
      }

      const data = await response.json();

      if (data.status !== "success") {
        throw new Error(data.message || "History request failed.");
      }

      setHistory(data.history || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const churnCount = history.filter(
    (item) => item.prediction === "Churn"
  ).length;

  const retainedCount = history.filter(
    (item) => item.prediction === "No Churn"
  ).length;

  const filteredHistory = useMemo(() => {
    return history.filter((item) => {
      const matchesSearch =
        String(item.id).includes(search) ||
        item.prediction.toLowerCase().includes(search.toLowerCase());

      const matchesFilter =
        filter === "All" || item.prediction === filter;

      return matchesSearch && matchesFilter;
    });
  }, [history, search, filter]);

  const formatDate = (date) => {
    if (!date) return "—";

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) return date;

    return parsedDate.toLocaleString();
  };

  return (
    <section className="dashboard history-page">
      <div className="welcome-section">
        <div>
          <p className="eyebrow">PREDICTION MANAGEMENT</p>
          <h1>Prediction History</h1>
          <p className="subtitle">
            Review and monitor your previous customer churn predictions.
          </p>
        </div>

        <button
          className="history-refresh"
          onClick={fetchHistory}
          disabled={loading}
        >
          {loading ? "Loading..." : "↻ Refresh"}
        </button>
      </div>

      <div className="history-stats">
        <div className="history-stat-card">
          <span>Total Predictions</span>
          <h2>{history.length}</h2>
          <p>All saved predictions</p>
        </div>

        <div className="history-stat-card">
          <span>Churn Predictions</span>
          <h2 className="history-danger">{churnCount}</h2>
          <p>Customers predicted to leave</p>
        </div>

        <div className="history-stat-card">
          <span>Retained Predictions</span>
          <h2 className="history-success">{retainedCount}</h2>
          <p>Customers predicted to stay</p>
        </div>
      </div>

      <div className="panel history-panel">
        <div className="panel-header">
          <div>
            <h3>Prediction Records</h3>
            <p>History retrieved from your SQLite database</p>
          </div>
          <span className="chart-tag">
            {filteredHistory.length} RECORDS
          </span>
        </div>

        <div className="history-toolbar">
          <input
            type="text"
            placeholder="Search by prediction ID or result..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          >
            <option value="All">All Predictions</option>
            <option value="Churn">Churn</option>
            <option value="No Churn">No Churn</option>
          </select>
        </div>

        {loading ? (
          <div className="history-message">Loading prediction records...</div>
        ) : error ? (
          <div className="history-error">
            <strong>Unable to load history</strong>
            <p>{error}</p>
            <button onClick={fetchHistory}>Try Again</button>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="history-message">
            No matching prediction records found.
          </div>
        ) : (
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Prediction ID</th>
                  <th>Prediction Result</th>
                  <th>Churn Probability</th>
                  <th>Date & Time</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {filteredHistory.map((item) => (
                  <tr key={item.id}>
                    <td>#{item.id}</td>
                    <td>{item.prediction}</td>
                    <td>{Number(item.churn_probability).toFixed(2)}%</td>
                    <td>{formatDate(item.created_at)}</td>
                    <td>
                      <span
                        className={`history-badge ${
                          item.prediction === "Churn"
                            ? "churn-badge"
                            : "retained-badge"
                        }`}
                      >
                        {item.prediction}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <footer>
        ChurnIQ © 2026 · Prediction History
        <span>Powered by Machine Learning</span>
      </footer>
    </section>
  );
}

export default History;
