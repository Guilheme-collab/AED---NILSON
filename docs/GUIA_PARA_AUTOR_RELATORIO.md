# Guia de repasse para quem escreverá o artigo/relatório

Este documento não é o artigo científico. É um roteiro técnico para que o integrante responsável pela redação use os materiais corretos, não misture versões e não atribua resultados simulados ou teóricos como se fossem medições físicas.

## 1. Arquivos de leitura obrigatória

| Para escrever sobre | Fonte principal |
|---|---|
| Requisitos do professor | `docs/Enunciado_Projeto_Pesquisa.pdf` |
| Arquitetura e ressalvas da implementação | `docs/RELATORIO_TECNICO_REPASSE.md` |
| Atendimento requisito a requisito | `docs/MATRIZ_ATENDIMENTO_ENUNCIADO.md` |
| Algoritmos | `src/nyquist_toolkit/` |
| Modelos e números dos benchmarks | `resultados/tabelas/benchmark_resumo.csv` |
| Cross-validation | `resultados/tabelas/validacao_cruzada_scipy.csv` |
| Complexidade numérica n=5,10,20 | `resultados/tabelas/escalabilidade_n5_n10_n20.csv` |
| Routh por sistema | `resultados/tabelas/routh_sistema_*.csv` |
| Bode numérico | `resultados/tabelas/bode_sistema_*.csv` |
| Root Locus numérico | `resultados/tabelas/root_locus_sistema_*.csv` |
| Atraso exato e Padé | `resultados/tabelas/erro_atraso_exato_vs_pade.csv` e `resultados/figuras/atraso_exato_vs_pade_sistema_D.svg` |
| Teoria PI/PID da planta RC | `resultados/tabelas/margens_teoricas_PI_PID.csv` |
| Ensaios no Proteus | `docs/evidencias/Evidencias_Proteus_Fonte_Completa.pdf`, capturas, `dados/csv/` e `dados/resumo_ensaios.csv` |

## 2. Sugestão de estrutura para a seção técnica

1. **Metodologia computacional:** explique representação polinomial, avaliação complexa e ferramentas de apoio (NumPy/SciPy), deixando claro que não foi usada a toolbox `python-control`.
2. **Critério de Nyquist:** explique o contorno do semiplano direito, o mapeamento e a convenção `Z=P+N`. Use os quatro diagramas `nyquist_sistema_A.svg` até `nyquist_sistema_D.svg` e a tabela `benchmark_resumo.csv`.
3. **Métodos clássicos:** apresente Routh-Hurwitz e suas exceções, polos e Lugar das Raízes; use as tabelas de Routh e os gráficos de Root Locus.
4. **Bode e margens:** use tabelas de Bode e margens. Não force valor finito de margem de ganho quando o modelo não apresenta cruzamento de fase finito na faixa/análise adotada.
5. **Atraso:** compare o termo exato `exp(-jωτ)` com Padé 1/3/5; deixe claro que Routh aplicado ao sistema D usa uma aproximação racional Padé-3, enquanto Nyquist usa o atraso exato.
6. **Validação:** apresente as divergências/erros medidos na validação cruzada com SciPy, incluindo a interpretação adequada.
7. **Escalabilidade:** apresente tempos medidos no ambiente desta execução e o erro numérico de raízes para n=5, 10 e 20. Os tempos não são universais.
8. **Aplicação EC:** apresente as evidências Proteus, arquitetura Arduino/RC e os dez CSVs, descrevendo o atraso como atraso de medição em software.

## 3. Como usar a parte prática sem misturar PI e PID

- **PI histórico:** `firmware/PI_Nyquist_Proteus_Arduino.ino`, com `Kp=1.40`, `Ki=1.00`, `Kd=0.00`.
- **PID posterior:** `firmware/PID_Nyquist_Proteus_Arduino_PID.ino`, com `Kp=1.40`, `Ki=1.00`, `Kd=0.08` e filtro derivativo de `0.05 s`.
- **HEX associado ao pacote PID:** `firmware/PID_Nyquist_Proteus_Arduino_PID.ino.hex`. A estrutura/checksums são válidos, mas a compilação fonte-binário não foi confirmada neste ambiente.
- **Projeto Proteus:** `proteus/AED.pdsprj`, cujo caminho de programa foi ajustado para apontar relativamente para o HEX PID.

O PDF de evidências foi enviado junto com os arquivos PID/Proteus e o projeto Proteus referencia o caminho do HEX PID. Isso é coerente com a atribuição do lote à versão PID, mas não há manifesto de compilação, hash de origem ou sessão de execução que prove bit a bit que cada captura veio exatamente desse `.ino`/HEX.

## 4. Como interpretar os dez ensaios

As configurações são 0, 100, 200, 400, 600, 800, 870, 880, 890 e 900 ms. A tabela da primeira página da evidência contém somente oito configurações; 870 e 890 ms aparecem em séries posteriores do mesmo documento. Os dados foram extraídos por linhas CSV completas, resultando em 9.534 amostras.

Nos ensaios de 0 a 400 ms, o PWM não atinge os extremos 0 ou 255 nos dados extraídos. Em 600 ms há duas amostras em PWM=255; em 800-900 ms a fração de amostras em 0/255 cresce. Interprete isso como saturação do atuador simulado e não linearidade; não declare estabilidade/instabilidade apenas pela saturação.

Os registros duram aproximadamente 9,4 a 10,0 segundos e os intervalos amostrais observados são 10 ou 11 ms, embora o período nominal seja 10 ms. A última linha da série de 890 ms aparece incompleta no PDF e foi descartada.

## 5. Resultados teóricos da planta RC

Para o modelo nominal `G(s)=1/(0.47s+1)`:

- PI: `C_PI(s)=1.4+1/s`; margem de fase calculada ≈ `115.607°`, frequência de cruzamento ≈ `2.28343 rad/s`, margem de atraso ≈ `883.636 ms`.
- PID filtrado: `C_PID(s)=1.4+1/s+0.08s/(0.05s+1)`; margem de fase ≈ `122.815°`, frequência de cruzamento ≈ `2.22171 rad/s`, margem de atraso ≈ `964.813 ms`.

Esses valores são previsões teóricas lineares e contínuas. Eles não são medições obtidas do osciloscópio virtual e não demonstram que o experimento encontrou o atraso crítico.

## 6. O que não deve ser escrito como fato

- Descrever a aplicação EC exclusivamente como simulação no Proteus, com atraso variável inserido por software.
- Não atribuir os resultados simulados a medições de equipamento real.
- Não dizer que 883,636 ms ou 964,813 ms foram medidos no Proteus.
- Não declarar limite crítico experimental confirmado pelos dez ensaios.
- Não chamar ensaios PI (Kd=0) de PID com derivada ativa.
- Não corrigir/estimar linhas CSV truncadas; mantenha a exclusão explícita.
- Não atribuir o núcleo computacional geral ao firmware Arduino; são módulos independentes.

## 7. Reprodutibilidade

Com Python instalado: `python -m pip install -r requirements.txt`, `PYTHONPATH=src python -m pytest -q` e `PYTHONPATH=src python scripts/gerar_resultados.py`. Isso reconstitui os resultados e gráficos a partir dos modelos e CSVs que já estão no repositório.
