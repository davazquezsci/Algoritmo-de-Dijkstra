# -*- coding: utf-8 -*-
# Gephi Scripting Plugin (Jython 2.5)
# Batch: importar .gv, aplicar layout + appearance ranking, exportar PNG con labels
#
# - Soporta dos estructuras de entrada:
#   A) outputs/gv/<modelo>/*.gv
#   B) outputs/gv/*.gv   (sin subcarpetas)  -> exporta en outputs/img/_root
#
# - Fuerza labels reales para que Preview los renderice:
#   * Node label = ID del nodo
#   * Edge label = weight (2 decimales)
#
# - Preview:
#   * Node labels: Serif 20 blanco + outline negro
#   * Edge labels: Serif 14 Italic negro
#   * Arrows: solo en árboles (_bfs/_dfs/_dijkstra)
#
# Nota: este script corre dentro de Gephi (Window -> Scripting), NO en Python normal.

print("=== START gephi_batch_export ===")

import os
from java.io import File
from org.openide.util import Lookup

from org.gephi.project.api import ProjectController
from org.gephi.io.importer.api import ImportController
from org.gephi.io.processor.plugin import DefaultProcessor
from org.gephi.graph.api import GraphController

# Layouts
from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2
from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2Builder

from java.util import Random as JRandom

# Preview + Export
from org.gephi.preview.api import PreviewController, PreviewProperty
from org.gephi.io.exporter.api import ExportController

# Font/Color
from java.awt import Color, Font


# ---- AJUSTA ESTO A TU RUTA ----
# Ejemplos:
# ROOT = r"P:\Algoritmo-de-Dijkstra"
# ROOT = r"C:\P2"
ROOT = r"C:\P2"

GV_DIR = File(ROOT, "outputs\\gv")
IMG_DIR = File(ROOT, "outputs\\img")

print("ROOT =", ROOT)
print("GV_DIR =", GV_DIR.getAbsolutePath(), "exists?", GV_DIR.exists(), "isDir?", GV_DIR.isDirectory())
print("IMG_DIR =", IMG_DIR.getAbsolutePath(), "exists?", IMG_DIR.exists(), "isDir?", IMG_DIR.isDirectory())

# PNG
PNG_WIDTH  = 2400
PNG_HEIGHT = 1600

# Layout config
FA2_ITERS_1 = 400   # FA2 sin prevent overlap
FA2_ITERS_2 = 400   # FA2 con prevent overlap (adjust sizes)

# Appearance sizes
MIN_NODE_SIZE = 5.0
MAX_NODE_SIZE = 40.0


def ensure_dir(path_or_file):
    if isinstance(path_or_file, File):
        if not path_or_file.exists():
            path_or_file.mkdirs()
    else:
        if not os.path.exists(path_or_file):
            os.makedirs(path_or_file)


def is_tree(name):
    name = name.lower()
    return ("_bfs" in name) or ("_dfs" in name) or ("_dijkstra" in name)


def randomize_positions(workspace, seed=1337, scale=1000.0):
    """
    Inicializa posiciones (x,y) al azar sin depender del Random layout plugin.
    Evita API mismatch de layouts en 0.10.x.
    """
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()

    rng = JRandom(seed)

    graph.writeLock()
    try:
        it = graph.getNodes().iterator()
        while it.hasNext():
            n = it.next()
            x = (rng.nextDouble() - 0.5) * scale
            y = (rng.nextDouble() - 0.5) * scale
            n.setX(float(x))
            n.setY(float(y))
    finally:
        graph.writeUnlock()


def run_forceatlas2(workspace, iters, prevent_overlap):
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)

    fa2 = ForceAtlas2(ForceAtlas2Builder())
    fa2.setGraphModel(graphModel)

    # Parámetros base
    fa2.setScalingRatio(2.0)
    fa2.setGravity(1.0)
    fa2.setStrongGravityMode(False)
    fa2.setLinLogMode(False)

    # Prevent overlap ~= Adjust sizes
    fa2.setAdjustSizes(True if prevent_overlap else False)

    fa2.initAlgo()
    for i in range(iters):
        fa2.goAlgo()
    fa2.endAlgo()


