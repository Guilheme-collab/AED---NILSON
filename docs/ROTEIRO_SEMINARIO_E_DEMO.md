# Roteiro de seminário e demonstração — 12 a 15 minutos

> Roteiro para apresentação da trilha EC. A aplicação é inteiramente simulada no Proteus. As imagens/figuras devem ser inseridas a partir de `resultados/figuras/`.

## Slide 1 — Título e objetivo (1 min)
- Análise Computacional e Comparativa de Critérios de Estabilidade em Sistemas Dinâmicos.
- Objetivo: implementar Nyquist e comparar com Routh, Lugar das Raízes e Bode.
- Ferramentas: Python, NumPy e SciPy para validação.

## Slide 2 — Fundamento de Nyquist (1,5 min)
- Princípio do Argumento e mapeamento do contorno do semiplano direito.
- Convenção: N positivo para envoltórios horários; Z=P+N.
- Ressaltar que a contagem de polos instáveis em malha aberta é essencial.

## Slide 3 — Arquitetura implementada (1 min)
- Apresentar `models`, `frequency`, `nyquist`, `routh`, `root_locus`, `delay`.
- Informar que não foi usada toolbox pronta `python-control`.
- Mostrar testes unitários e workflow de CI.

## Slide 4 — Quatro benchmarks (2 min)
- A: estável, 3ª ordem.
- B: instável em malha aberta, P=1; N=-1; Z=0.
- C: zero no semiplano direito.
- D: atraso puro 0,35 s; Nyquist exato, Padé-3 nos métodos polinomiais.
- Inserir os quatro diagramas Nyquist e a tabela `benchmark_resumo.csv`.

## Slide 5 — Métodos comparativos (1 min)
- Routh: estabilidade algébrica e casos especiais.
- Root Locus: evolução dos polos com K.
- Bode: magnitude, fase e margens.
- Nyquist: atrasos e malha aberta instável.

## Slide 6 — Validação cruzada (1 min)
- Comparação com SciPy: erro máximo de resposta na ordem de 1e-17 na grade utilizada.
- Contagem Routh vs autovalores SciPy concorda; D usa Padé-3.
- Mostrar `validacao_cruzada_scipy.csv`.

## Slide 7 — Escalabilidade e precisão (1 min)
- 25 repetições para n=5, 10 e 20.
- Mostrar tempos medianos e erro de raízes.
- Destacar n=20: erro de recuperação ~0,123 apesar de resíduo polinomial ~2,13e-16; discutir condicionamento.

## Slide 8 — Aplicação EC simulada (2 min)
- Planta RC nominal: R=4,7 kΩ, C=100 µF, tau=0,47 s.
- Arduino Uno virtual no Proteus; PI histórico e PID posterior são versões separadas.
- Atraso é inserido por software no histórico da medição.
- Mostrar topologia e capturas; explicar telemetria e saturação nos atrasos altos.

## Slide 9 — Margens teóricas e interpretação (1 min)
- PI: margem de atraso teórica ~883,636 ms.
- PID filtrado: ~964,813 ms.
- Não são valores medidos; os dez ensaios não confirmam o limite crítico.

## Slide 10 — Limitações e conclusão (1 min)
- Aplicação inteiramente simulada no Proteus.
- Proteus não foi reexecutado nesta auditoria; HEX não foi recompilado do fonte.
- O polo no eixo imaginário é tratado por indentação semicircular numérica; explicar que o raio/discretização devem ser verificados em casos críticos.
- Concluir: núcleo computacional testado; aplicação e limitações explicitamente documentadas.

## Perguntas prováveis
**Por que Nyquist é útil com malha aberta instável?** Porque incorpora P na relação Z=P+N; o benchmark B demonstra o caso.

**Por que Padé é usado?** Routh e Root Locus requerem polinômios; Nyquist pode avaliar o atraso exponencial exato.

**Os 883,636 ms foram medidos?** Não. São previsão teórica do modelo contínuo PI/RC.

**Como foi realizada a aplicação?** Por simulação no Proteus, com atraso introduzido por software.

**O que significa o erro em n=20?** Sensibilidade do cálculo das raízes aos coeficientes em alta ordem, apesar de pequeno resíduo polinomial.
