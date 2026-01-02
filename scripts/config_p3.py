# scripts/config_p3.py
from __future__ import annotations

import sys
from pathlib import Path

# Raíz del repo de Proyecto 3 (Algoritmo-de-Dijkstra/)
ROOT = Path(__file__).resolve().parent.parent

# Ruta al repo del Proyecto 1 (submódulo)
P1_ROOT = ROOT / "lib" / "Biblioteca-grafos"

# Para que funcione: import src.modelos, import src.grafo, etc.
sys.path.insert(0, str(P1_ROOT))

from src import modelos  # noqa: E402


# Dos tamanos por modelo (pocos / muchos)
N_POCOS = 30
N_MUCHOS = 500

# Semillas fijas para reproducibilidad
SEED_BASE_POCOS = 123
SEED_BASE_MUCHOS = 456

# Pesos (uniformes)
W_MIN = 1.0
W_MAX = 10.0
SEED_PESOS_POCOS = 111
SEED_PESOS_MUCHOS = 222


def build_base_graph(modelo: str, n: int, seed: int):
    """
    Construye un grafo (Proyecto 1) de acuerdo a cada modelo.
    Ajusta parámetros para que el grafo no sea ridículamente denso.
    """
    dirigido = False

    if modelo == "Malla":
        # Para aproximar n nodos: m*n = n
        if n == 30:
            m, k = 5, 6
        else:
            m, k = 20, 25  # 500
        return modelos.grafoMalla(m, k, dirigido=dirigido)

    if modelo == "ErdosRenyi":
        # m aristas ~ 2n (sparse) para ambos tamaños
        m = 2 * n
        return modelos.grafoErdosRenyi(n, m, dirigido=dirigido, seed=seed)

    if modelo == "Gilbert":
        # p baja para n grande
        p = 0.12 if n == 30 else 0.01
        return modelos.grafoGilbert(n, p, dirigido=dirigido, seed=seed)

    if modelo == "Geografico":
        # r típica (unit square)
        r = 0.30 if n == 30 else 0.06
        return modelos.grafoGeografico(n, r, dirigido=dirigido, seed=seed)

    if modelo == "BarabasiAlbert":
        d = 3
        return modelos.grafoBarabasiAlbert(n, d, dirigido=dirigido, seed=seed)

    if modelo == "DorogovtsevMendes":
        return modelos.grafoDorogovtsevMendes(n, dirigido=dirigido, seed=seed)

    raise ValueError(f"Modelo desconocido: {modelo}")
