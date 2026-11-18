# Integridade do HEX PID

Arquivo recebido: `PID_Nyquist_Proteus_Arduino_PID.ino.hex`.

- Formato: Intel HEX.
- Registros verificados: 339.
- Registros de dados: 338.
- Registro EOF tipo `01`: 1.
- Checksum: válido em todos os registros (soma dos bytes do registro módulo 256 igual a zero).
- SHA-256: `012e3c69eeb1a7937473d8698a624afba0e849e2b92872e17e9396a65db15ff8`.

Essa validação prova integridade estrutural do arquivo Intel HEX, mas não que ele foi compilado exatamente a partir do `.ino` que está no repositório. O toolchain Arduino/AVR não estava disponível nesta execução para recompilar a fonte e comparar os binários.

O projeto Proteus referencia este HEX pelo caminho relativo `../firmware/PID_Nyquist_Proteus_Arduino_PID.ino.hex`. Caso uma nova compilação seja feita, mantenha a fonte, o HEX e o hash da mesma revisão Git.
