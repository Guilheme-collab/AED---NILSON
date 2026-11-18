#!/usr/bin/env python3
"""Gera tabelas e figuras reproduziveis a partir dos modelos e CSVs de ensaio."""
from __future__ import annotations
import csv
import json
import math
import statistics
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import linalg, signal
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nyquist_toolkit import (  # noqa: E402
    TransferFunction, benchmark_systems, bode_data, closed_loop_denominator,
    nyquist_analysis, pade_delay, root_locus, routh_table, stability_margins,
    with_pade,
)

CSV_DIR = ROOT / "dados" / "csv"
TABLES = ROOT / "resultados" / "tabelas"
FIGS = ROOT / "resultados" / "figuras"
for directory in (TABLES, FIGS):
    directory.mkdir(parents=True, exist_ok=True)

DELAYS_ORDER = [0, 100, 200, 400, 600, 800, 870, 880, 890, 900]


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_series() -> list[tuple[int, Path, list[dict[str, str]]]]:
    series = []
    for delay in DELAYS_ORDER:
        path = CSV_DIR / f"ensaio_{delay:03d}ms.csv"
        if not path.is_file():
            raise FileNotFoundError(f"CSV de ensaio ausente: {path.relative_to(ROOT)}")
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            raise ValueError(f"CSV vazio: {path.name}")
        series.append((delay, path, rows))
    return series


def generate_experimental_summary(series) -> list[dict]:
    rows_out = []
    for idx, (delay, path, rows) in enumerate(series, start=1):
        t = np.asarray([int(r["tempo_ms"]) for r in rows])
        sp = np.asarray([float(r["setpoint_V"]) for r in rows])
        y = np.asarray([float(r["saida_V"]) for r in rows])
        ydel = np.asarray([float(r["saida_atrasada_V"]) for r in rows])
        pwm = np.asarray([int(r["pwm"]) for r in rows])
        intervals = np.diff(t)
        saturation = int(np.count_nonzero((pwm == 0) | (pwm == 255)))
        rows_out.append({
            "experimento": idx,
            "atraso_ms": delay,
            "arquivo": path.name,
            "amostras_completas": len(rows),
            "inicio_ms": int(t[0]),
            "fim_ms": int(t[-1]),
            "duracao_observada_s": round(float((t[-1] - t[0]) / 1000), 3),
            "setpoint_medio_V": round(float(np.mean(sp)), 3),
            "saida_min_V": round(float(np.min(y)), 3),
            "saida_max_V": round(float(np.max(y)), 3),
            "saida_final_V": round(float(y[-1]), 3),
            "saida_atrasada_final_V": round(float(ydel[-1]), 3),
            "pwm_min": int(np.min(pwm)),
            "pwm_max": int(np.max(pwm)),
            "pwm_zero_amostras": int(np.count_nonzero(pwm == 0)),
            "pwm_255_amostras": int(np.count_nonzero(pwm == 255)),
            "pwm_saturado_pct": round(100.0 * saturation / len(pwm), 2),
            "intervalo_amostragem_min_ms": int(np.min(intervals)) if len(intervals) else 0,
            "intervalo_amostragem_max_ms": int(np.max(intervals)) if len(intervals) else 0,
            "intervalo_amostragem_medio_ms": round(float(np.mean(intervals)), 3) if len(intervals) else 0.0,
        })
    write_csv(ROOT / "dados" / "resumo_ensaios.csv", rows_out)
    return rows_out


