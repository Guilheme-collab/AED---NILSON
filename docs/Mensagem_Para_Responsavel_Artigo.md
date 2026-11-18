# Mensagem para encaminhar ao responsavel pelo artigo/relatorio

Estou encaminhando a parte pratica da trilha de Engenharia da Computacao: firmware do Arduino, projeto do Proteus, evidencias dos ensaios e telemetria organizada em CSV.

O PDF de evidencias contem a montagem e dez ensaios com atrasos de 0, 100, 200, 400, 600, 800, 880, 900, 870 e 890 ms. A versao atual corrigiu o ensaio de 100 ms e acrescentou 870 e 890 ms. Os dados foram separados em arquivos CSV individuais para facilitar a geracao de graficos.

Parametros principais dos ensaios: Arduino Uno/ATmega328P, clock de 16 MHz, RC nominal de 4,7 kOhm e 100 uF (tau nominal de 0,47 s), Kp=1,40, Ki=1,00 e Kd=0,00, amostragem nominal de 10 ms e setpoint registrado de aproximadamente 2,502 V.

Observacoes que precisam ser mantidas no texto: os ensaios registrados duram cerca de 9,4 a 10,0 s; a partir de 800 ms ha saturacao do PWM em parte das amostras; o atraso foi aplicado por software ao historico de A0; a montagem atual e co-simulacao no Proteus e nao comprova HIL fisico nem atraso de rede fisica; como Kd=0, os ensaios sao de PI, nao de PID com derivada ativa.

O documento de repasse tecnico explica o que esta implementado e o que permanece como responsabilidade da analise computacional geral do grupo (Nyquist, winding number, Routh-Hurwitz, Lugar das Raizes, Bode, quatro benchmarks e benchmarking n=5,10,20). Essa parte geral nao deve ser atribuida automaticamente a esta entrega pratica.

Anexos incluidos: documento de repasse, PDF completo das evidencias, projeto Proteus, INO, dez CSVs, resumo e graficos. O arquivo HEX precisa ser gerado localmente no Arduino IDE para garantir que corresponda ao INO final.