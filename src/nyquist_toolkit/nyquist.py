"""Contorno de Nyquist, numero de enrolamento e relacao do Principio do Argumento."""
from __future__ import annotations
import numpy as np
from .models import TransferFunction
from .frequency import evaluate_s


def nyquist_contour(tf: TransferFunction, samples_axis: int = 6001, samples_arc: int = 801,
                    radius: float | None = None, indentation_radius: float | None = None) -> np.ndarray:
    """Contorno horario do semiplano direito com indentacoes para polos no eixo jω.

    O eixo imaginario e percorrido de -jR a +jR. Cada polo sobre o eixo e
    contornado por um pequeno semiarco no semiplano direito, excluindo-o do
    dominio delimitado. O arco externo fecha o contorno de +jR a -jR.
    Polos na fronteira sao reportados separadamente pela analise; nao entram em P.
    """
    poles = tf.poles
    if samples_axis < 101 or samples_arc < 21:
        raise ValueError("Resolucao do contorno insuficiente")
    if radius is None:
        radius = max(1e3, 100.0 * float(np.max(np.abs(poles))), 100.0 * float(np.max(np.abs(tf.zeros))) if tf.zeros.size else 0.0)
    if radius <= 0 or not np.isfinite(radius):
        raise ValueError("Raio do contorno invalido")

    boundary_poles = poles[(np.abs(np.real(poles)) < 1e-9) & (np.abs(np.imag(poles)) < radius)]
    pole_frequencies = sorted(float(np.imag(p)) for p in boundary_poles)
    scale = max(1.0, float(radius))
    eps = float(indentation_radius) if indentation_radius is not None else max(1e-6, min(1e-3, scale * 1e-7))
    if eps <= 0 or not np.isfinite(eps):
        raise ValueError("Raio de indentacao invalido")
    if len(pole_frequencies) > 1 and np.min(np.diff(pole_frequencies)) <= 2.1 * eps:
        raise ValueError("Polos no eixo imaginario muito proximos para a indentacao escolhida")

    wmax = float(radius)
    wmin = max(1e-7, wmax * 1e-8)
    positive = np.geomspace(wmin, wmax, (samples_axis - 1) // 2)
    omega = np.concatenate((-positive[::-1], np.array([0.0]), positive))
    if not pole_frequencies:
        axis_s = 1j * omega
    else:
        pieces: list[np.ndarray] = []
        cursor = -np.inf
        for wp in pole_frequencies:
            below = omega[(omega > cursor) & (omega < wp - eps)]
            if below.size:
                pieces.append(1j * below)
            theta_indent = np.linspace(-np.pi / 2.0, np.pi / 2.0,
                                       max(41, samples_arc // max(1, len(pole_frequencies))))
            pieces.append(1j * wp + eps * np.exp(1j * theta_indent))
            cursor = wp + eps
        above = omega[omega > cursor]
        if above.size:
            pieces.append(1j * above)
        axis_s = np.concatenate(pieces) if pieces else 1j * omega
    theta = np.linspace(np.pi / 2.0, -np.pi / 2.0, samples_arc)
    arc_s = radius * np.exp(1j * theta)
    return np.concatenate((axis_s, arc_s[1:-1]))


def winding_number(curve: np.ndarray, point: complex = -1.0 + 0j, tolerance: float = 1e-8) -> int:
    """Numero inteiro de voltas anti-horarias da curva em torno de `point`."""
    z = np.asarray(curve, dtype=complex).reshape(-1) - point
    if z.size < 4:
        raise ValueError("Curva insuficiente para contar envoltorios")
    if np.min(np.abs(z)) < tolerance:
        raise ValueError("Curva passa demasiadamente perto do ponto critico")
    if abs(z[-1] - z[0]) > 1e-6 * max(1.0, abs(z[0])):
        z = np.append(z, z[0])
    increments = np.angle(z[1:] / z[:-1])
    return int(np.rint(np.sum(increments) / (2.0 * np.pi)))


def nyquist_analysis(tf: TransferFunction, gain: float = 1.0, samples_axis: int = 6001,
                     samples_arc: int = 801) -> dict[str, object]:
    contour_s = nyquist_contour(tf, samples_axis=samples_axis, samples_arc=samples_arc)
    mapped = evaluate_s(tf, contour_s, gain=gain)
    w_ccw = winding_number(mapped, point=-1.0 + 0j)
    p = int(np.count_nonzero(np.real(tf.poles) > 1e-9))
    boundary_poles = int(np.count_nonzero((np.abs(np.real(tf.poles)) < 1e-9)))
    # Convencao do enunciado: N positivo no sentido horario; portanto N=-w_ccw.
    n_clockwise = -w_ccw
    z = p + n_clockwise
    return {
        "contour_s": contour_s,
        "mapped_curve": mapped,
        "winding_ccw": w_ccw,
        "encirclements_clockwise_N": n_clockwise,
        "open_loop_rhp_poles_P": p,
        "open_loop_imaginary_axis_poles": boundary_poles,
        "closed_loop_rhp_poles_Z": z,
        "convention": "Z = P + N; N positivo para envoltorios horarios",
        "boundary_pole_treatment": "polos no eixo jω excluidos por indentacao no semiplano direito; nao contabilizados em P",
    }
