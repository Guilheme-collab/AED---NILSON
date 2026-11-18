# Relatório técnico de repasse — Engenharia da Computação

**Projeto:** Análise Computacional e Comparativa de Critérios de Estabilidade em Sistemas Dinâmicos  
**Natureza:** implementação de algoritmos, dados reproduzíveis e aplicação inteiramente simulada no Proteus.  
**Status documental:** material técnico de apoio; não substitui a revisão final do artigo no template SBC/IEEE nem a apresentação do grupo.

## 1. Síntese da entrega

A consolidação reúne um núcleo computacional em Python para análise de estabilidade, os quatro benchmarks requeridos, validação cruzada, escalabilidade n=5/10/20, firmware PI histórico, firmware PID fornecido posteriormente, HEX PID, projeto Proteus, dez conjuntos CSV, figuras e documentação de repasse. A suíte atual possui 55 testes automatizados.

A aplicação da trilha EC é inteiramente simulada no Proteus. O projeto representa um Arduino Uno R3/ATmega328P e uma planta RC em ambiente de simulação. O atraso é colocado por software sobre o histórico da leitura A0. O relatório deve identificar claramente os resultados como simulação.

## 2. Arquitetura computacional

O pacote `src/nyquist_toolkit/` contém:

- `models.py`: representação de `N(s)/D(s)` com atraso opcional, polos e zeros, escalonamento e denominador de malha fechada para modelos racionais sem atraso.
- `frequency.py`: avaliação de `G(jω)`, magnitude/fase Bode, cruzamentos de 0 dB e -180°, margens de ganho/fase e estimativa de margem de atraso.
- `nyquist.py`: contorno fechado do semiplano direito, mapeamento de frequência e semicircunferência, e contagem de winding number.
- `routh.py`: tabela de Routh-Hurwitz, substituição `ε` para primeira coluna nula, polinômio auxiliar em linha nula e identificação de raízes no eixo imaginário.
- `root_locus.py`: cálculo de raízes de `D(s)+K N(s)` em uma malha de ganhos e associação de ramos por custo mínimo.
- `delay.py`: aproximação racional de Padé `[n/n]` e composição com função de transferência.
- `benchmarks.py`: modelos de referência A-D.

Não se utiliza a toolbox `python-control`. NumPy e SciPy são dependências numéricas auxiliares e referências independentes para validação. Para Nyquist, a contagem é obtida geometricamente no plano complexo.

### 2.1 Convenção de Nyquist

A função `winding_number` devolve o número assinado de voltas anti-horárias `W_CCW` da curva mapeada em torno de `-1+j0`. Para seguir a convenção do enunciado, define-se `N=-W_CCW`, positivo para envoltórios horários. Assim, `Z=P+N`.

O contorno implementa semiarcos de indentação no semiplano direito para polos no eixo imaginário. A análise informa separadamente os polos de fronteira, sem incluí-los em P.

## 3. Benchmarks

| Sistema | Modelo | Característica | K |
|---|---|---|---:|
| A | `1/(s³+6s²+11s+6)` | malha aberta estável, terceira ordem | 1 |
| B | `1/(s²+s-2)` | um polo de malha aberta no semiplano direito | 3 |
| C | `(s-1)/(s²+3s+2)` | zero no semiplano direito | 1 |
| D | `e^(-0.35s)/(0.5s+1)` | atraso puro exato de 0,35 s | 2 |

Os ganhos foram escolhidos para dar cenários comparáveis e exemplos de realimentação negativa estável. São modelos computacionais de benchmark; não devem ser descritos como identificação matemática da planta Arduino RC.

### 3.1 Resultado agregado

A tabela completa está em `resultados/tabelas/benchmark_resumo.csv`. Para A, B e C, Routh foi aplicado diretamente ao denominador característico polinomial. Para D, Nyquist usa o fator de atraso exato `exp(-jωτ)`; Routh e Root Locus usam explicitamente a aproximação Padé-3, pois o atraso puro não tem uma representação polinomial racional finita exata.

