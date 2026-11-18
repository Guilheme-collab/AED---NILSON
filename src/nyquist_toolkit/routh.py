"""Tabela de Routh-Hurwitz com casos especiais de primeira coluna nula e linha nula."""
from __future__ import annotations
import numpy as np


def routh_table(coefficients: np.ndarray | list[float], epsilon: float = 1e-9) -> dict[str, object]:
    c = np.asarray(coefficients, dtype=float).reshape(-1)
    c = np.trim_zeros(c, trim="f")
    if c.size < 2 or not np.all(np.isfinite(c)):
        raise ValueError("Polinomio real nao constante e finito e obrigatorio")
    if epsilon <= 0:
        raise ValueError("epsilon deve ser positivo")
    n = c.size - 1
    cols = (n + 2) // 2
    table = np.zeros((n + 1, cols), dtype=float)
    table[0, :len(c[::2])] = c[::2]
    table[1, :len(c[1::2])] = c[1::2]
    special_first_column: list[int] = []
    special_zero_rows: list[int] = []

    for i in range(2, n + 1):
        if np.all(np.abs(table[i - 1]) < epsilon):
            special_zero_rows.append(i - 1)
            power = n - (i - 2)
            aux = table[i - 2].copy()
            powers = np.arange(power, -1, -2, dtype=float)
            derivative = aux[:len(powers)] * powers
            table[i - 1, :len(derivative)] = derivative
        if abs(table[i - 1, 0]) < epsilon:
            special_first_column.append(i - 1)
            table[i - 1, 0] = epsilon
        for j in range(cols - 1):
            table[i, j] = (
                table[i - 1, 0] * table[i - 2, j + 1]
                - table[i - 2, 0] * table[i - 1, j + 1]
            ) / table[i - 1, 0]
        if np.all(np.abs(table[i]) < epsilon) and i < n:
            # A linha toda nula pode surgir depois do calculo e sera tratada na iteracao seguinte.
            pass

    first_col = table[:, 0].copy()
    signs = np.sign(first_col)
    signs[signs == 0] = 1
    sign_changes = int(np.count_nonzero(signs[1:] * signs[:-1] < 0))
    # A tabela identifica polos no semiplano direito; uma raiz no eixo imaginario
    # e detectada separadamente para nao classificar estabilidade marginal como estrita.
    roots = np.roots(c)
    axis_roots = roots[np.abs(np.real(roots)) <= 1e-8 * np.maximum(1.0, np.abs(roots))]
    return {
        "table": table,
        "first_column": first_col,
        "sign_changes": sign_changes,
        "rhp_pole_count": sign_changes,
        "imaginary_axis_pole_count": int(axis_roots.size),
        "imaginary_axis_roots": axis_roots,
        "strictly_stable": sign_changes == 0 and axis_roots.size == 0,
        "special_first_column_zero_rows": special_first_column,
        "special_all_zero_rows": special_zero_rows,
    }


def routh_stability(coefficients: np.ndarray | list[float]) -> bool:
    result = routh_table(coefficients)
    return bool(result["strictly_stable"])
