# ChurnIQ — Customer Churn Prediction Platform

ChurnIQ is a machine learning-powered customer intelligence platform that predicts customer churn and helps businesses identify customers who are likely to discontinue their services.

The application combines a trained XGBoost classification model with an interactive React dashboard and Flask API to provide customer predictions, analytics, and prediction history.

## Live Demo

**Frontend:** https://churn-42pm5ximj-churn-iq.vercel.app/

**GitHub Repository:** https://github.com/rishithbhardwaj/ChurnIQ

## Features

- **Customer Churn Prediction:** Predict whether a customer is likely to churn using a trained machine learning model.
- **Churn Probability:** Display the estimated probability of customer churn.
- **Customer Management:** Browse, search, and filter customer records.
- **Analytics Dashboard:** Visualize customer distribution, churn rate, and retention metrics.
- **Business Insights:** Present insights derived from customer data.
- **Prediction History:** Store and review previous prediction records.
- **Responsive Interface:** Modern dashboard designed for different screen sizes.
- **REST API:** Flask backend connects the machine learning model to the frontend.

## Model Performance

The project evaluates multiple machine learning algorithms and uses hyperparameter tuning with cross-validation to select the best-performing model.

| Metric | Result |
|---|---:|
| Selected Model | XGBoost |
| Test Accuracy | 76.15% |
| Test F1-Score | 0.6371 |

*Results are from the project's reported test-set evaluation.*

## Technology Stack

**Frontend**
- React.js
- Vite
- JavaScript
- HTML5
- CSS3

**Backend**
- Python
- Flask
- REST API

**Machine Learning**
- Scikit-learn
- XGBoost
- Pandas
- NumPy
- Joblib

**Database**
- SQLite

**Deployment**
- Vercel — Frontend
- Render — Backend

## Project Structure

```text
ChurnIQ/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── App.jsx
│       └── main.jsx
│
├── models/
│   ├── best_churn_model.pkl
│   └── preprocessor.joblib
│
├── reports/
│
├── src/
│   ├── app.py
│   ├── data_inspection.py
│   ├── data_preprocessing.py
│   ├── eda.py
│   ├── feature_engineering.py
│   └── model_training.py
│
├── requirements.txt
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/rishithbhardwaj/ChurnIQ.git
cd ChurnIQ
```

### 2. Set up the Python backend

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python src/app.py
```

The backend runs at:

`http://127.0.0.1:5000`

### 3. Set up the React frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local Vite URL shown in the terminal, usually:

`http://localhost:5173`

## Machine Learning Workflow

1. Dataset inspection and exploratory data analysis.
2. Data cleaning and preprocessing.
3. Feature engineering.
4. Model training and comparison.
5. Hyperparameter tuning and cross-validation.
6. Model evaluation on the test dataset.
7. Saving the trained model and preprocessing pipeline.
8. Integrating the model with the Flask API.
9. Displaying predictions and analytics through the React dashboard.

## Project Objective

The objective of ChurnIQ is to demonstrate how machine learning can support customer retention by identifying potential churn risks and presenting actionable customer intelligence through an interactive web application.

## Author

Rishith Bhardwaj

GitHub: https://github.com/rishithbhardwaj
