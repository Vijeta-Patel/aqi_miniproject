#ifndef SENSORS_H
#define SENSORS_H

extern int baseline;
struct SensorData {
    int   mq135_raw;
    float temperature;
    float humidity;
};

void initSensors();
SensorData readSensors();

#endif
