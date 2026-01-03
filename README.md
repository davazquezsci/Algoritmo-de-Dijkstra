# Proyecto 3 — Algoritmo de Dijkstra sobre una Biblioteca de Grafos

## Descripción general

En este proyecto se implementa el **algoritmo de Dijkstra** utilizando la biblioteca de grafos desarrollada previamente en el **Proyecto 1**.  
El objetivo es calcular, a partir de un nodo fuente \( s \), el **árbol de caminos más cortos** hacia todos los demás nodos del grafo.

El proyecto incluye:
- Generación de grafos aleatorios usando distintos modelos.
- Cálculo del árbol de caminos mínimos mediante Dijkstra.
- Exportación de grafos y resultados.
- Visualización automática con Gephi.

---

## Objetivo

Implementar el método:

```python
def Dijkstra(self, s):


en la clase Grafo, de tal forma que, dado un nodo fuente s, se calcule la distancia mínima desde s hacia todos los demás nodos, y se construya el árbol de caminos más cortos inducido por dichas distancias. 

## Estructura


    Proyecto-3/
    │
    ├── lib/
    │   └── Biblioteca-grafos/        # Proyecto 1 (submódulo)
    │       ├── src/
    │       │   ├── grafo.py
    │       │   └── modelos.py
    │
    ├── scripts/
    │   ├── dijkstra.py               # Implementación del algoritmo de Dijkstra
    │   ├── generar_grafos.py         # Generación de grafos aleatorios
    │   ├── generar_dijkstra.py       # Cálculo de árboles de caminos mínimos
    │   └── gephi_batch_export.py     # Exportación automática con Gephi
    │
    ├── outputs/
    │   ├── gv/
    │   │   ├── generados/            # Grafos originales
    │   │   └── dijkstra/             # Árboles de caminos más cortos
    │   │
    │   └── img/
    │       ├── generados/            # Visualizaciones de grafos originales
    │       └── dijkstra/             # Visualizaciones de árboles Dijkstra
    │
    ├── tests/
    │
    └── README.md


## Modelos de grafos utilizados

Se generan grafos a partir de los siguientes modelos:

    Erdős–Rényi

    Gilbert

    Malla

    Geográfico

    Barabási–Albert

    Dorogovtsev–Mendes

Para cada modelo se generan dos tamaños de grafo:

    Pocos nodos

    Muchos nodos 


## Algoritmo de Dijkstra

El algoritmo implementado:

    Utiliza pesos positivos en las aristas.

    Calcula la distancia mínima desde el nodo fuente s a todos los demás nodos.

    Construye un grafo dirigido que representa el árbol de caminos más cortos.

## Representación de la distancia

    La distancia mínima calculada desde el nodo fuente se almacena directamente en el grafo resultante:

    Como parte del nombre del nodo, por ejemplo:

        nodo_2 (22.45)


    donde 22.45 representa la distancia mínima desde el nodo fuente hasta nodo_2.

Esta información puede verificarse directamente inspeccionando los archivos del grafo exportados. 


## Visualización con Gephi

Los grafos se visualizan automáticamente usando Gephi (v0.10.x) mediante un script en Jython.

Convenciones de visualización

    Grafos generados:

        Aristas curvas

        Sin flechas

        Tamaño de nodos proporcional al grado

    Árboles de Dijkstra:

        Aristas rectas

        Dirigidas

        Tamaño de nodos uniforme

Nota importante sobre etiquetas (labels):
Para grafos medianos y grandes, mostrar etiquetas de nodos y aristas genera saturación visual y dificulta la interpretación de la estructura.
Por esta razón, las visualizaciones no muestran necesariamente los labels, aunque la información de distancia sí está presente en los datos del grafo.

Esta decisión sigue buenas prácticas de visualización de grafos y no afecta la validez de los resultados. 

## Entregables

El repositorio contiene:

    Código fuente del algoritmo de Dijkstra.

    Grafos generados (dos tamaños por modelo).

    Grafos calculados (árboles de caminos más cortos).

    Distancia mínima al nodo origen almacenada en los datos del grafo.

    Imágenes de visualización de todos los grafos generados y calculados. 

## Autor

    Daniel Vázquez
    Maestría en Ciencias de la Computación
    Instituto Politécnico Nacional (CIC-IPN)