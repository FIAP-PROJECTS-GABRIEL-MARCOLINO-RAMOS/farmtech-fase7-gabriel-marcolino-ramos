// FarmTech Fase 7. DHT22 mede UMIDADE DO AR. LDR simula pH.
// Saída JSON Lines para scripts/serial_bridge.py; relé não é acionado por regra não calibrada.
#include <Arduino.h>
#include <DHT.h>
#define DHTPIN 27
#define DHTTYPE DHT22
DHT dht(DHTPIN,DHTTYPE);
unsigned long sequenceNumber=0;
void setup(){
 Serial.begin(115200);dht.begin();pinMode(12,INPUT_PULLUP);pinMode(14,INPUT_PULLUP);
 pinMode(26,OUTPUT);digitalWrite(26,LOW);
}
void loop(){
 float humidity=dht.readHumidity(),temperature=dht.readTemperature();
 if(isnan(humidity)||isnan(temperature)){delay(2000);return;}
 int ldr=analogRead(34);
 float phSimulated=ldr*14.0f/4095.0f;
 Serial.printf("{\"sensor_id\":\"esp32-01\",\"sequencia\":%lu,\"umidade_ar\":%.2f,\"temperatura\":%.2f,\"umidade_solo\":null,\"ph\":%.2f,\"ph_simulado\":true,\"fosforo\":%d,\"potassio\":%d}\n",
 sequenceNumber++,humidity,temperature,phSimulated,digitalRead(12)==LOW,digitalRead(14)==LOW);
 delay(2000);
}
