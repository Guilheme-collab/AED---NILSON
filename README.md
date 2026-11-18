# Análise Computacional e Comparativa de Critérios de Estabilidade em Sistemas Dinâmicos

**Entrega técnica — Engenharia da Computação (EC)**

Este repositório reúne a implementação computacional de análise de estabilidade, os quatro sistemas de benchmark, validações com SciPy, experimentos de escalabilidade, os firmwares PI/PID, o projeto Proteus, os dez conjuntos de telemetria e evidências visuais da simulação.

> **Escopo EC:** toda a aplicação é computacional e simulada. A demonstração da planta/controlador é feita no Proteus, com atraso variável inserido por software no histórico de medições. Descreva os resultados como simulação/co-simulação no Proteus; identifique-os sempre como resultados simulados.

## Comece por aqui

1. Leia [`docs/GUIA_PARA_AUTOR_RELATORIO.md`](docs/GUIA_PARA_AUTOR_RELATORIO.md) para saber quais resultados e figuras usar na elaboração do artigo/relatório.
2. Leia [`docs/RELATORIO_TECNICO_REPASSE.md`](docs/RELATORIO_TECNICO_REPASSE.md) para a arquitetura, modelos, resultados, limites e discrepâncias corrigidas.
3. Consulte [`docs/MATRIZ_ATENDIMENTO_ENUNCIADO.md`](docs/MATRIZ_ATENDIMENTO_ENUNCIADO.md) para a matriz técnica original e [`docs/AUDITORIA_CONFORMIDADE_INTEGRAL.md`](docs/AUDITORIA_CONFORMIDADE_INTEGRAL.md) para a revisão integral do PDF.
4. Use [`docs/ARTIGO_CIENTIFICO_RASCUNHO_SBC_IEEE.md`](docs/ARTIGO_CIENTIFICO_RASCUNHO_SBC_IEEE.md) como rascunho técnico e [`docs/ROTEIRO_SEMINARIO_E_DEMO.md`](docs/ROTEIRO_SEMINARIO_E_DEMO.md) como roteiro de apresentação.
5. Consulte os CSVs brutos em [`dados/csv/`](dados/csv/), os resultados computacionais em [`resultados/tabelas/`](resultados/tabelas/) e as figuras em [`resultados/figuras/`](resultados/figuras/).
6. As capturas do circuito e dos dez ensaios estão em [`docs/evidencias/`](docs/evidencias/).

## Escopo e separação das contribuições

- **Núcleo computacional EC:** funções de transferência, Nyquist/winding number, margens, Routh-Hurwitz, cálculo de polos, Lugar das Raízes, Bode, atraso exato, Padé, benchmarks, testes, validação cruzada e escalabilidade.
- **Aplicação embarcada simulada:** firmware PI histórico e firmware PID posterior, projeto editável Proteus, CSVs e evidências visuais.
- **Artigo científico e seminário:** entregáveis gerais do grupo, mas a redação do artigo e a apresentação não fazem parte desta contribuição técnica individual, conforme divisão de trabalho informada pelo usuário.
- **Trilha CC:** a aplicação visual interativa indicada no enunciado é específica da trilha de Ciência da Computação e não está incluída na entrega EC.

## Instalação e reprodução dos resultados computacionais

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Executar a suíte automatizada:

```bash
PYTHONPATH=src python -m pytest -q
```

Regenerar tabelas e figuras (inclui leitura dos dez CSVs já extraídos):

```bash
PYTHONPATH=src python scripts/gerar_resultados.py
```

Extrair novamente as linhas completas do PDF original de evidências:

```bash
python scripts/extrair_telemetria_pdf.py /caminho/para/aed.pdf
```

Executar a auditoria estrutural do pacote:

```bash
python scripts/validar_entrega.py
```

A extração só conserva linhas CSV completas. Linhas cortadas nas bordas das páginas não são preenchidas por estimativa.

## Núcleo computacional

Código em [`src/nyquist_toolkit/`](src/nyquist_toolkit/):

