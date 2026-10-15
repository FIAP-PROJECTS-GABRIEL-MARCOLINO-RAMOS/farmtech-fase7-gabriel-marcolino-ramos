// Sistema de Irrigação Inteligente - ESP32
// Fase 3 - FIAP
//
// Sensores simulados:
// - Botão 1: Fósforo (P)
// - Botão 2: Potássio (K)
// - LDR: pH
// - DHT22: Umidade
// - Relé: Bomba d'água
// - LED: Status da bomba

#include <Arduino.h>
#include <DHT.h>

// Definições dos pinos (ajuste conforme o circuito)
#define PIN_FOSFORO 12
#define PIN_POTASSIO 14
#define PIN_LDR 34
#define PIN_DHT 27
#define PIN_RELE 26
#define PIN_LED 2
#define DHTTYPE DHT22

DHT dht(PIN_DHT, DHTTYPE);

void setup() {
  Serial.begin(115200);
  pinMode(PIN_FOSFORO, INPUT_PULLUP);
  pinMode(PIN_POTASSIO, INPUT_PULLUP);
  pinMode(PIN_LDR, INPUT);
  pinMode(PIN_RELE, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  dht.begin();
}

void loop() {
  // Leitura dos sensores
  bool fosforo = digitalRead(PIN_FOSFORO) == LOW; // Pressionado = presença
  bool potassio = digitalRead(PIN_POTASSIO) == LOW;
  int ldrValue = analogRead(PIN_LDR); // Simula pH
  float umidade = dht.readHumidity();

  // Lógica de irrigação (exemplo: personalize conforme sua regra)
  bool irrigar = (umidade < 60) && fosforo && potassio && (ldrValue > 1000);

  // Controle do relé e LED
  digitalWrite(PIN_RELE, irrigar ? HIGH : LOW);
  digitalWrite(PIN_LED, irrigar ? HIGH : LOW);

  // Envio dos dados para o monitor serial
  Serial.print("Fosforo:"); Serial.print(fosforo);
  Serial.print(",Potassio:"); Serial.print(potassio);
  Serial.print(",pH:"); Serial.print(ldrValue);
  Serial.print(",Umidade:"); Serial.print(umidade);
  Serial.print(",Irrigacao:"); Serial.println(irrigar);

  delay(2000); // Aguarda 2 segundos
} 