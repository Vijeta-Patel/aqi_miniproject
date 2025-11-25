#include <Arduino.h>
#include "config.h"
#include "sensors.h"
#include "classifier.h"
#include "wifi_comm.h"
//#include "SPIFFS.h"


void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Air Quality Monitor starting...");

    //SPIFFS.begin(true);

    initSensors();
    initWiFi();  // stub for now
}

void loop() {
    SensorData data = readSensors();
    String label = classify(data);
    unsigned long ts=millis();
    /*Serial.print("MQ135: ");
    Serial.print(data.mq135_raw);
    Serial.print(" | Temp: ");
    Serial.print(data.temperature);
    Serial.print(" | Hum: ");
    Serial.print(data.humidity);
    Serial.print(" => ");
    Serial.println(label);*/
    Serial.printf("%lu,%d,%.2f,%.2f\n", ts, data.mq135_raw, data.temperature, data.humidity);

    //sendToCloud(data, label); // currently prints CSV line
    handleWiFi();
    delay(SAMPLING_INTERVAL);
}