def plot_experiment(series) -> None:
    fig, axes = plt.subplots(5, 2, figsize=(15, 17), sharex=False)
    for ax, (delay, _, rows) in zip(axes.flat, series):
        t = np.asarray([int(r["tempo_ms"]) for r in rows]) / 1000.0
        y = np.asarray([float(r["saida_V"]) for r in rows])
        sp = np.asarray([float(r["setpoint_V"]) for r in rows])
        ax.plot(t, y, label="Saida da planta")
        ax.plot(t, sp, linestyle="--", label="Setpoint")
        ax.set_title(f"Atraso configurado/registrado: {delay} ms")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Tensao (V)")
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.1, 5.1)
    axes.flat[0].legend(loc="best")
    fig.suptitle("Telemetria Proteus - resposta da planta RC (dez ensaios)")
    fig.tight_layout()
    fig.savefig(FIGS / "telemetria_resposta_10_ensaios.svg", dpi=120, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(5, 2, figsize=(15, 17), sharex=False)
    for ax, (delay, _, rows) in zip(axes.flat, series):
        t = np.asarray([int(r["tempo_ms"]) for r in rows]) / 1000.0
        pwm = np.asarray([int(r["pwm"]) for r in rows])
        ax.plot(t, pwm, label="PWM")
        ax.axhline(0, linestyle=":")
        ax.axhline(255, linestyle=":")
        ax.set_title(f"Atraso: {delay} ms")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("PWM (0-255)")
        ax.set_ylim(-8, 263)
        ax.grid(True, alpha=0.3)
    fig.suptitle("Telemetria Proteus - comando PWM (dez ensaios)")
    fig.tight_layout()
    fig.savefig(FIGS / "telemetria_pwm_10_ensaios.svg", dpi=120, bbox_inches="tight")
    plt.close(fig)


def companion_roots(coeffs: np.ndarray) -> np.ndarray:
    coeffs = np.asarray(coeffs, dtype=float)
    return linalg.eigvals(linalg.companion(coeffs))


def count_rhp(roots: np.ndarray, tol: float = 1e-7) -> int:
    return int(np.count_nonzero(np.real(roots) > tol))


def validate_against_scipy() -> list[dict]:
    omega = np.geomspace(1e-3, 1e3, 1201)
    rows = []
    for name, item in benchmark_systems().items():
        tf = item["tf"]
        gain = float(item["gain"])
        # A avaliacao propria inclui exp(-tau*s); a referencia SciPy cobre a parte
        # racional e o fator exponencial e conferido independentemente.
        ours = gain * np.polyval(tf.numerator, 1j * omega) / np.polyval(tf.denominator, 1j * omega)
        ref = signal.freqresp((tf.numerator, tf.denominator), w=omega)[1] * gain
        if tf.delay:
            ours = ours * np.exp(-1j * omega * tf.delay)
        max_freq_err = float(np.max(np.abs(ours - ref * np.exp(-1j * omega * tf.delay))))
        if tf.delay == 0:
            den_cl = closed_loop_denominator(tf, gain)
            own_roots = np.roots(den_cl)
            scipy_roots = companion_roots(den_cl)
            routh = routh_table(den_cl)
            pole_err = float(np.max(np.abs(np.sort_complex(own_roots) - np.sort_complex(scipy_roots))))
            own_rhp = int(routh["rhp_pole_count"])
            scipy_rhp = count_rhp(scipy_roots)
            routh_status = "CONCORDA" if own_rhp == scipy_rhp else "DIVERGE"
        else:
            tf_pade = with_pade(tf, 3)
            den_cl = closed_loop_denominator(tf_pade, gain)
            own_roots = np.roots(den_cl)
            scipy_roots = companion_roots(den_cl)
            pole_err = float(np.max(np.abs(np.sort_complex(own_roots) - np.sort_complex(scipy_roots))))
            routh = routh_table(den_cl)
            own_rhp = int(routh["rhp_pole_count"])
            scipy_rhp = count_rhp(scipy_roots)
            routh_status = "CONCORDA_PARA_PADE3" if own_rhp == scipy_rhp else "DIVERGE_PARA_PADE3"
        rows.append({
            "sistema": name,
            "comparacao_resposta_frequencia": "SciPy signal.freqresp + fator exp(-tau*jw) independente",
            "erro_maximo_abs_resposta": f"{max_freq_err:.6e}",
            "comparacao_polos": "scipy.linalg.eigvals(companion)" + ("; aproximacao Pade-3" if tf.delay else ""),
            "erro_maximo_abs_polos": f"{pole_err:.6e}",
            "polos_RHP_Routh": own_rhp,
            "polos_RHP_SciPy": scipy_rhp,
            "validacao_Routh_vs_SciPy": routh_status,
        })
    write_csv(TABLES / "validacao_cruzada_scipy.csv", rows)
    return rows


def generate_benchmark_results() -> tuple[list[dict], list[dict]]:
    summary = []
    margins_rows = []
    omega = np.geomspace(1e-4, 1e4, 2400)
    for name, item in benchmark_systems().items():
        tf = item["tf"]
        gain = float(item["gain"])
        nyq = nyquist_analysis(tf, gain, samples_axis=12001, samples_arc=1201)
        margin = stability_margins(tf, omega)
        if tf.delay == 0:
            den_cl = closed_loop_denominator(tf, gain)
            rt = routh_table(den_cl)
            roots_cl = np.roots(den_cl)
            routh_text = "ESTAVEL" if rt["strictly_stable"] else "INSTAVEL_OU_MARGINAL"
            routh_rhp = int(rt["rhp_pole_count"])
        else:
            pade_tf = with_pade(tf, 3)
            den_cl = closed_loop_denominator(pade_tf, gain)
            rt = routh_table(den_cl)
            roots_cl = np.roots(den_cl)
            routh_text = "Pade-3: " + ("ESTAVEL" if rt["strictly_stable"] else "INSTAVEL_OU_MARGINAL")
            routh_rhp = int(rt["rhp_pole_count"])
        summary.append({
            "sistema": name,
            "descricao": item["description"],
            "numerador_aberto": json.dumps(tf.numerator.tolist()),
            "denominador_aberto": json.dumps(tf.denominator.tolist()),
            "atraso_exato_s": tf.delay,
            "ganho_K": gain,
            "polos_RHP_malha_aberta_P": nyq["open_loop_rhp_poles_P"],
            "winding_anti_horario": nyq["winding_ccw"],
            "envoltorios_horarios_N": nyq["encirclements_clockwise_N"],
            "polos_RHP_malha_fechada_Z_Nyquist": nyq["closed_loop_rhp_poles_Z"],
            "Routh_malha_fechada": routh_text,
            "polos_RHP_Routh_ou_Pade3": routh_rhp,
            "margem_fase_graus": "" if margin["phase_margin_deg"] is None else f"{margin['phase_margin_deg']:.6f}",
            "margem_ganho_dB": "SEM_CRUZAMENTO_FINITO" if margin["gain_margin_db"] is None else f"{margin['gain_margin_db']:.6f}",
            "frequencia_cruzamento_ganho_rad_s": "" if margin["gain_crossover_rad_s"] is None else f"{margin['gain_crossover_rad_s']:.8f}",
            "margem_atraso_estimativa_ms": "" if margin["delay_margin_s"] is None else f"{1000*margin['delay_margin_s']:.6f}",
            "polos_malha_fechada_modelo_Routh_ou_Pade3": json.dumps([[round(float(r.real), 8), round(float(r.imag), 8)] for r in roots_cl]),
        })
        # Bode and Nyquist plots.
        w, mag, phase = bode_data(tf, omega, gain)
        write_csv(TABLES / f"bode_sistema_{name}.csv", [
            {"omega_rad_s": f"{wi:.12g}", "magnitude_dB": f"{mi:.12g}", "phase_deg": f"{pi:.12g}"}
            for wi, mi, pi in zip(w, mag, phase)
        ])
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.semilogx(w, mag, label="Magnitude (dB)")
        ax1.set_xlabel("Frequencia (rad/s)")
        ax1.set_ylabel("Magnitude (dB)")
        ax1.grid(True, which="both", alpha=0.3)
        ax2 = ax1.twinx()
        ax2.semilogx(w, phase, linestyle="--", label="Fase (graus)")
        ax2.set_ylabel("Fase (graus)")
        ax1.set_title(f"Sistema {name} - Diagrama de Bode (atraso exato, quando aplicavel)")
        fig.tight_layout()
        fig.savefig(FIGS / f"bode_sistema_{name}.svg", dpi=120, bbox_inches="tight")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 7))
        curve = nyq["mapped_curve"]
        ax.plot(np.real(curve), np.imag(curve), label="L(jw) no contorno Nyquist")
        ax.plot([-1], [0], marker="x", markersize=10, label="Ponto critico -1+j0")
        ax.axhline(0, linewidth=0.7)
        ax.axvline(0, linewidth=0.7)
        ax.set_xlabel("Parte real")
        ax.set_ylabel("Parte imaginaria")
        ax.set_title(f"Sistema {name} - Mapeamento de Nyquist; P={nyq['open_loop_rhp_poles_P']}, N={nyq['encirclements_clockwise_N']}, Z={nyq['closed_loop_rhp_poles_Z']}")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        ax.set_aspect("equal", adjustable="datalim")
        fig.tight_layout()
        fig.savefig(FIGS / f"nyquist_sistema_{name}.svg", dpi=120, bbox_inches="tight")
        plt.close(fig)

        # Root locus: for D, explicitly label the Padé approximation.
        if tf.delay:
            locus_tf = with_pade(tf, 3)
            locus_label = " (Padé-3; atraso aproximado)"
        else:
            locus_tf = tf
            locus_label = ""
        gains = np.linspace(0, max(8.0, 3.0 * gain), 220)
        kgrid, branches = root_locus(locus_tf.numerator, locus_tf.denominator, gains)
        locus_rows = []
        for ki, branch_roots in zip(kgrid, branches):
            row = {"K": f"{ki:.10g}"}
            for branch, root in enumerate(branch_roots, start=1):
                row[f"ramo_{branch}_real"] = f"{root.real:.12g}"
                row[f"ramo_{branch}_imag"] = f"{root.imag:.12g}"
            locus_rows.append(row)
        write_csv(TABLES / f"root_locus_sistema_{name}.csv", locus_rows)
        fig, ax = plt.subplots(figsize=(8, 6))
        for branch in range(branches.shape[1]):
            ax.plot(np.real(branches[:, branch]), np.imag(branches[:, branch]), linewidth=1.0)
        ax.axvline(0, linestyle="--", linewidth=0.9)
        ax.set_xlabel("Parte real dos polos (1/s)")
        ax.set_ylabel("Parte imaginaria dos polos (1/s)")
        ax.set_title(f"Sistema {name} - Lugar das Raizes{locus_label}")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(FIGS / f"root_locus_sistema_{name}.svg", dpi=120, bbox_inches="tight")
        plt.close(fig)

        routh_rows = []
        for i, row in enumerate(rt["table"]):
            routh_rows.append({"potencia_s": len(rt["table"]) - 1 - i,
                               **{f"coluna_{j+1}": f"{value:.12g}" for j, value in enumerate(row)}})
        write_csv(TABLES / f"routh_sistema_{name}{'_pade3' if tf.delay else ''}.csv", routh_rows)

    write_csv(TABLES / "benchmark_resumo.csv", summary)

    # PI/PID continuous-time models for the nominal RC plant.
    controllers = {
        "PI": TransferFunction([1.4, 1.0], [0.47, 1.0, 0.0], name="L_PI"),
        "PID_filtrado": TransferFunction([0.15, 1.45, 1.0], [0.0235, 0.52, 1.0, 0.0], name="L_PID_filtrado"),
    }
    for name, model in controllers.items():
        m = stability_margins(model, np.geomspace(1e-5, 1e5, 120000))
        margins_rows.append({
            "controlador": name,
            "planta": "G(s)=1/(0.47s+1)",
            "modelo_controlador": "PI: 1.4 + 1/s" if name == "PI" else "PID filtrado: 1.4 + 1/s + 0.08s/(0.05s+1)",
            "Kp": 1.4, "Ki": 1.0, "Kd": 0.0 if name == "PI" else 0.08,
            "frequencia_cruzamento_ganho_rad_s": f"{m['gain_crossover_rad_s']:.9f}" if m["gain_crossover_rad_s"] is not None else "",
            "margem_fase_graus": f"{m['phase_margin_deg']:.9f}" if m["phase_margin_deg"] is not None else "",
            "margem_ganho_dB": "SEM_CRUZAMENTO_DE_FASE_FINITO" if m["gain_margin_db"] is None else f"{m['gain_margin_db']:.9f}",
            "margem_atraso_teorica_ms": f"{1000*m['delay_margin_s']:.6f}" if m["delay_margin_s"] is not None else "",
            "natureza": "Previsao teorica continua; nao e medicao Proteus",
        })
    write_csv(TABLES / "margens_teoricas_PI_PID.csv", margins_rows)

    # Comparison exact delay vs Padé orders 1, 3 and 5 for benchmark D.
    d = benchmark_systems()["D"]["tf"]
    w = np.geomspace(1e-2, 1e2, 800)
    from nyquist_toolkit import frequency_response
    exact = frequency_response(d, w, gain=2.0)
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    axes[0].semilogx(w, 20*np.log10(np.maximum(np.abs(exact), 1e-15)), label="Atraso exato")
    axes[1].semilogx(w, np.unwrap(np.angle(exact))*180/np.pi, label="Atraso exato")
    for order in (1, 3, 5):
        approx_tf = with_pade(d, order)
        approx = frequency_response(approx_tf, w, gain=2.0)
        axes[0].semilogx(w, 20*np.log10(np.maximum(np.abs(approx), 1e-15)), linestyle="--", label=f"Padé-{order}")
        axes[1].semilogx(w, np.unwrap(np.angle(approx))*180/np.pi, linestyle="--", label=f"Padé-{order}")
    axes[0].set_ylabel("Magnitude (dB)")
    axes[1].set_ylabel("Fase (graus)")
    axes[1].set_xlabel("Frequencia (rad/s)")
    axes[0].set_title("Sistema D - atraso puro exato versus aproximacoes de Padé")
    for ax in axes:
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(FIGS / "atraso_exato_vs_pade_sistema_D.svg", dpi=120, bbox_inches="tight")
    plt.close(fig)
    pade_rows = []
    for order in (1, 3, 5):
        approx = frequency_response(with_pade(d, order), w, gain=2.0)
        phase_error_deg = np.angle(approx * np.conjugate(exact), deg=True)
        pade_rows.append({
            "ordem_pade": order,
            "erro_magnitude_max_abs": f"{float(np.max(np.abs(np.abs(approx)-np.abs(exact)))):.8e}",
            "erro_fase_circular_max_abs_graus": f"{float(np.max(np.abs(phase_error_deg))):.8f}",
            "erro_fase_circular_rms_graus": f"{float(np.sqrt(np.mean(phase_error_deg**2))):.8f}",
            "metrica_fase": "abs(angle(H_pade * conj(H_exato))) em graus, intervalo [-180,180]",
            "faixa_omega_rad_s": f"{w[0]:g} a {w[-1]:g}",
        })
    write_csv(TABLES / "erro_atraso_exato_vs_pade.csv", pade_rows)
    return summary, margins_rows


