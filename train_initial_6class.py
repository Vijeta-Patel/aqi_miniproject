import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

# Path to your base dataset (change only if your CSV is elsewhere)
BASE_DATASET = "Gas_Sensors_Measurements.csv"

if not os.path.exists(BASE_DATASET):
    raise SystemExit(f"Base dataset not found at '{BASE_DATASET}'")

# Load dataset
df = pd.read_csv(BASE_DATASET)

# pick a numeric sensor column heuristically
num_cols = df.select_dtypes(include=[np.number]).columns
if len(num_cols) == 0:
    raise SystemExit("No numeric columns found in dataset.")

sensor_col = None
for c in df.columns:
    lc = c.lower()
    if "mq" in lc or "adc" in lc or "sensor" in lc:
        sensor_col = c
        break
if sensor_col is None:
    sensor_col = num_cols[0]

# Proxy values (sensor readings)
proxy = df[sensor_col].fillna(0).values

# ----- Option C: absolute ADC bins (0 - 4095) -----
bins = [0, 200, 400, 800, 1400, 2600, 4095]
# create 6 classes using np.digitize (labels 0..5)
df['label'] = np.digitize(proxy, bins[1:], right=True)

# select features (sensor + optional temp/humidity)
features = [sensor_col]
for c in df.columns:
    lc = c.lower()
    if lc in ("temp", "temperature", "t") and "temp" not in features:
        features.append(c)
    if lc in ("rh", "humidity") and "humidity" not in features:
        features.append(c)

X = df[features].fillna(0).values
y = df['label'].astype(int).values

# scale and train
scaler = StandardScaler()
Xs = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.2, random_state=42, stratify=y)

clf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

print("Classification report (on test split):")
print(classification_report(y_test, clf.predict(X_test)))

# Save model and scaler and feature names
joblib.dump({"model": clf, "scaler": scaler, "features": features}, "initial_model_6class.pkl")
print("Saved initial_model_6class.pkl")
