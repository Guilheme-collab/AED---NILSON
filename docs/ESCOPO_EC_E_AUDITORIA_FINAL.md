# Escopo Engenharia da Computação — auditoria final dos artefatos computacionais

**Data da reexecução:** 18/11/2026  
**Escopo:** exclusivamente Engenharia da Computação (EC). A aplicação prática é integralmente simulada. A simulação Proteus e suas evidências foram fornecidas pelo aluno; este pacote preserva os arquivos associados, mas a presente auditoria concentra-se nos componentes que podem ser reproduzidos sem abrir o Proteus.

## Resultado executivo

- Suíte automatizada: **55/55 testes aprovados**.
- Geração de resultados: concluída com código de saída 0.
- Geração de figuras de telemetria: concluída com código de saída 0.
- Validação estrutural: concluída com código de saída 0.
- Benchmarks: quatro cenários A–D.
- Validação cruzada: quatro registros de comparação com SciPy.
- Escalabilidade: ordens 5, 10 e 20, com 25 repetições por ordem.
- Telemetria já fornecida: 10 séries e 9.534 amostras completas; nenhuma amostra truncada foi reconstruída.

## Checklist do enunciado, restrito à trilha EC

| Requisito | Artefato / evidência | Resultado da auditoria |
|---|---|---|
| Ferramenta computacional para sistemas LIT | `src/nyquist_toolkit/models.py` e `README.md` | Implementado |
| Nyquist e Princípio do Argumento | `nyquist.py`, `benchmark_resumo.csv`, figuras Nyquist A–D | Implementado para os benchmarks sem polos no eixo imaginário; limitação de indentação explicitada |
| Mapeamento de malha aberta | `nyquist.py`, curvas exportadas | Implementado |
| Margens de ganho e fase | `frequency.py`, Bode e tabelas de margens | Implementado; ausência de cruzamento é indicada sem inventar valor |
| Routh-Hurwitz próprio | `routh.py` e testes de casos especiais | Implementado; 55 testes aprovados |
| Lugar das Raízes próprio | `root_locus.py`, quatro CSVs e quatro figuras | Implementado; para D usa-se Padé-3 por ser método polinomial |
| Comparação com Bode | `frequency.py`, quatro CSVs e quatro figuras | Implementado |
| Atraso puro exato versus Padé | `delay.py`, CSV e figura comparativa | Implementado; interpretação da fase requer métrica circular complementar |
| Quatro benchmarks | `benchmarks.py`, tabelas e figuras A–D | Implementado |
| Validação cruzada | `validacao_cruzada_scipy.csv` | Executada para os casos e grade descritos no CSV |
| Complexidade e erro numérico | `escalabilidade_n5_n10_n20.csv` | Executada; 25 repetições em cada ordem |
| Aplicação específica EC com atraso variável | Firmware PI/PID, projeto Proteus, dez séries CSV e evidências já fornecidas | Artefatos incluídos; caracterizar exclusivamente como simulação |
| Previsão de atraso crítico via Nyquist | `margens_teoricas_PI_PID.csv` | Calculada teoricamente; não confundir previsão com medição |
| Reprodutibilidade | `requirements.txt`, scripts, testes e workflow CI | Instruções e automação incluídas |
| Artigo SBC/IEEE | `ARTIGO_CIENTIFICO_RASCUNHO_SBC_IEEE.md` | Rascunho técnico completo como base; falta revisão/autoria e aplicação do template oficial |
| Seminário e demonstração | `ROTEIRO_SEMINARIO_E_DEMO.md` | Roteiro preparado; apresentação oral é atividade do grupo |

A aplicação interativa da trilha CC não é requisito desta entrega individual EC e não deve ser listada como pendência.

## Correções matemáticas incluídas nesta revisão

- O contorno de Nyquist contorna polos no eixo imaginário por semiarcos no semiplano direito; a quantidade de polos na fronteira é retornada separadamente. Foi testado com integrador e com par de polos imaginários.
- O erro de fase Padé é circular: `angle(H_pade * conj(H_exato))`, em graus, limitado a [-180°, 180°].

## Resultados numéricos reproduzidos nesta execução

| Ordem | Tempo mediano Routh (µs) | Tempo mediano NumPy roots (µs) | Tempo mediano SciPy companion (µs) | Erro máx. raízes vs. raízes geradoras | Resíduo polinomial normalizado |
|---:|---:|---:|---:|---:|---:|
| 5 | 116,308 | 34,874 | 66,399 | 4,174439e-14 | 1,480297e-16 |
| 10 | 229,952 | 48,129 | 100,784 | 7,770331e-10 | 5,462092e-16 |
| 20 | 477,729 | 99,944 | 159,811 | 1,228020e-1 | 2,132472e-16 |

Os tempos são específicos desta execução/ambiente. O erro de localização de raízes em ordem 20 deve ser discutido como sensibilidade numérica, não omitido.

## Limitações técnicas que precisam constar no relatório

1. `nyquist_contour()` implementa indentação semicircular para polos no eixo imaginário, desviando o contorno para o semiplano direito. A análise informa separadamente quantos polos de fronteira foram encontrados; eles não são somados a P.
2. A tabela de comparação de atraso/Padé contém diferenças de fase circular. Não usar esse valor isoladamente como erro angular circular; a discussão deve registrar essa limitação.
3. O HEX foi verificado estruturalmente (339 registros, 338 registros de dados e EOF único, checksums válidos), mas não foi recompilado neste ambiente a partir do `.ino`; não afirmar rastreabilidade binária confirmada.
4. Os valores de margem de atraso PI/PID são previsões teóricas do modelo contínuo, não resultados medidos nos ensaios simulados.
5. A telemetria foi extraída de evidência documental; uma linha parcial do ensaio de 890 ms foi descartada, sem interpolação ou fabricação de amostras.
6. O artigo está em formato Markdown de rascunho e precisa ser adaptado ao template SBC/IEEE adotado pela disciplina, com autoria e revisão final.
7. O roteiro do seminário está preparado, mas a apresentação oral e a demonstração pelo grupo ainda precisam ocorrer.

## Comandos reproduzidos

```bash
PYTHONPATH=src python -m pytest -q
python scripts/gerar_resultados.py
python scripts/plotar_telemetria.py
python scripts/validar_entrega.py
```

Todos os comandos retornaram código 0; a suíte retornou 55 testes aprovados. A validação estrutural também verificou os CSVs, o Intel HEX e a estrutura dos arquivos associados à simulação.

## Conclusão

O pacote contém o núcleo computacional EC, os quatro benchmarks, resultados quantitativos, tabelas, figuras, dados de simulação fornecidos, firmware, documentação e roteiro para elaboração do relatório. A auditoria comprova a execução dos testes e geradores listados. Não se declara conformidade absoluta para casos matemáticos não implementados (polos de Nyquist na fronteira), nem que rascunho de artigo/apresentação equivalham aos entregáveis finais do grupo. Esta é a conclusão verificável sem extrapolar o que os arquivos e execuções demonstram.
