# Análise computacional e comparativa de critérios de estabilidade em sistemas dinâmicos
## Rascunho técnico para adaptação ao modelo SBC ou IEEE

> **Status:** rascunho técnico baseado nos resultados computacionais reproduzidos no pacote. Não é submissão final. Os autores devem revisar citações, autoria, instituição, formatação oficial SBC/IEEE e resultados da demonstração antes de entregar.

### Resumo
Este trabalho apresenta uma implementação própria, em Python, de ferramentas para análise de estabilidade de sistemas lineares invariantes no tempo. O núcleo implementa avaliação em frequência, mapeamento de Nyquist e contagem de envoltórios, margens de estabilidade, tabela de Routh-Hurwitz, Lugar das Raízes e aproximação racional de Padé. Quatro benchmarks foram avaliados: planta estável de terceira ordem, planta instável em malha aberta, sistema de fase não mínima e sistema com atraso puro. A resposta em frequência foi comparada com SciPy, e a escalabilidade foi medida para polinômios de ordens 5, 10 e 20. Como aplicação da trilha de Engenharia da Computação, são documentados firmwares PI/PID e uma co-simulação Arduino/RC no Proteus com atraso de medição inserido por software. Os resultados indicam concordância numérica com SciPy na grade testada e evidenciam sensibilidade do cálculo de raízes em ordem elevada. A aplicação da trilha EC é inteiramente simulada no Proteus.

**Palavras-chave:** estabilidade; Nyquist; Routh-Hurwitz; Lugar das Raízes; atraso de transporte; sistemas embarcados.

### 1. Introdução
A estabilidade de sistemas realimentados pode ser examinada por métodos algébricos e por métodos no domínio da frequência. O critério de Nyquist é particularmente útil quando a malha aberta possui polos instáveis ou inclui atraso puro, pois relaciona os polos instáveis em malha fechada ao número de polos instáveis em malha aberta e aos envoltórios do ponto crítico. O objetivo deste projeto é implementar algoritmos reproduzíveis e comparar seus resultados em cenários representativos, sem utilizar uma toolbox pronta de controle.

### 2. Metodologia e arquitetura
A implementação foi desenvolvida em Python, com NumPy para operações numéricas e SciPy como referência independente de validação. A toolbox `python-control` não é utilizada. Os módulos estão em `src/nyquist_toolkit/`: `models.py`, `frequency.py`, `nyquist.py`, `routh.py`, `root_locus.py`, `delay.py` e `benchmarks.py`.

O módulo de Nyquist constrói um contorno do semiplano direito, mapeia a função de malha aberta e calcula o winding number geométrico em torno de \(-1+j0\). A implementação armazena o winding anti-horário \(W_{CCW}\) e converte para a convenção do enunciado, \(N=-W_{CCW}\), positivo para envoltórios horários. Assim, utiliza-se \(Z=P+N\). Polos exatamente no eixo imaginário são contornados por semiarcos de indentação no semiplano direito. A quantidade de polos na fronteira é reportada separadamente e não é contabilizada em P; o contorno indentado exclui esses pontos singulares.

A tabela de Routh trata elemento nulo na primeira coluna por substituição \(\epsilon\) e linha nula por polinômio auxiliar. O Lugar das Raízes é calculado para uma grade de ganhos e seus ramos são associados numericamente. Para sistemas com atraso, Nyquist avalia o fator exponencial exato \(e^{-j\omega\tau}\), enquanto métodos que exigem polinômio usam Padé-3, explicitamente identificado.

### 3. Modelos de benchmark
Foram adotados os seguintes modelos de malha aberta e ganhos:

| Caso | Função de transferência | Ganho | Característica |
|---|---|---:|---|
| A | \(1/(s^3+6s^2+11s+6)\) | 1 | estável, terceira ordem |
| B | \(1/(s^2+s-2)\) | 3 | um polo no semiplano direito |
| C | \((s-1)/(s^2+3s+2)\) | 1 | zero no semiplano direito |
| D | \(e^{-0,35s}/(0,5s+1)\) | 2 | atraso puro de 0,35 s |

Os modelos são benchmarks computacionais selecionados para cobrir os cenários do enunciado; não representam identificação experimental da planta RC.

### 4. Resultados dos critérios
No benchmark A, a análise encontrou \(P=0\), \(N=0\) e \(Z=0\), com estabilidade também indicada por Routh. No benchmark B, há um polo instável em malha aberta (\(P=1\)); o mapeamento apresenta \(W_{CCW}=+1\), logo \(N=-1\), e \(Z=0\) para o ganho escolhido. Esse exemplo mostra por que não se deve interpretar Nyquist ignorando a instabilidade de malha aberta. No benchmark C, o zero no semiplano direito é preservado no modelo, enquanto o sistema realimentado escolhido apresenta \(Z=0\). No benchmark D, o atraso exato é utilizado no Nyquist e Padé-3 é utilizado nas análises polinomiais; o Routh sobre Padé-3 indica estabilidade para o ganho escolhido.

As margens automáticas são calculadas a partir dos cruzamentos da resposta em frequência. Quando não há cruzamento de fase finito em \(-180^\circ\) na faixa analisada, a margem de ganho é registrada como “sem cruzamento finito”, em vez de se atribuir um valor arbitrário. Os CSVs de Bode, margens e benchmark preservam os valores completos.

