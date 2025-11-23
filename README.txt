# Real-Time Air Quality Monitoring System (AQI-IoT-ML)

A real-time air quality monitoring system using ESP32, MQ135 gas sensor, DHT11 temperature & humidity sensor, and a Python machine learning pipeline. The system reads live sensor data, classifies it into AQI categories (Good → Hazardous), logs data, and continuously retrains the ML model using both the base dataset and live readings. Includes an optional local dashboard for visualization.

---

## Features

- Real-time air quality data acquisition via ESP32
- AQI classification into 6 categories using ML
- Continuous model retraining with live and historical data
- Data logging and local dashboard visualization
- Modular pipeline for easy extension

---

## Hardware Used

| Component | Purpose                          |
|-----------|----------------------------------|
| ESP32     | Microcontroller for data logging |
| MQ135     | Gas sensor (air quality)         |
| DHT11     | Temperature & humidity sensor    |

---

## Dataset Source

- **Kaggle:** [ADL Classification Dataset](https://www.kaggle.com/datasets/saurabhshahane/adl-classification)

---

## AQI Category Mapping

| AQI Range   | Category        |
|-------------|----------------|
| 0–200       | Good           |
| 201–400     | Moderate       |
| 401–800     | USG            |
| 801–1400    | Unhealthy      |
| 1401–2600   | Very Unhealthy |
| 2601–4095   | Hazardous      |

---

## Project Folder Structure

```
aqi_miniproject_/
│
├── esp32_logger/
│     └── esp32_logger.ino
├── final_model_6class.pkl
├── Gas_Sensors_Measurements.csv
├── initial_model_6class.pkl
├── label_local_data.py
├── live_minimal.html
├── merge_and_retrain.py
├── my_realtime_data.csv
├── README.txt
├── realtime_full_pipeline.py
├── requirements.txt
├── train_initial_6class.py
```

---

## Install & Usage Commands

```bash
pip install -r requirements.txt
python train_initial_6class.py
# Upload esp32_logger.ino to ESP32 (close Serial Monitor after upload)
python realtime_full_pipeline.py
python -m http.server 5500
```

---

## File Descriptions

| File                        | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `esp32_logger.ino`          | ESP32 firmware: reads MQ135 & DHT11, sends data via serial                  |
| `train_initial_6class.py`   | Trains initial ML model on base dataset for 6 AQI classes                   |
| `merge_and_retrain.py`      | Merges live and base data, retrains model periodically                      |
| `realtime_full_pipeline.py` | Reads live serial data, applies ML model, logs predictions                  |
| `label_local_data.py`       | Labels new local sensor data for retraining                                 |
| `Gas_Sensors_Measurements.csv` | Main dataset file (from Kaggle)                                          |
| `my_realtime_data.csv`      | Stores live sensor readings from ESP32                                      |
| `final_model_6class.pkl`    | Latest trained ML model (pickle file)                                       |
| `initial_model_6class.pkl`  | Initial trained ML model (pickle file)                                      |
| `live_minimal.html`         | Minimal dashboard for local visualization                                   |
| `requirements.txt`          | Python dependencies                                                         |
| `README.txt`                | Project documentation                                                       |

---

## How the Live Pipeline Works

- ESP32 streams sensor data via serial to host PC.
- `realtime_full_pipeline.py` reads serial data, applies the trained ML model, and logs predictions.
- Data is stored for future retraining and dashboard visualization.

---

## How Retraining Works

- `merge_and_retrain.py` periodically merges new live data with the base dataset.
- The ML model is retrained to adapt to changing environmental conditions.
- Updated models are saved and used for future predictions.

---

## How the Dashboard Works

- Run `python -m http.server 5500` in the project folder.
- Access the dashboard via `http://localhost:5500/dashboard/` in your browser.
- Visualizes live and historical AQI data.

---

## Requirements

- Python 3.7+
- Required libraries (see `requirements.txt`):
  - numpy
  - pandas
  - scikit-learn
  - pyserial
  - joblib
  

---

## Future Improvements

- Add support for more sensors and AQI parameters
- Cloud-based dashboard and remote alerts
- Advanced ML models (deep learning, anomaly detection)
- Automated firmware updates for ESP32
- Mobile app integration

---
