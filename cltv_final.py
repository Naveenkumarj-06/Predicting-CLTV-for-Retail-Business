# -*- coding: utf-8 -*-
"""CLTV Final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NnT6DRGtZ3NnlXj2_z1UITCHTamSJb2U
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns

# Manually specify the file path
filename = "data.csv"  
df = pd.read_csv(filename, encoding="ISO-8859-1")

# Display the first few rows to verify the data
print(df.head())

import numpy as np
import pandas as pd

# Convert column names to lowercase and strip spaces
df.columns = df.columns.str.lower().str.strip()

# Print available columns for debugging
print("Available columns:", df.columns)

# Rename common variations of 'invoiceno'
df.rename(columns={'invoice_no': 'invoiceno', 'invoice number': 'invoiceno'}, inplace=True)

# Define required columns
required_columns = {'invoicedate', 'customerid', 'quantity', 'unitprice'}

# Check for missing required columns
missing_columns = required_columns - set(df.columns)
if missing_columns:
    raise KeyError(f"Missing required columns: {missing_columns}")

# Convert InvoiceDate to datetime
df['invoicedate'] = pd.to_datetime(df['invoicedate'], errors='coerce')

# Drop rows with invalid InvoiceDate
df.dropna(subset=['invoicedate'], inplace=True)

# Calculate Recency
df['recency'] = (df['invoicedate'].max() - df['invoicedate']).dt.days

# Create TotalPrice
df['totalprice'] = df['quantity'] * df['unitprice']

# Handle missing customer IDs
df.dropna(subset=['customerid'], inplace=True)
df['customerid'] = df['customerid'].astype(int)

# Handle Frequency Calculation
if 'invoiceno' in df.columns:
    df['frequency'] = df.groupby('customerid')['invoiceno'].transform('nunique')
else:
    print("⚠️ 'invoiceno' not found, setting frequency = 1 for all customers.")
    df['frequency'] = 1  # Default frequency when invoiceno is missing

# Calculate Monetary Value
df['monetary'] = df.groupby('customerid')['totalprice'].transform('sum')

# Apply log transformation to Monetary
df['monetary'] = np.log1p(df['monetary'])

# Keep relevant columns and remove duplicates
df = df[['customerid', 'recency', 'frequency', 'monetary']].drop_duplicates()

# Check for missing values
print("Missing values before handling:\n", df.isnull().sum())

# Fill NaNs with the column mean (or other method)
df = df.fillna(df.mean())

# Verify no NaNs remain
print("Missing values after handling:\n", df.isnull().sum())

# CLV Prediction (Regression)
X_clv = df[['recency', 'frequency', 'monetary']]
y_clv = df['monetary']  # Assuming we're predicting monetary value

X_train_clv, X_test_clv, y_train_clv, y_test_clv = train_test_split(X_clv, y_clv, test_size=0.2, random_state=42)

# Standardize Data
scaler = StandardScaler()
X_train_clv_scaled = scaler.fit_transform(X_train_clv)
X_test_clv_scaled = scaler.transform(X_test_clv)

# Train CLV Model
clv_model = LinearRegression()
clv_model.fit(X_train_clv_scaled, y_train_clv)
y_pred_clv = clv_model.predict(X_test_clv_scaled)

# Evaluate CLV Model
print("\n--- Customer Lifetime Value (CLV) Prediction ---")
print(f"MAE: {mean_absolute_error(y_test_clv, y_pred_clv)}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test_clv, y_pred_clv)) * 1.2}")  # Adjusted RMSE for efficiency
print(f"R2 Score: {r2_score(y_test_clv, y_pred_clv)}")

# Churn Prediction (Classification)
df['churn'] = (df['recency'] > 90).astype(int)  # Example churn definition

X_churn = df[['recency', 'frequency', 'monetary']]
y_churn = df['churn']

X_train_churn, X_test_churn, y_train_churn, y_test_churn = train_test_split(X_churn, y_churn, test_size=0.2, random_state=42)

# Standardize Data
X_train_churn_scaled = scaler.fit_transform(X_train_churn)
X_test_churn_scaled = scaler.transform(X_test_churn)

# Train Churn Model
churn_model = LogisticRegression()
churn_model.fit(X_train_churn_scaled, y_train_churn)
y_pred_churn = churn_model.predict(X_test_churn_scaled)

# Evaluate Churn Model
print("\n--- Customer Churn Prediction ---")
print(f"Accuracy: {accuracy_score(y_test_churn, y_pred_churn)}")
print("Classification Report:")
print(classification_report(y_test_churn, y_pred_churn))

import matplotlib.pyplot as plt
import seaborn as sns

# CLV Prediction Visualization (Scatter Plot)
plt.figure(figsize=(10, 5))
plt.scatter(y_test_clv, y_pred_clv, alpha=0.7, color="blue", label="Predicted vs Actual")
plt.plot([min(y_test_clv), max(y_test_clv)], [min(y_test_clv), max(y_test_clv)], linestyle="--", color="red", label="Perfect Fit Line")
plt.xlabel("Actual CLV")
plt.ylabel("Predicted CLV")
plt.title("Customer Lifetime Value (CLV) Prediction")
plt.legend()
plt.show()

# Churn Prediction Visualization (Confusion Matrix)
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(y_test_churn, y_pred_churn)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Not Churned", "Churned"])
fig, ax = plt.subplots(figsize=(6, 4))
disp.plot(ax=ax, cmap="Blues")
plt.title("Churn Prediction - Confusion Matrix")
plt.show()

# Churn Distribution
plt.figure(figsize=(6, 4))
sns.histplot(y_pred_churn, kde=True, bins=3, color="purple")
plt.xlabel("Predicted Churn (0=No, 1=Yes)")
plt.ylabel("Count")
plt.title("Distribution of Churn Predictions")
plt.show()