### 5. Validação cruzada e escalabilidade
A comparação da resposta em frequência própria com `scipy.signal.freqresp`, aplicando independentemente o fator exponencial do atraso, apresentou erros absolutos máximos de \(7,47\\times10^{-17}\) (A), \(5,55\\times10^{-17}\) (B) e zero na precisão registrada (C e D) para a grade usada. A contagem de polos de Routh concordou com os autovalores da matriz companheira via SciPy nos casos racionais; no sistema D, a comparação algébrica refere-se explicitamente à aproximação Padé-3.

Foram realizadas 25 repetições por ordem. Nesta execução, os tempos medianos (µs) de Routh / `numpy.roots` / SciPy companion foram: n=5, 173,076 / 37,499 / 73,381; n=10, 215,813 / 46,391 / 81,309; n=20, 473,296 / 97,253 / 146,812. O erro máximo na recuperação dos polos geradores foi \(4,17\\times10^{-14}\), \(7,77\\times10^{-10}\) e \(1,228\\times10^{-1}\), respectivamente. Em n=20, o resíduo polinomial normalizado permaneceu \(2,13\\times10^{-16}\), embora a localização individual das raízes tenha piorado. Isso ilustra condicionamento numérico e sensibilidade dos problemas de raízes em alta ordem. Os tempos dependem do ambiente e não são constantes universais.

### 6. Atraso puro e aproximação de Padé
O modelo D utiliza o termo exponencial exato no domínio da frequência. Padé fornece uma representação racional aproximada necessária aos métodos polinomiais, mas não é idêntica ao atraso puro. A tabela `erro_atraso_exato_vs_pade.csv` contém a comparação implementada. A comparação quantitativa de fase utiliza erro angular circular, calculado como \(\left|\angle(H_{Pad\acute{e}}H_{exato}^{*})\right|\), em graus e no intervalo \([-180^\circ,180^\circ]\). Essa métrica evita que diferenças artificiais de ramo causadas pelo desenrolamento da fase contaminem o erro. A faixa de frequência analisada permanece registrada no CSV.

### 7. Aplicação da trilha EC: co-simulação
A aplicação utiliza um modelo nominal RC com \(R=4,7\\,k\\Omega\), \(C=100\\,\\mu F\) e constante de tempo de 0,47 s, além de firmware para Arduino Uno/ATmega328P. O PWM é emitido em D9; A0 mede a saída, A1 recebe o setpoint e A2 configura o atraso. O firmware mantém histórico de amostras e aplica atraso de medição por software. Há uma versão PI histórica (\(K_p=1,40\), \(K_i=1,00\), \(K_d=0\)) e uma versão PID posterior (\(K_p=1,40\), \(K_i=1,00\), \(K_d=0,08\), filtro derivativo de 0,05 s).

Os dados disponíveis contêm dez séries para atrasos de 0, 100, 200, 400, 600, 800, 870, 880, 890 e 900 ms, com 9.534 amostras completas extraídas dos documentos de evidência. Os intervalos de amostragem observados variam entre 10 e 11 ms, apesar do período nominal de 10 ms. A linha parcial final do ensaio de 890 ms foi descartada. Há saturação PWM nos atrasos elevados. Esses registros não comprovam experimentalmente o atraso crítico.

Para o modelo contínuo nominal, as previsões teóricas são: PI, cruzamento de ganho 2,283434 rad/s, margem de fase 115,607° e margem de atraso 883,636 ms; PID filtrado, 2,221707 rad/s, 122,815° e 964,813 ms. São previsões teóricas, não medições dos ensaios. O artefato Proteus foi inspecionado estruturalmente, mas não executado nesta auditoria; o firmware não foi recompilado com toolchain AVR neste ambiente. Portanto, a demonstração deve ser denominada **co-simulação Proteus com atraso de medição por software**.

### 8. Reprodutibilidade
Instalar as dependências de `requirements.txt`, executar `PYTHONPATH=src python -m pytest -q`, `python scripts/gerar_resultados.py`, `python scripts/plotar_telemetria.py` e `python scripts/validar_entrega.py`. As tabelas e figuras são regeneradas a partir dos modelos e dos CSVs versionados. A execução auditada registrou 55 testes aprovados.

### 9. Limitações e trabalhos futuros
As principais limitações são: (i) a indentação de polos no eixo imaginário exige escolha de raio de desvio e análise de convergência da discretização; (ii) limitações de rastreabilidade da compilação fonte-HEX nesta auditoria; (iii) dados de telemetria derivados de evidência documental, não logs brutos originais independentes; (iv) saturação em atrasos elevados; (v) dependência da comparação Padé em relação à faixa de frequência selecionada. Como trabalhos futuros, recomenda-se ampliar testes de convergência do contorno indentado, preservar as evidências da simulação Proteus já realizada, recompilar o firmware e realizar uma varredura de atraso com critério quantitativo de estabilidade.

### Referências
[1] K. Ogata, *Engenharia de Controle Moderno*, 5ª ed. São Paulo: Pearson, 2010.

[2] N. S. Nise, *Engenharia de Sistemas de Controle*, 7ª ed. Rio de Janeiro: LTC, 2017.

[3] K. J. Åström e R. M. Murray, *Feedback Systems: An Introduction for Scientists and Engineers*. Princeton University Press, 2008.

As referências acima reproduzem a bibliografia recomendada no enunciado; conferir o estilo de citação exigido pelo template SBC/IEEE adotado.
