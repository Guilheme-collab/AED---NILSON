"""Quatro cenarios de benchmark definidos para o projeto."""
from .models import TransferFunction


def benchmark_systems() -> dict[str, dict[str, object]]:
    return {
        "A": {"description": "Planta padrao, malha aberta estavel de terceira ordem",
              "tf": TransferFunction([1.0], [1.0, 6.0, 11.0, 6.0], name="A"), "gain": 1.0},
        "B": {"description": "Planta instavel em malha aberta (um polo no semiplano direito)",
              "tf": TransferFunction([1.0], [1.0, 1.0, -2.0], name="B"), "gain": 3.0},
        "C": {"description": "Planta de fase nao minima com zero no semiplano direito",
              "tf": TransferFunction([1.0, -1.0], [1.0, 3.0, 2.0], name="C"), "gain": 1.0},
        "D": {"description": "Planta de primeira ordem com atraso puro exato significativo",
              "tf": TransferFunction([1.0], [0.5, 1.0], delay=0.35, name="D"), "gain": 2.0},
    }
