#!/usr/bin/env python3
"""Valida a estrutura basica da entrega EC Nyquist (CSV, HEX e projeto Proteus)."""
from __future__ import annotations

import csv
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [0, 100, 200, 400, 600, 800, 870, 880, 890, 900]
FIELDS = ["tempo_ms", "setpoint_V", "saida_V", "saida_atrasada_V", "pwm", "atraso_ms"]
REQUIRED = [
    ROOT / "README.md",
    ROOT / "firmware" / "PID_Nyquist_Proteus_Arduino.ino",
    ROOT / "firmware" / "PID_Nyquist_Proteus_Arduino.hex",
    ROOT / "proteus" / "AED.pdsprj",
    ROOT / "docs" / "evidencias" / "Evidencias_Proteus_10_ensaios.pdf",
]


def validate_hex(path: Path) -> tuple[int, bool]:
    records = 0
    eof = False
    for line_no, raw in enumerate(path.read_text(encoding="ascii").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if not line.startswith(":"):
            raise ValueError(f"HEX linha {line_no}: registro sem ':'")
        try:
            data = bytes.fromhex(line[1:])
        except ValueError as exc:
            raise ValueError(f"HEX linha {line_no}: hexadecimal invalido") from exc
        if len(data) < 5 or data[0] != len(data) - 5:
            raise ValueError(f"HEX linha {line_no}: comprimento inconsistente")
        if sum(data) % 256 != 0:
            raise ValueError(f"HEX linha {line_no}: checksum incorreto")
        record_type = data[3]
        if record_type == 1:
            eof = True
        records += 1
    if not eof:
        raise ValueError("HEX sem registro EOF (tipo 01)")
    return records, eof


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"Arquivo obrigatorio ausente: {path.relative_to(ROOT)}")

    csv_dir = ROOT / "dados" / "csv"
    delays_seen: list[int] = []
    for delay in EXPECTED:
        path = csv_dir / f"ensaio_{delay:03d}ms.csv"
        if not path.is_file():
            errors.append(f"CSV ausente: {path.relative_to(ROOT)}")
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != FIELDS:
                errors.append(f"Cabecalho inesperado em {path.name}: {reader.fieldnames}")
                continue
            rows = list(reader)
        if not rows:
            errors.append(f"CSV vazio: {path.name}")
            continue
        try:
            times = [int(row["tempo_ms"]) for row in rows]
            logged_delays = {int(row["atraso_ms"]) for row in rows}
            pwm = [int(row["pwm"]) for row in rows]
            for row in rows:
                for field in ("setpoint_V", "saida_V", "saida_atrasada_V"):
                    float(row[field])
            if len(logged_delays) != 1 or logged_delays.pop() != delay:
                errors.append(f"Atraso registrado nao corresponde ao nome do arquivo: {path.name}")
            if any(b <= a for a, b in zip(times, times[1:])):
                errors.append(f"Tempo nao crescente em {path.name}")
            if any(value < 0 or value > 255 for value in pwm):
                errors.append(f"PWM fora de 0..255 em {path.name}")
            delays_seen.append(delay)
        except (TypeError, ValueError, KeyError) as exc:
            errors.append(f"Dados invalidos em {path.name}: {exc}")

    hex_path = ROOT / "firmware" / "PID_Nyquist_Proteus_Arduino.hex"
    if hex_path.is_file():
        try:
            records, _ = validate_hex(hex_path)
            print(f"HEX: {records} registros com checksum valido e EOF presente.")
        except ValueError as exc:
            errors.append(str(exc))

    proteus_path = ROOT / "proteus" / "AED.pdsprj"
    if proteus_path.is_file():
        try:
            with zipfile.ZipFile(proteus_path) as archive:
                names = set(archive.namelist())
            for member in ("ROOT.DSN", "ROOT.CDB", "PROJECT.XML", "SCRIPTS/PWRRAILS.DAT"):
                if member not in names:
                    errors.append(f"Projeto Proteus sem {member}")
            print("Proteus: contenedor do projeto e arquivos internos verificados.")
        except zipfile.BadZipFile:
            errors.append("AED.pdsprj nao e um pacote ZIP valido.")

    if errors:
        print("FALHA NA VALIDACAO:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"CSV: {len(delays_seen)} ensaios validados ({', '.join(map(str, delays_seen))} ms).")
    print("Arquivos obrigatorios encontrados.")
    print("Validacao estrutural concluida. Isso nao substitui compilar o INO no Arduino IDE nem executar o circuito no Proteus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
