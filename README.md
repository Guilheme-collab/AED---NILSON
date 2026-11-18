# Engenharia da Computacao - Implementacao e simulacao do prototipo Nyquist

Este repositorio documenta **a contribuicao pratica da trilha de Engenharia da Computacao**: firmware do Arduino, circuito RC no Proteus, atraso de realimentacao implementado por software e dados de telemetria dos ensaios.

> **Escopo:** esta pasta nao substitui o nucleo computacional geral do projeto (algoritmos de Nyquist, Routh-Hurwitz, Lugar das Raizes, Bode e benchmarking). Esses itens devem ser integrados pelo integrante/equipe responsavel por essa frente.

## Estrutura

```text
firmware/                 Codigo-fonte Arduino (.ino), binario (.hex) e nota do HEX
proteus/                  Projeto do Proteus (.pdsprj)
dados/csv/                Dez arquivos CSV, um por atraso
 dados/resumo_ensaios.csv Resumo descritivo extraido da telemetria
figuras/                  Graficos gerados a partir dos CSVs
scripts/                  Script para regenerar resumo e graficos
docs/                     Documento de repasse, enunciado e evidencias
```

## Ambiente e arquitetura

- Proteus 8 Professional, Release 8.13 SP0 (Build 31525), conforme informado no registro do projeto.
- Arduino Uno R3 / ATmega328P, clock nominal de 16 MHz.
- Arduino IDE para compilar o firmware.
- Serial: 115200 baud, 8-N-1.
- Planta RC nominal: R = 4,7 kOhm; C = 100 uF; tau = R*C = 0,47 s.
- RV1: setpoint no cursor conectado a A1; RV2: atraso no cursor conectado a A2.
- A0 mede PLANT_OUT; D9 fornece PWM atraves de R1 para a planta.
- D1/TX do Arduino vai ao RXD do Virtual Terminal.
- O atraso e aplicado por software a amostras de A0, usando buffer circular; nao e atraso de rede fisica.

## Pinos

| Arduino | Funcao |
|---|---|
| D9 | PWM para a planta RC |
| A0 | Medicao atual da planta (PLANT_OUT) |
| A1 | Setpoint (RV1) |
| A2 | Atraso solicitado (RV2) |
| D1/TX | Telemetria serial para RXD do Virtual Terminal |
| GND | Referencia comum |

Osciloscopio: canal A em D9; canal B em PLANT_OUT.

## Firmware

O firmware executa um controlador cuja estrutura inclui termos P, I e D. Nos ensaios documentados, **Kp=1,40; Ki=1,00; Kd=0,00**. Portanto, os resultados registrados correspondem a um **controlador PI** (a acao derivativa esta desabilitada). Nao descreva os ensaios como PID com derivada ativa.

- Periodo de amostragem nominal: 10 ms.
- Atraso configuravel: 0 a 1000 ms, em passos nominais de 10 ms.
- Buffer circular: 101 posicoes.
- PWM: 0 a 255.
- Anti-windup: integracao condicional.
- Telemetria: `tempo_ms,setpoint_V,saida_V,saida_atrasada_V,pwm,atraso_ms`.

### Compilacao e arquivo HEX

O pacote agora inclui `firmware/PID_Nyquist_Proteus_Arduino.hex`, fornecido pelo usuario. Os registros Intel HEX e seus checksums foram validados estruturalmente. **Essa verificacao nao prova, por si so, que o HEX foi compilado exatamente a partir do INO que acompanha o pacote.** Para garantir correspondencia entre fonte e binario, recompile localmente o INO definitivo:

1. Abra `firmware/PID_Nyquist_Proteus_Arduino.ino` no Arduino IDE.
2. Em **Tools > Board**, selecione **Arduino Uno**.
3. Confirme o processador ATmega328P e clock de 16 MHz no modelo do Proteus.
4. Use **Sketch > Export Compiled Binary** (ou o comando equivalente da versao instalada).
5. Localize o `.hex` na pasta do sketch/build.
6. No Proteus, abra as propriedades do Arduino e selecione o HEX em **Program File**.
7. Execute e confirme o cabecalho e os valores serial no Virtual Terminal.
8. Guarde no repositorio o HEX efetivamente usado, junto com a versao do INO que o gerou.

Nao use um HEX antigo com um INO diferente.

## Ensaios documentados na versao atual das evidencias

O PDF de evidencias contem dez ensaios:

| Ensaio | RV1 | RV2 | Atraso registrado |
|---:|---:|---:|---:|
| 1 | 50% | 0% | 0 ms |
| 2 | 50% | 10% | 100 ms |
| 3 | 50% | 20% | 200 ms |
| 4 | 50% | 40% | 400 ms |
| 5 | 50% | 60% | 600 ms |
| 6 | 50% | 80% | 800 ms |
| 7 | 50% | 88% | 880 ms |
| 8 | 50% | 90% | 900 ms |
| 9 | 50% | 87% | 870 ms |
| 10 | 50% | 89% | 890 ms |

