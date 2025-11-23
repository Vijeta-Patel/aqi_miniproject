
#include <Arduino.h>
#include "DHT.h"
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN,DHTTYPE);
#define MQ_PIN 34

void setup(){
  Serial.begin(115200);
  dht.begin();
  delay(2000);
  Serial.println("ts,adc_raw,temp,humidity");
}

void loop(){
  unsigned long ts=millis();
  int raw=analogRead(MQ_PIN);
  float t=dht.readTemperature();
  float h=dht.readHumidity();
  Serial.printf("%lu,%d,%.2f,%.2f\n",ts,raw,t,h);
  delay(2000);
}
