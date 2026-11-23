
import { useEffect, useState } from "react";
import "./Customers.css";

function Customers() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [churn, setChurn] = useState("All");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    const loadCustomers = async () => {
      setLoading(true);
      setError("");

      try {
        const params = new URLSearchParams({
          search,
          churn,
          page: String(page),
          per_page: "10",
        });

        const response = await fetch(
          `/api/customers?${params.toString()}`,
          { signal: controller.signal }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Unable to load customers.");
        }

        setCustomers(data.customers);
        setTotal(data.total);
        setTotalPages(Math.max(1, data.total_pages));
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadCustomers();

    return () => controller.abort();
  }, [search, churn, page]);

  const exportCSV = async () => {
    try {
      const params = new URLSearchParams({
        search,
        churn,
        page: "1",
        per_page: "100",
      });

      const response = await fetch(`/api/customers?${params}`);

      if (!response.ok) {
        throw new Error("Unable to export customer records.");
      }

      const data = await response.json();

      const headers = [
        "Customer ID",
        "Tenure",
        "Contract",
        "Monthly Charges",
        "Total Charges",
        "Churn",
      ];

      const rows = data.customers.map((customer) => [
        customer.customerID,
        customer.tenure,
        customer.Contract,
        customer.MonthlyCharges,
        customer.TotalCharges,
        customer.Churn,
      ]);

      const csv = [headers, ...rows]
        .map((row) =>
          row
            .map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`)
            .join(",")
        )
        .join("\n");

      const blob = new Blob([csv], {
        type: "text/csv;charset=utf-8;",
      });

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "churniq-customers.csv";
      link.click();

      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section className="dashboard customers-page">
      <div className="welcome-section">
        <div>
          <p className="eyebrow">CUSTOMER MANAGEMENT</p>
          <h1>Customers</h1>
          <p className="subtitle">
            Explore customer records and monitor churn status.
          </p>
        </div>

        <button className="export-button" onClick={exportCSV}>
          Export CSV
        </button>
      </div>

      <div className="customer-stats">
        <div className="customer-stat-card">
          <span>Matching Customers</span>
          <h2>{total.toLocaleString()}</h2>
        </div>

        <div className="customer-stat-card">
          <span>Records Per Page</span>
          <h2>10</h2>
        </div>

        <div className="customer-stat-card">
          <span>Current Page</span>
          <h2>{page} / {totalPages}</h2>
        </div>
      </div>

      <div className="customer-table-panel">
        <div className="customer-toolbar">
          <input
            type="search"
            placeholder="Search customer ID..."
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
          />

          <select
            value={churn}
            onChange={(event) => {
              setChurn(event.target.value);
              setPage(1);
            }}
          >
            <option value="All">All Customers</option>
            <option value="Churn">Churn</option>
            <option value="No Churn">No Churn</option>
          </select>
        </div>

        {error && <div className="customer-error">{error}</div>}

        <div className="table-scroll">
          <table className="customer-table">
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Tenure</th>
                <th>Contract</th>
                <th>Monthly Charges</th>
                <th>Total Charges</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="table-message">
                    Loading customers...
                  </td>
                </tr>
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan="6" className="table-message">
                    No customers found.
                  </td>
                </tr>
              ) : (
                customers.map((customer) => (
                  <tr key={customer.customerID}>
                    <td className="customer-id">
                      {customer.customerID}
                    </td>
                    <td>{customer.tenure} months</td>
                    <td>{customer.Contract}</td>
                    <td>${Number(customer.MonthlyCharges).toFixed(2)}</td>
                    <td>${Number(customer.TotalCharges || 0).toFixed(2)}</td>
                    <td>
                      <span
                        className={`customer-status ${
                          customer.Churn === "Yes"
                            ? "status-churn"
                            : "status-active"
                        }`}
                      >
                        {customer.Churn === "Yes" ? "Churn" : "No Churn"}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="customer-pagination">
          <span>
            Showing {customers.length} of {total} matching records
          </span>

          <div>
            <button
              disabled={page <= 1 || loading}
              onClick={() => setPage((current) => current - 1)}
            >
              Previous
            </button>

            <strong>{page}</strong>

            <button
              disabled={page >= totalPages || loading}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Customers;
