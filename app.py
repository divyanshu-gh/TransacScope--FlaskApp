from flask import Flask, render_template, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DATA_PATH = 'data/Fraud_Detection_Dataset.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_dataset():
    # Load the default dataset (no user-specific file)
    df = pd.read_csv(DATA_PATH)

    # Add synthetic date column if not present
    if 'Date' not in df.columns:
        df['Date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')

    df['High_Risk_User'] = df['Previous_Fraudulent_Transactions'].apply(lambda x: 'Yes' if x >= 3 else 'No')
    return df

@app.route('/')
def home():
    return redirect('/dashboard')  # Redirect to the dashboard after visiting the home page

@app.route('/dashboard')
def dashboard():
    df = load_dataset()

    # Stats
    total_txn = df.shape[0]
    total_fraud = df['Fraudulent'].sum()
    total_non_fraud = total_txn - total_fraud
    fraud_rate = round((total_fraud / total_txn) * 100, 2)
    top_users = df[df['High_Risk_User'] == 'Yes'].nlargest(5, 'Previous_Fraudulent_Transactions')

    # Fraud trend
    fraud_trend = df.groupby(df['Date'].dt.to_period("M")).agg({'Fraudulent': 'sum'})
    fraud_trend.index = fraud_trend.index.astype(str)
    trend_labels = list(fraud_trend.index)
    trend_values = list(fraud_trend['Fraudulent'])

    return render_template('index.html',
                           total_txn=total_txn,
                           total_fraud=total_fraud,
                           total_non_fraud=total_non_fraud,
                           fraud_rate=fraud_rate,
                           top_users=top_users.to_dict(orient='records'),
                           trend_labels=trend_labels,
                           trend_values=trend_values)

if __name__ == '__main__':
    app.run(debug=True)
