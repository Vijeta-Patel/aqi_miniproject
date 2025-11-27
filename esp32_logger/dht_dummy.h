#ifndef DHT_DUMMY_H
#define DHT_DUMMY_H

#include "DHT.h"
#include "config.h"

DHT dht(DHT_PIN, DHT11);
// Temporary fake functions

void intitDHT(){
    dht.begin();
}
float readTemp()    { 
    return dht.readTemperature(); 
    }   // fake temperature
float readHumid()   { 
    return dht.readHumidity(); 
    }   // fake humidity

#endif
