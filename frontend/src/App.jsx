import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import './App.css'; // We'll create a simple CSS file for the navigation

function App() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <nav className="app-nav">
        <div className="nav-logo">
          AI-Coach
        </div>
        <div className="nav-links">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            Deep Search
          </Link>
          <Link to="/practice" className={location.pathname === '/practice' ? 'active' : ''}>
            Translation Practice
          </Link>
        </div>
      </nav>

      <main>
        {/* React Router renders the current page component here */}
        <Outlet />
      </main>
    </div>
  );
}

export default App;