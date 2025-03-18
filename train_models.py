import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def process_data(file_path):
    """Load dataset and compute RFM metrics."""
    try:
        # Load CSV with proper encoding
        df = pd.read_csv(file_path, encoding="ISO-8859-1")

        # Convert column names to lowercase
        df.columns = df.columns.str.lower()

        # Ensure expected columns exist
        expected_cols = {'invoiceno', 'customerid', 'invoicedate', 'quantity', 'unitprice'}
        if not expected_cols.issubset(set(df.columns)):
            raise ValueError(f"Missing expected columns! Found: {list(df.columns)}")

        # Remove rows where CustomerID is missing
        df = df.dropna(subset=['customerid'])

        # Convert customerid to integer
        df['customerid'] = df['customerid'].astype(int)

        # Convert invoicedate to datetime
        df['invoicedate'] = pd.to_datetime(df['invoicedate'])

        # Calculate monetary value (total revenue per transaction)
        df['total_price'] = df['quantity'] * df['unitprice']

        # Set snapshot date (assume max invoice date as today)
        snapshot_date = df['invoicedate'].max()

        # Compute RFM metrics
        rfm = df.groupby('customerid').agg({
            'invoicedate': lambda x: (snapshot_date - x.max()).days,  # Recency
            'invoiceno': 'count',  # Frequency
            'total_price': 'sum'   # Monetary
        }).reset_index()

        # Rename columns
        rfm.columns = ['customerid', 'recency', 'frequency', 'monetary']

        # Ensure monetary is positive
        rfm = rfm[rfm['monetary'] > 0]

        # Apply log transformation to monetary
        rfm['monetary'] = np.log1p(rfm['monetary'])

        return rfm

    except Exception as e:
        print(f"Error processing data: {e}")
        return None


def train_models(file_path):
    """Train clustering model using RFM data."""
    df = process_data(file_path)
    
    if df is None:
        print("Data processing failed. Check your dataset!")
        return

    print("Training models with the following data:")
    print(df.head())

    # Extract features
    X = df[['recency', 'frequency', 'monetary']].values

    # Handle infinite values
    X[np.isinf(X)] = np.nan
    X = np.nan_to_num(X, nan=np.nanmax(X))  # Replace NaNs with max finite value

    # Standardize data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train K-Means model
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    # Save models
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    with open("kmeans_model.pkl", "wb") as f:
        pickle.dump(kmeans, f)

    print("Models trained and saved successfully!")

if __name__ == "__main__":
    train_models("data.csv")
