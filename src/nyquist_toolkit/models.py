"""Modelos LIT racionais, com atraso puro opcional no canal de malha aberta."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class TransferFunction:
    """Funcao de transferencia N(s)/D(s) * exp(-delay*s), coeficientes em ordem decrescente."""
    numerator: np.ndarray
    denominator: np.ndarray
    delay: float = 0.0
    name: str = "G(s)"

    def __post_init__(self) -> None:
        # Copias propias impiden que mutaciones externas alteren un modelo congelado.
        num = np.array(self.numerator, dtype=float, copy=True).reshape(-1)
        den = np.array(self.denominator, dtype=float, copy=True).reshape(-1)
        if num.size == 0 or den.size < 2:
            raise ValueError("Numerador nao vazio e denominador de grau >= 1 sao obrigatorios")
        if not np.all(np.isfinite(num)) or not np.all(np.isfinite(den)):
            raise ValueError("Coeficientes devem ser finitos")
        if abs(den[0]) < 1e-15:
            raise ValueError("Coeficiente lider do denominador nao pode ser zero")
        if self.delay < 0 or not np.isfinite(self.delay):
            raise ValueError("O atraso deve ser finito e nao negativo")
        num = np.trim_zeros(num, trim="f")
        if num.size == 0:
            num = np.array([0.0])
        den = np.trim_zeros(den, trim="f")
        object.__setattr__(self, "numerator", num)
        object.__setattr__(self, "denominator", den)

    @property
    def poles(self) -> np.ndarray:
        return np.roots(self.denominator)

    @property
    def zeros(self) -> np.ndarray:
        return np.roots(self.numerator) if self.numerator.size > 1 else np.array([], dtype=complex)

    def scaled(self, gain: float) -> "TransferFunction":
        return TransferFunction(self.numerator * float(gain), self.denominator, self.delay, f"{gain:g}*{self.name}")

    def without_delay(self) -> "TransferFunction":
        return TransferFunction(self.numerator, self.denominator, 0.0, self.name)


def closed_loop_denominator(tf: TransferFunction, gain: float = 1.0) -> np.ndarray:
    """Denominador polinomial com realimentacao unitaria negativa (sem atraso puro)."""
    if tf.delay != 0:
        raise ValueError("Atraso puro nao gera denominador polinomial finito; use Padé explicitamente")
    n = tf.numerator
    d = tf.denominator
    if n.size < d.size:
        n = np.pad(n, (d.size - n.size, 0))
    elif n.size > d.size:
        d = np.pad(d, (n.size - d.size, 0))
    return d + float(gain) * n