def apply_degree_size_ranking(workspace, min_size, max_size):
    """
    Ranking por degree -> size, aplicado manualmente:
    size = min_size + (deg - deg_min)/(deg_max-deg_min) * (max_size-min_size)
    """
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()

    degrees = {}
    deg_min = None
    deg_max = None

    it = graph.getNodes().iterator()
    while it.hasNext():
        n = it.next()
        d = n.getInDegree() + n.getOutDegree()
        degrees[n.getId()] = d

        if deg_min is None or d < deg_min:
            deg_min = d
        if deg_max is None or d > deg_max:
            deg_max = d

    denom = float(deg_max - deg_min) if (deg_max is not None and deg_min is not None and deg_max != deg_min) else 1.0
    span = float(max_size - min_size)

    graph.writeLock()
    try:
        it2 = graph.getNodes().iterator()
        while it2.hasNext():
            n = it2.next()
            d = degrees.get(n.getId(), 0)
            t = float(d - deg_min) / denom
            size = float(min_size + t * span)
            n.setSize(size)
    finally:
        graph.writeUnlock()


def force_labels(workspace, want_node_labels=True, want_edge_labels=True):
    """
    Garantiza que existan labels reales en el grafo:
    - Nodos: label = id (Preview usa Node.getLabel(), no el ID)
    - Aristas: label = peso (edge.getWeight()) con 2 decimales
    """
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()

    graph.writeLock()
    try:
        if want_node_labels:
            itn = graph.getNodes().iterator()
            while itn.hasNext():
                n = itn.next()
                if n.getLabel() is None or len(n.getLabel()) == 0:
                    n.setLabel(str(n.getId()))

        if want_edge_labels:
            ite = graph.getEdges().iterator()
            while ite.hasNext():
                e = ite.next()
                w = e.getWeight()  # si no hay weight, suele ser 1.0
                e.setLabel("%.2f" % float(w))
    finally:
        graph.writeUnlock()


def configure_preview(workspace, tree_mode, show_node_labels, show_edge_labels):
    previewController = Lookup.getDefault().lookup(PreviewController)
    previewModel = previewController.getModel(workspace)
    props = previewModel.getProperties()

    # =========================
    # EDGES
    # =========================
    props.putValue(PreviewProperty.SHOW_EDGES, True)
    props.putValue(PreviewProperty.EDGE_CURVED, (not tree_mode))
    props.putValue(PreviewProperty.EDGE_THICKNESS, 1.0)
    props.putValue(PreviewProperty.EDGE_OPACITY, 100)

    # =========================
    # NODE LABELS  (CLAVE)
    # =========================
    props.putValue(PreviewProperty.SHOW_NODE_LABELS, show_node_labels)

    # ❗ MUY IMPORTANTE
    # Evita que el tamaño dependa del tamaño del nodo
    props.putValue(PreviewProperty.NODE_LABEL_PROPORTIONAL_SIZE, False)

    props.putValue(PreviewProperty.NODE_LABEL_FONT, Font("Arial", Font.PLAIN, 20))
    props.putValue(PreviewProperty.NODE_LABEL_COLOR, Color(0, 0, 0))  # negro
    props.putValue(PreviewProperty.NODE_LABEL_OUTLINE_SIZE, 1.0)
    props.putValue(PreviewProperty.NODE_LABEL_OUTLINE_COLOR, Color(255, 255, 255))
    props.putValue(PreviewProperty.NODE_LABEL_OUTLINE_OPACITY, 100)

    # Caja OFF (como en tu captura)
    props.putValue(PreviewProperty.NODE_LABEL_SHOW_BOX, False)

    # =========================
    # EDGE LABELS
    # =========================
    props.putValue(PreviewProperty.SHOW_EDGE_LABELS, show_edge_labels)
    props.putValue(PreviewProperty.EDGE_LABEL_FONT, Font("Arial", Font.PLAIN, 14))
    props.putValue(PreviewProperty.EDGE_LABEL_COLOR, Color(0, 0, 0))
    props.putValue(PreviewProperty.EDGE_LABEL_OUTLINE_SIZE, 1.0)
    props.putValue(PreviewProperty.EDGE_LABEL_OUTLINE_COLOR, Color(255, 255, 255))
    props.putValue(PreviewProperty.EDGE_LABEL_OUTLINE_OPACITY, 100)

    # =========================
    # REFRESH (OBLIGATORIO)
    # =========================
    previewController.refreshPreview(workspace)



