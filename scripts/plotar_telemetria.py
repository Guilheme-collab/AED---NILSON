#!/usr/bin/env python3
"""Compatibilidade: regenera todos os resultados e figuras do projeto."""
from pathlib import Path
import runpy

SCRIPT = Path(__file__).resolve().with_name("gerar_resultados.py")
runpy.run_path(str(SCRIPT), run_name="__main__")
