
# ==========================================
# CHURNIQ - MODEL TRAINING
# ==========================================

import pandas as pd
import numpy as np
import joblib

from pathlib import Path

# Machine Learning Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Model Evaluation
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)
# Hyperparameter Tuning
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from scipy.stats import randint, uniform

# ==========================================
# PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\n========== CHURNIQ MODEL TRAINING ==========")
print("Project paths configured successfully!")


# ==========================================
# LOAD PROCESSED DATA
# ==========================================

X_train = pd.read_csv(DATA_DIR / "X_train.csv")
X_test = pd.read_csv(DATA_DIR / "X_test.csv")

y_train = pd.read_csv(DATA_DIR / "y_train.csv").squeeze("columns")
y_test = pd.read_csv(DATA_DIR / "y_test.csv").squeeze("columns")

print("\nDataset Loaded Successfully!")

print("X_train Shape:", X_train.shape)
print("X_test Shape:", X_test.shape)

print("y_train Shape:", y_train.shape)
print("y_test Shape:", y_test.shape)

print("\nTraining Target Distribution:")
print(y_train.value_counts())


# ==========================================
# INITIALIZE MACHINE LEARNING MODELS
# ==========================================

print("\n========== INITIALIZING MODELS ==========")

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=8,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost": XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=2.77,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)
}

print("\nModels Initialized Successfully!")

for model_name in models:
    print(model_name)


# ==========================================
# TRAIN MACHINE LEARNING MODELS
# ==========================================

print("\n========== MODEL TRAINING STARTED ==========")

trained_models = {}

for model_name, model in models.items():

    print(f"\nTraining {model_name}...")

    model.fit(X_train, y_train)

    trained_models[model_name] = model

    print(f"{model_name} trained successfully!")

print("\n========== ALL MODELS TRAINED ==========")


# ==========================================
# MODEL EVALUATION
# ==========================================

print("\n========== MODEL EVALUATION ==========")

results = []

for model_name, model in trained_models.items():

    print(f"\nEvaluating {model_name}...")

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "ROC-AUC": roc_auc
    })

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

# Create comparison table
results_df = pd.DataFrame(results)

print("\n========== MODEL COMPARISON ==========")
print(results_df.to_string(index=False))

# Save evaluation results
results_df.to_csv(
    REPORT_DIR / "model_comparison.csv",
    index=False
)

print("\nModel evaluation completed successfully!")


# ==========================================
# HYPERPARAMETER TUNING
# ==========================================

print("\n========== HYPERPARAMETER TUNING ==========")

# Cross-validation strategy
cv_strategy = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

# Define parameter search spaces
param_grids = {

    "Logistic Regression": {
        "C": uniform(0.01, 10),
        "solver": ["lbfgs", "liblinear"]
    },

    "Decision Tree": {
        "max_depth": randint(3, 16),
        "min_samples_split": randint(2, 20),
        "min_samples_leaf": randint(1, 10)
    },

    "Random Forest": {
        "n_estimators": randint(100, 301),
        "max_depth": randint(5, 20),
        "min_samples_split": randint(2, 15),
        "min_samples_leaf": randint(1, 8)
    },

    "XGBoost": {
        "n_estimators": randint(100, 301),
        "max_depth": randint(3, 9),
        "learning_rate": uniform(0.01, 0.19),
        "subsample": uniform(0.7, 0.3),
        "colsample_bytree": uniform(0.7, 0.3)
    }
}

# Store tuned models
tuned_models = {}
tuned_results = []

# Tune each model
for model_name, model in models.items():

    print(f"\nTuning {model_name}...")

    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_grids[model_name],
        n_iter=10,
        scoring="f1",
        cv=cv_strategy,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )

    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    tuned_models[model_name] = best_model

    # Evaluate tuned model on test data
    y_pred = best_model.predict(X_test)

    tuned_f1 = f1_score(
        y_test, y_pred, zero_division=0
    )

    tuned_accuracy = accuracy_score(y_test, y_pred)

    tuned_results.append({
        "Model": model_name,
        "Best CV F1": search.best_score_,
        "Test Accuracy": tuned_accuracy,
        "Test F1 Score": tuned_f1
    })

    print(f"Best Parameters: {search.best_params_}")
    print(f"Best CV F1 Score: {search.best_score_:.4f}")
    print(f"Test F1 Score: {tuned_f1:.4f}")

# Create tuned model comparison
tuned_results_df = pd.DataFrame(tuned_results)

print("\n========== TUNED MODEL COMPARISON ==========")
print(tuned_results_df.to_string(index=False))

# Save tuning results
tuned_results_df.to_csv(
    REPORT_DIR / "tuned_model_comparison.csv",
    index=False
)

print("\nHyperparameter tuning completed successfully!")



from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report,
    roc_curve,
    auc
)

import matplotlib.pyplot as plt
import seaborn as sns


# ==========================================
# CONFUSION MATRIX ANALYSIS
# ==========================================

print("\n========== CONFUSION MATRIX ANALYSIS ==========")

for model_name, model in tuned_models.items():
    y_pred = model.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(7, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["No Churn", "Churn"],
        yticklabels=["No Churn", "Churn"]
    )

    plt.title(f"Confusion Matrix - {model_name}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png",
        dpi=300
    )

    plt.show()

    print(f"\n{model_name} Classification Report:")
    print(classification_report(y_test, y_pred))


# ==========================================
# ROC CURVE COMPARISON
# ==========================================

plt.figure(figsize=(10, 7))

for model_name, model in tuned_models.items():

    y_prob = model.predict_proba(X_test)[:, 1]

    fpr, tpr, thresholds = roc_curve(y_test, y_prob)

    roc_auc_value = auc(fpr, tpr)

    plt.plot(
        fpr,
        tpr,
        label=f"{model_name} (AUC = {roc_auc_value:.3f})"
    )

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Random Classifier"
)

plt.title("ROC Curve Comparison - ChurnIQ")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.legend()
plt.tight_layout()

plt.savefig(
    REPORT_DIR / "roc_curve_comparison.png",
    dpi=300
)

plt.show()

print("\nCONFUSION MATRIX AND ROC ANALYSIS COMPLETED!")

# ==========================================
# SAVE BEST TUNED MODEL
# ==========================================

# Find model with highest cross-validation F1
best_model_index = tuned_results_df["Best CV F1"].idxmax()

best_model_name = tuned_results_df.loc[
    best_model_index, "Model"
]

best_model = tuned_models[best_model_name]

# Save the best model
joblib.dump(
    best_model,
    MODEL_DIR / "best_churn_model.pkl"
)

print("\nBEST MODEL SAVED SUCCESSFULLY!")
print("Best Model:", best_model_name)
print("Best CV F1:", tuned_results_df.loc[
    best_model_index, "Best CV F1"
])

# Save fitted preprocessing pipeline
joblib.dump(
    joblib.load(
        PROJECT_ROOT / "data" / "processed" / "preprocessor.joblib"
    ),
    MODEL_DIR / "preprocessor.joblib"
)

print("Preprocessor saved successfully!")

