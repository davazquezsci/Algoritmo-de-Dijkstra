# scripts/grafo_dijkstra.py
from __future__ import annotations

import heapq
import math
import random
from typing import Dict, Tuple, Any

from src.grafo import Grafo


class GrafoDijkstra(Grafo):
    """
    Extiende Grafo (Proyecto 1) SIN modificarlo:
    - Maneja pesos en un dict interno (por key de arista)
    - Implementa Dijkstra(s) y regresa el árbol SPT como Grafo (P1)
      con nodos renombrados "id (dist)".
    """

    def __init__(self, dirigido: bool = False):
        super().__init__(dirigido=dirigido)
        self._w: Dict[Tuple[Any, Any], float] = {}  # key_arista -> peso

    def add_arista(self, u_id, v_id, peso: float = 1.0) -> bool:
        ok = super().add_arista(u_id, v_id)
        if ok:
            if peso <= 0:
                raise ValueError("Dijkstra requiere pesos positivos (>0)")
            u = self.get_nodo(u_id)
            v = self.get_nodo(v_id)
            k = self._key_arista(u, v)
            self._w[k] = float(peso)
        return ok

    def set_peso(self, u_id, v_id, peso: float):
        if peso <= 0:
            raise ValueError("Dijkstra requiere pesos positivos (>0)")
        u = self.get_nodo(u_id)
        v = self.get_nodo(v_id)
        k = self._key_arista(u, v)
        if k not in self._aristas_key:
            raise KeyError(f"No existe arista entre {u_id} y {v_id}")
        self._w[k] = float(peso)

    def peso_arista(self, u_id, v_id) -> float:
        u = self.get_nodo(u_id)
        v = self.get_nodo(v_id)
        k = self._key_arista(u, v)
        return float(self._w.get(k, 1.0))  # default 1.0 si no se asignó

    @staticmethod
    def from_grafo(base: Grafo) -> "GrafoDijkstra":
        """Copia Grafo(P1) -> GrafoDijkstra (pesos por defecto = 1.0)."""
        g = GrafoDijkstra(dirigido=base.dirigido)
        for n in base.nodos():
            g.add_nodo(n.id, x=n.x, y=n.y)
        for a in base.aristas():
            g.add_arista(a.origen.id, a.destino.id, peso=1.0)
        return g

    def asignar_pesos_uniformes(self, w_min: float, w_max: float, seed: int):
        rng = random.Random(seed)
        for a in self.aristas():
            u, v = a.origen.id, a.destino.id
            self.set_peso(u, v, rng.uniform(w_min, w_max))

    def Dijkstra(self, s):
        """
        Regresa: (T, dist)
        - T: Grafo(P1) dirigido, árbol SPT desde s
        - dist: dict id_original -> distancia (float/inf)
        """
        if s not in self._nodos:
            raise KeyError(f"El nodo fuente {s} no existe en el grafo")

        dist = {n.id: math.inf for n in self.nodos()}
        parent = {n.id: None for n in self.nodos()}
        dist[s] = 0.0

        heap = [(0.0, s)]
        visited = set()

        while heap:
            d_u, u_id = heapq.heappop(heap)
            if u_id in visited:
                continue
            visited.add(u_id)

            for v in self.vecinos(u_id):
                v_id = v.id
                w = self.peso_arista(u_id, v_id)
                nd = d_u + w
                if nd < dist[v_id]:
                    dist[v_id] = nd
                    parent[v_id] = u_id
                    heapq.heappush(heap, (nd, v_id))

        def label(nid):
            if math.isinf(dist[nid]):
                return f"{nid} (inf)"
            return f"{nid} ({dist[nid]:.2f})"

        # Árbol dirigido para visualización (padre -> hijo)
        T = Grafo(dirigido=True)
        new_id = {nid: label(nid) for nid in dist.keys()}

        # nodos (con mismas coords)
        for nid, nodo in self._nodos.items():
            T.add_nodo(new_id[nid], x=nodo.x, y=nodo.y)

        # aristas del SPT
        for v_id, u_id in parent.items():
            if u_id is None:
                continue
            T.add_arista(new_id[u_id], new_id[v_id])

        return T, dist
