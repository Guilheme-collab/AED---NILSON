/*
  PROJETO: Controle PI/PID com atraso variavel na realimentacao
  Plataforma: Arduino Uno R3 / ATmega328P - Proteus 8.13

  LIGACOES:
    D9 (PWM) -> R1 4k7 -> PLANT_OUT -> A0
                                |
                              C1 100uF
                                |
                               GND

    RV1 (Setpoint): extremidades em +5V e GND; cursor em A1
    RV2 (Atraso):   extremidades em +5V e GND; cursor em A2
    D1/TX do Arduino -> RXD do Virtual Terminal

  OSCILOSCOPIO:
    Canal A -> D9 (antes de R1)
    Canal B -> PLANT_OUT (depois de R1; mesmo ponto de A0 e C1 positivo)

  TELEMETRIA CSV (115200 baud):
    tempo_ms,setpoint_V,saida_V,saida_atrasada_V,pwm,atraso_ms

  OBSERVACAO:
    O atraso e implementado por software, usando um buffer circular de
    amostras da medicao A0. Esta montagem e uma co-simulacao no Proteus;
    representa uma simulacao computacional no Proteus.
*/

#include <Arduino.h>

const uint8_t PIN_PWM      = 9;
const uint8_t PIN_PLANT    = A0;
const uint8_t PIN_SETPOINT = A1;
const uint8_t PIN_DELAY    = A2;

const unsigned long SAMPLE_TIME_MS = 10UL;
const unsigned long MAX_DELAY_MS   = 1000UL;
const uint8_t MAX_DELAY_SAMPLES = (uint8_t)(MAX_DELAY_MS / SAMPLE_TIME_MS);
const uint8_t BUFFER_SIZE = MAX_DELAY_SAMPLES + 1U;

// Kd=0 caracteriza PI. O termo derivativo permanece parametrizado por historico.
const float KP = 1.40f;
const float KI = 1.00f;
const float KD = 0.00f;
const float DERIVATIVE_FILTER_S = 0.05f;
const float INTEGRAL_LIMIT = 2.0f;
const float ADC_REFERENCE_V = 5.0f;

float yHistory[BUFFER_SIZE];
uint8_t writeIndex = 0;
float integralTerm = 0.0f;
float previousDelayedY = 0.0f;
float filteredDerivative = 0.0f;
unsigned long lastSampleMs = 0UL;

float saturate01(float value) {
  if (value < 0.0f) return 0.0f;
  if (value > 1.0f) return 1.0f;
  return value;
}

float readNormalized(uint8_t pin) {
  return (float)analogRead(pin) / 1023.0f;
}

uint8_t calculateDelaySamples(uint16_t delayRaw) {
  const uint32_t numerator = (uint32_t)delayRaw * (uint32_t)MAX_DELAY_SAMPLES + 511UL;
  uint32_t samples = numerator / 1023UL;
  if (samples > MAX_DELAY_SAMPLES) samples = MAX_DELAY_SAMPLES;
  return (uint8_t)samples;
}

void setup() {
  pinMode(PIN_PWM, OUTPUT);
  analogWrite(PIN_PWM, 0);
  Serial.begin(115200);

  const float initialY = readNormalized(PIN_PLANT);
  for (uint8_t i = 0; i < BUFFER_SIZE; i++) yHistory[i] = initialY;
  previousDelayedY = initialY;
  integralTerm = 0.0f;
  filteredDerivative = 0.0f;
  writeIndex = 0;

  Serial.println(F("tempo_ms,setpoint_V,saida_V,saida_atrasada_V,pwm,atraso_ms"));
  lastSampleMs = millis();
}

void loop() {
  const unsigned long now = millis();
  const unsigned long elapsedMs = now - lastSampleMs;
  if (elapsedMs < SAMPLE_TIME_MS) return;

  const float dt = (float)elapsedMs / 1000.0f;
  lastSampleMs = now;

  const float setpoint = readNormalized(PIN_SETPOINT);
  const float yNow = readNormalized(PIN_PLANT);
  const uint16_t delayRaw = (uint16_t)analogRead(PIN_DELAY);
  const uint8_t delaySamples = calculateDelaySamples(delayRaw);
  const unsigned long delayAppliedMs = (unsigned long)delaySamples * SAMPLE_TIME_MS;

  yHistory[writeIndex] = yNow;
  const uint16_t readPosition = ((uint16_t)writeIndex + (uint16_t)BUFFER_SIZE - (uint16_t)delaySamples) % (uint16_t)BUFFER_SIZE;
  const float yDelayed = yHistory[(uint8_t)readPosition];
  const float error = setpoint - yDelayed;

  const float derivativeRaw = (yDelayed - previousDelayedY) / dt;
  const float alpha = DERIVATIVE_FILTER_S / (DERIVATIVE_FILTER_S + dt);
  filteredDerivative = alpha * filteredDerivative + (1.0f - alpha) * derivativeRaw;

  float controlRaw = KP * error + KI * integralTerm - KD * filteredDerivative;
  const bool canIntegrate =
      (controlRaw >= 0.0f && controlRaw <= 1.0f) ||
      (controlRaw > 1.0f && error < 0.0f) ||
      (controlRaw < 0.0f && error > 0.0f);

  if (canIntegrate) {
    integralTerm += error * dt;
    if (integralTerm > INTEGRAL_LIMIT) integralTerm = INTEGRAL_LIMIT;
    else if (integralTerm < -INTEGRAL_LIMIT) integralTerm = -INTEGRAL_LIMIT;
  }

  controlRaw = KP * error + KI * integralTerm - KD * filteredDerivative;
  const float control = saturate01(controlRaw);
  const uint8_t pwmValue = (uint8_t)(control * 255.0f + 0.5f);
  analogWrite(PIN_PWM, pwmValue);

  previousDelayedY = yDelayed;
  writeIndex++;
  if (writeIndex >= BUFFER_SIZE) writeIndex = 0;

  Serial.print(now);
  Serial.print(',');
  Serial.print(setpoint * ADC_REFERENCE_V, 3);
  Serial.print(',');
  Serial.print(yNow * ADC_REFERENCE_V, 3);
  Serial.print(',');
  Serial.print(yDelayed * ADC_REFERENCE_V, 3);
  Serial.print(',');
  Serial.print(pwmValue);
  Serial.print(',');
  Serial.println(delayAppliedMs);
}
