# Registro da auditoria técnica — 18/11/2026

## O que foi verificado

- 55 testes automatizados aprovados na última execução.
- Quatro benchmarks A–D, com gráficos, tabelas e modelos documentados.
- Validação cruzada da resposta em frequência e contagem de polos com SciPy.
- Escalabilidade para ordens 5, 10 e 20, com 25 repetições por ordem.
- Dez arquivos CSV de telemetria, totalizando 9.534 linhas completas.
- PDF original integral de evidências (348 páginas) preservado junto às capturas WebP selecionadas.
- Firmware PI histórico separado do firmware PID posterior.
- Arquivo HEX PID: 339 registros (338 de dados e um EOF), checksums válidos; SHA-256 `012e3c69eeb1a7937473d8698a624afba0e849e2b92872e17e9396a65db15ff8`.
- Projeto Proteus: contêiner ZIP e membros internos esperados verificados; caminho relativo do HEX configurado.
- Links locais de Markdown verificados sem destinos quebrados; pacote de distribuição com CRC íntegro.

## Limites que precisam continuar explícitos

- O firmware não foi compilado neste ambiente por ausência do toolchain Arduino/AVR. A relação binária entre o HEX recebido e o `.ino` não está comprovada.
- O projeto foi inspecionado estruturalmente; o simulador Proteus não foi executado nesta auditoria.
- A aplicação da trilha EC é inteiramente simulada no Proteus, com atraso da medição introduzido por software. Os resultados devem ser identificados como simulação.
- As margens PI/PID são resultados teóricos do modelo contínuo RC nominal; não são medições do Proteus.
- Os dez registros observados não demonstram, isoladamente, o atraso crítico experimental. Há saturação PWM nos atrasos elevados.
- A linha final truncada no registro de 890 ms foi omitida, sem preenchimento estimado.
- O contorno agora implementa indentação semicircular numérica no semiplano direito para polos no eixo imaginário; a quantidade de polos na fronteira é reportada separadamente. Para casos críticos, avaliar convergência com diferentes raios e discretizações.
- O aplicativo visual interativo está na trilha CC e não integra esta entrega individual EC. A redação do artigo e o seminário ficam com o integrante/grupo responsável.

## Onde começar

1. `README.md` — visão geral e reprodução.
2. `docs/GUIA_PARA_AUTOR_RELATORIO.md` — roteiro para o redator.
3. `docs/MATRIZ_ATENDIMENTO_ENUNCIADO.md` — rastreabilidade de 45 verificações.
4. `docs/RELATORIO_TECNICO_REPASSE.md` — parâmetros, dados, interpretação e ressalvas.
5. `dados/csv/` e `resultados/tabelas/` — dados quantitativos de origem e resultados calculados.
6. `docs/evidencias/` — imagens da simulação e mapa de origem.
