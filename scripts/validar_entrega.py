#!/usr/bin/env python3
"""Auditoria estrutural da entrega; nao executa o aplicativo Proteus."""
from __future__ import annotations
import csv
import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DELAYS = [0, 100, 200, 400, 600, 800, 870, 880, 890, 900]
FIELDS = ["tempo_ms", "setpoint_V", "saida_V", "saida_atrasada_V", "pwm", "atraso_ms"]
REQUIRED = [
    ROOT / "README.md",
    ROOT / "requirements.txt",
    ROOT / "src" / "nyquist_toolkit" / "models.py",
    ROOT / "src" / "nyquist_toolkit" / "frequency.py",
    ROOT / "src" / "nyquist_toolkit" / "nyquist.py",
    ROOT / "src" / "nyquist_toolkit" / "routh.py",
    ROOT / "src" / "nyquist_toolkit" / "root_locus.py",
    ROOT / "src" / "nyquist_toolkit" / "delay.py",
    ROOT / "src" / "nyquist_toolkit" / "benchmarks.py",
    ROOT / "tests" / "test_core.py",
    ROOT / "firmware" / "PI_Nyquist_Proteus_Arduino.ino",
    ROOT / "firmware" / "PID_Nyquist_Proteus_Arduino_PID.ino",
    ROOT / "firmware" / "PID_Nyquist_Proteus_Arduino_PID.ino.hex",
    ROOT / "firmware" / "LEIA-ME_HEX.md",
    ROOT / "proteus" / "AED.pdsprj",
    ROOT / "dados" / "resumo_ensaios.csv",
    ROOT / "docs" / "Enunciado_Projeto_Pesquisa.pdf",
    ROOT / "docs" / "MATRIZ_ATENDIMENTO_ENUNCIADO.md",
    ROOT / "docs" / "RELATORIO_TECNICO_REPASSE.md",
    ROOT / "docs" / "GUIA_PARA_AUTOR_RELATORIO.md",
    ROOT / "docs" / "evidencias" / "LEIA-ME.md",
    ROOT / "docs" / "evidencias" / "capturas" / "circuito_e_tabela_inicial.webp",
    ROOT / "resultados" / "tabelas" / "benchmark_resumo.csv",
    ROOT / "resultados" / "tabelas" / "validacao_cruzada_scipy.csv",
    ROOT / "resultados" / "tabelas" / "escalabilidade_n5_n10_n20.csv",
]


def validate_hex(path: Path) -> tuple[int, int, str]:
    records = 0
    eof_records = 0
    data_records = 0
    for line_no, raw in enumerate(path.read_text(encoding="ascii").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if not line.startswith(":"):
            raise ValueError(f"HEX linha {line_no}: registro sem ':'")
        try:
            record = bytes.fromhex(line[1:])
        except ValueError as exc:
            raise ValueError(f"HEX linha {line_no}: hexadecimal invalido") from exc
        if len(record) < 5 or record[0] != len(record) - 5:
            raise ValueError(f"HEX linha {line_no}: comprimento inconsistente")
        if sum(record) % 256 != 0:
            raise ValueError(f"HEX linha {line_no}: checksum incorreto")
        record_type = record[3]
        if record_type == 1:
            eof_records += 1
        elif record_type == 0:
            data_records += 1
        records += 1
    if eof_records != 1:
        raise ValueError(f"HEX deve conter exatamente um EOF, encontrado: {eof_records}")
    return records, data_records, hashlib.sha256(path.read_bytes()).hexdigest()


def validate_csvs(errors: list[str]) -> tuple[int, int]:
    count = 0
    sample_total = 0
    for delay in EXPECTED_DELAYS:
        path = ROOT / "dados" / "csv" / f"ensaio_{delay:03d}ms.csv"
        if not path.is_file():
            errors.append(f"CSV ausente: {path.relative_to(ROOT)}")
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != FIELDS:
                errors.append(f"Cabecalho inesperado: {path.name}")
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
                    value = float(row[field])
                    if not (value == value and abs(value) != float("inf")):
                        raise ValueError(f"valor nao finito em {field}")
            if logged_delays != {delay}:
                errors.append(f"Atraso interno nao corresponde ao nome do arquivo: {path.name}")
            if any(b <= a for a, b in zip(times, times[1:])):
                errors.append(f"Tempo nao crescente: {path.name}")
            if any(v < 0 or v > 255 for v in pwm):
                errors.append(f"PWM fora de 0..255: {path.name}")
        except (KeyError, ValueError, TypeError) as exc:
            errors.append(f"Dados invalidos em {path.name}: {exc}")
            continue
        count += 1
        sample_total += len(rows)
    return count, sample_total


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"Arquivo obrigatorio ausente: {path.relative_to(ROOT)}")
    for path in (ROOT / "resultados" / "figuras").glob("*.webp"):
        if path.stat().st_size < 1024:
            errors.append(f"Figura suspeita/vazia: {path.relative_to(ROOT)}")
    csv_count, sample_count = validate_csvs(errors)

    hex_path = ROOT / "firmware" / "PID_Nyquist_Proteus_Arduino_PID.ino.hex"
    if hex_path.is_file():
        try:
            records, data, digest = validate_hex(hex_path)
            print(f"HEX: {records} registros ({data} dados), EOF unico, checksums validos; SHA256={digest}")
        except ValueError as exc:
            errors.append(str(exc))

    proteus_path = ROOT / "proteus" / "AED.pdsprj"
    if proteus_path.is_file():
        try:
            with zipfile.ZipFile(proteus_path) as archive:
                if archive.testzip() is not None:
                    errors.append("Projeto Proteus contem membro ZIP corrompido")
                names = set(archive.namelist())
                for member in ("ROOT.DSN", "ROOT.CDB", "PROJECT.XML", "SCRIPTS/PWRRAILS.DAT"):
                    if member not in names:
                        errors.append(f"Projeto Proteus sem {member}")
                dsn = archive.read("ROOT.DSN").decode("latin1", errors="replace")
                expected_ref = r"..\firmware\PID_Nyquist_Proteus_Arduino_PID.ino.hex"
                if expected_ref not in dsn:
                    errors.append("Caminho relativo do HEX PID nao encontrado em ROOT.DSN")
            print("Proteus: container ZIP, membros e referencia relativa do HEX conferidos; sem execucao do simulador.")
        except (zipfile.BadZipFile, KeyError) as exc:
            errors.append(f"Projeto Proteus invalido: {exc}")

    summary_path = ROOT / "dados" / "resumo_ensaios.csv"
    if summary_path.is_file():
        with summary_path.open(encoding="utf-8", newline="") as f:
            summary = list(csv.DictReader(f))
        summary_delays = [int(row["atraso_ms"]) for row in summary]
        if summary_delays != EXPECTED_DELAYS:
            errors.append("Resumo dos ensaios nao contem a ordem esperada de dez atrasos")

    if errors:
        print("FALHA NA AUDITORIA:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"CSV: {csv_count} ensaios e {sample_count} amostras completas validadas.")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    test = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, env=env, text=True)
    if test.returncode != 0:
        print("FALHA na suíte automatizada.")
        return test.returncode
    print("Auditoria estrutural e suíte de testes concluídas. Esta validação não compila Arduino nem executa Proteus.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