No benchmark B, `P=1`; o mapeamento resulta em `W_CCW=+1`, portanto `N=-1`, e `Z=P+N=0` para o ganho escolhido. Esse caso demonstra a importância de contabilizar a instabilidade em malha aberta em vez de interpretar a curva como se `P=0`.

## 4. Validação cruzada

`resultados/tabelas/validacao_cruzada_scipy.csv` confronta a resposta racional com `scipy.signal.freqresp`, aplica de modo independente o fator exponencial do atraso exato e compara a contagem de polos pelo critério de Routh com os autovalores de matrizes companheiras calculados por `scipy.linalg.eigvals`.

Os erros máximos absolutos de resposta em frequência foram inferiores a `7.5e-17` para os quatro exemplos na grade usada. As contagens de polos RHP concordaram para A-C; para D a comparação Routh/SciPy foi feita na aproximação Padé-3 e está rotulada como tal. A validação não afirma que Padé-3 seja idêntico ao atraso exato.

Os testes unitários verificam também a resposta de primeira ordem contra forma fechada, casos estáveis/instáveis de Routh, casos especiais, convergência da aproximação Padé, lugar das raízes, winding number e margens teóricas da planta RC. O relatório de execução atual está em `resultados/execucao_geracao.log`; a suíte foi executada como `PYTHONPATH=src python -m pytest -q`.

## 5. Escalabilidade e erros numéricos

`resultados/tabelas/escalabilidade_n5_n10_n20.csv` mede 25 execuções por ordem, usa polinômios construídos a partir de polos reais negativos conhecidos e registra mediana de tempo de Routh, NumPy roots e SciPy companion, além de erros de raízes e resíduo polinomial normalizado.

| Ordem | Tempo mediano Routh (µs) | NumPy roots (µs) | SciPy companion (µs) | Erro máx. polos recuperados |
|---:|---:|---:|---:|---:|
| 5 | 116,308 | 34,874 | 66,399 | `4,17e-14` |
| 10 | 229,952 | 48,129 | 100,784 | `7,77e-10` |
| 20 | 477,729 | 99,944 | 159,811 | `1,23e-1` |

Os tempos exatos são salvos no CSV gerado na execução e dependem do ambiente e da carga do sistema. O resultado de n=20 mostra que o polinômio pode ter resíduo normalizado muito pequeno enquanto a localização individual das raízes se afasta dos polos que geraram os coeficientes. Isso é uma evidência útil de condicionamento e sensibilidade numérica, não um número para ocultar.

## 6. Atraso puro e Padé

O sistema D é avaliado em Nyquist com o atraso exato `exp(-jωτ)`. A tabela `erro_atraso_exato_vs_pade.csv` e o gráfico `atraso_exato_vs_pade_sistema_D.svg` confrontam as aproximações Padé 1, 3 e 5 no intervalo de frequência especificado no próprio CSV.

Routh e Root Locus precisam de polinômios; portanto, para D, a documentação usa Padé-3 e identifica a aproximação no nome do arquivo/título. O atraso exato e a aproximação racional não são intercambiáveis, especialmente fora da faixa de frequência em que a aproximação foi avaliada.

## 7. Margens teóricas da planta RC

A planta nominal é `G(s)=1/(0.47s+1)`, decorrente de `R=4.7 kΩ` e `C=100 µF`, portanto `τ_RC=0.47 s`.

**Controlador PI:** `C_PI(s)=1.4+1/s`, logo `L_PI(s)=(1.4s+1)/(s(0.47s+1))`. A análise contínua numérica obteve cruzamento de ganho próximo de `2.283434 rad/s`, margem de fase próxima de `115.607°` e margem de atraso estimada de `883.636 ms`.

