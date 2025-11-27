#include "wifi_comm.h"
#include "config.h"
#include <WiFi.h>
#include <WebServer.h>
#include "sensors.h"
#include "classifier.h"
//#include "SPIFFS.h"

WebServer server(80);

void handleRoot() {
    String page = R"=====(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Air Quality Dashboard</title>
  <style>
    :root {
      --good: #4caf50;
      --moderate: #ffb300;
      --unhealthy: #f4511e;
      --bg: #0f172a;
      --card: #111827;
      --text: #e5e7eb;
      --sub: #9ca3af;
      --accent: #38bdf8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #1f2937, #020617);
      color: var(--text);
      display: flex;
      justify-content: center;
      min-height: 100vh;
    }
    .container {
      width: 100%;
      max-width: 900px;
      padding: 24px;
    }
    h1 {
      text-align: center;
      margin-bottom: 8px;
      font-weight: 700;
    }
    .subtitle {
      text-align: center;
      color: var(--sub);
      font-size: 0.9rem;
      margin-bottom: 20px;
    }
    .status-card {
      border-radius: 18px;
      padding: 24px;
      margin-bottom: 18px;
      text-align: center;
      font-size: 1.8rem;
      font-weight: 600;
      transition: background 0.3s ease;
      color: #fff;
    }
    .status-good      { background: var(--good); }
    .status-moderate  { background: var(--moderate); }
    .status-unhealthy { background: var(--unhealthy); }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }
    .card {
      background: rgba(15,23,42,0.9);
      border-radius: 14px;
      padding: 12px 14px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.45);
      border: 1px solid rgba(148,163,184,0.2);
    }
    .card-label {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--sub);
      margin-bottom: 6px;
    }
    .card-value {
      font-size: 1.2rem;
      font-weight: 600;
    }
    .chip {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(148,163,184,0.15);
      font-size: 0.75rem;
      color: var(--sub);
      margin-top: 4px;
    }
    .chart-card {
      background: rgba(15,23,42,0.9);
      border-radius: 18px;
      padding: 16px;
      border: 1px solid rgba(148,163,184,0.2);
      box-shadow: 0 10px 35px rgba(0,0,0,0.55);
    }
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 4px;
    }
    .chart-header span {
      font-size: 0.8rem;
      color: var(--sub);
    }
    canvas {
      width: 100%;
      max-height: 260px;
    }
    @media (max-width: 640px) {
      .grid {
        grid-template-columns: 1fr;
      }
      h1 { font-size: 1.5rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Air Quality Dashboard</h1>
    <p class="subtitle">ESP32 · MQ135 · IOT</p>

    <div id="statusBox" class="status-card status-good">Loading...</div>

    <div class="grid">
      <div class="card">
        <div class="card-label">Gas Sensor (MQ135)</div>
        <div class="card-value"><span id="mq135">-</span> <span class="chip">ADC</span></div>
      </div>
      <div class="card">
        <div class="card-label">Temperature</div>
        <div class="card-value"><span id="temp">-</span> &deg;C</div>
      </div>
      <div class="card">
        <div class="card-label">Humidity</div>
        <div class="card-value"><span id="hum">-</span> %</div>
      </div>
    </div>

    <div class="chart-card">
      <div class="chart-header">
        <strong>Live MQ135 Trend</strong>
        <span>last 60 seconds</span>
      </div>
      <canvas id="mqChart"></canvas>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    let mqChart;
    let mqData = [];
    let mqLabels = [];

    function classifyColor(aqi) {
      const s = aqi.toLowerCase();
      if (s.includes("good")) return "status-good";
      if (s.includes("moderate")) return "status-moderate";
      return "status-unhealthy";
    }

    function initChart() {
      const ctx = document.getElementById('mqChart').getContext('2d');
      mqChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: mqLabels,
          datasets: [{
            label: 'MQ135',
            data: mqData,
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              ticks: { display: false },
              grid: { display: false }
            },
            y: {
              ticks: { color: '#9ca3af' },
              grid: { color: 'rgba(148,163,184,0.2)' }
            }
          }
        }
      });
    }

    function updateChart(mqValue) {
      const now = new Date();
      mqLabels.push(now.toLocaleTimeString());
      mqData.push(mqValue);

      if (mqData.length > 60) {
        mqData.shift();
        mqLabels.shift();
      }

      mqChart.update();
    }

    function updateData() {
      fetch('/data')
        .then(res => res.json())
        .then(data => {
          document.getElementById("mq135").innerText = data.mq135;
          document.getElementById("temp").innerText = data.temp.toFixed(1);
          document.getElementById("hum").innerText  = data.hum.toFixed(1);

          const box = document.getElementById("statusBox");
          box.textContent = data.aqi;
          box.className = "status-card " + classifyColor(data.aqi);

          updateChart(data.mq135);
        });
    }

    window.onload = function() {
      initChart();
      updateData();
      setInterval(updateData, 1000);
    }
  </script>
</body>
</html>
)=====";

    server.send(200, "text/html", page);
}



void handleData() {
    SensorData d = readSensors();
    String aqi = classify(d);

    String json = "{";
    json += "\"mq135\":" + String(d.mq135_raw) + ",";
    json += "\"temp\":" + String(d.temperature) + ",";
    json += "\"hum\":" + String(d.humidity) + ",";
    json += "\"aqi\":\"" + aqi + "\"";
    json += "}";

    server.send(200, "application/json", json);
}

void initWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting to WiFi");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    server.on("/", handleRoot);
    server.on("/data", handleData);
    server.begin();

    Serial.println("Web server started.");
}

void handleWiFi() {
    server.handleClient();
}
