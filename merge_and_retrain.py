import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Paths
BASE_DATASET = "Gas_Sensors_Measurements.csv"
LIVE_LABELED = "my_collected_data_labeled.csv"  # produced by label script or pipeline
OUT_MODEL = "final_model_6class.pkl"

if not os.path.exists(BASE_DATASET):
    raise SystemExit(f"Base dataset not found at '{BASE_DATASET}'")
if not os.path.exists(LIVE_LABELED):
    raise SystemExit(f"Live labeled dataset not found at '{LIVE_LABELED}' (run labeling first)")

df1 = pd.read_csv(BASE_DATASET)
df2 = pd.read_csv(LIVE_LABELED)

# sensor detection
def pick_sensor(df):
    for c in df.columns:
        lc = c.lower()
        if "mq" in lc or "adc" in lc or "sensor" in lc:
            return c
    numerics = df.select_dtypes(include=[np.number]).columns
    if len(numerics) == 0:
        raise RuntimeError("No numeric column found for sensor.")
    return numerics[0]

s1 = pick_sensor(df1)
s2 = pick_sensor(df2)

df1 = df1.rename(columns={s1: "sensor"})
df2 = df2.rename(columns={s2: "sensor"})

# ensure temp/humidity columns exist or fill with 0
def ensure_temp_hum(df):
    if "temp" not in df.columns:
        for c in df.columns:
            if c.lower() in ("temperature", "temp", "t"):
                df["temp"] = df[c]
                break
        else:
            df["temp"] = 0
    if "humidity" not in df.columns:
        for c in df.columns:
            if c.lower() in ("humidity", "rh"):
                df["humidity"] = df[c]
                break
        else:
            df["humidity"] = 0

ensure_temp_hum(df1)
ensure_temp_hum(df2)

# Create labels for base dataset using the same absolute bins if missing
if "label" not in df1.columns:
    proxy = df1["sensor"].fillna(0).values
    bins = [0, 200, 400, 800, 1400, 2600, 4095]
    df1["label"] = np.digitize(proxy, bins[1:], right=True)

# Ensure df2 has label
if "label" not in df2.columns:
    raise SystemExit("Live labeled dataset must contain 'label' column. Run labeling script first.")

# Combine datasets
combined = pd.concat([
    df1[["sensor", "temp", "humidity", "label"]],
    df2[["sensor", "temp", "humidity", "label"]]
], ignore_index=True).dropna()

X = combined[["sensor", "temp", "humidity"]].values
y = combined["label"].astype(int).values

scaler = StandardScaler()
Xs = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.2, random_state=42, stratify=y)

clf = RandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

print("Classification report (final model):")
print(classification_report(y_test, clf.predict(X_test)))

joblib.dump({"model": clf, "scaler": scaler, "features": ["sensor", "temp", "humidity"]}, OUT_MODEL)
print(f"Saved final model to {OUT_MODEL}")