**Controlador PID filtrado:** `C_PID(s)=1.4+1/s+0.08s/(0.05s+1)`. A malha aberta equivalente é `L_PID(s)=(0.15s²+1.45s+1)/(0.0235s³+0.52s²+s)`. A análise obteve cruzamento de ganho próximo de `2.221707 rad/s`, margem de fase próxima de `122.815°` e margem de atraso estimada de `964.813 ms`.

Nos dois modelos não foi encontrado cruzamento de fase finito em -180° na análise usada; por isso a margem de ganho aparece como “sem cruzamento finito”, não como um número arbitrariamente escolhido. Esses resultados são previsões teóricas do modelo contínuo e não devem ser confundidos com os valores observados nas séries de simulação.

## 8. Protótipo simulado Arduino/Proteus

### 8.1 Hardware virtual e topologia

- Arduino Uno R3 / ATmega328P, clock de 16 MHz.
- Planta RC nominal `R1=4.7 kΩ`, `C1=100 µF`, constante de tempo `0.47 s`.
- D9: PWM do controlador.
- A0: medição da saída RC.
- A1: setpoint.
- A2: ajuste de atraso por potenciômetro.
- Buffer circular de amostras, com atraso até 1000 ms em passos nominais de 10 ms.
- Telemetria serial CSV a 115200 baud.

O circuito editável está em `proteus/AED.pdsprj`. O caminho do Programa/HEX foi trocado de um caminho antigo e específico de máquina para `../firmware/PID_Nyquist_Proteus_Arduino_PID.ino.hex`. O projeto é um arquivo ZIP/DSN estruturalmente válido; não foi aberto no aplicativo Proteus neste ambiente.

### 8.2 Firmware PI e PID

O arquivo antigo do repositório se chamava `PID_Nyquist_Proteus_Arduino.ino`, mas seu conteúdo definia `KD=0.00`; tecnicamente era firmware PI. Ele foi preservado e renomeado para `PI_Nyquist_Proteus_Arduino.ino`. O firmware posterior com `KD=0.08`, filtro derivativo `0.05 s` e mesma topologia foi incluído separadamente como `PID_Nyquist_Proteus_Arduino_PID.ino`. O HEX recebido acompanha a versão PID.

A separação evita usar um nome PID para um ensaio PI ou inferir ação derivativa onde `Kd=0`.

### 8.3 Ensaios e evidências

O PDF original fornecido contém 348 páginas e está preservado em `docs/evidencias/Evidencias_Proteus_Fonte_Completa.pdf`. A primeira tabela mostra oito atrasos (0, 100, 200, 400, 600, 800, 880 e 900 ms); o restante do mesmo documento contém séries completas para 870 e 890 ms. Foram extraídas dez séries, na ordem `0, 100, 200, 400, 600, 800, 870, 880, 890, 900 ms`, com total de 9.534 linhas completas.

As capturas selecionadas estão individualmente em `docs/evidencias/capturas/`; o mapa de cada imagem e sua página de origem estão em `docs/evidencias/LEIA-ME.md`. O CSV de cada atraso preserva os valores completos de `tempo_ms`, `setpoint_V`, `saida_V`, `saida_atrasada_V`, `pwm` e `atraso_ms`.

| Atraso (ms) | Amostras completas | Duração (s) | Saída final (V) | PWM saturado (%) |
|---:|---:|---:|---:|---:|
| 0 | 1001 | 10,039 | 2,493 | 0,00 |
| 100 | 939 | 9,417 | 2,488 | 0,00 |
| 200 | 940 | 9,427 | 2,493 | 0,00 |
| 400 | 941 | 9,437 | 2,498 | 0,00 |
| 600 | 945 | 9,477 | 2,507 | 0,21 |
| 800 | 952 | 9,548 | 1,667 | 6,09 |
| 870 | 954 | 9,568 | 3,348 | 15,83 |
| 880 | 954 | 9,568 | 3,539 | 17,51 |
| 890 | 954 | 9,568 | 3,734 | 18,97 |
| 900 | 954 | 9,568 | 3,881 | 20,02 |