Os dez CSVs em `dados/csv/` foram extraidos das linhas completas da telemetria presentes no PDF. A ultima linha da pagina 348 aparece truncada no PDF e foi omitida da exportacao; nenhuma linha incompleta foi inventada.

## Leitura cautelosa dos resultados

- Para 0, 100, 200 e 400 ms, a saida registrada aproxima-se do setpoint de aproximadamente 2,502 V durante a janela observada.
- Em 600 ms, aparecem oscilacoes com amplitude menor ao longo da janela.
- Em 800 a 900 ms, as oscilacoes aumentam e ha saturacao do PWM (valores 0 e/ou 255). A saturacao torna inadequado interpretar essas respostas como uma verificacao puramente linear do limite de Nyquist.
- Cada ensaio no PDF cobre aproximadamente 9,4 a 10,0 s, nao 60 s. Portanto, o documento nao comprova ensaios longos de 60-120 s.
- Nao declare 880 ms como estavel nem 900 ms como instavel apenas com esses registros. Para classificar a fronteira, e necessario prolongar a janela, observar crescimento/decadencia de amplitude e documentar o efeito da saturacao.

## O que esta pasta nao comprova

1. **HIL fisico:** o projeto anexado e uma co-simulacao de firmware e circuito no Proteus. Nao demonstra, por si so, Arduino fisico conectado a uma planta simulada externa por interface fisica.
2. **Atraso de rede fisica:** o atraso e um buffer de amostras no firmware, nao uma rede/comunicacao fisica.
3. **PID com derivada ativa:** os ensaios usam Kd=0 e, portanto, controlador PI.
4. **Quatro benchmarks A-D:** a planta RC e o prototipo pratico da trilha EC, nao comprovacao dos quatro sistemas de benchmark.
5. **Algoritmos do nucleo geral:** nao estao neste firmware os algoritmos de Nyquist/winding number, Routh-Hurwitz, Lugar das Raizes ou Bode, nem benchmark de ordem n=5,10,20.

## Precisa executar MATLAB/Octave?

Nao para compilar ou executar este firmware. Arduino IDE + Proteus sao suficientes para a contribuicao de firmware/co-simulacao descrita aqui. O enunciado, entretanto, exige para o projeto como um todo uma ferramenta em Python, C++ ou MATLAB/Octave para a analise computacional e os metodos comparativos. Octave e apenas uma alternativa: Python ou C++ tambem atendem a escolha de linguagem. Confirme que outro integrante assumiu essa frente; se ninguem a assumiu, o projeto coletivo ainda tem entregas pendentes.

## Validar os arquivos da entrega

Execute na raiz do projeto:

```bash
python scripts/validar_entrega.py
```

Esse teste confere a presenca dos arquivos obrigatorios, os dez CSVs e seus atrasos, os checksums do HEX e os arquivos internos do pacote Proteus. Ele nao compila o firmware nem executa o Proteus.

## Gerar resumo e graficos dos CSVs

```bash
python -m pip install -r requirements.txt
python scripts/plotar_telemetria.py
```

O script atualiza `dados/resumo_ensaios.csv` e gera graficos de resposta temporal e PWM em `figuras/`. Ele e um utilitario de estatistica descritiva/visualizacao dos ensaios, nao implementa Nyquist nem substitui a analise matematica.

## Arquivos para o responsavel pelo artigo

1. `docs/Repasse_Tecnico_Para_Artigo.docx` (ou PDF): escopo, arquitetura, parametros, estado e limitacoes.
2. `docs/evidencias/Evidencias_Proteus_10_ensaios.pdf`: PDF original com circuito, capturas e telemetria.
3. `proteus/AED.pdsprj`: projeto Proteus editavel.
4. `firmware/PID_Nyquist_Proteus_Arduino.ino`: fonte do firmware.
5. `dados/csv/`: dez series de telemetria em CSV limpo.
6. `dados/resumo_ensaios.csv` e `figuras/`: resumo e graficos para facilitar a analise.
7. `firmware/PID_Nyquist_Proteus_Arduino.hex` e `firmware/LEIA-ME_HEX.md`: HEX fornecido pelo usuario e nota de verificacao/reproducibilidade.

## Como citar a contribuicao no artigo

Descrever como **co-simulacao de firmware Arduino Uno e planta RC no Proteus, com atraso de realimentacao implementado por buffer circular em software**. Informar ganhos e configuracoes reais. Nao chamar de HIL fisico nem de atraso de rede fisica sem uma implementacao e evidencia adicionais.

## Repositorio GitHub

Repositorio remoto: https://github.com/Guilheme-collab/AED---NILSON (branch `main`). Para enviar todos os arquivos do pacote local, inclusive evidencias, CSVs, HEX, DOCX e scripts, siga `docs/COMO_SUBIR_GITHUB.md`. O repositorio remoto ja possui um commit inicial: clone-o antes de copiar os arquivos completos e fazer o push; nao rode `git init` novamente.
