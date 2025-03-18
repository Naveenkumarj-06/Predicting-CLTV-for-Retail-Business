import React, { useState } from 'react';
import axios from 'axios';

const UploadForm = () => {
    const [file, setFile] = useState(null);
    const [clvPredictions, setClvPredictions] = useState([]);
    const [churnPredictions, setChurnPredictions] = useState([]);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async (endpoint) => {
        if (!file) {
            alert("Please select a file first!");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`http://127.0.0.1:5000/${endpoint}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (endpoint === 'predict-clv') {
                setClvPredictions(response.data.predictions);
            } else {
                setChurnPredictions(response.data.predictions);
            }
        } catch (error) {
            console.error("Error uploading file:", error);
        }
    };

    return (
        <div>
            <h2>Upload CSV for Predictions</h2>
            <input type="file" accept=".csv" onChange={handleFileChange} />
            <button onClick={() => handleUpload('predict-clv')}>Predict CLV</button>
            <button onClick={() => handleUpload('predict-churn')}>Predict Churn</button>

            <h3>CLV Predictions:</h3>
            <ul>{clvPredictions.map((p, index) => <li key={index}>{p}</li>)}</ul>

            <h3>Churn Predictions:</h3>
            <ul>{churnPredictions.map((p, index) => <li key={index}>{p}</li>)}</ul>
        </div>
    );
};

export default UploadForm;
