"""Mapa de Madrid desde el Callejero oficial del Ayuntamiento (datos.madrid.es), sin OpenStreetMap.

Reconstruye cada vía uniendo sus cruces (árbol de expansión mínima por calle) y la clasifica
por tipo de vía en capas/plumas. Fuente: "Callejero oficial: cruces" (CSV) de datos.madrid.es.

  python mapa_madrid_callejero.py cruces.csv -o madrid.svg --papel A3 --radio 2600
  --centro 40.4168,-3.7038 (Puerta del Sol)  --titulo "MADRID"
"""
import argparse
import csv
import math
from collections import defaultdict
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial.distance import pdist, squareform
from shapely.geometry import LineString, box
import plotlib

PRINCIPALES = {"AVENIDA", "PASEO", "AUTOVIA", "AUTOPISTA", "CARRETERA", "RONDA", "GRAN VIA", "BULEVAR", "VIA"}
PEQUENAS = {"CAMINO", "PASAJE", "CALLEJON", "SENDA", "COLONIA", "PARTICULAR", "VEREDA", "CAÑADA", "ARROYO", "GALERIA", "PASADIZO"}


def latlon_to_utm30(lat, lon):
    """WGS84 -> UTM zona 30N (m). Suficiente para dibujar."""
    a, f, k0 = 6378137.0, 1 / 298.257223563, 0.9996
    e2 = f * (2 - f); ep2 = e2 / (1 - e2)
    lat, lon = math.radians(lat), math.radians(lon)
    lon0 = math.radians(-3)
    N = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    T = math.tan(lat) ** 2; C = ep2 * math.cos(lat) ** 2; A = math.cos(lat) * (lon - lon0)
    M = a * ((1 - e2 / 4 - 3 * e2 ** 2 / 64) * lat - (3 * e2 / 8 + 3 * e2 ** 2 / 32) * math.sin(2 * lat)
             + (15 * e2 ** 2 / 256) * math.sin(4 * lat))
    x = k0 * N * (A + (1 - T + C) * A ** 3 / 6) + 500000
    y = k0 * (M + N * math.tan(lat) * (A ** 2 / 2 + (5 - T + 9 * C) * A ** 4 / 24))
    return x, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cruces"); ap.add_argument("-o", "--salida", default="madrid.svg")
    ap.add_argument("--papel", default="A3"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--centro", default="40.4168,-3.7038")
    ap.add_argument("--radio", type=float, default=2600, help="media anchura del lado mayor (m)")
    ap.add_argument("--max-tramo", type=float, default=450, help="no unir cruces a más de N m")
    ap.add_argument("--titulo", default="MADRID")
    ap.add_argument("--direcciones", help="CSV de direcciones del callejero: afina la forma de las calles curvas")
    a = ap.parse_args()

    pts, clase = defaultdict(set), {}
    cruce_pts = set()
    with open(a.cruces, encoding="latin-1", newline="") as f:
        r = csv.reader(f, delimiter=";")
        next(r)
        for row in r:
            try:
                x, y = int(row[10]) / 100, int(row[11]) / 100
            except ValueError:
                continue
            pts[row[0]].add((x, y)); clase[row[0]] = row[2].strip(); cruce_pts.add((x, y))
            pts[row[5]].add((x, y)); clase.setdefault(row[5], row[7].strip())

    if a.direcciones:  # números impares de cada vía: siguen la curva de la calle (a un lado)
        import re
        with open(a.direcciones, encoding="latin-1", newline="") as f:
            r = csv.reader(f, delimiter=";")
            next(r)
            for row in r:
                lit = row[5]
                mnum = re.match(r"NUM0*(\d+)", lit.strip())
                if not mnum or int(mnum.group(1)) % 2 == 0 or row[2].strip() in PRINCIPALES:
                    continue
                try:
                    pts[row[1]].add((int(row[16]) / 100, int(row[17]) / 100))
                except ValueError:
                    pass

    lat, lon = map(float, a.centro.split(","))
    cx, cy = latlon_to_utm30(lat, lon)
    w, h = plotlib.paper(a.papel, a.horizontal)
    hw, hh = a.radio * w / max(w, h), a.radio * h / max(w, h)
    clip = box(cx - hw, cy - hh, cx + hw, cy + hh)
    big = clip.buffer(a.max_tramo)

    layers = {"principales": [], "calles": [], "pequenas": []}
    for code, P in pts.items():
        P = np.array([p for p in P if big.bounds[0] <= p[0] <= big.bounds[2] and big.bounds[1] <= p[1] <= big.bounds[3]])
        if len(P) < 2:
            continue
        D = squareform(pdist(P))
        mst = minimum_spanning_tree(D).tocoo()
        c = clase.get(code, "CALLE")
        layer = "principales" if c in PRINCIPALES else "pequenas" if c in PEQUENAS else "calles"
        edges = [(i, j, d) for i, j, d in zip(mst.row, mst.col, mst.data) if d <= a.max_tramo]
        if a.direcciones:  # poda "espinas": hojas que son portales y están a < 40 m
            deg = np.bincount(np.r_[[e[0] for e in edges], [e[1] for e in edges]].astype(int), minlength=len(P)) if edges else []
            is_cruce = [tuple(p) in cruce_pts for p in P]
            edges = [(i, j, d) for i, j, d in edges
                     if not (d < 40 and ((deg[i] == 1 and not is_cruce[i]) or (deg[j] == 1 and not is_cruce[j])))]
        for i, j, d in edges:
            seg = LineString([P[i], P[j]]).intersection(clip)
            if not seg.is_empty and seg.geom_type == "LineString":
                layers[layer].append(np.array(seg.coords))

    # coordenadas -> mm (Y hacia abajo), dejando hueco abajo para el título
    m, foot = 18, 32 if a.titulo else 0
    s = min((w - 2 * m) / (2 * hw), (h - 2 * m - foot) / (2 * hh))
    ox, oy = (w - 2 * hw * s) / 2, m
    def tr(l):
        l = np.asarray(l)
        return np.c_[ox + (l[:, 0] - (cx - hw)) * s, oy + ((cy + hh) - l[:, 1]) * s]
    layers = {k: [tr(l) for l in v] for k, v in layers.items()}
    x0, y0, x1, y1 = ox, oy, ox + 2 * hw * s, oy + 2 * hh * s
    layers["marco"] = [np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])]
    plotlib.write_svg(a.salida, layers, (w, h),
                      colors={"principales": "#111", "calles": "#444", "pequenas": "#888", "marco": "#111"},
                      widths={"principales": 0.7, "calles": 0.3, "pequenas": 0.2, "marco": 0.8})
    if a.titulo:  # texto de un solo trazo (Hershey) con vpype, para que el plotter lo dibuje
        import subprocess, shutil, os
        vp = shutil.which("vpype") or os.path.join(os.path.dirname(__import__("sys").executable), "vpype")
        sub = f"{lat:.4f}° N  ·  {abs(lon):.4f}° {'W' if lon < 0 else 'E'}"
        tmp = a.salida + ".tmp.svg"
        subprocess.run([vp, "read", "--no-crop", a.salida,
                        "text", "-f", "futuram", "-s", "60", "-a", "center", "-p", f"{w/2}mm", f"{y1 + 17}mm", "-l", "5", a.titulo,
                        "text", "-f", "futural", "-s", "18", "-a", "center", "-p", f"{w/2}mm", f"{y1 + 25}mm", "-l", "5", sub,
                        "color", "-l", "5", "#111111", "penwidth", "-l", "5", "0.5mm",
                        "pagesize", f"{w}mmx{h}mm", "write", tmp], check=True)
        os.replace(tmp, a.salida)
        print("Título añadido (capa 5 = texto)")


if __name__ == "__main__":
    main()
