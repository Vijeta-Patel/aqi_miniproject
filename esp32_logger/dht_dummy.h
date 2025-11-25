#ifndef DHT_DUMMY_H
#define DHT_DUMMY_H

#include "DHT.h"
#include "config.h"

DHT dht(DHT_PIN, DHT11);
// Temporary fake functions

void intitDHT(){
    dht.begin();
}
float readTemp()    { return 25;//dht.readTemperature(); 
    }   // fake temperature
float readHumid()   { return 50;//dht.readHumidity(); 
    }   // fake humidity

#endif
