# Lista de arquivos para entregar ao responsavel pelo artigo/relatorio

## Enviar obrigatoriamente

1. **`Repasse_Tecnico_Para_Artigo.pdf` ou `.docx`** - resumo tecnico da contribuicao da Engenharia da Computacao: arquitetura, pinos, parametros, ensaios, limites e ressalvas.
2. **`evidencias/Evidencias_Proteus_10_ensaios.pdf`** - documento original de 348 paginas, com esquema, capturas do osciloscopio/Virtual Terminal e telemetria.
3. **`evidencias/capturas/`** - imagens PNG individuais extraidas das capturas do PDF para facilitar a insercao no artigo. `LEIA-ME_Capturas.md` informa a pagina original e o conteudo de cada imagem.
4. **`../proteus/AED.pdsprj`** - projeto editavel do Proteus.
5. **`../firmware/PID_Nyquist_Proteus_Arduino.ino`** - codigo-fonte do microcontrolador.
6. **`../dados/csv/`** - dez arquivos CSV, um por atraso.
7. **`../dados/resumo_ensaios.csv`** - resumo quantitativo derivado dos CSVs.
8. **`../figuras/`** - graficos de saida da planta e PWM gerados a partir das dez series.
9. **`../README.md`** - instrucoes de reproducao da simulacao e descricao dos arquivos.

## Enviar depois de gerar localmente

10. **Arquivo HEX** compilado no Arduino IDE a partir do mesmo INO que foi carregado no Proteus. Ele nao foi incluido porque precisa ser gerado no ambiente local e conferido pelo usuario.

## Mensagem que deve acompanhar os arquivos

Explique que esta e a contribuicao pratica da trilha de Engenharia da Computacao. Os ensaios atuais sao co-simulacao de firmware Arduino e planta RC no Proteus; o atraso de realimentacao e implementado em software por buffer circular; Kd=0, portanto os ensaios documentados correspondem a PI; e os registros cobrem aproximadamente 9,4 a 10,0 segundos por ensaio, com saturacao de PWM nos atrasos elevados. Nao apresentar isso como HIL fisico nem afirmar que o limite critico foi experimentalmente comprovado.

## Como selecionar as figuras para o artigo

Use a imagem do circuito (`00_circuito_completo_e_tabela.png`) e escolha capturas representativas, por exemplo: 0, 400, 600, 800, 870, 880, 890 e 900 ms. O PDF completo deve ser mantido como evidencia suplementar. A pagina 1 do PDF lista os oito atrasos originais; os ensaios de 870 e 890 ms foram adicionados em uma tabela complementar perto da pagina 278 e aparecem como ensaios 9 e 10 no documento de repasse.

## Observacao sobre a ultima linha

A ultima linha de telemetria na pagina 348 do PDF aparece incompleta. Os CSVs exportados incluem somente linhas completas; nao foram inventados valores para completar o registro truncado. Se existir um log serial original completo, ele pode ser usado para substituir essa linha com evidencia.