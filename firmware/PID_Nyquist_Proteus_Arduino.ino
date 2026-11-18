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
    nao representa, por si so, uma implementacao HIL fisica.
*/

#include <Arduino.h>

// -----------------------------------------------------------------------------
// Pinos do Arduino Uno
// -----------------------------------------------------------------------------
const uint8_t PIN_PWM      = 9;
const uint8_t PIN_PLANT    = A0;
const uint8_t PIN_SETPOINT = A1;
const uint8_t PIN_DELAY    = A2;

// -----------------------------------------------------------------------------
// Temporizacao da malha
// -----------------------------------------------------------------------------
const unsigned long SAMPLE_TIME_MS = 10UL;  // periodo nominal: 10 ms (100 Hz)
const unsigned long MAX_DELAY_MS   = 1000UL;

// 1000 ms / 10 ms = 100 amostras de atraso maximo.
const uint8_t MAX_DELAY_SAMPLES =
    (uint8_t)(MAX_DELAY_MS / SAMPLE_TIME_MS);

// +1 para manter a amostra atual e as 100 amostras anteriores.
const uint8_t BUFFER_SIZE = MAX_DELAY_SAMPLES + 1U;

// -----------------------------------------------------------------------------
// Ganhos do controlador: com KD = 0, o controlador opera como PI.
// As grandezas de erro e saida estao normalizadas entre 0 e 1.
// -----------------------------------------------------------------------------
const float KP = 1.40f;
const float KI = 1.00f;
const float KD = 0.00f;

// Filtro da derivada (utilizado quando KD for diferente de zero).
const float DERIVATIVE_FILTER_S = 0.05f;

// Limite da memoria integral.
const float INTEGRAL_LIMIT = 2.0f;

// Referencia nominal do ADC do Arduino Uno.
// Se a alimentacao real/modelada diferir de 5 V, recalibrar este valor.
const float ADC_REFERENCE_V = 5.0f;

// -----------------------------------------------------------------------------
// Buffer circular da medicao da planta
// -----------------------------------------------------------------------------
float yHistory[BUFFER_SIZE];
uint8_t writeIndex = 0;

// -----------------------------------------------------------------------------
// Estados do controlador e temporizacao
// -----------------------------------------------------------------------------
float integralTerm = 0.0f;
float previousDelayedY = 0.0f;
float filteredDerivative = 0.0f;
unsigned long lastSampleMs = 0UL;

// Limita a saida do controlador ao intervalo permitido pelo PWM.
float saturate01(float value) {
  if (value < 0.0f) return 0.0f;
  if (value > 1.0f) return 1.0f;
  return value;
}

// Le o ADC e normaliza a leitura para o intervalo 0.0 a 1.0.
float readNormalized(uint8_t pin) {
  return (float)analogRead(pin) / 1023.0f;
}

// Converte a leitura de RV2 em uma quantidade inteira de amostras.
// O arredondamento evita o erro anterior em que 10% podia resultar em 90 ms.
uint8_t calculateDelaySamples(uint16_t delayRaw) {
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

  // Inicializa o buffer com a leitura inicial para evitar valores indefinidos.
  const float initialY = readNormalized(PIN_PLANT);

  for (uint8_t i = 0; i < BUFFER_SIZE; i++) {
    yHistory[i] = initialY;
  }

  previousDelayedY = initialY;
  integralTerm = 0.0f;
  filteredDerivative = 0.0f;
  writeIndex = 0;

  // Inicia a contagem apos transmitir o cabecalho CSV.
  Serial.println(F("tempo_ms,setpoint_V,saida_V,saida_atrasada_V,pwm,atraso_ms"));
  lastSampleMs = millis();
}

void loop() {
  const unsigned long now = millis();
  const unsigned long elapsedMs = now - lastSampleMs;

  // Executa uma atualizacao por periodo nominal de amostragem.
  if (elapsedMs < SAMPLE_TIME_MS) {
    return;
  }

  // Usa o intervalo efetivamente transcorrido no calculo do controlador.
  const float dt = (float)elapsedMs / 1000.0f;
  lastSampleMs = now;

  // Leituras analogicas normalizadas.
  const float setpoint = readNormalized(PIN_SETPOINT);
  const float yNow = readNormalized(PIN_PLANT);
  const uint16_t delayRaw = (uint16_t)analogRead(PIN_DELAY);

  // RV2: 0% -> 0 ms; 100% -> 1000 ms.
  // O atraso e quantizado em passos nominais de 10 ms.
  const uint8_t delaySamples = calculateDelaySamples(delayRaw);
  const unsigned long delayAppliedMs =
      (unsigned long)delaySamples * SAMPLE_TIME_MS;

  // Armazena a amostra atual e recupera a amostra atrasada.
  yHistory[writeIndex] = yNow;

  const uint16_t readPosition =
      ((uint16_t)writeIndex + (uint16_t)BUFFER_SIZE -
       (uint16_t)delaySamples) % (uint16_t)BUFFER_SIZE;

  const float yDelayed = yHistory[(uint8_t)readPosition];

  // Erro calculado com a medicao atrasada.
  const float error = setpoint - yDelayed;

  // Derivada aplicada sobre a medicao, evitando derivada do setpoint.
  const float derivativeRaw = (yDelayed - previousDelayedY) / dt;
  const float alpha = DERIVATIVE_FILTER_S /
                      (DERIVATIVE_FILTER_S + dt);

  filteredDerivative = alpha * filteredDerivative +
                       (1.0f - alpha) * derivativeRaw;

  // Primeira estimativa da acao de controle.
  float controlRaw = KP * error + KI * integralTerm -
                     KD * filteredDerivative;

  // Anti-windup por integracao condicional:
  // integra dentro da faixa ou quando o erro ajuda a sair da saturacao.
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

  // Recalcula a saida com o estado integral atualizado.
  controlRaw = KP * error + KI * integralTerm -
               KD * filteredDerivative;

  const float control = saturate01(controlRaw);

  // Converte a saida normalizada em PWM de 8 bits (0 a 255).
  const uint8_t pwmValue = (uint8_t)(control * 255.0f + 0.5f);
  analogWrite(PIN_PWM, pwmValue);

  // Atualiza o estado da derivada e avanca o buffer circular.
  previousDelayedY = yDelayed;

  writeIndex++;
  if (writeIndex >= BUFFER_SIZE) {
    writeIndex = 0;
  }

  // Telemetria em volts para facilitar a analise e a exportacao dos dados.
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