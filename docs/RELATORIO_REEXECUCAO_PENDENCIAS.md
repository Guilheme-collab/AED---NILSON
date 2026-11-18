# Relatório de reexecução e correções — 18/11/2026

## Escopo
Entrega exclusiva da trilha Engenharia da Computação. A aplicação prática é inteiramente simulada no Proteus, com atraso de medição inserido por software. Não há alegação de montagem, medição ou ensaio físico.

## Correções realizadas nesta revisão
1. `nyquist_contour()` passou a construir semiarcos de indentação no semiplano direito para polos no eixo imaginário, removendo o ponto singular do caminho.
2. `nyquist_analysis()` passou a informar `open_loop_imaginary_axis_poles` e a documentar que polos na fronteira não são contabilizados em P.
3. A comparação exato versus Padé passou a usar erro de fase circular `angle(H_pade * conj(H_exato))`, em graus, no intervalo [-180°, 180°].
4. Foram adicionados testes para polo integrador e par de polos imaginários; a suíte total passou a 55 testes.
5. Tabelas, figuras e documentação foram regeneradas/atualizadas.

## Verificações reproduzidas
- `PYTHONPATH=src python -m pytest -q`: 55 testes aprovados.
- `python scripts/gerar_resultados.py`: código de saída 0; quatro benchmarks, quatro validações cruzadas, dois modelos de margem, dez séries de telemetria e escalabilidade n=5, 10 e 20.
- `python scripts/plotar_telemetria.py`: código de saída 0.
- `python scripts/validar_entrega.py`: código de saída 0; 10 CSVs/9.534 amostras completas e HEX estruturalmente íntegro.

## Limitações remanescentes que devem constar no relatório
- A indentação é numérica e depende do raio de desvio/discretização; resultados perto de polos ou zeros de malha fechada na fronteira exigem análise específica de convergência e não devem ser interpretados como estabilidade estrita automaticamente.
- O HEX foi verificado estruturalmente, mas não recompilado nesta auditoria a partir do `.ino`.
- O projeto Proteus e suas evidências são fornecidos pelo grupo; esta execução não abriu nem executou o simulador.
- O artigo está em rascunho Markdown e precisa ser adaptado ao template SBC/IEEE, com autoria e revisão final.
- O roteiro do seminário está pronto; a apresentação oral cabe ao grupo.
- Tempos de escalabilidade são específicos do ambiente. O erro de recuperação das raízes em n=20 (aprox. 0,1228) deve ser discutido, não ocultado.

## Conclusão
O núcleo computacional e os geradores foram reexecutados com sucesso, e os dois pontos técnicos corrigíveis identificados anteriormente foram implementados e testados. Esta auditoria não afirma execução do Proteus, recompilação do firmware ou conclusão das atividades acadêmicas que dependem dos autores.
