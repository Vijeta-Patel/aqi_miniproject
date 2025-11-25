#include <Arduino.h>
#include "config.h"
#include "sensors.h"
#include "dht_dummy.h"

int baseline = 0;

void initSensors() {
    pinMode(MQ135_PIN, INPUT);

    // Calibrate MQ135 baseline
    long sum = 0;
    const int samples = 200;
    for (int i = 0; i < samples; i++) {
        sum += analogRead(MQ135_PIN);
        delay(10);
    }
    baseline = sum / samples;
    Serial.print("MQ135 baseline: ");
    Serial.println(baseline);
}

SensorData readSensors() {
    SensorData d;

    d.mq135_raw = analogRead(MQ135_PIN);

    // For now, use dummy temp/humidity
    d.temperature = readTempDummy();
    d.humidity    = readHumidDummy();

    return d;
}
