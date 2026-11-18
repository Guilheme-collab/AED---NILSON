"""Avaliacao de resposta em frequencia, Bode e margens de estabilidade."""
from __future__ import annotations
import numpy as np
from .models import TransferFunction


def evaluate_s(tf: TransferFunction, s: np.ndarray | complex, gain: float = 1.0) -> np.ndarray:
    s_arr = np.asarray(s, dtype=complex)
    den = np.polyval(tf.denominator, s_arr)
    if np.any(np.abs(den) < 1e-14):
        raise ZeroDivisionError("Avaliacao sobre polo da funcao de transferencia")
    rational = float(gain) * np.polyval(tf.numerator, s_arr) / den
    return rational * np.exp(-tf.delay * s_arr)


def frequency_response(tf: TransferFunction, omega: np.ndarray, gain: float = 1.0) -> np.ndarray:
    w = np.asarray(omega, dtype=float)
    if np.any(w < 0) or not np.all(np.isfinite(w)):
        raise ValueError("omega deve conter frequencias finitas e nao negativas")
    return evaluate_s(tf, 1j * w, gain=gain)


def bode_data(tf: TransferFunction, omega: np.ndarray, gain: float = 1.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h = frequency_response(tf, omega, gain=gain)
    magnitude_db = 20.0 * np.log10(np.maximum(np.abs(h), np.finfo(float).tiny))
    phase_deg = np.unwrap(np.angle(h)) * 180.0 / np.pi
    return np.asarray(omega, dtype=float), magnitude_db, phase_deg


def _zero_db_crossings(logw: np.ndarray, values: np.ndarray) -> list[float]:
    out: list[float] = []
    for i in range(len(values) - 1):
        a, b = values[i], values[i + 1]
        if a == 0:
            out.append(float(np.exp(logw[i])))
        elif a * b < 0 or b == 0:
            frac = -a / (b - a) if b != a else 0.0
            out.append(float(np.exp(logw[i] + frac * (logw[i + 1] - logw[i]))))
    return sorted(set(round(x, 12) for x in out))


def stability_margins(tf: TransferFunction, omega: np.ndarray, gain: float = 1.0) -> dict[str, float | None | list[float]]:
    """Calcula MG/MF por interpolacao em log-frequencia; nao usa toolbox de controle."""
    w, mag_db, phase_deg = bode_data(tf, omega, gain=gain)
    if len(w) < 2 or np.any(w <= 0) or np.any(np.diff(w) <= 0):
        raise ValueError("omega deve ser estritamente crescente e positivo")
    logw = np.log(w)
    gain_cross = _zero_db_crossings(logw, mag_db)
    phase_margins: list[float] = []
    delay_candidates: list[float] = []
    for wc in gain_cross:
        phase = float(np.interp(np.log(wc), logw, phase_deg))
        margin = 180.0 + phase
        phase_margins.append(margin)
        if margin > 0:
            delay_candidates.append(float(np.deg2rad(margin) / wc))

    phase_cross: list[tuple[float, float]] = []
    low = int(np.floor((np.min(phase_deg) + 180.0) / 360.0)) - 1
    high = int(np.ceil((np.max(phase_deg) + 180.0) / 360.0)) + 1
    for k in range(low, high + 1):
        target = -180.0 - 360.0 * k
        shifted = phase_deg - target
        for wc in _zero_db_crossings(logw, shifted):
            mag = float(np.interp(np.log(wc), logw, mag_db))
            phase_cross.append((wc, -mag))
    gm_values = [v for _, v in phase_cross]
    gm = min(gm_values) if gm_values else None
    pm = min(phase_margins) if phase_margins else None
    wgc = gain_cross[0] if gain_cross else None
    delay_margin = min(delay_candidates) if delay_candidates else None
    return {
        "gain_margin_db": gm,
        "phase_margin_deg": pm,
        "gain_crossover_rad_s": wgc,
        "phase_crossovers_rad_s": [w for w, _ in phase_cross],
        "gain_crossovers_rad_s": gain_cross,
        "delay_margin_s": delay_margin,
    }