def generate_scalability() -> list[dict]:
    rows = []
    rng = np.random.default_rng(20261118)
    for order in (5, 10, 20):
        true_poles = -np.linspace(0.5, 4.5, order)
        coefficients = np.poly(true_poles)
        # A repeticao estabiliza a mediana e deixa o ambiente explicitamente mensuravel.
        t_routh = []
        t_numpy = []
        t_scipy = []
        last_routh = None
        last_np = None
        last_sp = None
        for _ in range(25):
            start = time.perf_counter_ns(); last_routh = routh_table(coefficients); t_routh.append(time.perf_counter_ns()-start)
            start = time.perf_counter_ns(); last_np = np.roots(coefficients); t_numpy.append(time.perf_counter_ns()-start)
            start = time.perf_counter_ns(); last_sp = companion_roots(coefficients); t_scipy.append(time.perf_counter_ns()-start)
        rows_arr, cols_arr = linear_sum_assignment(np.abs(last_np[:, None]-true_poles[None, :]))
        max_root_error = float(np.max(np.abs(last_np[rows_arr]-true_poles[cols_arr])))
        match_own, match_scipy = linear_sum_assignment(np.abs(last_np[:, None]-last_sp[None, :]))
        max_cross_error = float(np.max(np.abs(last_np[match_own]-last_sp[match_scipy])))
        residual = float(np.max(np.abs(np.polyval(coefficients, last_np)) / np.maximum(1.0, np.polyval(np.abs(coefficients), np.abs(last_np)))))
        rows.append({
            "ordem_polinomio_n": order,
            "poles_known": json.dumps([round(float(x), 6) for x in true_poles.tolist()]),
            "numero_repeticoes": 25,
            "tempo_mediano_routh_us": round(statistics.median(t_routh)/1000, 3),
            "tempo_mediano_np_roots_us": round(statistics.median(t_numpy)/1000, 3),
            "tempo_mediano_scipy_companion_us": round(statistics.median(t_scipy)/1000, 3),
            "polos_RHP_Routh": last_routh["rhp_pole_count"],
            "polos_RHP_referencia": count_rhp(last_sp),
            "erro_max_raizes_vs_polos_geradores": f"{max_root_error:.6e}",
            "erro_max_raizes_numpy_vs_scipy": f"{max_cross_error:.6e}",
            "residuo_polinomial_normalizado_max": f"{residual:.6e}",
        })
    write_csv(TABLES / "escalabilidade_n5_n10_n20.csv", rows)
    fig, ax = plt.subplots(figsize=(9, 5))
    x = [r["ordem_polinomio_n"] for r in rows]
    ax.plot(x, [r["tempo_mediano_routh_us"] for r in rows], marker="o", label="Routh-Hurwitz")
    ax.plot(x, [r["tempo_mediano_np_roots_us"] for r in rows], marker="o", label="Raizes NumPy")
    ax.plot(x, [r["tempo_mediano_scipy_companion_us"] for r in rows], marker="o", label="Polos SciPy companion")
    ax.set_xlabel("Ordem do polinomio (n)")
    ax.set_ylabel("Tempo mediano (microsegundos)")
    ax.set_title("Escalabilidade computacional - mediana de 25 execucoes")
    ax.set_xticks(x)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGS / "escalabilidade_n5_n10_n20.svg", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return rows


def main() -> int:
    series = read_series()
    exp_summary = generate_experimental_summary(series)
    plot_experiment(series)
    cross = validate_against_scipy()
    benchmark, margins = generate_benchmark_results()
    scaling = generate_scalability()
    print(f"Ensaios: {len(exp_summary)} series; amostras completas: {sum(r['amostras_completas'] for r in exp_summary)}")
    print(f"Benchmarks: {len(benchmark)}; validacoes cruzadas: {len(cross)}; modelos de margem: {len(margins)}")
    print("Escalabilidade:")
    for r in scaling:
        print(r)
    print(f"Resultados gerados em {ROOT / 'resultados'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
