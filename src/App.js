import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [clvPredictions, setClvPredictions] = useState([]);
  const [churnPredictions, setChurnPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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

      const data = await response.json();

      if (endpoint === "predict-clv") {
        setClvPredictions(data.predictions);
      } else {
        setChurnPredictions(data.predictions);
      }
    } catch (error) {
      setError("Error processing the request.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>Customer Predictions</h2>

      <input type="file" accept=".csv" onChange={handleFileChange} />
      <br />
      <button onClick={() => uploadFile("predict-clv")} disabled={loading}>
        Predict CLV
      </button>
      <button onClick={() => uploadFile("predict-churn")} disabled={loading}>
        Predict Churn
      </button>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <h3>CLV Predictions:</h3>
      <ul>
        {clvPredictions.map((pred, index) => (
          <li key={index}>{pred.toFixed(2)}</li>
        ))}
      </ul>

      <h3>Churn Predictions:</h3>
      <ul>
        {churnPredictions.map((pred, index) => (
          <li key={index}>{pred === 1 ? "Churn" : "Not Churn"}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