| Módulo | Responsabilidade |
|---|---|
| `models.py` | Modelo LIT racional, polos/zeros, avaliação de denominador de malha fechada sem atraso |
| `frequency.py` | Resposta em frequência, Bode, cruzamentos, margens e margem de atraso |
| `nyquist.py` | Contorno do semiplano direito, mapeamento e winding number com convenção de sinais documentada |
| `routh.py` | Tabela de Routh-Hurwitz, primeira coluna nula, linha nula e identificação de polos no eixo imaginário |
| `root_locus.py` | Varredura de ganho e associação numérica dos ramos do Lugar das Raízes |
| `delay.py` | Resposta com atraso puro exato e aproximação racional de Padé de ordem configurável |
| `benchmarks.py` | Definições explícitas dos quatro benchmarks A-D |

As implementações não usam a toolbox `python-control`. SciPy/NumPy são usados como referências numéricas e para operações matemáticas auxiliares.

### Convenção do critério de Nyquist

O código calcula o winding number anti-horário `W_CCW` do mapeamento em torno de `-1+j0`. Para seguir a convenção do enunciado, define `N = -W_CCW`, ou seja, `N` é positivo para envoltórios horários. A relação é `Z = P + N`, em que `P` é o número de polos de malha aberta no semiplano direito e `Z` o número de polos instáveis de malha fechada. A documentação e os CSVs mantêm essa convenção explícita.

### Benchmarks

| Sistema | Propriedade | Modelo de malha aberta | Ganho K |
|---|---|---|---:|
| A | Estável, 3ª ordem | `1/(s³ + 6s² + 11s + 6)` | 1 |
| B | Um polo no semiplano direito | `1/(s² + s - 2)` | 3 |
| C | Zero no semiplano direito | `(s - 1)/(s² + 3s + 2)` | 1 |
| D | Atraso puro | `e^(-0.35s)/(0.5s + 1)` | 2 |

Os modelos e ganhos foram escolhidos para contemplar os cenários exigidos e obter exemplos comparáveis. Eles são benchmarks computacionais documentados, não identificações experimentais da planta do Arduino.

## Resultados computacionais

- [`resultados/tabelas/benchmark_resumo.csv`](resultados/tabelas/benchmark_resumo.csv): `P`, winding, `N`, `Z`, Routh/Padé e margens para A-D.
- [`resultados/tabelas/validacao_cruzada_scipy.csv`](resultados/tabelas/validacao_cruzada_scipy.csv): comparação da resposta em frequência e contagem de polos com SciPy.
- [`resultados/tabelas/escalabilidade_n5_n10_n20.csv`](resultados/tabelas/escalabilidade_n5_n10_n20.csv): tempo mediano de 25 execuções e erros para ordens 5, 10 e 20.
- [`resultados/tabelas/margens_teoricas_PI_PID.csv`](resultados/tabelas/margens_teoricas_PI_PID.csv): margem de atraso teórica dos modelos PI/PID para a planta RC nominal.
- [`resultados/tabelas/erro_atraso_exato_vs_pade.csv`](resultados/tabelas/erro_atraso_exato_vs_pade.csv): erros de fase/magnitude de Padé 1, 3 e 5 frente ao atraso exato.
- Tabelas de Routh, dados numéricos de Bode e pontos do Lugar das Raízes também estão em `resultados/tabelas/`.
- Figuras de Nyquist, Bode, Lugar das Raízes, atraso exato/Padé, escalabilidade e telemetria estão em `resultados/figuras/`.

Os tempos de escalabilidade dependem do hardware/ambiente e são informativos, não constantes universais. O caso de ordem 20 evidencia erro máximo de aproximadamente 0,123 na recuperação dos polos geradores, apesar de resíduo polinomial normalizado baixo; isso ilustra sensibilidade/condicionamento de raízes em alta ordem e deve ser discutido, não escondido.

## Aplicação simulada Arduino/Proteus

### Firmwares separados

| Versão | Arquivo | Kp | Ki | Kd | Uso correto |
|---|---|---:|---:|---:|---|
| PI histórico | [`firmware/PI_Nyquist_Proteus_Arduino.ino`](firmware/PI_Nyquist_Proteus_Arduino.ino) | 1,40 | 1,00 | 0,00 | Firmware que já estava no Git; preservado e renomeado para não confundir PI com PID |
| PID posterior | [`firmware/PID_Nyquist_Proteus_Arduino_PID.ino`](firmware/PID_Nyquist_Proteus_Arduino_PID.ino) | 1,40 | 1,00 | 0,08 | Firmware PID fornecido posteriormente pelo usuário |