def export_png(workspace, out_file):
    exportController = Lookup.getDefault().lookup(ExportController)
    pngExporter = exportController.getExporter("png")

    pngExporter.setWidth(PNG_WIDTH)
    pngExporter.setHeight(PNG_HEIGHT)

    if isinstance(out_file, File):
        exportController.exportFile(out_file, pngExporter)
    else:
        exportController.exportFile(File(out_file), pngExporter)


def iter_gv_targets(gv_root):
    """
    Devuelve una lista de tuplas (input_dir, output_dir_name)
    - Si hay subdirectorios, procesa cada uno.
    - Si NO hay subdirectorios, procesa la raíz como "_root".
    """
    children = gv_root.listFiles()
    if children is None:
        return []

    subdirs = [f for f in children if f.isDirectory()]
    subdirs.sort(key=lambda f: f.getName().lower())

    if len(subdirs) == 0:
        return [(gv_root, "_root")]
    else:
        return [(d, d.getName()) for d in subdirs]


def main():
    pc = Lookup.getDefault().lookup(ProjectController)
    importController = Lookup.getDefault().lookup(ImportController)

    if not GV_DIR.exists():
        print("No existe GV_DIR:", GV_DIR.getAbsolutePath())
        raise IOError("GV_DIR no existe")

    ensure_dir(IMG_DIR)

    targets = iter_gv_targets(GV_DIR)
    if len(targets) == 0:
        print("No se pudo listar o no hay contenido en:", GV_DIR.getAbsolutePath())
        return

    for (in_dir, out_name) in targets:
        out_dir = File(IMG_DIR, out_name)
        ensure_dir(out_dir)

        files_here = in_dir.listFiles()
        if files_here is None:
            continue

        gv_files = [f for f in files_here if f.isFile() and f.getName().lower().endswith(".gv")]
        gv_files.sort(key=lambda f: f.getName().lower())

        if len(gv_files) == 0:
            print("Sin .gv en:", in_dir.getAbsolutePath())
            continue

        for gv_file in gv_files:
            name = gv_file.getName()[:-3]  # quita ".gv"
            out_png = File(out_dir, name + ".png")

            print("Importando:", gv_file.getAbsolutePath())

            pc.newProject()
            workspace = pc.getCurrentWorkspace()

            container = importController.importFile(gv_file)
            importController.process(container, DefaultProcessor(), workspace)

            tree_mode = is_tree(name)

            # 1) Random layout
            randomize_positions(workspace, seed=1337, scale=1000.0)

            # 2) ForceAtlas2 SIN prevent overlap
            run_forceatlas2(workspace, FA2_ITERS_1, prevent_overlap=False)

            # 3) Appearance: Ranking Degree -> Size
            apply_degree_size_ranking(workspace, MIN_NODE_SIZE, MAX_NODE_SIZE)

            # 4) ForceAtlas2 CON prevent overlap
            run_forceatlas2(workspace, FA2_ITERS_2, prevent_overlap=True)

            # 5) Labels reales + Preview
            force_labels(workspace, want_node_labels=True, want_edge_labels=True)
            configure_preview(workspace, tree_mode, show_node_labels=True, show_edge_labels=True)

            # Refresca justo antes de exportar (extra estabilidad)
            Lookup.getDefault().lookup(PreviewController).refreshPreview(workspace)

            # 6) Export
            export_png(workspace, out_png)

            print("Exportado:", out_png.getAbsolutePath())

    print("DONE.")


try:
    main()
    print("=== END gephi_batch_export ===")
except Exception:
    import traceback
    err = traceback.format_exc()
    print(err)

    # Guardar error dentro de ROOT/scripts
    try:
        scripts_dir = File(ROOT, "scripts")
        ensure_dir(scripts_dir)
        err_path = os.path.join(ROOT, "scripts", "gephi_batch_error.txt")
        f = open(err_path, "w")
        f.write(err)
        f.close()
        print("ERROR guardado en", err_path)
    except:
        pass

    print("=== END gephi_batch_export ===")
