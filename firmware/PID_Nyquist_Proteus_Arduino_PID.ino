/*
  PROJETO: Controle PID com atraso variavel na realimentacao
  Plataforma: Arduino Uno R3 / ATmega328P - Proteus 8.x

  ESTE ARQUIVO E UMA VERSAO SEPARADA DO FIRMWARE PI ORIGINAL.
  Preserve PI_Nyquist_Proteus_Arduino.ino para os ensaios PI.

  LIGACOES (NAO ALTERAR O CIRCUITO):
    D9 (PWM) -> R1 4k7 -> PLANT_OUT -> A0
                                |
                              C1 100uF
                                |
                               GND
    RV1: cursor em A1 (setpoint)
    RV2: cursor em A2 (atraso)
    D1/TX -> RXD do Virtual Terminal

  TELEMETRIA CSV (115200 baud):
    tempo_ms,setpoint_V,saida_V,saida_atrasada_V,pwm,atraso_ms

  CONTROLADOR:
    PID com derivada sobre a medicao atrasada, filtro de primeira ordem
    e anti-windup por integracao condicional.

  IMPORTANTE:
    Kp=1.40, Ki=1.00 e Kd=0.08 sao valores INICIAIS para ensaio.
    Kd diferente de zero habilita efetivamente a acao derivativa.
    Esses ganhos nao estao declarados como otimizados/validados.
*/

#include <Arduino.h>

// ------------------------------ Pinos ----------------------------------------
const uint8_t PIN_PWM      = 9;
const uint8_t PIN_PLANT    = A0;
const uint8_t PIN_SETPOINT = A1;
const uint8_t PIN_DELAY    = A2;

// --------------------------- Temporizacao ------------------------------------
const unsigned long SAMPLE_TIME_US = 10000UL;  // 10 ms (100 Hz)
const unsigned long SAMPLE_TIME_MS = 10UL;
const unsigned long MAX_DELAY_MS   = 1000UL;

const uint8_t MAX_DELAY_SAMPLES =
    (uint8_t)(MAX_DELAY_MS / SAMPLE_TIME_MS);
const uint8_t BUFFER_SIZE = MAX_DELAY_SAMPLES + 1U;

// ------------------------- Ganhos do PID -------------------------------------
// Unidades normalizadas: entrada e saida entre 0.0 e 1.0.
// Estes sao valores iniciais; nao os trate como sintonia final.
const float KP = 1.40f;
const float KI = 1.00f;
const float KD = 0.08f;

// Constante de tempo do filtro da derivada (segundos).
const float DERIVATIVE_FILTER_S = 0.05f;

// Limite da memoria integral.
const float INTEGRAL_LIMIT = 2.0f;

// Referencia ADC nominal do Arduino Uno.
const float ADC_REFERENCE_V = 5.0f;

// --------------------------- Buffer de atraso --------------------------------
float yHistory[BUFFER_SIZE];
uint8_t writeIndex = 0;

// --------------------------- Estado do PID -----------------------------------
float integralTerm = 0.0f;
float previousDelayedY = 0.0f;
float filteredDerivative = 0.0f;
unsigned long lastSampleUs = 0UL;

// ------------------------------ Funcoes --------------------------------------
float saturate01(float value) {
  if (value < 0.0f) return 0.0f;
  if (value > 1.0f) return 1.0f;
  return value;
}

float readNormalized(uint8_t pin) {
  return (float)analogRead(pin) / 1023.0f;
}

uint8_t calculateDelaySamples(uint16_t delayRaw) {
  // Arredonda para o passo de amostragem mais proximo (10 ms).
  const uint32_t numerator =
      (uint32_t)delayRaw * (uint32_t)MAX_DELAY_SAMPLES + 511UL;
  uint32_t samples = numerator / 1023UL;

  if (samples > MAX_DELAY_SAMPLES) {
    samples = MAX_DELAY_SAMPLES;
  }
  return (uint8_t)samples;
}

void setup() {
  pinMode(PIN_PWM, OUTPUT);
  analogWrite(PIN_PWM, 0);

  Serial.begin(115200);

  const float initialY = readNormalized(PIN_PLANT);
  for (uint8_t i = 0; i < BUFFER_SIZE; i++) {
    yHistory[i] = initialY;
  }

  writeIndex = 0;
  integralTerm = 0.0f;
  previousDelayedY = initialY;
  filteredDerivative = 0.0f;

  Serial.println(F("tempo_ms,setpoint_V,saida_V,saida_atrasada_V,pwm,atraso_ms"));
  lastSampleUs = micros();
}

void loop() {
  const unsigned long nowUs = micros();
  const unsigned long elapsedUs = nowUs - lastSampleUs;

  if (elapsedUs < SAMPLE_TIME_US) {
    return;
  }

  // Usa o tempo realmente transcorrido na atualizacao.
  const float dt = (float)elapsedUs / 1000000.0f;
  lastSampleUs = nowUs;

  const float setpoint = readNormalized(PIN_SETPOINT);
  const float yNow = readNormalized(PIN_PLANT);
  const uint16_t delayRaw = (uint16_t)analogRead(PIN_DELAY);

  const uint8_t delaySamples = calculateDelaySamples(delayRaw);
  const unsigned long delayAppliedMs =
      (unsigned long)delaySamples * SAMPLE_TIME_MS;

  // Armazena a leitura atual e recupera a leitura atrasada.
  yHistory[writeIndex] = yNow;

  const uint16_t readPosition =
      ((uint16_t)writeIndex + (uint16_t)BUFFER_SIZE -
       (uint16_t)delaySamples) % (uint16_t)BUFFER_SIZE;

  const float yDelayed = yHistory[(uint8_t)readPosition];
  const float error = setpoint - yDelayed;

  // Derivada sobre a medicao (nao sobre o setpoint), reduzindo derivative kick.
  const float derivativeRaw = (yDelayed - previousDelayedY) / dt;
  const float alpha = DERIVATIVE_FILTER_S /
                      (DERIVATIVE_FILTER_S + dt);

  filteredDerivative =
      alpha * filteredDerivative + (1.0f - alpha) * derivativeRaw;

  // Acao PID: P + I - D_medicao.
  float controlRaw =
      KP * error + KI * integralTerm - KD * filteredDerivative;

  // Anti-windup por integracao condicional.
  const bool canIntegrate =
      (controlRaw >= 0.0f && controlRaw <= 1.0f) ||
      (controlRaw > 1.0f && error < 0.0f) ||
      (controlRaw < 0.0f && error > 0.0f);

  if (canIntegrate) {
    integralTerm += error * dt;

    if (integralTerm > INTEGRAL_LIMIT) {
      integralTerm = INTEGRAL_LIMIT;
    } else if (integralTerm < -INTEGRAL_LIMIT) {
      integralTerm = -INTEGRAL_LIMIT;
    }
  }

  // Recalcula a saida com a integral atualizada.
  controlRaw =
      KP * error + KI * integralTerm - KD * filteredDerivative;

  const float control = saturate01(controlRaw);
  const uint8_t pwmValue = (uint8_t)(control * 255.0f + 0.5f);

  analogWrite(PIN_PWM, pwmValue);

  previousDelayedY = yDelayed;

  writeIndex++;
  if (writeIndex >= BUFFER_SIZE) {
    writeIndex = 0;
  }

  // Mantem o mesmo formato CSV dos ensaios anteriores.
  Serial.print(millis());
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