O setpoint registrado é aproximadamente constante em `2.502 V`. As amostras de tempo têm incrementos de 10 e 11 ms, apesar do período nominal de 10 ms. A fração saturada foi calculada como amostras em PWM=0 ou PWM=255, divididas pelo total de linhas completas. A resposta dos atrasos elevados apresenta saturação e divergência em relação ao setpoint na janela registrada; isso não deve ser convertido automaticamente em um rótulo formal de estabilidade.

A última linha visível da série 890 ms está truncada em `9588,2.502,3.705,3.`. Ela não foi completada nem exportada para o CSV. Linhas parciais em outras fronteiras de página também foram descartadas pelo extrator.

## 9. Integridade de arquivos e limites de validação

- O HEX foi lido como Intel HEX: 339 registros, um registro EOF e checksums válidos em todos os registros. SHA-256: `012e3c69eeb1a7937473d8698a624afba0e849e2b92872e17e9396a65db15ff8`.
- Isso não prova que o HEX corresponde exatamente ao `.ino`, pois `arduino-cli`, `avr-g++`, `avr-gcc` e `avr-objcopy` não estavam disponíveis para recompilação neste ambiente.
- O `.pdsprj` foi validado como arquivo ZIP com `ROOT.DSN`, `ROOT.CDB`, `PROJECT.XML` e `SCRIPTS/PWRRAILS.DAT`; o caminho do HEX foi ajustado. A auditoria atual não reexecutou o Proteus; as evidências da simulação foram fornecidas pelo aluno.
- O PDF original de evidências serviu de fonte dos CSVs e imagens. As imagens WebP do repositório são uma seleção de telas, não o PDF completo de 348 páginas.
- A aplicação é exclusivamente simulada; todos os resultados devem ser identificados como simulação.

## 10. Discrepâncias encontradas e decisões de consolidação

1. **Firmware mal nomeado:** o arquivo remoto com “PID” continha `Kd=0`; foi preservado como PI, com nome corrigido. O firmware PID posterior com `Kd=0.08` foi incluído em arquivo separado.
2. **Documentação apontava para arquivos ausentes:** README/listas anteriores citavam CSVs individuais, figuras, relatório PDF/DOCX e evidências que não estavam na árvore `main`. A nova documentação aponta somente para arquivos presentes nesta consolidação.
3. **Tabela inicial com apenas oito ensaios:** 870 e 890 ms foram recuperados do corpo do PDF e adicionados ao índice; nenhum dado foi descartado por não estar na primeira tabela.
4. **Linha truncada:** linhas CSV incompletas, incluindo a última linha de 890 ms, foram omitidas; nenhum valor sintético foi criado.
5. **Caminho HEX absoluto/antigo no Proteus:** substituído por caminho relativo para o HEX da versão PID deste repositório.
6. **PI x PID na evidência:** firmware, resultados teóricos e evidências são identificados separadamente. A associação das capturas ao lote PID é coerente com o arquivo de projeto e o contexto do usuário, mas não há prova criptográfica de compilação fonte-binário.
7. **Atraso crítico:** `883.636 ms` (PI) e `964.813 ms` (PID filtrado) são previsões teóricas; não são valores medidos nos CSVs. Os ensaios têm janelas finitas e saturação nos atrasos altos.
8. **Escopo da aplicação:** documentar como simulação Proteus com atraso de medição aplicado por software.
9. **Escalabilidade:** medições n=5,10,20 e erros foram gerados nesta execução, com ressalva sobre dependência de ambiente e condicionamento em n=20.

## 11. Responsabilidades e estado final

A parte técnica EC está organizada para repasse: algoritmos, modelos, testes, resultados, fontes dos firmwares, projeto Proteus, dados, evidências e matriz de atendimento estão no repositório. O integrante responsável pelo artigo deve redigir a interpretação acadêmica, inserir as figuras/tabelas pertinentes, discutir limitações e formatar conforme SBC/IEEE. O seminário continua como atividade do grupo e não foi produzido neste pacote.
