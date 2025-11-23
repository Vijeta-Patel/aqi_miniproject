# realtime_full_pipeline.py
# Full realtime collector/predictor/retrainer using absolute ADC bins mapping.
# Set SERIAL_PORT appropriately, close Arduino Serial Monitor before running.

import serial
import serial.tools.list_ports
import pandas as pd
import numpy as np
import joblib
import os
import time
import math
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# CONFIG - set your serial port
SERIAL_PORT = "COM7"   # <-- change to your port (e.g., COM3 or /dev/ttyUSB0)
BAUD = 115200

BASE_DATASET = "Gas_Sensors_Measurements.csv"

LIVE_DATASET = "my_realtime_data.csv"
MODEL_FILE = "final_model_6class.pkl"
RETRAIN_INTERVAL = 60  # seconds

AQI_LABELS = [
    "Good",
    "Moderate",
    "Unhealthy for Sensitive Groups",
    "Unhealthy",
    "Very Unhealthy",
    "Hazardous"
]

# sanity checks
if not os.path.exists(BASE_DATASET):
    raise SystemExit(f"Base dataset not found at '{BASE_DATASET}'")

if not os.path.exists(LIVE_DATASET):
    with open(LIVE_DATASET, "w") as f:
        f.write("ts,adc_raw,temp,humidity,label\n")

# retrain merges base + live and creates MODEL_FILE using absolute bins for df1 if needed
def retrain_model():
    try:
        print("\n[TRAIN] Retraining model...")
        df1 = pd.read_csv(BASE_DATASET)
        df2 = pd.read_csv(LIVE_DATASET)

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

        # ensure temp/humidity or fill with 0
        for df in (df1, df2):
            if "temp" not in df.columns:
                found = False
                for c in df.columns:
                    if c.lower() in ("temperature", "temp", "t"):
                        df["temp"] = df[c]; found = True; break
                if not found: df["temp"] = 0
            if "humidity" not in df.columns:
                found = False
                for c in df.columns:
                    if c.lower() in ("humidity", "rh"):
                        df["humidity"] = df[c]; found = True; break
                if not found: df["humidity"] = 0

        # create labels for base dataset using absolute ADC bins (Option C)
        if "label" not in df1.columns:
            proxy = df1["sensor"].fillna(0).values
            bins = [0, 200, 400, 800, 1400, 2600, 4095]
            df1["label"] = np.digitize(proxy, bins[1:], right=True)

        # if df2 has no label, try qcut else digitize
        if "label" not in df2.columns:
            proxy2 = df2["sensor"].fillna(0).values
            try:
                df2["label"] = pd.qcut(proxy2, 6, labels=False)
            except Exception:
                df2["label"] = np.digitize(proxy2, bins[1:], right=True)

        comb = pd.concat([
            df1[["sensor", "temp", "humidity", "label"]],
            df2[["sensor", "temp", "humidity", "label"]]
        ], ignore_index=True).dropna()

        X = comb[["sensor", "temp", "humidity"]].values
        y = comb["label"].astype(int).values

        sc = StandardScaler()
        Xs = sc.fit_transform(X)

        Xtr, Xts, ytr, yts = train_test_split(Xs, y, test_size=0.2, random_state=42)

        clf = RandomForestClassifier(n_estimators=500, random_state=42)
        clf.fit(Xtr, ytr)

        joblib.dump({"model": clf, "scaler": sc}, MODEL_FILE)
        print("[TRAIN] Model updated and saved to", MODEL_FILE)

    except Exception as e:
        print("[TRAIN ERROR]", e)

# open serial port
try:
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
except Exception as e:
    ports = list(serial.tools.list_ports.comports())
    raise SystemExit(f"Could not open serial port {SERIAL_PORT}: {e}\nAvailable ports: {ports}")

print("Connected to", SERIAL_PORT)

# initial retrain
last_retrain = time.time()
retrain_model()

# wait for first valid sensor line (skip boot messages/headers)
print("Waiting for first valid sensor line (format: ts,adc_raw,temp,humidity)...")
while True:
    line = ser.readline().decode("utf-8", errors="ignore").strip()
    if not line:
        continue
    parts = line.split(",")
    if len(parts) >= 4:
        if parts[1].lower().strip() in ("adc_raw", "adc", "sensor"):
            # header - skip
            continue
        try:
            float(parts[1])
            print("Valid sensor data detected. Starting loop.")
            break
        except:
            continue
    else:
        continue

last_temp = None
last_hum = None

# main loop
try:
    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) < 4:
            # skip malformed
            continue

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # parse sensor
        try:
            sensor = float(parts[1])
        except:
            continue

        # parse temp/hum and sanitize
        raw_temp = parts[2].strip() if len(parts) > 2 else ""
        raw_hum = parts[3].strip() if len(parts) > 3 else ""
        try:
            temp = float(raw_temp) if raw_temp.lower() not in ("", "nan") else float("nan")
        except:
            temp = float("nan")
        try:
            hum = float(raw_hum) if raw_hum.lower() not in ("", "nan") else float("nan")
        except:
            hum = float("nan")

        if math.isnan(temp):
            temp = last_temp if last_temp is not None else 0.0
        if math.isnan(hum):
            hum = last_hum if last_hum is not None else 0.0

        last_temp = temp
        last_hum = hum

        # ensure model exists
        if not os.path.exists(MODEL_FILE):
            retrain_model()

        # safe model load
        try:
            meta = joblib.load(MODEL_FILE)
            clf = meta["model"]
            sc = meta["scaler"]
        except Exception:
            retrain_model()
            meta = joblib.load(MODEL_FILE)
            clf = meta["model"]
            sc = meta["scaler"]

        # FIX: Deterministic bin-based labeling
        bins = [0, 200, 400, 800, 1400, 2600, 4095]
        pred = np.digitize([sensor], bins[1:], right=True)[0]


        # cleaned output
        print(f"{AQI_LABELS[pred]} | sensor={sensor} temp={temp} hum={hum} ts={ts}")

        # append to live file
        with open(LIVE_DATASET, "a") as f:
            f.write(f"{ts},{sensor},{temp},{hum},{pred}\n")

        if time.time() - last_retrain > RETRAIN_INTERVAL:
            retrain_model()
            last_retrain = time.time()

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    try:
        ser.close()
    except:
        pass
