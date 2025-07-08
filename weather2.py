
import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from xgboost import XGBClassifier

# Step 1: Connect to MySQL and load data
conn = mysql.connector.connect(
    host="localhost",
    user="root",         
    password="24112001",     
    database="weather_db"
)
df = pd.read_sql("SELECT * FROM weather_forecast WHERE state = 'Oregon'", conn)
conn.close()

# Step 2: Preprocessing
df['hour'] = df['forecast_hour'].astype(str).str.slice(0, 2).astype(int)
df["precip_mm"] = df["precip_mm"].fillna(0.0)
df["day_of_week"] = pd.to_datetime(df["forecast_date"]).dt.dayofweek
df["is_morning"] = df["hour"].apply(lambda x: 1 if 5 <= x <= 11 else 0)

# --- Regression: Predict precip_mm ---
X_reg = df[["humidity", "dewpoint_c", "cloud", "wind_kph", "gust_kph", "uv_index", "hour", "day_of_week", "is_morning"]]
y_reg = df["precip_mm"]

X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

reg_model = RandomForestRegressor()
reg_model.fit(X_train_reg, y_train_reg)
reg_preds = reg_model.predict(X_test_reg)

rmse = np.sqrt(mean_squared_error(y_test_reg, reg_preds))
print("🌧️ RMSE for Precipitation (mm):", rmse)

# --- Classification: Predict Weather Type (Sunny/Cloudy/Overcast) ---
df["weather_type"] = df["condition_text"].map({
    "Sunny": "sunny",
    "Clear": "sunny",
    "Partly cloudy": "cloudy",
    "Cloudy": "cloudy",
    "Overcast": "overcast"
})
df = df[df["weather_type"].notna()]

le = LabelEncoder()
df["weather_code"] = le.fit_transform(df["weather_type"])

X_clf = df[["humidity", "dewpoint_c", "cloud", "wind_kph", "gust_kph", "uv_index", "hour", "day_of_week", "is_morning"]]
y_clf = df["weather_code"]

X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42)

clf_model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
clf_model.fit(X_train_clf, y_train_clf)
clf_preds = clf_model.predict(X_test_clf)

print("\n☀️ Weather Type Classification Report:")
print(classification_report(y_test_clf, clf_preds, target_names=le.classes_))

# --- Confusion Matrix ---
cm = confusion_matrix(y_test_clf, clf_preds)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
plt.title("☀️ Weather Type Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()
