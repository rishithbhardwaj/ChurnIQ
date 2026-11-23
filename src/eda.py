
import pandas as pd
from pathlib import Path

# Load cleaned dataset
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT / "data" / "processed"
    / "telco_customer_churn_cleaned.csv"
)

df = pd.read_csv(DATA_PATH)

print("\n========== CHURNIQ: EDA ==========\n")

# 1. Dataset overview
print("Dataset Shape:", df.shape)

# 2. Churn distribution
print("\nChurn Distribution:")
print(df["Churn"].value_counts())

# 3. Churn percentage
print("\nChurn Percentage:")
print(
    df["Churn"].value_counts(normalize=True) * 100
)

# 4. Customer churn rate
churn_rate = (df["Churn"] == "Yes").mean() * 100


import matplotlib.pyplot as plt
import seaborn as sns

# 5. Churn Distribution Visualization

plt.figure(figsize=(8, 5))

sns.countplot(
    data=df,
    x="Churn",
    hue="Churn",
    palette=["#2ecc71", "#e74c3c"],
    legend=False
)

plt.title("Customer Churn Distribution", fontsize=15)
plt.xlabel("Customer Churn")
plt.ylabel("Number of Customers")

plt.tight_layout()

# Save visualization
PROJECT_ROOT.joinpath("reports").mkdir(
    parents=True, exist_ok=True
)

plt.savefig(
    PROJECT_ROOT / "reports" / "churn_distribution.png",
    dpi=300
)

plt.show()


# 6. Tenure vs Customer Churn

plt.figure(figsize=(10, 6))

sns.histplot(
    data=df,
    x="tenure",
    hue="Churn",
    bins=30,
    multiple="stack",
    palette=["#2ecc71", "#e74c3c"]
)

plt.title("Customer Tenure vs Churn", fontsize=15)
plt.xlabel("Tenure (Months)")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "tenure_vs_churn.png",
    dpi=300
)

plt.show()

print("Tenure vs Churn chart saved successfully!")


print("Churn distribution chart saved successfully!")


# 7. Churn Rate by Tenure Groups

df["TenureGroup"] = pd.cut(
    df["tenure"],
    bins=[-1, 12, 24, 36, 48, 60, 72],
    labels=[
        "0-12 Months",
        "13-24 Months",
        "25-36 Months",
        "37-48 Months",
        "49-60 Months",
        "61-72 Months"
    ]
)

tenure_churn = df.groupby(
    "TenureGroup",
    observed=False
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
)

print("\nChurn Rate by Tenure Group:")
print(tenure_churn)

plt.figure(figsize=(10, 5))

sns.barplot(
    x=tenure_churn.index,
    y=tenure_churn.values,
    hue=tenure_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Customer Tenure")
plt.xlabel("Tenure Group")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "tenure_churn_rate.png",
    dpi=300
)

plt.show()


# 8. Churn Rate by Contract Type

contract_churn = df.groupby(
    "Contract"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
)

print("\nChurn Rate by Contract Type:")
print(contract_churn)

plt.figure(figsize=(9, 5))

sns.barplot(
    x=contract_churn.index,
    y=contract_churn.values,
    hue=contract_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Contract Type")
plt.xlabel("Contract Type")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "contract_churn_rate.png",
    dpi=300
)

plt.show()


# 9. Churn Rate by Payment Method

payment_churn = df.groupby(
    "PaymentMethod"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Payment Method:")
print(payment_churn)

plt.figure(figsize=(11, 6))

sns.barplot(
    x=payment_churn.index,
    y=payment_churn.values,
    hue=payment_churn.index,
    palette="magma",
    legend=False
)

plt.title("Churn Rate by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "payment_method_churn.png",
    dpi=300
)

plt.show()


# 10. Monthly Charges vs Churn

plt.figure(figsize=(9, 6))

sns.boxplot(
    data=df,
    x="Churn",
    y="MonthlyCharges",
    hue="Churn",
    palette="Set2",
    legend=False
)

plt.title("Monthly Charges vs Customer Churn")
plt.xlabel("Customer Churn")
plt.ylabel("Monthly Charges")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "monthly_charges_churn.png",
    dpi=300
)

plt.show()

# Average Monthly Charges by Churn

print("\nAverage Monthly Charges by Churn:")
print(df.groupby("Churn")["MonthlyCharges"].mean())


# 11. Churn Rate by Internet Service

