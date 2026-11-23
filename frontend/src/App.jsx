
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Overview from "./pages/Overview";
import Predictions from "./pages/Predictions";
import Customers from "./pages/Customers";
import Analytics from "./pages/Analytics";
import History from "./pages/History";
import "./App.css";

function AppLayout() {
  const location = useLocation();

  const pageTitles = {
    "/": "Overview",
    "/predictions": "Predictions",
    "/customers": "Customers",
    "/analytics": "Analytics",
    "/history": "Prediction History",
  };

  const activePage = pageTitles[location.pathname] || "Overview";

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace /</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className="live-indicator">
              <span className="status-dot"></span>
              Live system
            </span>

            <div className="top-avatar">CQ</div>
          </div>
        </header>

        <Routes>
          <Route path="/" element={<Overview />} />

          <Route
            path="/predictions"
            element={<Predictions />}
          />

          
          <Route
            path="/customers"
            element={<Customers />}
          />


          <Route
            path="/analytics"
            element={<Analytics />}
          />

          <Route path="/history" element={<History />} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

export default App;
