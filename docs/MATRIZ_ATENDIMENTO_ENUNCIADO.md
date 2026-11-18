# Matriz de atendimento ao enunciado — verificação técnica

**Referência:** `Enunciado_Projeto_Pesquisa.pdf` (seções 2 a 6).  
**Escopo individual:** exclusivamente Engenharia da Computação. Toda a aplicação é simulada; a simulação Proteus e suas evidências foram fornecidas pelo aluno.  
**Inventário:** 45 pontos de verificação rastreáveis criados para esta consolidação. A conversa anterior mencionou “45 coisas novas”, mas não continha uma lista nominal dos 45 itens anteriores; portanto, esta matriz não declara equivalência automática com uma lista histórica não disponível.

| # | Requisito / ponto de verificação | Implementação / evidência no repositório | Estado |
|---:|---|---|---|
| 1 | Representar função de transferência racional | `src/nyquist_toolkit/models.py` | IMPLEMENTADO |
| 2 | Validar coeficientes e parâmetros finitos | `models.py`; testes em `tests/test_core.py` | IMPLEMENTADO |
| 3 | Calcular polos e zeros | `TransferFunction.poles` e `.zeros` | IMPLEMENTADO |
| 4 | Avaliar função de transferência em variável complexa `s` | `frequency.py:evaluate_s` | IMPLEMENTADO |
| 5 | Aplicar atraso exato `exp(-τs)` na avaliação | `frequency.py`; teste `test_frequency_response_applies_exact_delay` | IMPLEMENTADO |
| 6 | Calcular resposta em frequência `G(jω)` | `frequency.py:frequency_response` | IMPLEMENTADO |
| 7 | Gerar magnitude Bode em dB | `frequency.py:bode_data`; CSVs em `resultados/tabelas/` | IMPLEMENTADO |
| 8 | Gerar fase Bode desenrolada | `frequency.py:bode_data`; CSVs em `resultados/tabelas/` | IMPLEMENTADO |
| 9 | Detectar automaticamente cruzamentos de ganho | `frequency.py:stability_margins` | IMPLEMENTADO |
| 10 | Detectar cruzamentos de fase | `frequency.py:stability_margins` | IMPLEMENTADO |
| 11 | Calcular margem de ganho | `frequency.py`; tabelas benchmark/margens | IMPLEMENTADO; “sem cruzamento finito” é reportado como tal |
| 12 | Calcular margem de fase | `frequency.py`; `margens_teoricas_PI_PID.csv` | IMPLEMENTADO |
| 13 | Estimar margem de atraso | `frequency.py`; tabela teórica PI/PID | IMPLEMENTADO |
| 14 | Construir contorno de Nyquist para semiplano direito | `nyquist.py:nyquist_contour` | IMPLEMENTADO |
| 15 | Mapear contorno pelo sistema em malha aberta | `nyquist.py:nyquist_analysis` | IMPLEMENTADO |
| 16 | Contar winding number ao redor de `-1+j0` | `nyquist.py:winding_number` | IMPLEMENTADO |
| 17 | Aplicar relação do Princípio do Argumento `Z=P+N` | `nyquist.py`; convenção assinada registrada nos resultados | IMPLEMENTADO |
| 18 | Contar polos de malha aberta no semiplano direito | `nyquist.py:nyquist_analysis` | IMPLEMENTADO |
| 19 | Tratar polos no eixo imaginário sem fingir contorno regular | Rejeição explícita e mensagem exigindo indentação | LIMITAÇÃO EXPLÍCITA / CASO COM INDENTAÇÃO NÃO IMPLEMENTADO |
| 20 | Construir tabela de Routh-Hurwitz própria | `routh.py:routh_table` | IMPLEMENTADO |
| 21 | Tratar zeros na primeira coluna com `ε` | `routh.py`; teste de regressão | IMPLEMENTADO |
| 22 | Tratar linha inteira nula com polinômio auxiliar | `routh.py`; teste de regressão | IMPLEMENTADO |
| 23 | Distinguir estabilidade estrita de polos no eixo imaginário | `routh.py`; `imaginary_axis_pole_count` | IMPLEMENTADO |
| 24 | Calcular polos de malha fechada para realimentação unitária | `models.py:closed_loop_denominator` e cálculo de raízes | IMPLEMENTADO PARA MODELOS RACIONAIS |
| 25 | Traçar Lugar das Raízes em função do ganho `K` | `root_locus.py`; gráficos A-D | IMPLEMENTADO; D usa Padé-3 |
| 26 | Associar numericamente os ramos do Lugar das Raízes | `root_locus.py` com atribuição de custo mínimo | IMPLEMENTADO |
| 27 | Gerar aproximação de Padé de ordem configurável | `delay.py:pade_delay` | IMPLEMENTADO |
| 28 | Comparar atraso exato com Padé | `erro_atraso_exato_vs_pade.csv` e figura dedicada | IMPLEMENTADO |
| 29 | Benchmark A: malha aberta estável, terceira ordem | `benchmarks.py`; tabelas, diagramas e testes | IMPLEMENTADO |
| 30 | Benchmark B: malha aberta instável | `benchmarks.py`; Nyquist mostra `P=1`, `N=-1`, `Z=0` para K=3 | IMPLEMENTADO |
| 31 | Benchmark C: zero no semiplano direito | `benchmarks.py`; figuras e tabelas | IMPLEMENTADO |
| 32 | Benchmark D: atraso puro significativo | `benchmarks.py`; Nyquist exato e Routh/Root Locus Padé-3 | IMPLEMENTADO COM MÉTODOS DIFERENCIADOS |
| 33 | Gerar diagramas de Bode | `resultados/figuras/bode_sistema_*.svg` | IMPLEMENTADO |
| 34 | Gerar diagramas de Nyquist | `resultados/figuras/nyquist_sistema_*.svg` | IMPLEMENTADO |
| 35 | Gerar figuras e dados de Lugar das Raízes | `resultados/figuras/root_locus_*.svg` e CSVs | IMPLEMENTADO |
| 36 | Disponibilizar tabelas de Routh | `resultados/tabelas/routh_sistema_*.csv` | IMPLEMENTADO |
| 37 | Validar resposta em frequência contra SciPy | `validacao_cruzada_scipy.csv` | IMPLEMENTADO; erro máximo observado abaixo de 7,5e-17 na grade usada |
| 38 | Validar contagem de polos contra SciPy | Routh versus autovalores da matriz companheira em `validacao_cruzada_scipy.csv` | IMPLEMENTADO; D usa Padé-3 para a parte polinomial |
| 39 | Manter suíte de testes automatizados | `tests/test_core.py`; 55 testes aprovados nesta execução | IMPLEMENTADO / TESTES APROVADOS |
| 40 | Dar instruções de reprodutibilidade | `README.md`, `requirements.txt`, scripts e workflow CI | IMPLEMENTADO |
| 41 | Testar escalabilidade para n=5 e n=10 | `escalabilidade_n5_n10_n20.csv` | IMPLEMENTADO |
| 42 | Testar escalabilidade para n=20 | Mesmo CSV; erro das raízes é explicitado | IMPLEMENTADO |
| 43 | Medir tempo e erro numérico | 25 repetições por ordem, mediana, erro de raízes e resíduo | IMPLEMENTADO; tempos dependem do ambiente |
| 44 | Preservar PI e PID, HEX e projeto Proteus editável | `firmware/PI_...ino`, `firmware/PID_...ino`, HEX e `proteus/AED.pdsprj` | IMPLEMENTADO; compilação fonte-HEX não comprovada |
| 45 | Disponibilizar telemetria, fotos e evidências para relatório | 10 CSVs, resumo, capturas visuais WebP e guia de relatório | IMPLEMENTADO; linhas truncadas foram omitidas |

## Itens do documento do professor que não são declarados como concluídos pela entrega individual

| Item do enunciado | Tratamento nesta entrega |
|---|---|
| Aplicação EC simulada com atraso variável | Evidências da co-simulação Proteus fornecidas pelo aluno; atraso configurado por software. Descrever sempre como simulação. |
| Aplicação visual interativa da trilha CC | Fora do escopo desta entrega individual da trilha EC. |
| Artigo científico SBC/IEEE | Redação atribuída ao outro integrante; esta entrega fornece dados, algoritmos e guia de repasse. |
| Seminário oral | Responsabilidade do grupo; não produzido nesta entrega técnica individual. |


## Critério de leitura da matriz

“Implementado” significa que existe código/artefato rastreável no repositório e que a validação indicada foi executada. Não significa que um circuito físico foi montado, que Proteus foi executado durante a auditoria, que o HEX foi recompilado, nem que o artigo/seminário estão concluídos. As limitações estão no estado e nas notas de cada linha.
