# ChurnIQ — Customer Churn Prediction

ChurnIQ is a machine learning-based customer churn prediction system built using Python, Flask, React, and SQLite. It helps analyze customer data, predict churn probability, and visualize patterns that can support customer retention decisions.

## Features

- **Customer Churn Prediction:** Predict whether a customer is likely to leave.
- **Churn Probability:** Display the model's estimated churn probability.
- **Analytics Dashboard:** Visualize churn distribution, contract patterns, payment methods, and customer tenure.
- **Customer Explorer:** Search, filter, and browse customer records.
- **Prediction History:** Store and review previous predictions.
- **CSV Export:** Export customer data from the customer explorer.
- **Responsive Interface:** Dark-themed dashboard designed for different screen sizes.

## Tech Stack

| Area | Technologies |
|---|---|
| Frontend | React, Vite, CSS |
| Backend | Python, Flask |
| Machine Learning | Scikit-learn, XGBoost, Pandas, NumPy |
| Data Visualization | Recharts |
| Database | SQLite |
| Model Persistence | Joblib |

## Machine Learning

The project uses the Telco Customer Churn dataset.

Models evaluated:
- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost

The models were compared using cross-validation with F1-score as the primary selection metric. XGBoost achieved the best cross-validation F1-score among the evaluated models.

The preprocessing pipeline includes:
- Handling missing values
- Numerical feature scaling
- Categorical feature encoding
- Stratified train-test splitting

## Project Structure

```text
ChurnIQ/
├── data/
│   ├── raw/
│   └── processed/
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       └── pages/
├── models/
├── reports/
├── src/
│   ├── app.py
│   ├── data_inspection.py
│   ├── data_preprocessing.py
│   ├── eda.py
│   ├── feature_engineering.py
│   └── model_training.py
├── requirements.txt
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ChurnIQ.git
cd ChurnIQ
```

### 2. Set up the Python environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the Flask backend

```bash
python src/app.py
```

The backend runs at:

`http://127.0.0.1:5000`

### 4. Start the React frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite, usually:

`http://localhost:5173`

## Model Performance

The best model was selected using cross-validation F1-score.

| Model | Cross-validation F1-score |
|---|---:|
| Logistic Regression | 0.6293 |
| Decision Tree | 0.5863 |
| Random Forest | 0.6324 |
| XGBoost | 0.6347 |

*These are cross-validation scores, not test-set scores.*

## Project Status

Developed as a machine learning and full-stack development project.

## Author

Rishith Bhardwaj

B.Tech — Electronics and Communication Engineering

GitHub: https://github.com/rishithbhardwaj