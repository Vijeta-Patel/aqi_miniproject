#include <Arduino.h>      // <-- ADD THIS if not present
#include "classifier.h"
#include "sensors.h"

String classify(const SensorData &d) {
    float mq = d.mq135_raw;
    float t  = d.temperature;
    float h  = d.humidity;

    /*if (mq <= 49.0) {
        if (h <= 53.50) {
            if (t <= 33.05) {
                if (h <= 48.00) {
                    return "Good";
                } else {
                    return "Good";
                }
            } else {
                if (t <= 33.35) {
                    return "Good";
                } else {
                    return "Good";
                }
            }
        } else {
            if (mq <= 42.50) {
                if (h <= 61.50) {
                    return "Good";
                } else {
                    return "Good";
                }
            } else {
                if (t <= 31.00) {
                    return "Good";
                } else {
                    return "Good";
                }
            }
        }
    } else {
        if (mq <= 437.50) {
            if (h <= 52.00) {
                return "Moderate";
            } else {
                return "Good";
            }
        } else {
            return "Unhealthy";
        }
    }*/

    if(mq<=200) {return "Good";}
    else if(mq>200&&mq<=400) {return "Moderate";}
    else if(mq>400&&mq<=800) {return "Unhealthy for Sensitive Groups";}
    else if(mq>800&&mq<=1400) {return "Unhealthy";}
    else if(mq>1400&&mq<=2600) {return "Very Unhealthy";}
    else  {return "Hazardous";}
}