O HEX fornecido junto com o firmware PID está em [`firmware/PID_Nyquist_Proteus_Arduino_PID.ino.hex`](firmware/PID_Nyquist_Proteus_Arduino_PID.ino.hex). Seus 339 registros Intel HEX e checksums foram validados estruturalmente. Não há confirmação bit a bit de que tenha sido compilado do `.ino` atual, pois o toolchain AVR/Arduino não está disponível neste ambiente. O hash e os limites da validação estão em [`firmware/LEIA-ME_HEX.md`](firmware/LEIA-ME_HEX.md).

### Circuito

Projeto editável: [`proteus/AED.pdsprj`](proteus/AED.pdsprj). A configuração documentada usa Arduino Uno R3/ATmega328P a 16 MHz, R1 de 4,7 kΩ, C1 de 100 µF (`τ=RC=0,47 s`), PWM em D9, leitura da planta em A0, setpoint em A1, ajuste do atraso em A2, buffer circular e telemetria serial a 115200 baud.

O caminho de HEX no projeto foi alterado para caminho relativo `../firmware/PID_Nyquist_Proteus_Arduino_PID.ino.hex`. A estrutura do arquivo Proteus foi verificada; abrir/executar no Proteus não foi possível neste ambiente.

### Evidências e telemetria

- Dez CSVs individuais em `dados/csv/`, totalizando **9.534 amostras completas** extraídas do PDF fornecido.
- [`dados/resumo_ensaios.csv`](dados/resumo_ensaios.csv) contém estatísticas regeneráveis.
- [`docs/evidencias/capturas/`](docs/evidencias/capturas/) contém as imagens individuais do circuito e dos dez ensaios; o índice registra as páginas originais.

A tabela inicial da evidência lista oito atrasos, mas o próprio PDF contém séries completas também para 870 ms e 890 ms. A consolidação mantém os dez valores: 0, 100, 200, 400, 600, 800, 870, 880, 890 e 900 ms. A última linha visível da série de 890 ms está cortada; a linha parcial não foi incluída nem reconstruída.

A malha foi configurada nominalmente para 10 ms, porém os timestamps extraídos incluem intervalos de 10 e 11 ms. A telemetria também mostra PWM saturado a partir de 600 ms e aumento da fração saturada em 800-900 ms. Essas janelas não comprovam experimentalmente o atraso crítico.

## Organização

```text
.
├── .github/workflows/tests.yml
├── dados/
│   ├── csv/                         # dez séries brutas, linhas completas
│   └── resumo_ensaios.csv
├── docs/
│   ├── Enunciado_Projeto_Pesquisa.pdf
│   ├── GUIA_PARA_AUTOR_RELATORIO.md
│   ├── MATRIZ_ATENDIMENTO_ENUNCIADO.md
│   ├── RELATORIO_TECNICO_REPASSE.md
│   └── evidencias/                  # índice e capturas visuais
├── firmware/                        # PI, PID, HEX e nota de integridade
├── proteus/AED.pdsprj
├── resultados/
│   ├── figuras/
│   └── tabelas/
├── scripts/                         # extracao, geracao, validacao e graficos
├── src/nyquist_toolkit/              # algoritmos
└── tests/                            # testes unitarios e regressao
```

## Limites que devem permanecer explícitos no artigo

1. Os resultados da aplicação EC são exclusivamente de simulação no Proteus.
2. Atraso é introduzido por software no histórico de A0, não por uma rede externa.
3. Os CSVs foram extraídos do PDF de evidências; não há logs originais brutos independentes anexados.
4. A linha final cortada da série 890 ms foi descartada.
5. A margem de atraso PI/PID apresentada é teórica, para modelo linear contínuo RC nominal; não é medição Proteus.
6. O HEX foi validado como Intel HEX, mas a correspondência binária com o `.ino` não foi recompilada/verificada.
7. As simulações em janelas de aproximadamente 9,4-10,0 s, com saturação de PWM para atrasos altos, não permitem alegar uma medição definitiva do atraso crítico.

## Referências de entrada

O enunciado original fornecido está preservado em [`docs/Enunciado_Projeto_Pesquisa.pdf`](docs/Enunciado_Projeto_Pesquisa.pdf). A evidência completa de 348 páginas foi a fonte de extração dos CSVs e das capturas selecionadas; o PDF visual do repositório é uma seleção de telas e não substitui a fonte de 348 páginas.
