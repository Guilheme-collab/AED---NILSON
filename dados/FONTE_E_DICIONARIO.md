# Fonte e dicionário da telemetria

Os dez CSVs foram extraídos do PDF original de evidências (348 páginas) fornecido pelo usuário. Somente linhas completas com seis campos foram exportadas; linhas parciais no rodapé das páginas foram descartadas. A primeira tabela do PDF lista oito ajustes, mas as séries 870 ms e 890 ms aparecem mais adiante e foram preservadas.

| Campo | Significado | Unidade / domínio |
|---|---|---|
| `tempo_ms` | timestamp acumulado do firmware/simulador | ms |
| `setpoint_V` | referência do controle | V |
| `saida_V` | medição atual da planta RC | V |
| `saida_atrasada_V` | medição usada na realimentação após buffer | V |
| `pwm` | comando PWM do Arduino virtual | inteiro 0-255 |
| `atraso_ms` | atraso efetivamente selecionado no buffer | ms |

O número de amostras válidas e as estatísticas regeneráveis ficam em `resumo_ensaios.csv`. A série de 890 ms apresenta uma última linha truncada no PDF; não foi preenchida por estimativa.
