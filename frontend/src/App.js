import React, { useState } from "react";
import { motion } from "framer-motion";
import { BrowserRouter as Router, Link, Routes, Route, Navigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, ResponsiveContainer } from 'recharts';
import './App.css';
import Calculator from "./Calculator";


function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [file, setFile] = useState(null);
  const [clvPredictions, setClvPredictions] = useState([]);
  const [churnPredictions, setChurnPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const uploadFile = async (endpoint) => {
    if (!file) {
      setError("Please upload a CSV file.");
      return;
    }

    setLoading(true);
    setError("");
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.predictions) {
        endpoint === "predict-clv" 
          ? setClvPredictions(data.predictions) 
          : setChurnPredictions(data.predictions);
      } else {
        setError("No predictions returned from the server.");
      }
    } catch (error) {
      setError("Error processing the request.");
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={isLoggedIn ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />} />
        <Route path="/dashboard/*" element={isLoggedIn ? <Dashboard handleFileChange={handleFileChange} uploadFile={uploadFile} loading={loading} error={error} clvPredictions={clvPredictions} churnPredictions={churnPredictions} /> : <Navigate to="/login" />} />
        <Route path="/calculator" element={<Calculator />} />  {/* ✅ Calculator route added */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin();
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="container">
      <motion.div initial={{ y: -50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="form-box">
        <h2>LOGIN!</h2>
        <form onSubmit={handleSubmit}>
          <motion.div initial={{ x: -50, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="input-group">
            <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </motion.div>
          
          <motion.div initial={{ x: 50, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="input-group">
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </motion.div>

          <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} type="submit">
            Login
          </motion.button>
        </form>
      </motion.div>
    </motion.div>
  );
};
const Dashboard = ({ handleFileChange, uploadFile, loading, error, clvPredictions, churnPredictions }) => {
  return (
    <div className="app">
      <Navigation />
      <main className="main-content">
        <Routes>
          <Route path="/" element={
            <Home 
              handleFileChange={handleFileChange}
              uploadFile={uploadFile}
              loading={loading}
              error={error}
              clvPredictions={clvPredictions}
              churnPredictions={churnPredictions}
            />
          } />
          <Route path="/predict-churn" element={<PredictChurn />} />
          <Route path="/upload-data" element={<UploadData />} />
          <Route path="/calculator" element={<Calculator />} /> {/* ✅ Calculator page added */}
          <Route path="/" element={<Home />} />
        </Routes>
      </main>
    </div>
  );
};

function Navigation() {
  return (
    <motion.nav className="navbar" initial={{ y: -100 }} animate={{ y: 0 }} transition={{ duration: 0.5 }}>
      <div className="brand">
        <span className="brand-name">CUSTOMER LIFETIME VALUE PREDICTION</span>
      </div>
      
      <div className="nav-items">
        <Link to="/" className="nav-link">Home</Link>
        <Link to="/predict-churn" className="nav-link">Predict Churn</Link>
        <Link to="/upload-data" className="nav-link">Upload Data</Link>
        <Link to="/calculator" className="nav-link">Calculator</Link>  {/* ✅ Calculator Link Added */}
      </div>
    </motion.nav>
  );
}

function Home({ handleFileChange, uploadFile, loading, error, clvPredictions, churnPredictions }) {
  // Format data for visualization
  const clvData = clvPredictions.map((pred, index) => ({ id: index + 1, clv: pred }));
  const churnData = churnPredictions.map((pred, index) => ({ id: index + 1, churn: pred }));

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="page-title">Customer Analytics Dashboard</h1>

        <motion.div
          className="upload-section"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <input type="file" accept=".csv" onChange={handleFileChange} className="file-input" />

          <div className="button-group">
            <motion.button onClick={() => uploadFile("predict-clv")} disabled={loading} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              Predict CLV
            </motion.button>
            <motion.button onClick={() => uploadFile("predict-churn")} disabled={loading} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              Predict Churn
            </motion.button>
          </div>

          {loading && <div className="loading-indicator">Processing...</div>}
          {error && <div className="error-message">{error}</div>}
        </motion.div>

        <div className="predictions-container">
          {/* CLV Visualization */}
          <div className="prediction-card">
            <h3>CLV Predictions</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={clvData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="id" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="clv" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Churn Visualization */}
          <div className="prediction-card">
            <h3>Churn Predictions</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={churnData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="id" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="churn" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Prediction Values Section */}
        <div className="predictions-values">
          <h2>Prediction Values</h2>

          <div className="prediction-value-card">
            <h3>CLV Prediction Values</h3>
            <ul>
              {clvPredictions.length > 0 ? (
                clvPredictions.map((pred, index) => (
                  <li key={index}>Customer {index + 1}: <strong>${pred.toFixed(2)}</strong></li>
                ))
              ) : (
                <p>No CLV predictions available.</p>
              )}
            </ul>
          </div>

          <div className="prediction-value-card">
            <h3>Churn Prediction Values</h3>
            <ul>
              {churnPredictions.length > 0 ? (
                churnPredictions.map((pred, index) => (
                  <li key={index}>Customer {index + 1}: <strong>{pred === 1 ? "Churn" : "Not Churn"}</strong></li>
                ))
              ) : (
                <p>No Churn predictions available.</p>
              )}
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function PredictChurn() {
  return (
    <div className="page-container">
      <h1 className="page-title">Predict Churn</h1>
      {/* Add churn prediction specific content here */}
    </div>
  );
}

function UploadData() {
  return (
    <div className="page-container">
      <h1 className="page-title">Upload Data</h1>
      {/* Add data upload specific content here */}
    </div>
  );
}

export default App;
