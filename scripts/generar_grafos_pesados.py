# scripts/generar_grafos_pesados.py
from __future__ import annotations

from pathlib import Path

from config_p3 import (
    ROOT,
    N_POCOS, N_MUCHOS,
    SEED_BASE_POCOS, SEED_BASE_MUCHOS,
    W_MIN, W_MAX, SEED_PESOS_POCOS, SEED_PESOS_MUCHOS,
    build_base_graph,
)
from grafo_dijkstra import GrafoDijkstra
from export_gv_pesos import export_graphviz


MODELOS = [
    "Malla",
    "ErdosRenyi",
    "Gilbert",
    "Geografico",
    "BarabasiAlbert",
    "DorogovtsevMendes",
]


def main():
    out_dir = ROOT / "outputs" / "gv" / "generados"

    for modelo in MODELOS:
        for tag, n, seed_base, seed_w in [
            ("pocos", N_POCOS, SEED_BASE_POCOS, SEED_PESOS_POCOS),
            ("muchos", N_MUCHOS, SEED_BASE_MUCHOS, SEED_PESOS_MUCHOS),
        ]:
            base = build_base_graph(modelo, n, seed_base)
            g = GrafoDijkstra.from_grafo(base)
            g.asignar_pesos_uniformes(W_MIN, W_MAX, seed=seed_w)

            path = out_dir / modelo / f"{modelo}_{tag}_n{n}.gv"
            export_graphviz(g, str(path), peso_fn=g.peso_arista)

            print(f"[OK] {path}")

    print("Listo: grafos generados con pesos.")


if __name__ == "__main__":
    main()
