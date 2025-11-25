#ifndef CLASSIFIER_H
#define CLASSIFIER_H

#include <Arduino.h>   // <-- ADD THIS
#include "sensors.h"

String classify(const SensorData &data);

#endif
