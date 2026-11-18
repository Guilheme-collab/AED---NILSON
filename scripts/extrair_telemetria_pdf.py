#!/usr/bin/env python3
"""Extrai somente linhas CSV completas do PDF de evidencias Proteus.

Uso: python scripts/extrair_telemetria_pdf.py /caminho/a/aed.pdf
As linhas incompletas no fim de paginas/series sao descartadas, nunca completadas.
"""
from __future__ import annotations
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RX = re.compile(r"^\s*(\d+),([0-9]+\.[0-9]+),([0-9]+\.[0-9]+),([0-9]+\.[0-9]+),(\d+),(\d+)\s*$")
EXPECTED = [0, 100, 200, 400, 600, 800, 870, 880, 890, 900]
FIELDS = ["tempo_ms", "setpoint_V", "saida_V", "saida_atrasada_V", "pwm", "atraso_ms"]


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python scripts/extrair_telemetria_pdf.py <evidencias.pdf>")
        return 2
    pdf = Path(sys.argv[1])
    if not pdf.is_file():
        print(f"PDF nao encontrado: {pdf}")
        return 2
    reader = PdfReader(str(pdf))
    groups: dict[int, list[dict[str, str]]] = defaultdict(list)
    pages: dict[int, list[int]] = defaultdict(list)
    for page_no, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for line in text.splitlines():
            match = RX.match(line)
            if not match:
                continue
            tempo, sp, y, yd, pwm, delay = match.groups()
            d = int(delay)
            if d not in EXPECTED:
                continue
            groups[d].append({
                "tempo_ms": tempo, "setpoint_V": sp, "saida_V": y,
                "saida_atrasada_V": yd, "pwm": pwm, "atraso_ms": delay,
            })
            if page_no not in pages[d]:
                pages[d].append(page_no)
    missing = sorted(set(EXPECTED) - set(groups))
    if missing:
        raise SystemExit(f"Series esperadas nao encontradas: {missing}")
    out = ROOT / "dados" / "csv"
    out.mkdir(parents=True, exist_ok=True)
    for delay in EXPECTED:
        rows = groups[delay]
        # Verificacao de integridade sem corrigir valores de origem.
        times = [int(r["tempo_ms"]) for r in rows]
        if any(b <= a for a, b in zip(times, times[1:])):
            raise SystemExit(f"Tempo nao crescente na serie {delay} ms")
        if {int(r["atraso_ms"]) for r in rows} != {delay}:
            raise SystemExit(f"Coluna atraso divergente na serie {delay} ms")
        path = out / f"ensaio_{delay:03d}ms.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"{delay:>3} ms: {len(rows):>4} linhas completas; paginas {pages[delay][0]}-{pages[delay][-1]}; salvo em {path.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
