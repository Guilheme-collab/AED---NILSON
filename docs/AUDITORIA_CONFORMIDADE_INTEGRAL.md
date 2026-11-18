# Auditoria de conformidade com o enunciado — revisão integral do pacote

**Fonte de requisitos:** `docs/Enunciado_Projeto_Pesquisa.pdf`, 3 páginas.  
**Escopo auditado:** pacote EC `Entrega_Tecnica_EC_Nyquist_Reexecutada.zip`, extraído e inspecionado em 18/11/2026.  
**Regra:** simulações numéricas são válidas como simulações, mas nunca são rotuladas como medições físicas.

## 1. Conferência item por item

| Requisito do PDF | Evidência no pacote | Situação |
|---|---|---|
| Ferramenta computacional para sistemas LIT (p.1, §2.1) | `src/nyquist_toolkit/`, README | Implementado para modelos suportados |
| Nyquist pelo Princípio do Argumento (p.1, §2.2; p.2, §3) | `nyquist.py`, `benchmark_resumo.csv` | Implementado; polos no eixo imaginário sem indentação |
| Mapeamento de G(s)H(s) (p.1, §2.2) | `nyquist.py`, figuras A-D | Implementado |
| Margens automáticas de ganho e fase (p.1) | `frequency.py`, CSVs Bode/margens | Implementado; margens inexistentes são reportadas como sem cruzamento finito |
| Routh próprio sem toolbox de controle (p.1) | `routh.py` e testes | Implementado |
| Root Locus próprio sem toolbox de controle (p.1) | `root_locus.py`, CSVs/figuras | Implementado; D usa Padé-3 |
| Comparação com Bode (p.1-2) | `frequency.py`, tabelas e figuras Bode | Implementado |
| Atraso exato versus Padé (p.1-2) | `delay.py`, CSV/figura | Implementado; interpretação de erro de fase precisa de métrica circular complementar |
| Complexidade e erro numérico (p.1, §2.2) | `escalabilidade_n5_n10_n20.csv` | Implementado, 25 repetições por ordem |
| Quatro benchmarks A-D (p.2, §5) | `benchmarks.py`, tabelas/figuras | Implementado |
| Contagem P, N e Z (p.2, §3) | `benchmark_resumo.csv` | Implementado nos quatro casos sem polos na fronteira |
| Routh com primeira coluna nula e linha nula (p.3, §5 Fase 2) | `routh.py`, testes | Implementado |
| Validação cruzada com SciPy (p.3, §5 Fase 3) | `validacao_cruzada_scipy.csv` | Implementado; D comparado na aproximação Padé-3 para polos |
| Escalabilidade n=5,10,20 (p.3) | `escalabilidade_n5_n10_n20.csv` | Implementado |
| Trilha EC: controlador PID em ambiente simulado com atraso variável (p.3, §5 Fase 4) | fontes PI/PID, HEX, projeto Proteus, dados e capturas já fornecidos | Atendido no escopo EC simulado informado pelo usuário; a auditoria atual valida os artefatos computacionais e não reexecuta o Proteus |
| Usar Nyquist para prever atraso crítico (p.3) | `margens_teoricas_PI_PID.csv` | Previsão teórica calculada; não validada experimentalmente |
| Trilha CC: aplicação visual interativa (p.3) | Não incluída no pacote EC | Não aplicável se a equipe escolheu EC; pendente se o grupo precisa entregar CC também |
| Artigo SBC ou IEEE (p.3, §6) | `ARTIGO_CIENTIFICO_RASCUNHO_SBC_IEEE.md` | Rascunho técnico fornecido; não é artigo final formatado/submetível |
| Repositório aberto, documentado, testes e reprodutibilidade (p.3) | código, README, requirements, workflow, testes | Conteúdo presente; publicação no GitHub só conta após push confirmado |
| Seminário e demonstração (p.3) | `ROTEIRO_SEMINARIO_E_DEMO.md` | Roteiro fornecido; apresentação oral ainda depende do grupo |

## 2. Execuções repetidas nesta auditoria

- `PYTHONPATH=src python -m pytest -q`: 55 testes aprovados.
- `python scripts/gerar_resultados.py`: código de saída 0; 10 séries / 9.534 amostras, quatro benchmarks, quatro validações cruzadas e dois modelos de margens; escalabilidade regenerada.
- `python scripts/plotar_telemetria.py`: código de saída 0; figuras de resposta e PWM regeneradas.
- `python scripts/validar_entrega.py`: código de saída 0; 55 testes, Intel HEX estruturalmente válido, dez CSVs e estrutura do projeto Proteus verificados.
- O aviso `Spreadsheet runtime warmup failed` é emitido por um pacote auxiliar do ambiente Python no início do processo; os comandos acima retornaram código 0 e as verificações do projeto concluíram. Não é erro originado no código do projeto.

## 3. Resultados importantes a preservar no relatório

- Validação de frequência: erro máximo registrado 7,47e-17 (A), 5,55e-17 (B), zero na precisão impressa (C e D).
- Escalabilidade: erro de recuperação de raízes 4,17e-14 (n=5), 7,77e-10 (n=10), 1,228e-1 (n=20). Resíduo normalizado n=20: 2,13e-16.
- Margem de atraso teórica PI: 883,636 ms; PID filtrado: 964,813 ms. Não são medições.
- Telemetria: dez atrasos; 9.534 amostras completas; linha final incompleta de 890 ms descartada; saturação PWM nos atrasos elevados.
- HEX: 339 registros (338 de dados e EOF), checksums válidos; isso não prova compilação do `.ino` que acompanha o ZIP.
- Projeto Proteus: estrutura interna e referência relativa do HEX verificadas; simulador não executado.

## 4. Pendências técnicas/entregáveis

1. Implementar e validar matematicamente a indentação de Nyquist para polos no eixo imaginário.
2. Recompilar os fontes Arduino com toolchain identificado e registrar o vínculo fonte/HEX.
3. Abrir e executar o projeto Proteus, gravando vídeo/log/capturas da sessão.
4. Registrar no relatório que a aplicação EC foi realizada integralmente por simulação no Proteus, conforme escopo informado pelo aluno.
5. Revisar a métrica de fase na comparação Padé, acrescentando erro circular.
6. Converter o rascunho do artigo para o template oficial SBC/IEEE, completar autoria e referências, revisão humana e resultados finais.
7. Realizar seminário e demonstração.
8. Se a equipe assumiu também a trilha CC, desenvolver e entregar a aplicação visual interativa.

## 5. Conclusão da auditoria
O pacote EC contém o núcleo computacional, os quatro benchmarks, os resultados quantitativos, as figuras, a telemetria disponível, firmware e documentação de apoio. Os testes e scripts disponíveis foram reexecutados com sucesso. **Escopo desta entrega:** Engenharia da Computação. A trilha CC não se aplica. A simulação Proteus já fornecida pelo aluno é considerada parte do material de projeto; esta auditoria concentra-se no núcleo computacional, nos dados reproduzíveis e na documentação. Permanecem explicitadas as limitações técnicas do algoritmo Nyquist para polos no eixo imaginário, a rastreabilidade fonte-HEX, o caráter de rascunho do artigo e a necessidade de o grupo realizar a apresentação oral.
