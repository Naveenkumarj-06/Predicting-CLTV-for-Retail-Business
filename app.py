from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.impute import SimpleImputer


app = Flask(__name__)
CORS(app)

# Model file paths
CLV_MODEL_PATH = "models/cltv_model.pkl"
CHURN_MODEL_PATH = "models/churn_model.pkl"
SCALER_PATH = "models/scaler.pkl"

def process_data(file):
    """
    Process input file (either a file object from request or a file path).
    Returns a cleaned Pandas DataFrame or an error string.
    """
    try:
        if isinstance(file, str):  # If file is a path
            print(f"Processing file from path: {file}")
            df = pd.read_csv(file, encoding="ISO-8859-1")
        else:  # If it's an uploaded file
            print(f"Processing uploaded file: {file.filename}")
            df = pd.read_csv(file, encoding="ISO-8859-1")

        print("Initial Dataframe Columns:", df.columns)  # Debugging log

        # Standardize column names (convert to lowercase, remove spaces)
        df.columns = df.columns.str.strip().str.lower()

        # Possible valid column sets
        expected_sets = [
            {'customerid', 'quantity', 'unitprice', 'invoicedate'},  # Original
            {'customerid', 'recency', 'frequency', 'monetary'},  # Another format
            {'customerid', 'last_transaction', 'first_transaction', 'frequency', 'monetary', 'recency', 'tenure', 'churn'},
        ]

        # Check if file contains at least one expected column set
        matched_set = next((cols for cols in expected_sets if cols.issubset(df.columns)), None)

        if not matched_set:
            raise ValueError(f"Missing required columns! Found: {df.columns}")

        # Handle different formats dynamically
        if 'invoicedate' in df.columns:  # Original dataset format
            df['customerid'] = pd.to_numeric(df['customerid'], errors='coerce')
            df['invoicedate'] = pd.to_datetime(df['invoicedate'], errors='coerce')
            df['recency'] = (df['invoicedate'].max() - df['invoicedate']).dt.days
            df['monetary'] = np.log1p(df['quantity'].clip(lower=1) * df['unitprice'].clip(lower=0.01))
            df['frequency'] = df.groupby('customerid')['invoicedate'].transform('count')
        elif 'last_transaction' in df.columns:  # Alternative format
            df['customerid'] = df['customerid']
            df['recency'] = df['recency']
            df['monetary'] = df['monetary']
            df['frequency'] = df['frequency']

        df = df[['customerid', 'recency', 'frequency', 'monetary']].drop_duplicates()

        # 🔹 **Handle missing values using SimpleImputer**
        imputer = SimpleImputer(strategy='mean')  # You can also use 'median' or 'most_frequent'
        df.iloc[:, 1:] = imputer.fit_transform(df.iloc[:, 1:])  # Only apply to numerical columns

        print("Processed Dataframe Sample:\n", df.head())  # Debugging log

        return df

    except Exception as e:
        print("Error in process_data:", str(e))
        return str(e)  # Return the error message

def train_models():
    if not os.path.exists("models"):
        os.makedirs("models")

    file_path = "data.csv"
    if not os.path.exists(file_path):
        print("Dataset not found, skipping model training.")
        return

    df = process_data(file_path)
    if not isinstance(df, pd.DataFrame):
        print(f"Data processing failed: {df}")
        return

    try:
        # Select features
        X = df[['recency', 'frequency', 'monetary']]
        y_clv = df['monetary']
        y_churn = (df['recency'] > 90).astype(int)

        # 🔹 Handle missing values
        missing_before = X.isna().sum().sum()
        X = X.dropna()  # Drop rows with NaN values
        missing_after = X.isna().sum().sum()

        if missing_before > 0:
            print(f"⚠️ Dropped {missing_before - missing_after} rows due to NaN values.")

        # Scale the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train CLV model
        clv_model = LinearRegression()
        clv_model.fit(X_scaled, y_clv.loc[X.index])  # Only train on non-NaN data

        # Train Churn model
        churn_model = LogisticRegression()
        churn_model.fit(X_scaled, y_churn.loc[X.index])  # Only train on non-NaN data

        # Save models
        joblib.dump(clv_model, CLV_MODEL_PATH)
        joblib.dump(churn_model, CHURN_MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)

        print("✅ Models trained and saved successfully!")

    except Exception as e:
        print(f"❌ Model training error: {str(e)}")

@app.route('/predict-clv', methods=['POST'])
def predict_clv():
    """
    Predict Customer Lifetime Value (CLV) based on uploaded CSV file.
    """
    if not os.path.exists(CLV_MODEL_PATH) or not os.path.exists(SCALER_PATH):
        return jsonify({'error': 'CLV model or scaler not found. Train the model first!'}), 500

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        df = process_data(file)
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': f'Data processing failed: {df}'}), 400

        # Load model and scaler
        scaler = joblib.load(SCALER_PATH)
        model = joblib.load(CLV_MODEL_PATH)

        X_scaled = scaler.transform(df[['recency', 'frequency', 'monetary']])
        predictions = model.predict(X_scaled)

        return jsonify({'predictions': predictions.tolist()})

    except Exception as e:
        print("❌ Error in predict_clv:", str(e))
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500


@app.route('/predict-churn', methods=['POST'])
def predict_churn():
    """
    Predict Customer Churn based on uploaded CSV file.
    """
    if not os.path.exists(CHURN_MODEL_PATH) or not os.path.exists(SCALER_PATH):
        return jsonify({'error': 'Churn model or scaler not found. Train the model first!'}), 500

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        df = process_data(file)
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': f'Data processing failed: {df}'}), 400

        # Load model and scaler
        scaler = joblib.load(SCALER_PATH)
        model = joblib.load(CHURN_MODEL_PATH)

        X_scaled = scaler.transform(df[['recency', 'frequency', 'monetary']])
        predictions = model.predict(X_scaled)

        return jsonify({'predictions': predictions.tolist()})

    except Exception as e:
        print("❌ Error in predict_churn:", str(e))
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500
    
@app.route("/manual-predict", methods=["POST"])
def manual_predict():
    try:
        data = request.json
        purchases = float(data["purchases"])
        frequency = float(data["frequency"])
        tenure = float(data["tenure"])
        avg_order_value = float(data["avg_order_value"])

        # Simple CLV Calculation Formula
        clv = purchases * frequency * avg_order_value * tenure

        # Dummy Churn Prediction (Replace with ML Model)
        churn = 1 if clv < 500 else 0

        return jsonify({"clv": clv, "churn": churn})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def home():
    return "Welcome to the CLV & Churn Prediction API. Use /predict-clv or /predict-churn endpoints."


if __name__ == '__main__':
    train_models()  # Ensure models are trained before running
    app.run(debug=True)
