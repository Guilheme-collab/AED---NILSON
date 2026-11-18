"""Lugar das raizes por varredura de ganho e pareamento de ramos."""
from __future__ import annotations
import numpy as np


def _assign(previous: np.ndarray, current: np.ndarray) -> np.ndarray:
    cost = np.abs(previous[:, None] - current[None, :])
    try:
        from scipy.optimize import linear_sum_assignment
        rows, cols = linear_sum_assignment(cost)
        order = np.empty_like(cols)
        order[rows] = cols
        return current[order]
    except Exception:
        # Fallback guloso para ambientes sem SciPy; os resultados continuam utilizaveis.
        remaining = list(range(len(current)))
        result = []
        for p in previous:
            k = min(remaining, key=lambda j: abs(p - current[j]))
            result.append(current[k]); remaining.remove(k)
        return np.asarray(result)


def root_locus(numerator: np.ndarray | list[float], denominator: np.ndarray | list[float],
               gains: np.ndarray | list[float]) -> tuple[np.ndarray, np.ndarray]:
    num = np.asarray(numerator, dtype=float).reshape(-1)
    den = np.asarray(denominator, dtype=float).reshape(-1)
    k_values = np.asarray(gains, dtype=float).reshape(-1)
    if den.size < 2 or num.size == 0 or np.any(k_values < 0):
        raise ValueError("Numerador/denominador validos e ganhos nao negativos sao obrigatorios")
    n = max(num.size, den.size)
    num = np.pad(num, (n - num.size, 0))
    den = np.pad(den, (n - den.size, 0))
    branches: list[np.ndarray] = []
    previous = None
    for gain in k_values:
        characteristic = den + gain * num
        characteristic = np.trim_zeros(characteristic, trim="f")
        roots = np.roots(characteristic)
        if previous is not None and len(roots) == len(previous):
            roots = _assign(previous, roots)
        branches.append(roots)
        previous = roots
    return k_values, np.asarray(branches, dtype=complex)
