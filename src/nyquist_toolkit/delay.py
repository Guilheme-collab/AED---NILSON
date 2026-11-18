"""Atraso puro exato no dominio da frequencia e aproximacao racional de Pade."""
from __future__ import annotations
import math
import numpy as np
from .models import TransferFunction


def pade_delay(delay_s: float, order: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Retorna numerador e denominador de [order/order] para exp(-delay*s)."""
    if delay_s < 0 or not np.isfinite(delay_s) or order < 1:
        raise ValueError("Atraso finito nao negativo e ordem >= 1 sao obrigatorios")
    coeff = []
    for k in range(order + 1):
        value = (math.factorial(2 * order - k) * math.factorial(order)) / (
            math.factorial(2 * order) * math.factorial(k) * math.factorial(order - k)
        )
        coeff.append(value * delay_s**k)
    den_ascending = np.asarray(coeff, dtype=float)
    num_ascending = den_ascending * np.asarray([(-1.0) ** k for k in range(order + 1)])
    return num_ascending[::-1], den_ascending[::-1]


def with_pade(tf: TransferFunction, order: int = 3) -> TransferFunction:
    if tf.delay == 0:
        return tf
    n_delay, d_delay = pade_delay(tf.delay, order)
    return TransferFunction(np.convolve(tf.numerator, n_delay),
                            np.convolve(tf.denominator, d_delay), 0.0,
                            f"{tf.name} com Pade-{order}")
