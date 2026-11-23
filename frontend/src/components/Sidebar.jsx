
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const navigation = [
  { name: "Overview", path: "/", icon: "▦" },
  { name: "Predictions", path: "/predictions", icon: "◇" },
  { name: "Customers", path: "/customers", icon: "♙" },
  { name: "Analytics", path: "/analytics", icon: "▥" },
  { name: "Prediction History", path: "/history", icon: "◷" },
];

function Sidebar() {
  return (
    <aside className="sidebar">

      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-logo">C</div>

        <div className="brand-text">
          <h2>ChurnIQ</h2>
          <span>INTELLIGENCE PLATFORM</span>
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar-section">
        WORKSPACE
      </div>

      <nav className="sidebar-nav">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            title={item.name}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="sidebar-icon">
              {item.icon}
            </span>

            <span className="sidebar-link-text">
              {item.name}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">

        <div
          className="system-status"
          title="System Operational"
        >
          <span className="status-dot"></span>

          <span className="system-status-text">
            System Operational
          </span>
        </div>

        <p>ChurnIQ v1.0.0</p>

      </div>
    </aside>
  );
}

export default Sidebar;