internet_churn = df.groupby(
    "InternetService"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Internet Service:")
print(internet_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=internet_churn.index,
    y=internet_churn.values,
    hue=internet_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Internet Service")
plt.xlabel("Internet Service")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "internet_service_churn.png",
    dpi=300
)

plt.show()


# 12. Churn Rate by Online Security

security_churn = df.groupby(
    "OnlineSecurity"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
)

print("\nChurn Rate by Online Security:")
print(security_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=security_churn.index,
    y=security_churn.values,
    hue=security_churn.index,
    palette="Set2",
    legend=False
)

plt.title("Churn Rate by Online Security")
plt.xlabel("Online Security Subscription")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "online_security_churn.png",
    dpi=300
)

plt.show()


# 13. Churn Rate by Tech Support

support_churn = df.groupby(
    "TechSupport"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Tech Support:")
print(support_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=support_churn.index,
    y=support_churn.values,
    hue=support_churn.index,
    palette="coolwarm",
    legend=False
)

plt.title("Churn Rate by Tech Support")
plt.xlabel("Technical Support Subscription")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "tech_support_churn.png",
    dpi=300
)

plt.show()


# 14. Churn Rate by Online Backup

backup_churn = df.groupby(
    "OnlineBackup"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Online Backup:")
print(backup_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=backup_churn.index,
    y=backup_churn.values,
    hue=backup_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Online Backup")
plt.xlabel("Online Backup Subscription")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "online_backup_churn.png",
    dpi=300
)

plt.show()


# 15. Churn Rate by Device Protection

device_churn = df.groupby(
    "DeviceProtection"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Device Protection:")
print(device_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=device_churn.index,
    y=device_churn.values,
    hue=device_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Device Protection")
plt.xlabel("Device Protection Subscription")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "device_protection_churn.png",
    dpi=300
)

plt.show()


# 16. Churn Rate by Streaming TV

streaming_churn = df.groupby(
    "StreamingTV"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Streaming TV:")
print(streaming_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=streaming_churn.index,
    y=streaming_churn.values,
    hue=streaming_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Streaming TV")
plt.xlabel("Streaming TV Subscription")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "streaming_tv_churn.png",
    dpi=300
)

plt.show()


# 17. Churn Rate by Streaming Movies

movies_churn = df.groupby(
    "StreamingMovies"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Streaming Movies:")
print(movies_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=movies_churn.index,
    y=movies_churn.values,
    hue=movies_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Streaming Movies")
plt.xlabel("Streaming Movies Subscription")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "streaming_movies_churn.png",
    dpi=300
)

plt.show()


# 18. Churn Rate by Paperless Billing

billing_churn = df.groupby(
    "PaperlessBilling"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Paperless Billing:")
print(billing_churn)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=billing_churn.index,
    y=billing_churn.values,
    hue=billing_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Paperless Billing")
plt.xlabel("Paperless Billing")
plt.ylabel("Churn Rate (%)")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "paperless_billing_churn.png",
    dpi=300
)

plt.show()


# 19. Churn Rate by Payment Method

payment_churn = df.groupby(
    "PaymentMethod"
)["Churn"].apply(
    lambda x: (x == "Yes").mean() * 100
).sort_values(ascending=False)

print("\nChurn Rate by Payment Method:")
print(payment_churn)

plt.figure(figsize=(11, 6))

sns.barplot(
    x=payment_churn.index,
    y=payment_churn.values,
    hue=payment_churn.index,
    palette="viridis",
    legend=False
)

plt.title("Churn Rate by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Churn Rate (%)")

plt.xticks(rotation=20, ha="right")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "payment_method_churn.png",
    dpi=300
)

plt.show()


print(f"\nOverall Churn Rate: {churn_rate:.2f}%")

print("\n========== EDA STEP 1 COMPLETED ==========")


# ==============================================
# 14. CORRELATION ANALYSIS
# ==============================================

print("\n========== CORRELATION ANALYSIS ==========")

# Encode Churn column
df["Churn_Encoded"] = df["Churn"].map({
    "No": 0,
    "Yes": 1
})

# Select numerical columns
numeric_df = df.select_dtypes(include="number")

# Calculate correlation matrix
correlation_matrix = numeric_df.corr()

print("\nCorrelation Matrix:")
print(correlation_matrix)

# Correlation with Churn
churn_correlation = (
    correlation_matrix["Churn_Encoded"]
    .drop("Churn_Encoded")
    .sort_values(ascending=False)
)

print("\nCorrelation with Customer Churn:")
print(churn_correlation)

# Generate correlation heatmap
plt.figure(figsize=(12, 8))

sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)

plt.title("Correlation Heatmap - ChurnIQ")

plt.tight_layout()

plt.savefig(
    PROJECT_ROOT / "reports" / "correlation_heatmap.png",
    dpi=300
)

plt.show()
plt.close()

print("\n========== CORRELATION ANALYSIS COMPLETED ==========")
