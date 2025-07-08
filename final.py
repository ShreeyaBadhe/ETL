import pandas as pd
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='24112001',
    database='weather_db'
)

# Query the full dataset
query = "SELECT * FROM weather_forecast;"
df = pd.read_sql(query, conn)

# Close connection
conn.close()

# Preview the data
print(df.shape)
print(df.head())
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# --- Step 1: Extract hour from forecast_hour ---
# Step 1: Safely extract hour from forecast_hour
df['hour'] = df['forecast_hour'].astype(str).str.slice(0, 2).astype(int)

# --- Step 2: Select features and target ---
features = [
    'hour', 'humidity', 'dewpoint_c',
    'wind_kph', 'gust_kph', 'cloud',
    'uv_index', 'pressure_mb', 'chance_of_rain'
]


target = 'temp_c'

# --- Step 3: Drop rows with missing values in selected columns ---
df_model = df[features + [target]].dropna()

# --- Step 4: Split into train/test ---
X = df_model[features]
y = df_model[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
# Evaluation metrics
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"📉 Mean Absolute Error: {mae:.2f}°C")
print(f"📈 R² Score: {r2:.2f}")
importances = model.feature_importances_
for f, imp in zip(X.columns, importances):
    print(f"{f}: {imp:.4f}")

from sklearn.metrics import mean_absolute_error, r2_score

# Evaluate on training data
y_train_pred = model.predict(X_train)
train_mae = mean_absolute_error(y_train, y_train_pred)
train_r2 = r2_score(y_train, y_train_pred)

print(f"Train MAE: {train_mae:.2f} | Train R²: {train_r2:.2f}")

from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
print(f"Cross-validated R² scores: {cv_scores}")
print(f"Mean R²: {cv_scores.mean():.2f}")


