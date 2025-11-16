import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Australian Compliance Automation Platform</h1>
        <p>APRA CPS 234 | ASD Essential Eight | OAIC | PCI DSS | ISO 27001</p>
        <div className="feature-grid">
          <div className="feature-card">
            <h3>Real-time Compliance</h3>
            <p>Continuous monitoring and assessment</p>
          </div>
          <div className="feature-card">
            <h3>Automated Checks</h3>
            <p>150+ compliance controls automated</p>
          </div>
          <div className="feature-card">
            <h3>Audit Reports</h3>
            <p>Generate reports in minutes</p>
          </div>
          <div className="feature-card">
            <h3>Risk Dashboard</h3>
            <p>Real-time compliance health visibility</p>
          </div>
        </div>
        <a
          className="api-link"
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
        >
          View API Documentation
        </a>
      </header>
    </div>
  );
}

export default App;
