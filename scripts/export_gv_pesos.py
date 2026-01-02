# scripts/export_gv_pesos.py
from __future__ import annotations
from pathlib import Path


def export_graphviz(g, path: str, peso_fn=None):
    """
    Exporta un .gv:
    - g: Grafo (P1) o GrafoDijkstra
    - peso_fn(u_id, v_id) -> float (si quieres label de peso en la arista)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    directed = getattr(g, "dirigido", False)
    head = "digraph G {" if directed else "graph G {"
    conn = "->" if directed else "--"

    lines = [head]
    lines.append("  overlap=false;")

    # nodos
    for n in g.nodos():
        if n.x is not None and n.y is not None:
            lines.append(f'  "{n.id}" [pos="{n.x},{n.y}!"];')
        else:
            lines.append(f'  "{n.id}";')

    # aristas
    for a in g.aristas():
        u, v = a.origen.id, a.destino.id
        if peso_fn is None:
            lines.append(f'  "{u}" {conn} "{v}";')
        else:
            w = float(peso_fn(u, v))
            lines.append(f'  "{u}" {conn} "{v}" [label="{w:.2f}"];')

    lines.append("}")
    path.write_text("\n".join(lines), encoding="utf-8")
