"""Mapas de calles / ríos desde OpenStreetMap -> SVG por capas (una pluma por capa).

Ejemplos:
  python mapa.py --lugar "Madrid, Spain" --radio 2500 --papel A3 -o madrid.svg
  python mapa.py --punto 40.4168,-3.7038 --radio 1500 --circulo -o sol.svg
  python mapa.py --osm mi_zona.osm -o zona.svg          # archivo .osm descargado (sin internet)
Capas: 1-principales (pluma gruesa), 2-secundarias, 3-pequeñas (fina), 4-agua.
"""
import argparse
import numpy as np
from shapely.geometry import Point, LineString, MultiLineString, box
import plotlib

MAIN = {"motorway", "trunk", "primary", "motorway_link", "trunk_link", "primary_link"}
MID = {"secondary", "tertiary", "secondary_link", "tertiary_link"}


def classify(hw):
    hw = hw[0] if isinstance(hw, list) else hw
    return "principales" if hw in MAIN else "secundarias" if hw in MID else "pequenas"


def lines_of(geom):
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, LineString):
        return [np.array(geom.coords)]
    if isinstance(geom, MultiLineString):
        return [np.array(g.coords) for g in geom.geoms]
    if hasattr(geom, "geoms"):
        return [l for g in geom.geoms for l in lines_of(g)]
    if hasattr(geom, "exterior"):  # polígono -> contorno
        return [np.array(geom.exterior.coords)] + [np.array(i.coords) for i in geom.interiors]
    return []


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--lugar"); g.add_argument("--punto"); g.add_argument("--osm"); g.add_argument("--pbf", help="extracto .osm.pbf (p.ej. de download.geofabrik.de), sin internet")
    ap.add_argument("--radio", type=float, default=2000, help="metros")
    ap.add_argument("--papel", default="A3"); ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--circulo", action="store_true", help="recorte circular")
    ap.add_argument("--sin-agua", action="store_true")
    ap.add_argument("-o", "--salida", default="mapa.svg")
    a = ap.parse_args()

    import osmnx as ox
    if a.pbf:
        return from_pbf(a)
    if a.osm:
        G = ox.graph_from_xml(a.osm, simplify=True, retain_all=True)
    else:
        if a.lugar:
            lat, lon = ox.geocode(a.lugar)
        else:
            lat, lon = map(float, a.punto.split(","))
        G = ox.graph_from_point((lat, lon), dist=a.radio, network_type="all", retain_all=True)
    G = ox.project_graph(G)
    edges = ox.graph_to_gdfs(G, nodes=False)
    crs = edges.crs
    cx, cy = edges.union_all().centroid.coords[0] if a.osm else ox.projection.project_geometry(Point(lon, lat), to_crs=crs)[0].coords[0]

    w, h = plotlib.paper(a.papel, a.horizontal)
    r = a.radio
    clip = Point(cx, cy).buffer(r) if a.circulo else box(cx - r * w / max(w, h), cy - r * h / max(w, h), cx + r * w / max(w, h), cy + r * h / max(w, h))

    layers = {"principales": [], "secundarias": [], "pequenas": [], "agua": []}
    for hw, geom in zip(edges["highway"], edges.geometry):
        layers[classify(hw)] += lines_of(geom.intersection(clip))

    if not a.sin_agua and not a.osm:
        try:
            water = ox.features_from_point((lat, lon), {"natural": ["water", "coastline"], "waterway": True}, dist=a.radio)
            for geom in ox.projection.project_gdf(water, to_crs=crs).geometry:
                layers["agua"] += lines_of(geom.intersection(clip).boundary if hasattr(geom, "exterior") else geom.intersection(clip))
        except Exception as e:
            print("Sin capa de agua:", e)
    layers["marco"] = lines_of(clip.boundary)
    layers = {k: v for k, v in layers.items() if v}
    layers = plotlib.fit(layers, (w, h), margin_mm=20, flip_y=True)  # Y de mapas crece hacia arriba
    plotlib.write_svg(a.salida, layers, (w, h),
                      colors={"principales": "#111", "secundarias": "#333", "pequenas": "#777", "agua": "#1d70b8", "marco": "#111"},
                      widths={"principales": 0.8, "secundarias": 0.5, "pequenas": 0.25, "agua": 0.4, "marco": 1.0})


def from_pbf(a):
    import pyrosm
    osm = pyrosm.OSM(a.pbf)
    edges = osm.get_network(network_type="all")
    crs = edges.estimate_utm_crs()
    edges = edges.to_crs(crs)
    cx, cy = edges.union_all().centroid.coords[0]
    w, h = plotlib.paper(a.papel, a.horizontal)
    r = a.radio
    clip = Point(cx, cy).buffer(r) if a.circulo else box(cx - r * w / max(w, h), cy - r * h / max(w, h), cx + r * w / max(w, h), cy + r * h / max(w, h))
    layers = {"principales": [], "secundarias": [], "pequenas": [], "agua": []}
    for hw, geom in zip(edges["highway"], edges.geometry):
        layers[classify(hw)] += lines_of(geom.intersection(clip))
    if not a.sin_agua:
        try:
            nat = osm.get_natural()
            if nat is not None:
                nat = nat.to_crs(crs)
                for geom in nat[nat["natural"].isin(["water", "coastline"])].geometry:
                    layers["agua"] += lines_of(geom.intersection(clip))
        except Exception as e:
            print("Sin capa de agua:", e)
    layers["marco"] = lines_of(clip.boundary)
    layers = {k: v for k, v in layers.items() if v}
    layers = plotlib.fit(layers, (w, h), margin_mm=20, flip_y=True)
    plotlib.write_svg(a.salida, layers, (w, h),
                      colors={"principales": "#111", "secundarias": "#333", "pequenas": "#777", "agua": "#1d70b8", "marco": "#111"},
                      widths={"principales": 0.8, "secundarias": 0.5, "pequenas": 0.25, "agua": 0.4, "marco": 1.0})


if __name__ == "__main__":
    main()
