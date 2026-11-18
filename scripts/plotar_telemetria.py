#!/usr/bin/env python3
"""Resume e plota as dez series de telemetria extraidas dos ensaios Proteus.

Este script nao implementa Nyquist, Routh-Hurwitz, Lugar das Raizes ou Bode.
Ele apenas calcula estatisticas descritivas dos CSVs e produz figuras.
"""
from pathlib import Path
import csv
import statistics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "csv"
OUT = ROOT / "figuras"
SUMMARY = ROOT / "dados" / "resumo_ensaios.csv"
OUT.mkdir(parents=True, exist_ok=True)


def read_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


ordem_experimentos = [0, 100, 200, 400, 600, 800, 880, 900, 870, 890]
arquivos_por_atraso = {
    int(p.stem.split("_")[1].replace("ms", "")): p
    for p in DATA.glob("ensaio_*ms.csv")
}
files = [arquivos_por_atraso[d] for d in ordem_experimentos if d in arquivos_por_atraso]
if not files:
    raise SystemExit(f"Nenhum CSV encontrado em {DATA}")

summary = []
all_rows = {}
for idx, path in enumerate(files, start=1):
    rows = read_rows(path)
    if not rows:
        print(f"AVISO: arquivo vazio: {path.name}")
        continue
    all_rows[path] = rows
    t = [int(r["tempo_ms"]) for r in rows]
    sp = [float(r["setpoint_V"]) for r in rows]
    y = [float(r["saida_V"]) for r in rows]
    pwm = [int(r["pwm"]) for r in rows]
    delay_values = {int(r["atraso_ms"]) for r in rows}
    if len(delay_values) != 1:
        raise SystemExit(f"Atraso varia dentro de {path.name}: {sorted(delay_values)}")
    delay = delay_values.pop()
    zero_count = sum(v == 0 for v in pwm)
    full_count = sum(v == 255 for v in pwm)
    sat_count = zero_count + full_count
    summary.append({
        "experimento": idx,
        "atraso_ms": delay,
        "arquivo": path.name,
        "amostras": len(rows),
        "inicio_ms": min(t),
        "fim_ms": max(t),
        "duracao_s": round((max(t) - min(t)) / 1000.0, 3),
        "setpoint_medio_V": round(statistics.mean(sp), 3),
        "saida_min_V": round(min(y), 3),
        "saida_max_V": round(max(y), 3),
        "saida_final_V": round(y[-1], 3),
        "pwm_min": min(pwm),
        "pwm_max": max(pwm),
        "pwm_0_amostras": zero_count,
        "pwm_255_amostras": full_count,
        "pwm_saturado_pct": round(100.0 * sat_count / len(pwm), 2),
    })

fields = [
    "experimento", "atraso_ms", "arquivo", "amostras", "inicio_ms", "fim_ms",
    "duracao_s", "setpoint_medio_V", "saida_min_V", "saida_max_V",
    "saida_final_V", "pwm_min", "pwm_max", "pwm_0_amostras",
    "pwm_255_amostras", "pwm_saturado_pct",
]
with SUMMARY.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(summary)

try:
    import matplotlib.pyplot as plt
except ImportError:
    print(f"Resumo gerado em {SUMMARY}. Para graficos: python -m pip install matplotlib")
    raise SystemExit(0)

for metric, ylabel, outname in [
    ("saida_V", "Tensao (V)", "respostas_temporais_10_ensaios.png"),
    ("pwm", "PWM (0-255)", "pwm_10_ensaios.png"),
]:
    fig, axes = plt.subplots(5, 2, figsize=(14, 10), sharex=False)
    for ax, path in zip(axes.flat, files):
        rows = all_rows[path]
        x = [int(r["tempo_ms"]) / 1000.0 for r in rows]
        values = [float(r[metric]) for r in rows]
        delay = int(rows[0]["atraso_ms"])
        ax.plot(x, values, label=ylabel)
        if metric == "saida_V":
            ax.plot(x, [float(r["setpoint_V"]) for r in rows], linestyle="--", label="Setpoint")
        ax.set_title(f"Atraso: {delay} ms")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
        if metric == "saida_V":
            ax.set_ylim(-0.1, 5.1)
        else:
            ax.set_ylim(-5, 260)
    fig.tight_layout()
    fig.savefig(OUT / outname, dpi=180, bbox_inches="tight")
    plt.close(fig)

print(f"Resumo e figuras atualizados em {ROOT}")
