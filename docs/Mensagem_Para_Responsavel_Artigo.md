# Mensagem de repasse ao responsável pelo artigo/relatório

Estou encaminhando a contribuição técnica da Engenharia da Computação: núcleo de análise de estabilidade em Python, quatro benchmarks, validação cruzada com SciPy, escalabilidade n=5/10/20, firmwares PI/PID separados, HEX da versão PID, projeto Proteus, dez CSVs e evidências visuais.

Comece por `GUIA_PARA_AUTOR_RELATORIO.md`, `RELATORIO_TECNICO_REPASSE.md` e `MATRIZ_ATENDIMENTO_ENUNCIADO.md`. Os resultados principais estão em `resultados/tabelas/`; os gráficos estão em `resultados/figuras/`; os dez registros de telemetria estão em `dados/csv/`.

A versão PI histórica usa Kp=1,40, Ki=1,00, Kd=0,00. A versão PID posterior usa Kp=1,40, Ki=1,00, Kd=0,08 e possui HEX fornecido. Não misture os dados/arquivos das duas versões.

A aplicação EC foi realizada por simulação Arduino/RC no Proteus, com atraso aplicado por software no histórico de A0. O PDF original lista oito atrasos na tabela inicial, mas contém dez séries completas: 0, 100, 200, 400, 600, 800, 870, 880, 890 e 900 ms. A série 890 ms termina com uma linha parcial, que não foi inventada nem incluída no CSV.

Os valores de margem de atraso de aproximadamente 883,636 ms (PI) e 964,813 ms (PID filtrado) são cálculos teóricos do modelo linear RC nominal, não medidas do Proteus. As janelas registradas têm cerca de 9,4-10,0 s e mostram saturação PWM nos atrasos altos, portanto não declare atraso crítico experimental comprovado.
